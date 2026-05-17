# -*- coding: utf-8 -*-
"""从当前配置的 OpenAI 兼容上游检索可用模型列表（如 DeepSeek）。"""
from __future__ import annotations

import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...common.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

logger = logging.getLogger(__name__)

llm_models_router = APIRouter(prefix="/api", tags=["llm"])


class LLMModelsResponse(BaseModel):
    """与 OpenAI `GET /v1/models` 类似的精简结果。"""

    model_ids: list[str] = Field(description="上游返回的模型 id 列表")
    configured_model: str = Field(description="当前环境变量 DEEPSEEK_MODEL")
    raw: dict[str, Any] | None = Field(
        default=None,
        description="上游 JSON 原文（便于调试）；失败时为 None",
    )


@llm_models_router.get("/llm-models", response_model=LLMModelsResponse)
async def list_upstream_llm_models(
    include_raw: bool = Query(
        False,
        description="为 true 时在响应中附带上游 JSON 全文（仅调试建议开启）",
    ),
) -> LLMModelsResponse:
    """
    调用上游 `GET {DEEPSEEK_BASE_URL}/models`，列出可用模型 id。

    用于本地核对「还能用哪些模型名」再写入 `DEEPSEEK_MODEL`。
    """
    if not DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DEEPSEEK_API_KEY 未配置，无法查询上游模型")

    base = DEEPSEEK_BASE_URL.rstrip("/")
    url = f"{base}/models"
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        logger.warning("查询上游模型列表失败: %s", exc)
        raise HTTPException(status_code=502, detail=f"无法连接上游: {exc}") from exc

    if resp.status_code != 200:
        body_preview = (resp.text or "")[:500]
        logger.warning("上游 /models 返回 %s: %s", resp.status_code, body_preview)
        raise HTTPException(
            status_code=502,
            detail=f"上游返回 HTTP {resp.status_code}",
        )

    try:
        payload = resp.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="上游返回非 JSON") from exc

    model_ids: list[str] = []
    data = payload.get("data")
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                model_ids.append(item["id"])

    raw_out: dict[str, Any] | None = None
    if include_raw and isinstance(payload, dict):
        raw_out = payload

    return LLMModelsResponse(
        model_ids=model_ids,
        configured_model=DEEPSEEK_MODEL,
        raw=raw_out,
    )
