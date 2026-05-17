# -*- coding: utf-8 -*-
"""
影子 AI — LLM 实例管理 (llm.py)

【职责】
  管理 DeepSeek LLM 单例，供各节点共用。
"""
from __future__ import annotations

import logging

from langchain_openai import ChatOpenAI

from ...common.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_MODEL,
    DEEPSEEK_REASONER_MODEL,
    DEEPSEEK_TEMPERATURE,
)

logger = logging.getLogger(__name__)

_llm_instance: ChatOpenAI | None = None
_reasoner_llm_instance: ChatOpenAI | None = None


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
            timeout=60,
        )
        logger.info(
            "LLM 实例已创建: model=%s, base_url=%s, max_tokens=%d, temp=%.2f",
            DEEPSEEK_MODEL,
            DEEPSEEK_BASE_URL,
            DEEPSEEK_MAX_TOKENS,
            DEEPSEEK_TEMPERATURE,
        )
    return _llm_instance


def get_reasoner_llm() -> ChatOpenAI:
    """获取 deepseek-reasoner 实例，用于最终打磨与逻辑增强。"""
    global _reasoner_llm_instance
    if _reasoner_llm_instance is None:
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置，请在 .env 或环境变量中配置")
        _reasoner_llm_instance = ChatOpenAI(
            model=DEEPSEEK_REASONER_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            max_tokens=DEEPSEEK_MAX_TOKENS,
            temperature=0.6,
            timeout=90,
        )
        logger.info("Reasoner LLM 实例已创建: model=%s", DEEPSEEK_REASONER_MODEL)
    return _reasoner_llm_instance


# 中间分析节点用的轻量 LLM（更少 tokens，更快响应）
_light_llm_instance: ChatOpenAI | None = None


def get_light_llm() -> ChatOpenAI:
    """获取轻量 LLM 实例，用于中间分析节点（max_tokens 更小，响应更快）。"""
    global _light_llm_instance
    if _light_llm_instance is None:
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY 未设置")
        _light_llm_instance = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            max_tokens=256,
            temperature=0.5,
            timeout=45,
        )
        logger.info("轻量 LLM 实例已创建: model=%s, max_tokens=256", DEEPSEEK_MODEL)
    return _light_llm_instance
