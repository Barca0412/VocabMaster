import json
import os
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration manager for application settings"""
    
    DEFAULT_CONFIG = {
        "window_position": {"x": None, "y": None},
        "display_interval": 10,  # seconds
        "theme": "light",  # light or dark
        "show_phonetic": True,
        "show_definitions": True,
        "show_examples": True,
        "current_wordlist": None,
        "auto_start_playback": False,  # Auto start when launching
        "always_on_top": True,  # Keep window on top
        "learning_goal": "",  # 用户的学习目标
        "learning_stats": {
            "total_words_learned": 0,
            "study_sessions": 0,
            "total_study_time": 0
        }
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".word_recite"
        self.config_file = self.config_dir / "config.json"
        self._ensure_config_dir()
        self.settings = self._load_config()
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new settings
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(loaded)
                    return config
            except (json.JSONDecodeError, IOError):
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value and save"""
        self.settings[key] = value
        self.save()
    
    def update_learning_stats(self, **kwargs):
        """Update learning statistics"""
        stats = self.settings.get("learning_stats", {})
        stats.update(kwargs)
        self.set("learning_stats", stats)
