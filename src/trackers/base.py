from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Article:
    title: str
    url: str
    author: str
    platform: str
    board: str
    content: str
    created_at: datetime
    
class BaseTracker(ABC):
    def __init__(self, author_id: str, platform: str, board: str):
        self.author_id = author_id
        self.platform = platform
        self.board = board

    @abstractmethod
    def fetch_latest_articles(self) -> List[Article]:
        """抓取該對象最新的文章並返回Article對象列表"""
        pass
