# -*- coding: utf-8 -*-
"""
影子 AI — HTTP 辅助 (http_support.py)

【职责】
  将上游 LLM 服务的 HTTP 错误映射为 FastAPI HTTPException。
"""
from __future__ import annotations

from fastapi import HTTPException


def upstream_model_http_exception(exc: Exception) -> HTTPException | None:
    """
    将上游模型（DeepSeek/OpenAI）的异常映射为 HTTPException。

    返回 None 表示无法识别/不处理。
    """
    exc_type = type(exc).__name__
    exc_module = type(exc).__module__

    # openai / langchain_openai 的常见错误
    if "openai" in exc_module.lower():
        status_code = getattr(exc, "status_code", None)
        if status_code == 401:
            return HTTPException(status_code=502, detail="上游模型认证失败，请检查 API Key")
        if status_code == 429:
            return HTTPException(status_code=502, detail="上游模型限流，请稍后重试")
        if status_code == 500:
            return HTTPException(status_code=502, detail="上游模型服务异常")
        if status_code:
            return HTTPException(status_code=502, detail=f"上游模型错误 ({status_code})")

    return None
