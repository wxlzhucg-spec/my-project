# -*- coding: utf-8 -*-
"""
影子 AI — 数据模型定义 (models.py)

【职责】
  定义主对话流水线（/api/chat）的请求体、响应体和 LangGraph 状态。
"""
from __future__ import annotations

from typing import Annotated, Any, Optional, TypedDict
from operator import add as _list_add

def _max_int(left: int, right: int) -> int:
    """取两个值的最大值，解决同一 step 中多节点并发写 int 的问题。"""
    return max(left or 0, right or 0)

def _or_bool(left: bool, right: bool) -> bool:
    """取两个值的逻辑或，解决同一 step 中多节点并发写 bool 的问题。"""
    return bool(left or right)

from langgraph.graph.message import add_messages
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
    category: Optional[str] = Field(
        None,
        description="前端直接指定类型：TAROT/ZODIAC/EMOTION_LOG；留空则由路由节点分类",
    )
    tarot_cards: Optional[list[dict]] = Field(
        None,
        description="塔罗选牌结果列表，每项可含 name/position/reversed/meaning 等字段",
    )
    zodiac_data: Optional[dict] = Field(
        None,
        description="星座运势前端数据，如 sign/period/horoscope_text 等",
    )
    emotion_log: Optional[dict] = Field(
        None,
        description="情绪记录数据，如 emotion/intensity/note/record_time 等",
    )
    emotion_keyword: str = Field(
        "",
        description="用户当前核心情绪关键词，如：焦虑/迷茫/愤怒/失落。留空由系统自动判断",
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

    session_id 始终返回，供前端多轮对话与 LangGraph thread 对齐（不依赖 debug_info）。
    category 返回路由分类结果，让调用方知道走了哪个分支。
    """

    session_id: str = Field(
        ...,
        description="本轮使用的会话 ID；后续请求原样带回以延续同一线程",
    )
    phase: str = Field(
        ...,
        description="当前阶段：clarifying=追问中，complete=分析完成",
        examples=["clarifying", "complete"],
    )
    category: str = Field(
        "",
        description="路由分类：GENERAL/WEB/EMOTION_DEEP/TAROT/ZODIAC/EMOTION_LOG",
        examples=["GENERAL", "WEB", "EMOTION_DEEP"],
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

    # ── 入口与统一路由 ──
    request: UserRequest
    """用户原始请求。"""
    category: str
    """路由分类：TAROT/ZODIAC/EMOTION_LOG/GENERAL/WEB/EMOTION_DEEP。"""
    web_search: Annotated[bool, _or_bool]
    """是否启用联网搜索。"""
    web_context: str
    """联网搜索补充上下文。"""
    user_info: dict
    """补全后的用户信息快照。"""
    messages: Annotated[list[Any], add_messages]
    """最终进入会话记忆的消息。"""
    internal_notes: Annotated[list[str], _list_add]
    """中间草稿暂存区，不写入 messages。"""
    refine_count: Annotated[int, _max_int]
    """打磨次数计数（取最大值避免并发冲突）。"""

    # ── clarify_node 产出 (LLM, 第一轮) ──
    clarification: str
    """LLM 生成的追问文本，像朋友一样询问用户补充信息。"""
    clarification_round: Annotated[int, _max_int]
    """当前追问轮次，从0开始。"""
    clarification_answers: list[str]
    """用户每轮追问的回答列表。"""

    # ── astro_node 产出 (本地计算) ──
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

    # ── search_node 产出 (联网搜索 + LLM) ──
    issue_search_query: str
    """问题联网搜索实际使用的 query。"""
    issue_web_context: str
    """问题联网搜索的原始语料/摘要，供调试与二次分析。"""
    issue_context: str
    """问题相关检索素材（场景/压力/最新案例/相关逻辑/在意/卡点）。"""

    # ── analyze_node 产出 (LLM) ──
    root_logic: str
    """底层逻辑分析（核心矛盾/为何现在明显/旧模式代价）。"""

    # ── combine_node 产出 (LLM) ──
    reply: str
    """最终合成回复，朋友语气，含核心分析+建议。"""
