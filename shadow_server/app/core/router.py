# -*- coding: utf-8 -*-
"""
影子 AI — 分类路由器 (router.py)

【职责】
  1. router_node: 识别用户意图，分为六类会话
  2. 条件路由函数: 根据分类结果分发到不同分支

【分类体系】
  专项分类（前端指定）: TAROT, ZODIAC, EMOTION_LOG
  LLM路由分类（自动判断）: GENERAL, WEB, EMOTION_DEEP
"""
from __future__ import annotations

import logging
import re

from langchain_core.messages import HumanMessage

from ..common.models import AgentState
from .llm.llm import get_light_llm
from .prompts import get_router_prompt

logger = logging.getLogger(__name__)

# ── 分类常量 ──────────────────────────────────────────────
SPECIALIST_CATEGORIES = {"TAROT", "ZODIAC", "EMOTION_LOG"}     # 专项（前端指定）
DIRECT_ROUTE_CATEGORIES = SPECIALIST_CATEGORIES | {"EMOTION_DEEP"}
LLM_ROUTE_CATEGORIES = {"GENERAL", "WEB", "EMOTION_DEEP"}      # LLM自动路由
ALL_CATEGORIES = SPECIALIST_CATEGORIES | LLM_ROUTE_CATEGORIES


def _extract_route_label(raw: str) -> str:
    """从 LLM 返回文本中提取分类标签。"""
    text = (raw or "").upper()
    for label in ALL_CATEGORIES:
        if re.search(rf"\b{label}\b", text):
            return label
    return "GENERAL"


def _user_info_snapshot(req) -> dict:
    """提取用户信息快照，存入状态供后续节点使用。"""
    return {
        "user_id": req.user_id,
        "open_id": req.open_id,
        "birth_time": req.birth_time,
        "birth_place": req.birth_place,
        "mbti": req.mbti,
        "blood_type": req.blood_type,
    }


# ══════════════════════════════════════════════════════════
#  router_node: 统一分类入口
# ══════════════════════════════════════════════════════════

async def router_node(state: AgentState) -> dict:
    """
    统一路由节点：识别六类会话类型并初始化当前轮临时状态。

    分类优先级：
      1. 前端通过 request.category 显式指定 TAROT / ZODIAC / EMOTION_LOG / EMOTION_DEEP
      2. 否则调用轻量 LLM 自动分类为 GENERAL / WEB / EMOTION_DEEP
    """
    req = state["request"]
    requested = (req.category or "").strip().upper()

    # 优先用前端指定的分类（包括显式要求走 EMOTION_DEEP）
    if requested in DIRECT_ROUTE_CATEGORIES:
        category = requested
        logger.info("[router_node] 使用前端指定分类: %s", category)
    else:
        # 调用轻量 LLM 自动分类
        logger.info("[router_node] 调用轻量 LLM 分类")
        prompt = get_router_prompt(
            question=req.question,
            emotion_keyword=req.emotion_keyword,
            mbti=req.mbti or "未知",
        )
        response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])
        category = _extract_route_label(response.content)
        # 专项分类不允许由LLM产生，降级为GENERAL
        if category in SPECIALIST_CATEGORIES:
            category = "GENERAL"
        logger.info("[router_node] 分类结果: %s", category)

    # 构造用户消息内容
    user_content = req.question
    if req.supplements:
        user_content = f"{req.question}\n补充：{req.supplements}"

    # 初始化当前轮临时状态
    updates = {
        "category": category,
        "web_search": category == "WEB",
        "web_context": "",
        "user_info": _user_info_snapshot(req),
        "reply": "",
        "clarification": "",
        "astro_analysis": "",
        "astro_context": "",
        "ephemeris_summary": "",
        "astro_focus": "",
        "issue_search_query": "",
        "issue_web_context": "",
        "issue_context": "",
        "root_logic": "",
        "internal_notes": [],
        "refine_count": 0,
        "messages": [HumanMessage(content=user_content)],
    }
    if not req.supplements:
        updates["clarification_round"] = 0
        updates["clarification_answers"] = []
    return updates


# ══════════════════════════════════════════════════════════
#  条件路由函数
# ══════════════════════════════════════════════════════════

def route_after_router(state: AgentState) -> str:
    """
    router_node 之后的分支分发：

      specialist  → specialist_node  (塔罗/星座/情绪记录)
      web         → web_search_node  (联网问答)
      emotion_deep → prepare_node    (情绪深度分析)
      general     → generate_node    (普通聊天)
    """
    category = state.get("category", "GENERAL")
    if category in SPECIALIST_CATEGORIES:
        return "specialist"
    if category == "WEB":
        return "web"
    if category == "EMOTION_DEEP":
        return "emotion_deep"
    return "general"


def route_after_prepare(state: AgentState) -> str:
    """
    prepare_node 之后的分支分发：

      clarify → clarify_node  (追问阶段)
      analyze → astro_node    (分析阶段)
    """
    req = state.get("request")
    has_supplements = bool(req and req.supplements and req.supplements.strip())
    round_num = state.get("clarification_round", 0)
    max_rounds = 1

    if has_supplements and round_num >= max_rounds:
        return "analyze"
    return "clarify"


def route_after_refine(state: AgentState) -> str:
    """
    refine_node 之后的分支分发：

      refine  → refine_node   (继续打磨)
      combine → combine_node  (合成最终回复)
    """
    if int(state.get("refine_count", 0)) < 2:
        return "refine"
    return "combine"
