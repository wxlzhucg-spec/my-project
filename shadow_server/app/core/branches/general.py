# -*- coding: utf-8 -*-
"""
影子 AI — 普通聊天分支 (general.py)

【路由】router_node → GENERAL → generate_node → END
【功能】普通问答 / 联网问答的最终回复生成
"""
from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage

from ...common.models import AgentState
from ..llm.llm import get_llm
from ..prompts import get_general_prompt

logger = logging.getLogger(__name__)


def _format_message_history(messages: list, limit: int = 8) -> str:
    """格式化对话记忆，供 Prompt 使用。"""
    if not messages:
        return ""
    lines = []
    for msg in messages[-limit:]:
        role = getattr(msg, "type", msg.__class__.__name__)
        content = getattr(msg, "content", str(msg))
        if content:
            lines.append(f"{role}: {content[:500]}")
    return "\n".join(lines)


async def generate_node(state: AgentState) -> dict:
    """
    普通/联网问答生成节点。

    输入: request.*, messages, web_context
    输出: reply, messages
    """
    req = state["request"]
    logger.info("[generate_node] 生成通用回复 web_search=%s", state.get("web_search", False))

    prompt = get_general_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti or "未知",
        blood_type=req.blood_type or "unknown",
        history=_format_message_history(state.get("messages", [])),
        web_context=state.get("web_context", ""),
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[generate_node] 通用回复生成完成")
    return {"reply": response.content, "messages": [AIMessage(content=response.content)]}
