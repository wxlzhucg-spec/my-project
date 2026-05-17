# -*- coding: utf-8 -*-
"""
影子 AI — 联网问答分支 (web_search.py)

【路由】router_node → WEB → web_search_node → generate_node → END
【功能】获取实时搜索上下文，供 generate_node 使用
【搜索后端】博查 AI Web Search API (POST https://api.bochaai.com/v1/web-search)
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from ...common.config import (
    SHADOW_SEARCH_API_KEY,
    SHADOW_SEARCH_API_URL,
    SHADOW_SEARCH_TIMEOUT_SECONDS,
)
from ...common.models import AgentState

logger = logging.getLogger(__name__)

# ── 博查 API 默认端点 ──
_BOCHA_DEFAULT_URL = "https://api.bochaai.com/v1/web-search"


def _safe_json(data: Any) -> str:
    """安全序列化数据为 JSON 字符串。"""
    if data is None:
        return "未提供"
    return json.dumps(data, ensure_ascii=False, default=str, indent=2)


def _normalize_query(query: str) -> str:
    """压缩多余空白，避免把脏 query 直接送给搜索服务。"""
    return " ".join((query or "").split())


def _truncate_text(text: str, limit: int = 4000) -> str:
    """统一裁剪搜索语料长度，避免后续节点 prompt 过长。"""
    clean_text = (text or "").strip()
    if len(clean_text) <= limit:
        return clean_text
    return clean_text[: limit - 3].rstrip() + "..."


def _extract_bocha_context(data: dict) -> str:
    """从博查 API 响应中提取关键文本上下文，供 LLM 消费。"""
    parts: list[str] = []
    web_pages = (data.get("data") or {}).get("webPages", {}).get("value", [])
    if not web_pages:
        return _safe_json(data)

    for idx, item in enumerate(web_pages[:8], start=1):
        name = item.get("name", "")
        url = item.get("url", "")
        summary = item.get("summary", "") or item.get("snippet", "")
        publish_time = item.get("dateLastCrawled", "") or item.get("datePublished", "")

        block = [f"【案例{idx}】{name or '未命名结果'}"]
        if publish_time:
            block.append(f"时间：{publish_time}")
        if summary:
            block.append(f"摘要：{summary}")
        if url:
            block.append(f"来源：{url}")
        parts.append("\n".join(block))

    return "\n\n".join(parts) if parts else _safe_json(data)


async def fetch_web_context(
    query: str,
    *,
    count: int = 8,
    freshness: str = "noLimit",
    missing_service_message: str,
    unavailable_message: str,
) -> dict[str, Any]:
    """获取联网搜索语料，供不同分支复用。"""
    normalized_query = _normalize_query(query)
    if not normalized_query:
        return {
            "context": "未提供有效搜索问题，无法生成联网语料。",
            "web_search": False,
            "search_query": "",
            "is_fallback": True,
        }

    logger.info("[fetch_web_context] 获取联网语料 query=%s", normalized_query)
    api_url = SHADOW_SEARCH_API_URL or _BOCHA_DEFAULT_URL

    if not SHADOW_SEARCH_API_KEY:
        return {
            "context": missing_service_message,
            "web_search": True,
            "search_query": normalized_query,
            "is_fallback": True,
        }

    try:
        headers = {
            "Authorization": f"Bearer {SHADOW_SEARCH_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "query": normalized_query,
            "summary": True,
            "count": count,
            "freshness": freshness,
        }

        async with httpx.AsyncClient(timeout=SHADOW_SEARCH_TIMEOUT_SECONDS) as client:
            resp = await client.post(api_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        if isinstance(data, dict) and "data" in data:
            context = _extract_bocha_context(data)
        else:
            context = _safe_json(data)

        logger.info("[fetch_web_context] 联网语料获取完成 query=%s", normalized_query)
        return {
            "context": _truncate_text(context),
            "web_search": True,
            "search_query": normalized_query,
            "is_fallback": False,
        }
    except Exception as exc:
        logger.warning("[fetch_web_context] 搜索服务不可用，降级回答 query=%s err=%s", normalized_query, exc)
        return {
            "context": unavailable_message,
            "web_search": True,
            "search_query": normalized_query,
            "is_fallback": True,
        }


async def web_search_node(state: AgentState) -> dict:
    """
    联网问答搜索上下文节点。

    输入: request.question
    输出: web_context, web_search

    支持博查 AI Web Search API（POST + JSON body），
    未配置搜索服务时降级，返回提示性文本。
    """
    req = state["request"]
    logger.info("[web_search_node] 获取联网上下文")

    result = await fetch_web_context(
        req.question,
        count=8,
        freshness="noLimit",
        missing_service_message="未配置实时搜索服务，无法确认最新实时信息；回答时不得伪造实时资料。",
        unavailable_message="实时搜索暂不可用；回答时请说明无法确认最新信息，并基于常识给出谨慎建议。",
    )

    logger.info("[web_search_node] 联网上下文获取完成")
    return {"web_context": result["context"], "web_search": result["web_search"]}
