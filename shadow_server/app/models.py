# -*- coding: utf-8 -*-
"""
影子 AI — 数据模型定义 (models.py)

【职责】
  定义主对话流水线（/api/chat）的请求体、响应体和 LangGraph 状态。
"""
from __future__ import annotations

from typing import Optional, TypedDict

from pydantic import BaseModel, Field


# ════════════════════════════════════════════════════════════
#  API 请求/响应模型
# ════════════════════════════════════════════════════════════


class UserRequest(BaseModel):
    """
    主对话流水线的请求体。

    两种使用方式：
      1. 传 open_id：自动从 users 表查询 birth_time/birth_place/mbti 等信息
      2. 手动填写：直接传入 birth_time/birth_place/mbti 等字段

    两阶段复用同一个请求体：
      第一轮（追问）：只填 question + 基础信息，不填 supplements
      第二轮（分析）：填 supplements（用户对追问的回答）
    """

    session_id: Optional[str] = Field(
        None,
        description="会话ID，用于多轮记忆（LangGraph checkpointer 根据 thread_id 区分会话）",
    )
    user_id: Optional[int] = Field(
        None,
        description="用户数据库 ID，优先级高于 open_id，直接从 users 表查用户资料",
    )
    open_id: Optional[str] = Field(
        None,
        description="微信 open_id，传入后自动从 users 表查询 birth_time/birth_place/mbti 等信息，无需手动填写",
    )
    birth_time: Optional[str] = Field(
        None,
        description="出生时间，支持多种格式：'1995-06-15 14:30' 或 '1995/06/15 14:30'。传了 open_id 可不填",
        examples=["1995-06-15 14:30", "1995/06/15 08:00"],
    )
    birth_place: Optional[str] = Field(
        None,
        description="出生地点，支持区县级中文地址：'甘肃省天水市武山县' 或 '上海市'。传了 open_id 可不填",
        examples=["甘肃省天水市武山县", "浙江省杭州市西湖区", "上海市"],
    )
    mbti: Optional[str] = Field(
        None,
        description="MBTI 性格类型，16种之一，影响分析和建议的语气与方向。传了 open_id 可不填",
        examples=["INFP", "INTJ", "ENFP"],
    )
    blood_type: Optional[str] = Field(
        None,
        description="血型（A/B/O/AB），传了 open_id 可不填",
    )
    emotion_keyword: str = Field(
        ...,
        description="用户当前核心情绪关键词，如：焦虑/迷茫/愤怒/失落",
        examples=["焦虑", "迷茫", "愤怒", "失落", "疲惫"],
    )
    question: str = Field(
        ...,
        description="用户倾诉的问题或困扰，这是整个对话的核心内容",
        examples=["工作压力太大不知道怎么办", "感觉人生没有意义"],
    )
    supplements: Optional[str] = Field(
        None,
        description=(
            "用户对追问的补充回答（第二轮传入）。"
            "第一轮请求不填此字段，系统会返回追问；"
            "用户回答后填入此字段，系统进入完整分析。"
        ),
        examples=["最近主要是和领导关系很紧张，加班到很晚也不敢拒绝"],
    )


class ChatResponse(BaseModel):
    """
    主对话流水线的响应体。

    phase 字段区分两阶段：
      - "clarifying"：追问阶段，需要用户补充信息
      - "complete"：分析完成，返回最终回复
    """

    phase: str = Field(
        ...,
        description="当前阶段：clarifying=追问中，complete=分析完成",
        examples=["clarifying", "complete"],
    )
    reply: str = Field(
        ...,
        description="影子回复内容（追问文本 或 最终分析回复）",
    )
    error: Optional[str] = Field(
        None,
        description="错误信息（如有）",
    )
    debug_info: Optional[dict] = Field(
        None,
        description="调试信息，包含各节点原始输出。",
    )


# ════════════════════════════════════════════════════════════
#  LangGraph 状态定义
# ════════════════════════════════════════════════════════════


class AgentState(TypedDict, total=False):
    """
    主对话流水线的共享状态。

    字段按流水线阶段逐步填充。
    total=False 表示所有字段都是可选的。
    """

    # ── 入口 ──
    request: UserRequest
    """用户原始请求。"""

    # ── clarify_node 产出 (LLM, 第一轮) ──
    clarification: str
    """LLM 生成的追问文本，像朋友一样询问用户补充信息。"""
    clarification_round: int
    """当前追问轮次，从0开始。"""
    clarification_answers: list[str]
    """用户每轮追问的回答列表。"""

    # ── astro_node 产出 (本地计算) ──
    astro_chart: Optional[dict]
    """原始星盘数据 dict，仅供 ephemeris_node 内部消费。"""
    astro_analysis: str
    """星盘完整文字版，供调试/展示。"""
    astro_context: str
    """星盘上下文精简摘要，供 LLM 节点消费。"""

    # ── ephemeris_node 产出 (本地计算) ──
    ephemeris_summary: str
    """近7天星历文字摘要。"""

    # ── astro_insight_node 产出 (LLM) ──
    astro_focus: str
    """占星输入素材（星象主轴/顺势资源/风险点/时间窗口）。"""

    # ── search_node 产出 (LLM) ──
    issue_context: str
    """问题相关检索素材（场景/压力/在意/卡点）。"""

    # ── analyze_node 产出 (LLM) ──
    root_logic: str
    """底层逻辑分析（核心矛盾/为何现在明显/旧模式代价）。"""

    # ── combine_node 产出 (LLM) ──
    reply: str
    """最终合成回复，朋友语气，含核心分析+建议。"""
