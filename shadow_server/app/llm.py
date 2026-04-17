# -*- coding: utf-8 -*-
"""
影子 AI — LLM 实例管理 (llm.py)

【职责】
  管理 DeepSeek LLM 单例，供各节点共用。
"""
from __future__ import annotations

import logging

from langchain_openai import ChatOpenAI

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_MODEL,
    DEEPSEEK_TEMPERATURE,
)

logger = logging.getLogger(__name__)

_llm_instance: ChatOpenAI | None = None


# ════════════════════════════════════════════════════════════
#  公开接口
# ════════════════════════════════════════════════════════════


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 实例（单例）。

    首次调用时创建实例并缓存，后续调用直接返回已缓存的实例。
    """
    global _llm_instance
    if _llm_instance is None:
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请在 .env 或环境变量中配置")
        _llm_instance = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            max_tokens=DEEPSEEK_MAX_TOKENS,
            temperature=DEEPSEEK_TEMPERATURE,
        )
        logger.info(
            "LLM 实例已创建: model=%s, base_url=%s, max_tokens=%d, temp=%.2f",
            DEEPSEEK_MODEL,
            DEEPSEEK_BASE_URL,
            DEEPSEEK_MAX_TOKENS,
            DEEPSEEK_TEMPERATURE,
        )
    return _llm_instance
