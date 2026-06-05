"""
API 调用客户端 - 兼容 OpenAI 格式的大模型 API 调用
"""

import re
import threading
from typing import Callable, Optional
from openai import OpenAI


class APIClient:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._current_request = None

    def _get_client(self) -> OpenAI:
        """根据配置创建 OpenAI 客户端"""
        api_config = self.config_manager.get_api_config()
        return OpenAI(
            base_url=api_config.get("base_url", "https://api.openai.com/v1"),
            api_key=api_config.get("api_key", ""),
        )

    @staticmethod
    def _extract_brackets(text: str) -> str:
        """截取「」中的内容，如果没有则返回原文"""
        match = re.search(r'「(.+?)」', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()

    def call(
        self,
        user_input: str,
        prompt_template: str,
        on_success: Callable[[str], None],
        on_error: Callable[[str], None],
        on_stream: Optional[Callable[[str], None]] = None,
    ):
        """
        异步调用大模型 API
        流程: B + "请你只输出最后的提示词内容且输出至「」中" + A → 大模型 → 截取「」内容 → C
        
        Args:
            user_input: 用户输入的文本 A
            prompt_template: 提示词模板 B
            on_success: 成功回调，参数为截取后的结果 C
            on_error: 错误回调，参数为错误信息
            on_stream: 流式输出回调，参数为增量文本（原始输出）
        """
        api_config = self.config_manager.get_api_config()

        # 构建消息: B + 固定后缀 + A
        content = f"{prompt_template}\n请你只输出最后的提示词内容且输出至「」中\n\n{user_input}"
        messages = [
            {"role": "user", "content": content}
        ]

        # 限制 max_tokens 不超过 API 支持的最大值（65536）
        max_tokens = api_config.get("max_tokens", 4096)
        if max_tokens > 65536:
            max_tokens = 65536
            print(f"[APIClient] 警告: max_tokens 超出限制，已自动调整为 {max_tokens}")

        def _run():
            try:
                client = self._get_client()

                if on_stream:
                    # 流式调用
                    stream = client.chat.completions.create(
                        model=api_config.get("model", "gpt-4o-mini"),
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=api_config.get("temperature", 0.7),
                        stream=True,
                    )
                    full_response = ""
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            delta = chunk.choices[0].delta.content
                            full_response += delta
                            on_stream(delta)
                    # 流式结束后截取「」内容
                    final = self._extract_brackets(full_response)
                    on_success(final)
                else:
                    # 非流式调用
                    response = client.chat.completions.create(
                        model=api_config.get("model", "gpt-4o-mini"),
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=api_config.get("temperature", 0.7),
                    )
                    result = response.choices[0].message.content
                    # 截取「」内容
                    final = self._extract_brackets(result)
                    on_success(final)

            except Exception as e:
                error_msg = f"API 调用失败: {str(e)}"
                on_error(error_msg)

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        self._current_request = thread
