# -*- coding: utf-8 -*-
"""主对话流水线调试路由。"""
from __future__ import annotations
import logging
from typing import Annotated, Literal
from fastapi import APIRouter, FastAPI, HTTPException, Query
from ..models import UserRequest
from ..nodes import analyze_node, astro_insight_node, astro_node, clarify_node, combine_node, ephemeris_node, search_node
from ..prompts import get_astro_focus_prompt, get_clarify_prompt, get_deep_synthesis_prompt, get_issue_context_prompt, get_root_logic_prompt

logger = logging.getLogger(__name__)
TestGraphNode = Literal["clarify", "astro", "ephemeris", "astro_insight", "search", "analyze", "combine"]
TestPromptNode = Literal["clarify", "astro_insight", "search", "analyze", "combine"]
_NODE_DISPATCH = {"clarify": clarify_node, "astro": astro_node, "ephemeris": ephemeris_node, "astro_insight": astro_insight_node, "search": search_node, "analyze": analyze_node, "combine": combine_node}

_MOCK_ASTRO_CONTEXT = "太阳双子座·第11宫；月亮巨蟹座·第12宫；上升狮子座。"
_MOCK_EPHEMERIS = "近7天星历窗口：本周主轴：情绪安全感与内在需求"
_MOCK_ASTRO_FOCUS = "【星象主轴】情绪安全感与自我表达之间的拉扯。\n【顺势资源】适合通过表达整理思绪。"
_MOCK_ISSUE_CONTEXT = "【问题场景】被工作压力和不确定感反复拉扯。\n【现实压力】任务密集且评价明确。"
_MOCK_ROOT_LOGIC = "【核心矛盾】一边渴望确认方向，一边害怕行动暴露不够好。"

async def _invoke_test_node(node, state):
    out = _NODE_DISPATCH[node](state)
    if hasattr(out, "__await__"): out = await out
    return out

async def _build_test_state(request, target_node):
    state = {"request": request}
    if target_node in {"clarify", "astro", "search"}: return state
    if target_node == "ephemeris":
        state.update(await _invoke_test_node("astro", state)); return state
    if target_node == "astro_insight":
        state.update(await _invoke_test_node("astro", state))
        state.update(await _invoke_test_node("ephemeris", state)); return state
    if target_node in {"analyze", "combine"}:
        state.update(await _invoke_test_node("astro", state))
        sr = await _invoke_test_node("search", state)
        state.update(await _invoke_test_node("ephemeris", state))
        state.update(await _invoke_test_node("astro_insight", state))
        state.update(sr)
        if target_node == "analyze": return state
        state.update(await _invoke_test_node("analyze", state)); return state
    return state

def register_pipeline_test_routes(application: FastAPI):
    test = APIRouter(prefix="/api/test", tags=["test"])

    @test.post("/node")
    async def test_single_node(request: UserRequest, node: Annotated[TestGraphNode, Query()]):
        try:
            state = await _build_test_state(request, node)
            out = await _invoke_test_node(node, state)
            return {"node": node, "output": out}
        except Exception as exc:
            logger.exception("测试节点 %s 失败", node)
            raise HTTPException(status_code=500, detail=str(exc))

    @test.post("/prompt")
    async def test_prompt(request: UserRequest, node: Annotated[TestPromptNode, Query()]):
        try:
            state = await _build_test_state(request, node)
        except Exception:
            state = {}
        builders = {
            "clarify": lambda: get_clarify_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti),
            "astro_insight": lambda: get_astro_focus_prompt(astro_analysis=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), question=request.question, supplements=request.supplements or ""),
            "search": lambda: get_issue_context_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti, supplements=request.supplements or ""),
            "analyze": lambda: get_root_logic_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti, astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), supplements=request.supplements or ""),
            "combine": lambda: get_deep_synthesis_prompt(emotion_keyword=request.emotion_keyword, question=request.question, mbti=request.mbti, astro_analysis=state.get("astro_analysis", _MOCK_ASTRO_CONTEXT), astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC), supplements=request.supplements or ""),
        }
        return {"node": node, "prompt": builders[node]()}

    application.include_router(test)
