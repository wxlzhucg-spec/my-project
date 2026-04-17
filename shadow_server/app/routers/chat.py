# -*- coding: utf-8 -*-
"""主对话：POST /api/chat。"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from ..config import CHAT_TIMEOUT_SECONDS, DEBUG, ENABLE_TEST_ROUTES
from ..deps import get_chat_graph
from ..http_support import upstream_model_http_exception
from ..models import ChatResponse, UserRequest

logger = logging.getLogger(__name__)
chat_router = APIRouter(prefix="/api", tags=["chat"])

@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: UserRequest, http_request: Request, graph: Any = Depends(get_chat_graph)):
    """
    多轮情感陪伴对话。
    第一轮（不填 supplements）：追问1个核心问题
    第二轮（填入 supplements）：完整分析
    """
    rid = getattr(http_request.state, "request_id", None)
    session_id = body.session_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    initial_state: dict = {"request": body}

    try:
        result = await asyncio.wait_for(
            graph.ainvoke(initial_state, config=config),
            timeout=CHAT_TIMEOUT_SECONDS,
        )
        if "clarification" in result:
            reply = result.get("clarification", "能多告诉我一些吗？")
            phase = "clarifying"
        else:
            reply = result.get("reply", "抱歉，影子暂时断开了链接...")
            phase = "complete"

        debug_info = None
        if DEBUG or ENABLE_TEST_ROUTES:
            debug_info = {
                "session_id": session_id,
                "phase": phase,
                "astro_analysis": result.get("astro_analysis", ""),
                "astro_context": result.get("astro_context", ""),
                "ephemeris_summary": result.get("ephemeris_summary", ""),
                "pipeline_trace": {
                    "clarification": result.get("clarification", ""),
                    "clarification_round": result.get("clarification_round", 0),
                    "astro_focus": result.get("astro_focus", ""),
                    "issue_context": result.get("issue_context", ""),
                    "root_logic": result.get("root_logic", ""),
                },
            }
        return ChatResponse(phase=phase, reply=reply, error=None, debug_info=debug_info)

    except asyncio.TimeoutError:
        logger.error("chat timeout request_id=%s session=%s after %.1fs", rid, getattr(body, "session_id", None), CHAT_TIMEOUT_SECONDS)
        raise HTTPException(status_code=504, detail=f"流水线执行超时（>{CHAT_TIMEOUT_SECONDS:.0f}s），请稍后重试")
    except KeyError as exc:
        logger.error("流水线状态缺失字段 request_id=%s err=%s", rid, exc)
        raise HTTPException(status_code=500, detail=f"内部状态异常：{exc}")
    except Exception as exc:
        mapped = upstream_model_http_exception(exc)
        if mapped is not None:
            logger.exception("上游模型错误 request_id=%s", rid)
            raise mapped
        logger.exception("后端工作流崩溃 request_id=%s", rid)
        raise HTTPException(status_code=500, detail="后端工作流崩溃，请稍后重试")
