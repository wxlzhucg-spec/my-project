# -*- coding: utf-8 -*-
"""主对话：POST /api/chat。"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from ..config import CHAT_TIMEOUT_SECONDS, DEBUG, ENABLE_TEST_ROUTES
from ..database import async_session_maker
from ..deps import get_chat_graph
from ..http_support import upstream_model_http_exception
from ..models import ChatResponse, UserRequest

logger = logging.getLogger(__name__)
chat_router = APIRouter(prefix="/api", tags=["chat"])


async def _fill_user_from_db(body: UserRequest) -> UserRequest:
    """
    如果传了 open_id，从 users 表查询 birth_time/birth_place/mbti/blood_type 补全。
    已手动填写的字段不会被覆盖。
    """
    if not body.open_id:
        # 没有 open_id，校验必填字段
        missing = []
        if not body.birth_time:
            missing.append("birth_time")
        if not body.birth_place:
            missing.append("birth_place")
        if not body.mbti:
            missing.append("mbti")
        if not body.blood_type:
            missing.append("blood_type")
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必填字段: {', '.join(missing)}，或传入 open_id 自动获取",
            )
        return body

    # 从数据库查询用户信息
    async with async_session_maker() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE open_id = :open_id LIMIT 1"),
            {"open_id": body.open_id},
        )
        row = result.mappings().first()

    if not row:
        raise HTTPException(status_code=404, detail=f"未找到 open_id={body.open_id} 对应的用户")

    user = dict(row)
    logger.info("[_fill_user_from_db] 查到用户 id=%s open_id=%s", user.get("id"), body.open_id)

    # 补全未填写的字段（优先使用前端传入的值）
    if not body.birth_time and user.get("birth_time"):
        # 拼接 birth_date + birth_time → "1995-06-15 14:30"
        birth_date = user.get("birth_date")
        birth_time_val = user.get("birth_time", "")
        if birth_date:
            date_str = str(birth_date)
            body.birth_time = f"{date_str} {birth_time_val}".strip() if birth_time_val else f"{date_str} 12:00"
        elif birth_time_val:
            body.birth_time = birth_time_val

    if not body.birth_place:
        # 拼接 birth_province + birth_city + birth_district
        parts = [
            user.get("birth_province", "") or "",
            user.get("birth_city", "") or "",
            user.get("birth_district", "") or "",
        ]
        place = "".join(p for p in parts if p.strip())
        if place:
            body.birth_place = place

    if not body.mbti and user.get("mbti"):
        body.mbti = user["mbti"]

    if not body.blood_type and user.get("blood_type"):
        body.blood_type = user["blood_type"]

    # 二次校验：补全后仍然缺少的关键字段
    if not body.birth_time or not body.birth_place or not body.mbti:
        missing = []
        if not body.birth_time:
            missing.append("birth_time")
        if not body.birth_place:
            missing.append("birth_place")
        if not body.mbti:
            missing.append("mbti")
        raise HTTPException(
            status_code=400,
            detail=f"用户资料不完整，缺少: {', '.join(missing)}，请先完善个人资料",
        )

    return body


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: UserRequest, http_request: Request, graph: Any = Depends(get_chat_graph)):
    """
    多轮情感陪伴对话。
    第一轮（不填 supplements）：追问1个核心问题
    第二轮（填入 supplements）：完整分析

    支持两种调用方式：
      1. 传 open_id：自动从 users 表补全 birth_time/birth_place/mbti 等
      2. 手动填写：直接传入 birth_time/birth_place/mbti 等
    """
    rid = getattr(http_request.state, "request_id", None)

    # 自动从数据库补全用户信息
    body = await _fill_user_from_db(body)

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
