# -*- coding: utf-8 -*-
"""
影子 AI — 情绪深度分析：生成阶段 (generate.py)

【流程】draft_node → refine_node（循环）→ combine_node → END
【功能】
  draft_node   : 生成情绪深度分析草稿（只进入 internal_notes）
  refine_node  : 打磨草稿（2轮循环）
  combine_node : 合成最终回复
"""
from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage

from ....common.models import AgentState
from ...llm.llm import get_llm, get_reasoner_llm
from ...prompts import get_deep_synthesis_prompt, get_draft_prompt, get_refine_prompt

logger = logging.getLogger(__name__)


async def draft_node(state: AgentState) -> dict:
    """
    情绪深度分析草稿节点，草稿只进入 internal_notes。

    输入: request.*, astro_context, astro_focus, issue_context, root_logic, supplements
    输出: internal_notes, refine_count
    """
    req = state["request"]
    answers = state.get("clarification_answers", [])
    combined_supplements = "\n".join(answers) if answers else (req.supplements or "")

    logger.info("[draft_node] 生成情绪深度分析草稿")

    prompt = get_draft_prompt(
        emotion_keyword=req.emotion_keyword,
        question=req.question,
        mbti=req.mbti or "未知",
        astro_context=state.get("astro_context") or state.get("astro_analysis", ""),
        ephemeris_summary=state.get("ephemeris_summary", ""),
        astro_focus=state.get("astro_focus", ""),
        issue_context=state.get("issue_context", ""),
        root_logic=state.get("root_logic", ""),
        supplements=combined_supplements,
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])

    notes = list(state.get("internal_notes", []))
    notes.append(response.content)

    logger.info("[draft_node] 草稿生成完成")
    return {"internal_notes": notes, "refine_count": 0}


async def refine_node(state: AgentState) -> dict:
    """
    情绪深度分析打磨节点，两轮循环后由 combine_node 落最终回复。

    输入: internal_notes, refine_count
    输出: internal_notes, refine_count
    """
    notes = list(state.get("internal_notes", []))
    draft = notes[-1] if notes else state.get("reply", "")
    refine_count = int(state.get("refine_count", 0))
    refine_round = refine_count + 1

    logger.info("[refine_node] 开始第 %d 轮打磨", refine_round)

    prompt = get_refine_prompt(
        draft=draft,
        refine_round=refine_round,
        astro_context=state.get("astro_context") or state.get("astro_analysis", ""),
        root_logic=state.get("root_logic", ""),
    )
    llm = get_llm() if refine_round == 1 else get_reasoner_llm()
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    notes.append(response.content)
    logger.info("[refine_node] 第 %d 轮打磨完成", refine_round)
    return {"internal_notes": notes, "refine_count": refine_round}


async def combine_node(state: AgentState) -> dict:
    """
    最终合成回复节点。

    如果经过2轮打磨，直接使用最终打磨稿。
    否则，用 deep_synthesis_prompt 重新合成。

    输入: 所有前面节点的产出 + clarification_answers
    输出: reply, messages
    """
    notes = state.get("internal_notes", [])
    if notes and state.get("refine_count", 0) >= 2:
        final = notes[-1]
        logger.info("[combine_node] 使用打磨最终稿写入回复")
        return {"reply": final, "messages": [AIMessage(content=final)]}

    req = state["request"]
    answers = state.get("clarification_answers", [])
    combined_supplements = "\n".join(answers) if answers else ""

    prompt = get_deep_synthesis_prompt(
        emotion_keyword=req.emotion_keyword,
        question=req.question,
        mbti=req.mbti,
        astro_analysis=state.get("astro_analysis", ""),
        astro_context=state.get("astro_context") or state.get("astro_analysis", ""),
        ephemeris_summary=state.get("ephemeris_summary", ""),
        astro_focus=state.get("astro_focus", ""),
        issue_context=state.get("issue_context", ""),
        root_logic=state.get("root_logic", ""),
        supplements=combined_supplements,
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[combine_node] 最终回复生成完成")
    return {"reply": response.content, "messages": [AIMessage(content=response.content)]}
