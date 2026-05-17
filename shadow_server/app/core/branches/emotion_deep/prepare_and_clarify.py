# -*- coding: utf-8 -*-
"""
影子 AI — 情绪深度分析：追问阶段 (prepare_and_clarify.py)

【流程】prepare_node → clarify_node → END（第一轮追问）
【功能】
  prepare_node : 判断追问轮次，决定走追问还是分析
  clarify_node : 像朋友一样追问1个核心问题
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage

from ....common.models import AgentState
from ...llm.llm import get_llm
from ...prompts import get_clarify_prompt

logger = logging.getLogger(__name__)


def prepare_node(state: AgentState) -> dict:
    """
    情绪深度分析入口节点。

    收到 supplements 时记录追加回答（为 analyze_node 提供上下文），
    同时更新 clarification_round（供后续多轮追问扩展使用）。

    输入: request.*
    输出: clarification_round, clarification_answers
    """
    req = state["request"]
    has_supplements = bool(req.supplements and req.supplements.strip())

    # 初始化状态字段
    round_num = state.get("clarification_round", 0)
    answers = state.get("clarification_answers", [])

    if has_supplements:
        # 用户提供了补充回答，追加到列表并递增轮次
        answers.append(req.supplements.strip())
        round_num += 1
        logger.info(
            "[prepare_node] 收到第 %d 轮回答，当前总回答数 %d",
            round_num, len(answers),
        )
    else:
        logger.info("[prepare_node] 无补充信息，开始追问阶段")

    return {
        "clarification_round": round_num,
        "clarification_answers": answers,
    }


async def clarify_node(state: AgentState) -> dict:
    """
    追问补充信息节点（LLM 调用）。

    基于之前的回答（如果有），像朋友一样追问1个核心问题。
    不做分析、不给建议，纯粹追问。

    输入: request.question, request.emotion_keyword, request.mbti, clarification_answers
    输出: clarification
    """
    req = state["request"]
    answers = state.get("clarification_answers", [])
    round_num = state.get("clarification_round", 0)

    logger.info("[clarify_node] 生成第 %d 轮追问，已有回答数 %d", round_num + 1, len(answers))

    prompt = get_clarify_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti,
        previous_answers=answers,
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[clarify_node] 追问生成完成")
    return {"clarification": response.content}
