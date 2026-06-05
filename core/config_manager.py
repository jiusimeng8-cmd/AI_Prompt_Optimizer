"""
配置管理器 - 管理 API 配置和快捷键设置
"""

import json
from pathlib import Path
from typing import Optional


class ConfigManager:
    DEFAULT_CONFIG = {
        "api": {
            "base_url": "https://api.openai.com/v1",
            "api_key": "",
            "model": "gpt-4o-mini",
            "max_tokens": 4096,
            "temperature": 0.7,
        },
        "hotkey": {
            "modifiers": ["ctrl", "shift"],
            "key": "o",
        },
        "active_prompt_id": "default",
    }

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.config_file = data_dir / "config.json"
        self._config = self.DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    # 深度合并配置
                    self._deep_update(self._config, loaded)
            except Exception:
                pass

    def _deep_update(self, base: dict, update: dict):
        """深度合并字典"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def save(self):
        """保存配置"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get_api_config(self) -> dict:
        return self._config.get("api", {})

    def set_api_config(self, key: str, value):
        self._config.setdefault("api", {})[key] = value
        self.save()

    def get_hotkey(self) -> dict:
        return self._config.get("hotkey", {})

    def set_hotkey(self, modifiers: list, key: str):
        self._config["hotkey"] = {"modifiers": modifiers, "key": key}
        self.save()

    def get_active_prompt_id(self) -> str:
        return self._config.get("active_prompt_id", "default")

    def set_active_prompt_id(self, prompt_id: str):
        self._config["active_prompt_id"] = prompt_id
        self.save()

    @property
    def config(self):
        return self._config
