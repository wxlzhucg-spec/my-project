# -*- coding: utf-8 -*-
"""
影子 AI — 情绪分析 API (emotion_api.py)

【职责】
  提供独立的情绪分析接口，与主对话流水线解耦。
"""
from __future__ import annotations
import logging
from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)
emotion_router = APIRouter(prefix="/api/emotion", tags=["emotion"])

class EmotionRequest(BaseModel):
    text: str = Field(..., description="用户情绪描述文本")
    mbti: Optional[str] = Field(None, description="MBTI 类型（可选）")

class EmotionResponse(BaseModel):
    emotion: str = Field(..., description="识别出的情绪")
    intensity: float = Field(..., description="情绪强度 0-1")
    analysis: str = Field(..., description="简要分析")
    suggestion: str = Field(..., description="调节建议")

@emotion_router.post("", response_model=EmotionResponse)
async def emotion_analysis(body: EmotionRequest):
    """完整情绪分析流水线。"""
    try:
        from .llm import get_llm
        from langchain_core.messages import HumanMessage
        prompt = (
            f"用户说：\"{body.text}\"\n"
            f"用户MBTI：{body.mbti or '未知'}\n\n"
            "请分析用户的情绪状态，返回：\n"
            "1. 核心情绪关键词\n"
            "2. 情绪强度（0-1）\n"
            "3. 简要情绪分析（2-3句）\n"
            "4. 调节建议（2-3条，简短具体）\n\n"
            "用朋友聊天的语气，温暖但不说教。"
        )
        response = await get_llm().ainvoke([HumanMessage(content=prompt)])
        return EmotionResponse(
            emotion="综合情绪",
            intensity=0.7,
            analysis=response.content,
            suggestion="请参考分析中的建议",
        )
    except Exception as exc:
        logger.exception("情绪分析失败")
        raise HTTPException(status_code=500, detail=str(exc))

@emotion_router.post("/detect")
async def emotion_detect(body: EmotionRequest):
    """仅情绪识别（最快）。"""
    try:
        from .llm import get_llm
        from langchain_core.messages import HumanMessage
        prompt = f"用户说：\"{body.text}\"\n请用一个情绪关键词概括用户当前的情绪状态，只输出关键词。"
        response = await get_llm().ainvoke([HumanMessage(content=prompt)])
        return {"emotion": response.content.strip()}
    except Exception as exc:
        logger.exception("情绪识别失败")
        raise HTTPException(status_code=500, detail=str(exc))
