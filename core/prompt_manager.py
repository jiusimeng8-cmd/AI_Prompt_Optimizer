"""
提示词管理器 - 管理多个自定义提示词模板
"""

import json
import uuid
from pathlib import Path
from typing import Optional


class PromptManager:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.prompts_file = data_dir / "prompts.json"
        self._prompts: list[dict] = []
        self._load()

    def _load(self):
        """加载提示词配置"""
        if self.prompts_file.exists():
            try:
                with open(self.prompts_file, "r", encoding="utf-8") as f:
                    self._prompts = json.load(f)
            except Exception:
                self._prompts = []
        if not self._prompts:
            self._create_default_prompts()

    def _create_default_prompts(self):
        """创建默认提示词"""
        self._prompts = [
            {
                "id": "default",
                "name": "通用优化",
                "content": "请对以下文本进行优化，使其表达更清晰、更专业，同时保持原意不变",
            },
            {
                "id": "translate_en",
                "name": "翻译为英文",
                "content": "请将以下中文翻译为自然流畅的英文",
            },
            {
                "id": "polish",
                "name": "润色润文",
                "content": "请对以下文本进行润色，修正语法错误，提升文采，使其更加优美流畅，同时保持原意",
            },
            {
                "id": "summarize",
                "name": "摘要总结",
                "content": "请对以下内容进行简洁的摘要总结，提炼核心要点",
            },
        ]
        self._save()

    def _save(self):
        """保存提示词配置"""
        self.prompts_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.prompts_file, "w", encoding="utf-8") as f:
            json.dump(self._prompts, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list[dict]:
        """获取所有提示词"""
        return self._prompts.copy()

    def get_by_id(self, prompt_id: str) -> Optional[dict]:
        """根据ID获取提示词"""
        for p in self._prompts:
            if p["id"] == prompt_id:
                return p
        return None

    def add(self, name: str, content: str) -> str:
        """添加提示词，返回ID"""
        pid = str(uuid.uuid4())[:8]
        self._prompts.append({"id": pid, "name": name, "content": content})
        self._save()
        return pid

    def update(self, prompt_id: str, name: str, content: str) -> bool:
        """更新提示词"""
        for p in self._prompts:
            if p["id"] == prompt_id:
                p["name"] = name
                p["content"] = content
                self._save()
                return True
        return False

    def delete(self, prompt_id: str) -> bool:
        """删除提示词"""
        if prompt_id == "default":
            return False  # 不允许删除默认提示词
        for i, p in enumerate(self._prompts):
            if p["id"] == prompt_id:
                self._prompts.pop(i)
                self._save()
                return True
        return False

    def get_names(self) -> list[str]:
        """获取所有提示词名称"""
        return [p["name"] for p in self._prompts]

    def get_ids(self) -> list[str]:
        """获取所有提示词ID"""
        return [p["id"] for p in self._prompts]
