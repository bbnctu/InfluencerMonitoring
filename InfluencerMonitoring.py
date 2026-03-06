import schedule
import time
import logging
from typing import Dict, Any

from src.config import Config
from src.db import DatabaseTarget
from src.notifier import EmailNotifier
from src.trackers.ptt import PttTracker

# 設定 Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_influencer(inf_cfg: Dict[str, Any], db: DatabaseTarget, notifier: EmailNotifier):
    """檢查單一網紅是否有新文章"""
    inf_id = inf_cfg.get("id")
    platform = inf_cfg.get("platform", "").lower()
    board = inf_cfg.get("board", "")
    receivers = inf_cfg.get("receivers", [])

    logger.info(f"Checking updates for {inf_id} on {platform} - {board}")

    # 根據 platform 初始化不同的 tracker
    tracker = None
    if platform == "ptt":
        tracker = PttTracker(author_id=inf_id, board=board)
    else:
        logger.warning(f"Unsupported platform: {platform}")
        return

    # 抓取最新文章
    articles = tracker.fetch_latest_articles()
    
    for article in articles:
        # 檢查是否已在資料庫中
        if not db.is_processed(article.url):
            logger.info(f"New article found: {article.title}")
            
            # 寄信通知
            notifier.send_notification(article, receivers)
            
            # 寫入資料庫標記已完成
            db.mark_as_processed(article.url, platform, inf_id)
        else:
            logger.debug(f"Article already processed: {article.title}")

def main():
    logger.info("Starting Influencer Monitoring System...")
    
    # 讀取設定
    config_obj = Config()
    email_settings = config_obj.email_settings
    
    if not email_settings.get("sender_account") or not email_settings.get("sender_password"):
        logger.error("Email configuration is missing. Please update config.json")
        return

    notifier = EmailNotifier(
        sender_account=email_settings["sender_account"],
        sender_password=email_settings["sender_password"]
    )
    db = DatabaseTarget()

    influencers = config_obj.influencers
    if not influencers:
        logger.warning("No influencers found in config.json")
        return

    # 根據設定建立排程
    for inf in influencers:
        freq = inf.get("frequency_minutes", 60)
        logger.info(f"Scheduling check for {inf['id']} every {freq} minutes.")
        schedule.every(freq).minutes.do(check_influencer, inf_cfg=inf, db=db, notifier=notifier)
        
        # 啟動時先執行一次
        check_influencer(inf, db=db, notifier=notifier)

    logger.info("Scheduler is running. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("System gracefully stopped by user.")

if __name__ == "__main__":
    main()
