import requests
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
import logging
from src.trackers.base import BaseTracker, Article

logger = logging.getLogger(__name__)

class PttTracker(BaseTracker):
    """PTT 爬蟲 Tracker"""
    BASE_URL = "https://www.ptt.cc"

    def __init__(self, author_id: str, board: str):
        # 由於 PttTracker 特定屬於 ptt 平台
        super().__init__(author_id=author_id, platform="ptt", board=board)
        self.session = requests.Session()
        # 設定 cookie，避免 18 禁看板需要同意
        self.session.cookies.set('over18', '1', domain='www.ptt.cc')
        # 設定常見的 User-Agent 避免被阻擋
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive"
        })

    def fetch_latest_articles(self) -> List[Article]:
        articles = []
        # 使用搜尋功能找出該看版下該作者的發文
        search_url = f"{self.BASE_URL}/bbs/{self.board}/search?q=author:{self.author_id}"
        logger.info(f"Fetching: {search_url}")

        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # 在搜尋結果頁中抓取文章區塊
            # 注意: PTT 搜尋結果可能需要處理分頁，但通常我們只關心最新發文(第一頁)
            post_divs = soup.find_all("div", class_="r-ent")

            # 從最新的開始解析
            for div in post_divs:
                title_elem = div.find("div", class_="title").find("a")
                if not title_elem:
                    continue  # 文章可能被刪除，只有標題並無連結

                title = title_elem.text.strip()
                # 排除公告或其他不相關內容（如果不希望追蹤特定回覆可在此過濾，例如 startswith 'Re:'）
                # 取得文章網址
                article_url = self.BASE_URL + title_elem["href"]

                # 嘗試進入文章內文頁面抓取完整內文
                content, created_at = self._fetch_article_content(article_url)

                if created_at is None:
                    # 如果抓不到時間通常代表文章可能格式異常，暫用當下時間
                    created_at = datetime.now()

                article = Article(
                    title=title,
                    url=article_url,
                    author=self.author_id,
                    platform=self.platform,
                    board=self.board,
                    content=content,
                    created_at=created_at
                )

                articles.append(article)
                
            # 排序：確保最新的在最前面或是依需求而定。通常 PTT search 越上面越新
            # 根據使用者需求，限定只回傳最新的一篇文章
            if articles:
                return [articles[0]]
            
            return articles

        except Exception as e:
            logger.error(f"Error fetching PTT rules for {self.author_id} at {self.board}: {e}")
            return []

    def _fetch_article_content(self, url: str) -> tuple[str, datetime]:
        """進入內頁抓取完整內容與發文時間"""
        content_text = ""
        created_at = None

        try:
            resp = self.session.get(url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            main_content = soup.find(id="main-content")
            if not main_content:
                return "無法解析內文。", None

            # 抓取發文時間 (通常在屬性 span 中)
            meta_values = main_content.find_all('span', class_='article-meta-value')
            if len(meta_values) >= 4:
                # 預設發文時間在第四項 (作者, 看板, 標題, 時間)
                time_str = meta_values[3].text.strip()
                try:
                    # e.g., 'Wed Mar  6 15:40:02 2026'
                    created_at = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                except ValueError:
                    logger.warning(f"Could not parse datetime: {time_str}")

            # 移除所有不必要的 meta tags, 以及推文區域
            # 推文區具有 class 'push'
            for push in main_content.find_all('div', class_='push'):
                push.extract()
            # meta lines
            for meta in main_content.find_all('div', class_='article-metaline'):
                meta.extract()
            for meta in main_content.find_all('div', class_='article-metaline-right'):
                meta.extract()

            # 取得純文字內容
            content_text = main_content.text.strip()

        except Exception as e:
            logger.error(f"Error fetching article content from {url}: {e}")
            content_text = f"抓取內文失敗: {str(e)}"

        return content_text, created_at
