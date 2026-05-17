# -*- coding: utf-8 -*-
"""主对话：POST /api/chat 与 POST /api/chat/stream。"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...common.config import CHAT_TIMEOUT_SECONDS, DEBUG, ENABLE_TEST_ROUTES
from ...common.database import async_session_maker
from ...common.deps import get_master_graph
from ...common.http_support import upstream_model_http_exception
from ...common.models import ChatResponse, UserRequest
from ...common.tarot_persist import save_tarot_session

logger = logging.getLogger(__name__)
chat_router = APIRouter(prefix="/api", tags=["chat"])


async def _fill_user_from_db(body: UserRequest) -> UserRequest:
    """
    支持三种调用方式：
      1. 传 user_id：直接用数据库 ID 查询（优先）
      2. 传 open_id：从 users 表查询 birth_time/birth_place/mbti 等信息
      3. 手动填写：直接传入 birth_time/birth_place/mbti 等字段
    已手动填写的字段不会被覆盖。
    """
    user = None

    # 优先用 user_id 查询
    if body.user_id:
        async with async_session_maker() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE id = :id LIMIT 1"),
                {"id": body.user_id},
            )
            row = result.mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 user_id={body.user_id} 对应的用户")
        user = dict(row)
        logger.info("[_fill_user_from_db] 用 user_id 查到用户 id=%s", body.user_id)

    elif body.open_id:
        # 用 open_id 查询；若是前端注册时写入的伪值 "p_手机号"，回退到 phone 查询
        async with async_session_maker() as session:
            result = await session.execute(
                text("SELECT * FROM users WHERE open_id = :open_id LIMIT 1"),
                {"open_id": body.open_id},
            )
            row = result.mappings().first()

            if not row and body.open_id.startswith("p_"):
                phone_guess = body.open_id[2:]
                logger.info(
                    "[_fill_user_from_db] open_id=%s 查无结果，回退用 phone=%s 查询",
                    body.open_id, phone_guess,
                )
                result = await session.execute(
                    text("SELECT * FROM users WHERE phone = :phone LIMIT 1"),
                    {"phone": phone_guess},
                )
                row = result.mappings().first()

        if not row:
            raise HTTPException(status_code=404, detail=f"未找到 open_id={body.open_id} 对应的用户")
        user = dict(row)
        logger.info("[_fill_user_from_db] 用 open_id 查到用户 id=%s", user.get("id"))

    else:
        # 没有 user_id/open_id，校验必填字段（blood_type 非关键，给默认值）
        if not body.blood_type:
            body.blood_type = "unknown"
        missing = []
        if not body.birth_time:
            missing.append("birth_time")
        if not body.birth_place:
            missing.append("birth_place")
        if not body.mbti:
            missing.append("mbti")
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"缺少必填字段: {', '.join(missing)}，或传入 user_id / open_id 自动获取",
            )
        return body

    logger.info("[_fill_user_from_db] 查到用户 id=%s open_id=%s", user.get("id"), user.get("open_id"))

    # 如果通过 open_id 查询到用户但未传入 user_id，则补全 user_id
    if not body.user_id and user.get("id"):
        body.user_id = user["id"]
        logger.info("[_fill_user_from_db] 补全 user_id=%s", body.user_id)

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

    if not body.blood_type:
        body.blood_type = "unknown"

    # 资料不完整时给默认值，让对话降级运行（星盘部分用占位文本）
    if not body.birth_time:
        body.birth_time = "2000-01-01 12:00"
        logger.warning("[_fill_user_from_db] 用户缺少 birth_time，使用默认值")
    if not body.birth_place:
        body.birth_place = "北京"
        logger.warning("[_fill_user_from_db] 用户缺少 birth_place，使用默认值")
    if not body.mbti:
        body.mbti = "INFP"
        logger.warning("[_fill_user_from_db] 用户缺少 mbti，使用默认值")

    return body


def _make_session_config(body: UserRequest) -> tuple[str, dict]:
    session_id = body.session_id or str(uuid.uuid4())
    body.session_id = session_id
    return session_id, {"configurable": {"thread_id": session_id}}


def _pick_phase_and_reply(result: dict) -> tuple[str, str]:
    final_reply = result.get("reply")
    if final_reply:
        return "complete", final_reply
    return "clarifying", result.get("clarification", "能多告诉我一些吗？")


def _make_debug_info(session_id: str, phase: str, result: dict) -> dict | None:
    if not (DEBUG or ENABLE_TEST_ROUTES):
        return None
    return {
        "session_id": session_id,
        "phase": phase,
        "category": result.get("category", ""),
        "web_search": result.get("web_search", False),
        "astro_analysis": result.get("astro_analysis", ""),
        "astro_context": result.get("astro_context", ""),
        "ephemeris_summary": result.get("ephemeris_summary", ""),
        "pipeline_trace": {
            "clarification": result.get("clarification", ""),
            "clarification_round": result.get("clarification_round", 0),
            "astro_focus": result.get("astro_focus", ""),
            "issue_search_query": result.get("issue_search_query", ""),
            "issue_web_context": result.get("issue_web_context", ""),
            "issue_context": result.get("issue_context", ""),
            "root_logic": result.get("root_logic", ""),
            "refine_count": result.get("refine_count", 0),
            "internal_notes_count": len(result.get("internal_notes", [])),
            "web_context": result.get("web_context", ""),
        },
    }


async def _try_prepare_resume(graph: Any, body: UserRequest, config: dict) -> bool:
    """若 LangGraph 存在中断快照且还有待执行节点，返回 True。"""
    if not body.supplements:
        return False
    try:
        snapshot = await graph.aget_state(config)
        values = getattr(snapshot, "values", None) if snapshot else None
        if not values:
            return False
        has_next = bool(getattr(snapshot, "next", None))
        logger.info("[chat_resume] 快照存在 has_next=%s", has_next)
        return has_next
    except Exception as exc:
        logger.info("[chat_resume] 快照检查异常: %s", exc)
        return False


async def _read_category_from_checkpoint(graph: Any, config: dict) -> str | None:
    """从已有 checkpoint 中读取上一轮的分类结果。"""
    try:
        snapshot = await graph.aget_state(config)
        values = getattr(snapshot, "values", None) if snapshot else None
        if values:
            return values.get("category")
    except Exception as exc:
        logger.info("[_read_category_from_checkpoint] 读取失败: %s", exc)
    return None


async def _invoke_graph(graph: Any, body: UserRequest, config: dict) -> dict:
    """
    调用 LangGraph 图，处理三种场景：

    1. 第一轮新对话（无 supplements）：走 router_node 正常分类
    2. 第二轮追问（有 supplements + session_id + checkpoint 有待执行节点）：
       从断点恢复执行
    3. 第二轮追问（有 supplements + session_id + checkpoint 已结束或不存在）：
       用上一轮 category 启动全新图执行；无 category 则丢弃 supplements 走路由
    """
    # ── 场景 2：checkpoint 还有待执行节点，可以直接恢复 ──
    if await _try_prepare_resume(graph, body, config):
        graph.update_state(config, {"request": body})
        result = await graph.ainvoke(None, config=config)
        return result or {}

    # ── 场景 3：有 supplements 但 checkpoint 已结束或不存在 ──
    if body.supplements and body.session_id:
        prev_category = await _read_category_from_checkpoint(graph, config)
        if prev_category:
            # 用上一轮分类结果启动全新图，router_node 会直接使用 req.category
            body.category = prev_category
            # 使用新 thread_id 避免旧 checkpoint 干扰
            new_session_id = f"{body.session_id}_r2"
            body.session_id = new_session_id
            new_config = {"configurable": {"thread_id": new_session_id}}
            logger.info(
                "[_invoke_graph] 第二轮全新执行: category=%s, new_thread=%s",
                prev_category, new_session_id,
            )
            # 只传 request，category 通过 body.category 传入，由 router_node 设置
            # 不要在 graph_input 中同时传 category，否则与 router_node 的输出冲突
            graph_input = {"request": body}
            result = await graph.ainvoke(graph_input, config=new_config)
            return result or {}
        else:
            # 无 checkpoint（会话过期/服务器重启）：丢弃 supplements 走正常路由
            logger.info("[_invoke_graph] 无快照分类信息，丢弃 supplements 走完整路由")
            body.supplements = None
            graph_input = {"request": body}

    # ── 场景 1：普通第一轮对话 ──
    else:
        graph_input = {"request": body}

    result = await graph.ainvoke(graph_input, config=config)
    return result or {}


_PUBLIC_STREAM_NODES = frozenset({"generate_node", "specialist_node", "clarify_node", "combine_node"})
_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _stream_event_node(event: dict) -> str:
    metadata = event.get("metadata") or {}
    return str(metadata.get("langgraph_node") or "")


def _stream_chunk_text(event: dict) -> str:
    chunk = event.get("data", {}).get("chunk")
    content = getattr(chunk, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "".join(parts)
    return ""


def _is_public_stream_token(event: dict) -> bool:
    return event.get("event") == "on_chat_model_stream" and _stream_event_node(event) in _PUBLIC_STREAM_NODES


def _make_done_payload(session_id: str, result: dict) -> dict:
    phase, reply = _pick_phase_and_reply(result)
    category = result.get("category", "")
    return {
        "session_id": session_id,
        "phase": phase,
        "category": category,
        "reply": reply,
        "error": None,
        "debug_info": _make_debug_info(session_id, phase, result),
    }


@chat_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(body: UserRequest, http_request: Request, graph: Any = Depends(get_master_graph)):
    """
    多轮影子对话。统一路由到专项分析、普通/联网问答或情绪深度分析。
    """
    rid = getattr(http_request.state, "request_id", None)
    body = await _fill_user_from_db(body)
    session_id, config = _make_session_config(body)

    try:
        result = await asyncio.wait_for(
            _invoke_graph(graph, body, config),
            timeout=CHAT_TIMEOUT_SECONDS,
        )
        phase, reply = _pick_phase_and_reply(result)
        category = result.get("category", "")
        return ChatResponse(
            session_id=session_id,
            phase=phase,
            category=category,
            reply=reply,
            error=None,
            debug_info=_make_debug_info(session_id, phase, result),
        )

    except asyncio.TimeoutError:
        logger.error("chat timeout request_id=%s session=%s after %.1fs", rid, session_id, CHAT_TIMEOUT_SECONDS)
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


@chat_router.post("/chat/stream")
async def chat_stream_endpoint(body: UserRequest, http_request: Request, graph: Any = Depends(get_master_graph)):
    """SSE 流式对话端点。"""
    rid = getattr(http_request.state, "request_id", None)
    body = await _fill_user_from_db(body)
    session_id, config = _make_session_config(body)

    async def event_generator():
        nonlocal body
        logger.info("[chat_stream] start session=%s request_id=%s", session_id, rid)
        yield _sse("session", {"session_id": session_id})

        should_resume = await _try_prepare_resume(graph, body, config)
        graph_input = None if should_resume else {"request": body}

        try:
            async for event in graph.astream_events(graph_input, config=config, version="v2"):
                if not _is_public_stream_token(event):
                    continue
                content = _stream_chunk_text(event)
                if content:
                    yield _sse("token", {"text": content, "node": _stream_event_node(event)})

            snapshot = await graph.aget_state(config)
            result = dict(getattr(snapshot, "values", {}) or {})
            yield _sse("done", _make_done_payload(session_id, result))
            logger.info("[chat_stream] done session=%s request_id=%s", session_id, rid)
        except Exception as exc:
            mapped = upstream_model_http_exception(exc)
            if isinstance(exc, HTTPException):
                status_code = exc.status_code
                message = exc.detail
            elif mapped is not None:
                status_code = mapped.status_code
                message = mapped.detail
            else:
                status_code = 500
                message = "流式对话执行失败，请稍后重试"
            logger.exception("[chat_stream] failed request_id=%s", rid)
            yield _sse("error", {"status_code": status_code, "message": message})

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=_SSE_HEADERS)


# ════════════════════════════════════════════════════════════════
#  统一影子 API：POST /api/shadow & /api/shadow/stream
#  简化版入口，只需 question，自动补全用户信息，自动路由分类
# ════════════════════════════════════════════════════════════════

class ShadowRequest(BaseModel):
    """统一影子对话请求体（简化版，只需 question）。"""
    question: str = Field(
        ...,
        description="用户倾诉的问题或困扰",
        examples=["工作压力太大不知道怎么办", "你好呀"],
    )
    user_id: Optional[int] = Field(
        None,
        description="用户数据库 ID（优先级最高，自动获取出生信息）",
    )
    open_id: Optional[str] = Field(
        None,
        description="微信 open_id（优先级次之）",
    )
    emotion_keyword: str = Field(
        "",
        description="当前核心情绪关键词（可选，留空由系统自动判断）",
        examples=["焦虑", "迷茫", "开心"],
    )
    session_id: Optional[str] = Field(
        None,
        description="会话ID，多轮对话时传入上一轮返回的 session_id",
    )
    supplements: Optional[str] = Field(
        None,
        description="追问补充回答（第二轮传入）",
    )

    # 高级可选字段（直接传入可跳过数据库查询）
    birth_time: Optional[str] = Field(None, description="出生时间，如 '1995-06-15 14:30'")
    birth_place: Optional[str] = Field(None, description="出生地点，如 '上海市'")
    mbti: Optional[str] = Field(None, description="MBTI 类型，如 INFP")
    blood_type: Optional[str] = Field(None, description="血型 A/B/O/AB")

    # 强制指定分类（可选，留空由路由器自动分类）
    category: Optional[str] = Field(
        None,
        description="强制指定分类（TAROT/ZODIAC/EMOTION_LOG/GENERAL/WEB/EMOTION_DEEP），留空自动分类",
    )

    # 专项数据（与 category 配合使用）
    zodiac_data: Optional[dict] = Field(
        None,
        description="星座运势数据，category=ZODIAC 时传入，如 sign/period/ratings/desc 等",
    )
    emotion_log: Optional[dict] = Field(
        None,
        description="情绪记录数据，category=EMOTION_LOG 时传入，如 trend/notes/scores 等",
    )
    tarot_cards: Optional[list[dict]] = Field(
        None,
        description="塔罗选牌结果，category=TAROT 时传入",
    )


class ShadowResponse(BaseModel):
    """统一影子对话响应体。"""
    session_id: str = Field(..., description="会话ID，下一轮带回以延续对话")
    phase: str = Field(
        ...,
        description="当前阶段：clarifying=追问中，complete=分析完成",
        examples=["clarifying", "complete"],
    )
    category: str = Field(
        ...,
        description="路由分类结果：GENERAL/WEB/EMOTION_DEEP",
        examples=["GENERAL", "WEB", "EMOTION_DEEP"],
    )
    reply: str = Field(..., description="影子回复内容")
    error: Optional[str] = Field(None, description="错误信息（如有）")


@chat_router.post("/shadow", response_model=ShadowResponse)
async def shadow_endpoint(body: ShadowRequest, http_request: Request, graph: Any = Depends(get_master_graph)):
    """
    统一影子对话 API（简化版）。

    只需传入 question，系统自动：
      1. 根据 user_id/open_id 从数据库补全用户出生信息
      2. 用 LLM 路由器自动分类问题类型
      3. 按分类走不同分支生成回答：
         - GENERAL：日常聊天、闲聊
         - WEB：需要实时信息的问答
         - EMOTION_DEEP：情绪深度分析（含追问 + 占星 + 联网搜索 + 多轮打磨）
    """
    rid = getattr(http_request.state, "request_id", None)

    # 将 ShadowRequest 转为 UserRequest
    user_req = UserRequest(
        question=body.question,
        user_id=body.user_id,
        open_id=body.open_id,
        emotion_keyword=body.emotion_keyword,
        session_id=body.session_id,
        supplements=body.supplements,
        birth_time=body.birth_time,
        birth_place=body.birth_place,
        mbti=body.mbti,
        blood_type=body.blood_type,
        category=body.category,
        zodiac_data=body.zodiac_data,
        emotion_log=body.emotion_log,
        tarot_cards=body.tarot_cards,
    )

    # 自动补全用户信息
    user_req = await _fill_user_from_db(user_req)

    session_id, config = _make_session_config(user_req)

    try:
        result = await asyncio.wait_for(
            _invoke_graph(graph, user_req, config),
            timeout=CHAT_TIMEOUT_SECONDS,
        )
        phase, reply = _pick_phase_and_reply(result)
        category = result.get("category", "")

        # 塔罗/星座/情绪专项：持久化会话数据到 tarot_sessions 表
        if category in ("TAROT", "ZODIAC", "EMOTION_LOG"):
            await save_tarot_session(
                user_id=user_req.user_id,
                session_id=session_id,
                category=category,
                request_body=user_req,
                result=result,
                phase=phase,
                reply=reply,
            )

        return ShadowResponse(
            session_id=session_id,
            phase=phase,
            category=category,
            reply=reply,
            error=None,
        )

    except asyncio.TimeoutError:
        logger.error("shadow timeout request_id=%s session=%s", rid, session_id)
        raise HTTPException(status_code=504, detail="影子思考时间较长，请稍后重试")
    except Exception as exc:
        mapped = upstream_model_http_exception(exc)
        if mapped is not None:
            raise mapped
        logger.exception("shadow error request_id=%s", rid)
        raise HTTPException(status_code=500, detail="影子暂时断开了连接，请稍后重试")


@chat_router.post("/shadow/stream")
async def shadow_stream_endpoint(body: ShadowRequest, http_request: Request, graph: Any = Depends(get_master_graph)):
    """
    统一影子对话 API（SSE 流式版）。

    与 /api/shadow 相同的参数和逻辑，但通过 SSE 逐 token 返回。
    """
    rid = getattr(http_request.state, "request_id", None)

    user_req = UserRequest(
        question=body.question,
        user_id=body.user_id,
        open_id=body.open_id,
        emotion_keyword=body.emotion_keyword,
        session_id=body.session_id,
        supplements=body.supplements,
        birth_time=body.birth_time,
        birth_place=body.birth_place,
        mbti=body.mbti,
        blood_type=body.blood_type,
        category=body.category,
        zodiac_data=body.zodiac_data,
        emotion_log=body.emotion_log,
        tarot_cards=body.tarot_cards,
    )

    user_req = await _fill_user_from_db(user_req)
    session_id, config = _make_session_config(user_req)

    async def event_generator():
        nonlocal user_req
        logger.info("[shadow_stream] start session=%s request_id=%s", session_id, rid)
        yield _sse("session", {"session_id": session_id})

        should_resume = await _try_prepare_resume(graph, user_req, config)
        graph_input = None if should_resume else {"request": user_req}

        try:
            async for event in graph.astream_events(graph_input, config=config, version="v2"):
                if not _is_public_stream_token(event):
                    continue
                content = _stream_chunk_text(event)
                if content:
                    yield _sse("token", {"text": content, "node": _stream_event_node(event)})

            snapshot = await graph.aget_state(config)
            result = dict(getattr(snapshot, "values", {}) or {})
            phase, reply = _pick_phase_and_reply(result)
            category = result.get("category", "")
            yield _sse("done", {
                "session_id": session_id,
                "phase": phase,
                "category": category,
                "reply": reply,
                "error": None,
            })
            logger.info("[shadow_stream] done session=%s category=%s request_id=%s", session_id, category, rid)

            # 塔罗/星座/情绪专项：持久化会话数据
            if category in ("TAROT", "ZODIAC", "EMOTION_LOG"):
                try:
                    await save_tarot_session(
                        user_id=user_req.user_id,
                        session_id=session_id,
                        category=category,
                        request_body=user_req,
                        result=result,
                        phase=phase,
                        reply=reply,
                    )
                except Exception as persist_err:
                    logger.warning("[shadow_stream] tarot session 持久化失败: %s", persist_err)
        except Exception as exc:
            mapped = upstream_model_http_exception(exc)
            if isinstance(exc, HTTPException):
                message = exc.detail
            elif mapped is not None:
                message = mapped.detail
            else:
                message = "流式对话执行失败，请稍后重试"
            logger.exception("[shadow_stream] failed request_id=%s", rid)
            yield _sse("error", {"message": message})

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=_SSE_HEADERS)
