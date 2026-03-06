import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseTarget:
    def __init__(self, db_path: str = "tracked_article.txt"):
        self.db_path = Path(db_path)
        self._init_db()

    def _init_db(self):
        if not self.db_path.exists():
            try:
                self.db_path.touch()
                logger.info("Text database initialized successfully.")
            except Exception as e:
                logger.error(f"Database initialization error: {e}")

    def is_processed(self, article_url: str) -> bool:
        """檢查文章是否已經處理/寄送過"""
        if not self.db_path.exists():
            return False
            
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
                # 只要網址存在於檔案就算處理過，這樣方便使用者手動刪除整行
                for line in lines:
                    if article_url in line:
                        return True
            return False
        except Exception as e:
            logger.error(f"Database read error: {e}")
            return False

    def mark_as_processed(self, article_url: str, platform: str, author_id: str):
        """將文章標記為已處理"""
        if self.is_processed(article_url):
            return

        try:
            with open(self.db_path, 'a', encoding='utf-8') as f:
                # 寫成純文字，每一筆記錄為一行。
                f.write(f"[{platform}] {author_id} - {article_url}\n")
        except Exception as e:
            logger.error(f"Database write error: {e}")
