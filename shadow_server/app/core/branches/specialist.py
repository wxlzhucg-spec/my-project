# -*- coding: utf-8 -*-
"""
影子 AI — 专项分析分支 (specialist.py)

【路由】router_node → TAROT/ZODIAC/EMOTION_LOG → specialist_node → END
【功能】塔罗解读 / 星座运势 / 情绪记录 的专项深度分析
"""
from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from ...common.models import AgentState
from ..llm.llm import get_llm
from ..prompts import get_specialist_prompt

logger = logging.getLogger(__name__)


def _safe_json(data: Any) -> str:
    """安全序列化数据为 JSON 字符串。"""
    if data is None:
        return "未提供"
    return json.dumps(data, ensure_ascii=False, default=str, indent=2)


async def specialist_node(state: AgentState) -> dict:
    """
    塔罗/星座/情绪记录 专项深度分析节点。

    输入: request.category, request.tarot_cards / zodiac_data / emotion_log
    输出: reply, messages
    """
    req = state["request"]
    category = state.get("category", "GENERAL")

    # 按分类提取专项数据
    payload = {
        "TAROT": req.tarot_cards,
        "ZODIAC": req.zodiac_data,
        "EMOTION_LOG": req.emotion_log,
    }.get(category)

    logger.info("[specialist_node] 开始专项分析: %s", category)

    prompt = get_specialist_prompt(
        category=category,
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti or "未知",
        blood_type=req.blood_type or "unknown",
        specialist_data=_safe_json(payload),
    )
    response = await get_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[specialist_node] 专项分析完成")
    return {"reply": response.content, "messages": [AIMessage(content=response.content)]}
