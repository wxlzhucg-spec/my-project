# -*- coding: utf-8 -*-
"""
影子 AI — 情绪深度分析：分析阶段 (analyze.py)

【流程】[astro_insight_node, search_node] → analyze_node → draft_node
【功能】
  search_node  : 联网搜索问题相关案例与机制，并整理成可分析语料
  analyze_node : 底层逻辑综合分析（LLM 轻量调用）
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage

from ....common.models import AgentState
from ..web_search import fetch_web_context
from ...llm.llm import get_light_llm
from ...prompts import get_issue_context_prompt, get_root_logic_prompt

logger = logging.getLogger(__name__)


def _combine_supplements(state: AgentState) -> str:
    """统一拼接追问回答与补充信息。"""
    answers = [item.strip() for item in state.get("clarification_answers", []) if item and item.strip()]
    if answers:
        return "\n".join(answers)
    req = state["request"]
    return (req.supplements or "").strip()


def _build_issue_search_query(question: str, emotion_keyword: str, supplements: str = "") -> str:
    """为情绪深度分析生成更贴近案例与机制的搜索 query。"""
    parts = [question.strip()]
    if supplements:
        parts.append(f"补充背景 {supplements.strip()}")
    if emotion_keyword:
        parts.append(f"{emotion_keyword} 情绪")
    parts.append("最新案例 原因 底层逻辑 心理机制 应对")
    query = " ".join(part for part in parts if part).strip()
    return query[:160]


async def search_node(state: AgentState) -> dict:
    """
    问题语境检索节点（联网搜索 + LLM 整理）。

    输入: request.*, supplements
    输出: issue_context, issue_search_query, issue_web_context
    """
    req = state["request"]
    combined_supplements = _combine_supplements(state)
    search_query = _build_issue_search_query(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        supplements=combined_supplements,
    )

    logger.info("[search_node] 检索问题语境并补充联网语料 query=%s", search_query)
    search_result = await fetch_web_context(
        search_query,
        count=6,
        freshness="noLimit",
        missing_service_message="未配置问题联网搜索服务，以下分析只能基于用户描述和已有上下文，不能伪造最新案例。",
        unavailable_message="问题联网搜索暂不可用，以下分析需以用户输入为主，最新案例与机制只能做谨慎泛化。",
    )

    prompt = get_issue_context_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti or "未知",
        supplements=combined_supplements,
        web_context=search_result["context"],
        search_query=search_result["search_query"],
    )
    response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[search_node] 问题语境检索完成")
    return {
        "issue_context": response.content,
        "issue_search_query": search_result["search_query"],
        "issue_web_context": search_result["context"],
        "web_search": search_result["web_search"],
    }


async def analyze_node(state: AgentState) -> dict:
    """
    底层逻辑综合分析节点（LLM 调用，轻量）。

    输入: astro_focus, issue_context, request.*, clarification_answers
    输出: root_logic
    """
    if state.get("root_logic"):
        return {"root_logic": state["root_logic"]}

    req = state["request"]
    combined_supplements = _combine_supplements(state)

    prompt = get_root_logic_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti or "未知",
        astro_focus=state.get("astro_focus", ""),
        issue_context=state.get("issue_context", ""),
        supplements=combined_supplements,
    )
    response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])

    return {"root_logic": response.content}
