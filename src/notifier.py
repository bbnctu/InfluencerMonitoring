import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import List
from src.trackers.base import Article

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self, sender_account: str, sender_password: str):
        self.sender_account = sender_account
        self.sender_password = sender_password

    def send_notification(self, article: Article, receivers: List[str]):
        if not receivers:
            logger.warning("No receivers assigned for this notification.")
            return

        # 根據使用者需求調整信件標題：使用者ID + 新文章通知 + 文章標題
        subject = f"[{article.author}] 新文章通知 {article.title}"
        
        # 建立內文 (純文字，也可以改成 HTML)
        body = f"""偵測到 {article.author} 發布了新文章！

標題：{article.title}
時間：{article.created_at}
連結：{article.url}

--- 文章內容 ---
{article.content}
-----------------

本信件由 InfluencerMonitoring 系統自動發送。
"""

        msg = MIMEMultipart()
        msg['From'] = self.sender_account
        # 允越多個收件者
        msg['To'] = ", ".join(receivers)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            # Gmail SMTP 伺服器
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_account, self.sender_password)
                server.send_message(msg)
                logger.info(f"Successfully sent notification email to {receivers} for {article.title}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
