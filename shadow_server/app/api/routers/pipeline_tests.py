# -*- coding: utf-8 -*-
"""主对话流水线调试路由。"""
from __future__ import annotations

import logging
import time
from typing import Annotated, Literal

from fastapi import APIRouter, Body, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from ...common.geocode import geocode, geocode_with_detail
from ...common.models import UserRequest
from ...core.router import router_node
from ...core.branches.general import generate_node
from ...core.branches.specialist import specialist_node
from ...core.branches.web_search import web_search_node
from ...core.branches.emotion_deep import (
    analyze_node,
    astro_insight_node,
    astro_node,
    clarify_node,
    combine_node,
    draft_node,
    ephemeris_node,
    prepare_node,
    refine_node,
    search_node,
)
from ...core.prompts import (
    get_astro_focus_prompt,
    get_clarify_prompt,
    get_deep_synthesis_prompt,
    get_draft_prompt,
    get_general_prompt,
    get_issue_context_prompt,
    get_refine_prompt,
    get_root_logic_prompt,
    get_router_prompt,
    get_specialist_prompt,
)

logger = logging.getLogger(__name__)
TestGraphNode = Literal[
    "router", "specialist", "web_search", "generate",
    "clarify", "astro", "ephemeris", "astro_insight", "search", "analyze", "draft", "refine", "combine",
]
TestPromptNode = Literal[
    "router", "specialist", "general", "clarify", "astro_insight", "search", "analyze", "draft", "refine", "combine",
]
_NODE_DISPATCH = {
    "router": router_node,
    "specialist": specialist_node,
    "web_search": web_search_node,
    "generate": generate_node,
    "clarify": clarify_node,
    "astro": astro_node,
    "ephemeris": ephemeris_node,
    "astro_insight": astro_insight_node,
    "search": search_node,
    "analyze": analyze_node,
    "draft": draft_node,
    "refine": refine_node,
    "combine": combine_node,
}

_MOCK_ASTRO_CONTEXT = "太阳双子座·第11宫；月亮巨蟹座·第12宫；上升狮子座。"
_MOCK_EPHEMERIS = "近7天星历窗口：本周主轴：情绪安全感与内在需求"
_MOCK_ASTRO_FOCUS = "【星象主轴】情绪安全感与自我表达之间的拉扯。\n【顺势资源】适合通过表达整理思绪。"
_MOCK_ISSUE_CONTEXT = "【问题场景】被工作压力和不确定感反复拉扯。\n【现实压力】任务密集且评价明确。"
_MOCK_ROOT_LOGIC = "【核心矛盾】一边渴望确认方向，一边害怕行动暴露不够好。"
_MOCK_DRAFT = "我能感觉到你现在不是简单的累，而是一直在撑着。你一边想把事情做好，一边又害怕自己怎么做都不够。"


def _make_prompt_builders(request, state):
    """根据 request 和 state 构造 prompt builder 字典。"""
    return {
        "router": lambda: get_router_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知"),
        "specialist": lambda: get_specialist_prompt(category=(request.category or "TAROT").upper(), question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", blood_type=request.blood_type or "unknown", specialist_data="{}"),
        "web_search": lambda: "<web_search 节点无 LLM 调用，纯 HTTP 请求>",
        "generate": lambda: get_general_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", blood_type=request.blood_type or "unknown", history="", web_context=state.get("web_context", "")),
        "clarify": lambda: get_clarify_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知"),
        "astro": lambda: "<astro 节点无 LLM 调用，纯 flatlib 本地计算>",
        "ephemeris": lambda: "<ephemeris 节点无 LLM 调用，纯本地计算>",
        "astro_insight": lambda: get_astro_focus_prompt(astro_analysis=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), question=request.question, supplements=request.supplements or ""),
        "search": lambda: get_issue_context_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", supplements=request.supplements or ""),
        "analyze": lambda: get_root_logic_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), supplements=request.supplements or ""),
        "draft": lambda: get_draft_prompt(emotion_keyword=request.emotion_keyword, question=request.question, mbti=request.mbti or "未知", astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC), supplements=request.supplements or ""),
        "refine": lambda: get_refine_prompt(draft=(state.get("internal_notes") or [_MOCK_DRAFT])[-1], refine_round=max(1, int(state.get("refine_count", 0)) + 1), astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC)),
        "combine": lambda: get_deep_synthesis_prompt(emotion_keyword=request.emotion_keyword, question=request.question, mbti=request.mbti or "未知", astro_analysis=state.get("astro_analysis", _MOCK_ASTRO_CONTEXT), astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC), supplements=request.supplements or ""),
    }


_PROMPT_BUILDERS = None  # 在 test/step 中动态构建


async def _invoke_test_node(node, state):
    out = _NODE_DISPATCH[node](state)
    if hasattr(out, "__await__"):
        out = await out
    return out


async def _build_deep_state(request):
    state = {"request": request}
    state.update(await _invoke_test_node("astro", state))
    sr = await _invoke_test_node("search", state)
    state.update(await _invoke_test_node("ephemeris", state))
    state.update(await _invoke_test_node("astro_insight", state))
    state.update(sr)
    state.update(await _invoke_test_node("analyze", state))
    return state


async def _build_test_state(request, target_node):
    state = {"request": request}
    if target_node in {"router", "clarify", "astro", "search"}:
        return state
    if target_node == "specialist":
        state["category"] = (request.category or "TAROT").upper()
        return state
    if target_node == "web_search":
        state.update({"category": "WEB", "web_search": True})
        return state
    if target_node == "generate":
        state.update({"category": "GENERAL", "web_search": False, "web_context": ""})
        return state
    if target_node == "ephemeris":
        state.update(await _invoke_test_node("astro", state))
        return state
    if target_node == "astro_insight":
        state.update(await _invoke_test_node("astro", state))
        state.update(await _invoke_test_node("ephemeris", state))
        return state
    if target_node in {"analyze", "draft", "refine", "combine"}:
        state = await _build_deep_state(request)
        if target_node == "analyze":
            return state
        state.update(await _invoke_test_node("draft", state))
        if target_node == "draft":
            return state
        state.update(await _invoke_test_node("refine", state))
        if target_node == "refine":
            return state
        state.update(await _invoke_test_node("refine", state))
        return state
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
            "router": lambda: get_router_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知"),
            "specialist": lambda: get_specialist_prompt(category=(request.category or "TAROT").upper(), question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", blood_type=request.blood_type or "unknown", specialist_data="{}"),
            "general": lambda: get_general_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", blood_type=request.blood_type or "unknown", history="", web_context=state.get("web_context", "")),
            "clarify": lambda: get_clarify_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知"),
            "astro_insight": lambda: get_astro_focus_prompt(astro_analysis=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), question=request.question, supplements=request.supplements or ""),
            "search": lambda: get_issue_context_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", supplements=request.supplements or ""),
            "analyze": lambda: get_root_logic_prompt(question=request.question, emotion_keyword=request.emotion_keyword, mbti=request.mbti or "未知", astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), supplements=request.supplements or ""),
            "draft": lambda: get_draft_prompt(emotion_keyword=request.emotion_keyword, question=request.question, mbti=request.mbti or "未知", astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC), supplements=request.supplements or ""),
            "refine": lambda: get_refine_prompt(draft=(state.get("internal_notes") or [_MOCK_DRAFT])[-1], refine_round=max(1, int(state.get("refine_count", 0)) + 1), astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC)),
            "combine": lambda: get_deep_synthesis_prompt(emotion_keyword=request.emotion_keyword, question=request.question, mbti=request.mbti or "未知", astro_analysis=state.get("astro_analysis", _MOCK_ASTRO_CONTEXT), astro_context=state.get("astro_context", _MOCK_ASTRO_CONTEXT), ephemeris_summary=state.get("ephemeris_summary", _MOCK_EPHEMERIS), astro_focus=state.get("astro_focus", _MOCK_ASTRO_FOCUS), issue_context=state.get("issue_context", _MOCK_ISSUE_CONTEXT), root_logic=state.get("root_logic", _MOCK_ROOT_LOGIC), supplements=request.supplements or ""),
        }
        return {"node": node, "prompt": builders[node]()}

    # ── 功能模块测试接口 ──

    @test.post("/geocode")
    async def test_geocode(address: str = Body(..., embed=True, description="中文地址，如 '上海市' 或 '甘肃省天水市武山县'")):
        """测试地理编码：地址 → 经纬度 + 标准化地址 + 匹配级别。"""
        try:
            t0 = time.monotonic()
            detail = geocode_with_detail(address)
            ms = round((time.monotonic() - t0) * 1000)
            return {**detail, "ms": ms}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))

    @test.post("/step")
    async def test_node_step(request: UserRequest, node: Annotated[TestGraphNode, Query()]):
        """
        单节点分步测试：返回 input_state / prompt / output / timing。
        可视化每一步的输入、Prompt、输出、耗时。
        """
        try:
            state = await _build_test_state(request, node)
            # 序列化 input_state（排除不可 JSON 化的字段）
            input_snapshot = {}
            for k, v in state.items():
                try:
                    import json
                    json.dumps({k: v}, default=str)
                    input_snapshot[k] = v
                except Exception:
                    input_snapshot[k] = f"<{type(v).__name__}>"

            # 获取 prompt（如果该节点有对应 prompt builder）
            prompt_text = None
            builders = _make_prompt_builders(request, state)
            if node in builders:
                try:
                    prompt_text = builders[node]()
                except Exception:
                    prompt_text = "<prompt 构建失败>"

            # 运行节点
            t0 = time.monotonic()
            out = await _invoke_test_node(node, state)
            ms = round((time.monotonic() - t0) * 1000)

            # 序列化 output
            output_snapshot = {}
            for k, v in out.items():
                try:
                    import json
                    json.dumps({k: v}, default=str)
                    output_snapshot[k] = v
                except Exception:
                    output_snapshot[k] = f"<{type(v).__name__}>"

            return {
                "node": node,
                "input_state": input_snapshot,
                "prompt": prompt_text,
                "output": output_snapshot,
                "ms": ms,
            }
        except Exception as exc:
            logger.exception("分步测试节点 %s 失败", node)
            raise HTTPException(status_code=500, detail=str(exc))

    application.include_router(test)
