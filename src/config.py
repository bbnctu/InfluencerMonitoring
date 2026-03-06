import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.settings: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {self.config_path}: {e}")
            return {}

    @property
    def email_settings(self) -> Dict[str, str]:
        return self.settings.get("email", {})

    @property
    def influencers(self) -> List[Dict[str, Any]]:
        return self.settings.get("influencers", [])
