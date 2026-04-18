# -*- coding: utf-8 -*-
"""
影子 AI — 主对话流水线节点定义 (nodes.py)

【职责】
  定义主对话流水线的节点函数，供 graph.py 组装 DAG。

【流程】

  第一轮（追问阶段，无 supplements）：
    prepare_node → clarify_node → END

  第二轮（完整分析阶段，有 supplements）：
    prepare_node → astro_node → [ephemeris_node, search_node（并行）]
    ephemeris_node → astro_insight_node
    [astro_insight_node, search_node] → analyze_node
    analyze_node → combine_node → END
"""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage

from .llm import get_llm, get_light_llm
from .models import AgentState
from .prompts import (
    get_astro_focus_prompt,
    get_clarify_prompt,
    get_deep_synthesis_prompt,
    get_issue_context_prompt,
    get_root_logic_prompt,
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
#  占星计算工具函数
# ════════════════════════════════════════════════════════════


def _compute_natal_chart(birth_time: str, birth_place: str) -> dict:
    """
    计算本命星盘（使用 flatlib 本地计算）。

    返回格式：
      {
        "raw": flatlib.Chart 对象,
        "text": 完整文字版星盘解读,
        "context": 精简版上下文摘要,
      }
    """
    try:
        from flatlib.chart import Chart
        from flatlib.datetime import Datetime as FlatDatetime
        from flatlib.geopos import GeoPos

        from .geocode import geocode

        # 解析出生时间
        parts = birth_time.replace("/", "-").strip().split()
        date_str = parts[0]
        time_str = parts[1] if len(parts) > 1 else "12:00"

        # 地理编码
        lat, lon = geocode(birth_place)
        pos = GeoPos(lat, lon)

        # 构造 flatlib Datetime
        date_parts = date_str.split("-")
        time_parts = time_str.split(":")
        flat_date = FlatDatetime(
            date_parts[0], date_parts[1], date_parts[2],
            time_parts[0], time_parts[1],
            "+08:00"  # 默认东八区
        )

        chart = Chart(flat_date, pos)

        # 生成文字版
        text = _format_chart_text(chart)
        context = _format_chart_context(chart)

        return {
            "raw": chart,
            "text": text,
            "context": context,
        }
    except Exception as exc:
        logger.warning("星盘计算失败，使用占位文本: %s", exc)
        return {
            "raw": None,
            "text": f"【星盘计算异常】出生时间: {birth_time}, 出生地点: {birth_place}",
            "context": "星盘数据暂不可用。",
        }


def _format_chart_text(chart) -> str:
    """将 Chart 对象格式化为完整文字版。"""
    try:
        from flatlib import const

        lines = ["【本命盘核心】"]

        # 太阳、月亮、上升
        sun = chart.getObject(const.SUN)
        moon = chart.getObject(const.MOON)
        asc = chart.getAngle(const.ASC)

        lines.append(f"太阳{sun.sign}·第{sun.house}宫")
        lines.append(f"月亮{moon.sign}·第{moon.house}宫")
        lines.append(f"上升{asc.sign}")

        # 其他行星
        for planet_id in [const.MERCURY, const.VENUS, const.MARS,
                          const.JUPITER, const.SATURN]:
            obj = chart.getObject(planet_id)
            if obj:
                lines.append(f"{planet_id}{obj.sign}·第{obj.house}宫")

        # 元素倾向
        elements = {"火象": 0, "土象": 0, "风象": 0, "水象": 0}
        fire = ["Aries", "Leo", "Sagittarius"]
        earth = ["Taurus", "Virgo", "Capricorn"]
        air = ["Gemini", "Libra", "Aquarius"]
        water = ["Cancer", "Scorpio", "Pisces"]

        for planet_id in [const.SUN, const.MOON, const.MERCURY, const.VENUS,
                          const.MARS, const.JUPITER, const.SATURN]:
            obj = chart.getObject(planet_id)
            if obj:
                sign = obj.sign
                if sign in fire:
                    elements["火象"] += 1
                elif sign in earth:
                    elements["土象"] += 1
                elif sign in air:
                    elements["风象"] += 1
                elif sign in water:
                    elements["水象"] += 1

        strong = max(elements, key=elements.get)
        weak = min(elements, key=elements.get)
        lines.append(f"元素倾向：强势{strong}，缺弱{weak}")

        # 关键相位
        lines.append("\n【关键相位】")
        aspects = chart.getAspects()
        for asp in aspects[:5]:
            lines.append(f"- {asp}")

        return "\n".join(lines)
    except Exception as exc:
        logger.warning("星盘文本格式化失败: %s", exc)
        return "星盘格式化异常"


def _format_chart_context(chart) -> str:
    """将 Chart 对象格式化为精简上下文摘要。"""
    try:
        from flatlib import const

        sun = chart.getObject(const.SUN)
        moon = chart.getObject(const.MOON)
        asc = chart.getAngle(const.ASC)

        return (
            f"太阳{sun.sign}·第{sun.house}宫；"
            f"月亮{moon.sign}·第{moon.house}宫；"
            f"上升{asc.sign}。"
        )
    except Exception:
        return "星盘数据暂不可用。"


def _compute_ephemeris(chart) -> str:
    """
    计算近7天星历摘要（本地简化版）。

    实际项目中应使用专业星历数据，此处为简化实现。
    """
    from datetime import datetime, timedelta

    try:
        from flatlib import const

        today = datetime.now()
        lines = [f"近7天星历窗口：{today.strftime('%Y-%m-%d')} 至 {(today + timedelta(days=7)).strftime('%Y-%m-%d')}"]
        lines.append("本周主轴：情绪安全感与内在需求")

        # 简化的星历要点
        lines.append("重点过境：")
        lines.append(f"- {today.strftime('%m-%d')} 月亮过境影响情绪波动")
        lines.append(f"- {(today + timedelta(days=2)).strftime('%m-%d')} 水星相位影响沟通表达")

        return "\n".join(lines)
    except Exception as exc:
        logger.warning("星历计算失败: %s", exc)
        return "星历数据暂不可用。"


# ════════════════════════════════════════════════════════════
#  DAG 节点定义
# ════════════════════════════════════════════════════════════


def prepare_node(state: AgentState) -> dict:
    """
    DAG 入口节点 + 阶段路由。

    多轮追问逻辑：
      - 如果 request.supplements 为空 → 第一轮追问开始
      - 如果 request.supplements 有值 → 追加到回答列表，递增轮次
        然后判断：如果轮次 < 1（只追问1轮），继续追问；否则进入完整分析
    
    初始化 clarification_round 和 clarification_answers 如果不存在。
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
            round_num, len(answers)
        )
    else:
        logger.info("[prepare_node] 无补充信息，开始或继续追问")
    
    # 决定下一阶段
    # 只进行1轮追问
    MAX_ROUNDS = 1
    if round_num >= MAX_ROUNDS:
        stage = "analyze"
        logger.info("[prepare_node] 已达到最大追问轮次 (%d)，进入分析阶段", MAX_ROUNDS)
    else:
        stage = "clarify"
        logger.info("[prepare_node] 继续追问阶段，当前轮次 %d", round_num)
    
    # 返回更新后的状态
    return {
        "clarification_round": round_num,
        "clarification_answers": answers,
    }


# ════════════════════════════════════════════════════════════
#  第一阶段：追问节点
# ════════════════════════════════════════════════════════════


async def clarify_node(state: AgentState) -> dict:
    """
    追问补充信息节点（LLM 调用）。

    输入：request.question, request.emotion_keyword, request.mbti, clarification_answers
    输出：clarification

    基于之前的回答（如果有），像朋友一样追问1个核心问题。
    不做分析、不给建议，纯粹追问。
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


# ════════════════════════════════════════════════════════════
#  第二阶段：完整分析节点
# ════════════════════════════════════════════════════════════


async def astro_node(state: AgentState) -> dict:
    """
    占星数据计算节点（纯本地计算，不调用 LLM）。

    输入：request.birth_time, request.birth_place
    输出：astro_chart, astro_analysis, astro_context
    """
    req = state["request"]
    logger.info("[astro_node] 计算本命星盘...")

    result = _compute_natal_chart(req.birth_time, req.birth_place)

    logger.info("[astro_node] 星盘计算完成")
    return {
        "astro_chart": result["raw"],
        "astro_analysis": result["text"],
        "astro_context": result["context"],
    }


async def ephemeris_node(state: AgentState) -> dict:
    """
    星历计算节点（纯本地计算，不调用 LLM）。

    输入：astro_chart
    输出：ephemeris_summary
    """
    logger.info("[ephemeris_node] 计算近7天星历...")

    chart = state.get("astro_chart")
    summary = _compute_ephemeris(chart)

    logger.info("[ephemeris_node] 星历计算完成")
    return {"ephemeris_summary": summary}


async def astro_insight_node(state: AgentState) -> dict:
    """
    占星素材提炼节点（LLM 调用，轻量）。

    输入：astro_analysis, ephemeris_summary, request.*, supplements
    输出：astro_focus
    """
    req = state["request"]
    answers = state.get("clarification_answers", [])
    combined_supplements = "\n".join(answers) if answers else ""

    logger.info("[astro_insight_node] 提炼占星素材...")

    prompt = get_astro_focus_prompt(
        astro_analysis=state.get("astro_analysis", ""),
        ephemeris_summary=state.get("ephemeris_summary", ""),
        question=req.question,
        supplements=combined_supplements,
    )
    response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[astro_insight_node] 占星素材提炼完成")
    return {"astro_focus": response.content}


async def search_node(state: AgentState) -> dict:
    """
    问题语境检索节点（LLM 调用，轻量）。

    输入：request.*, supplements
    输出：issue_context
    """
    req = state["request"]
    answers = state.get("clarification_answers", [])
    combined_supplements = "\n".join(answers) if answers else ""

    logger.info("[search_node] 检索问题语境...")

    prompt = get_issue_context_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti,
        supplements=combined_supplements,
    )
    response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])

    logger.info("[search_node] 问题语境检索完成")
    return {"issue_context": response.content}


async def analyze_node(state: AgentState) -> dict:
    """
    底层逻辑综合分析节点（LLM 调用，轻量）。

    输入：astro_focus, issue_context, request.*, clarification_answers
    输出：root_logic
    """
    if state.get("root_logic"):
        return {"root_logic": state["root_logic"]}

    req = state["request"]
    answers = state.get("clarification_answers", [])
    combined_supplements = "\n".join(answers) if answers else ""
    
    prompt = get_root_logic_prompt(
        question=req.question,
        emotion_keyword=req.emotion_keyword,
        mbti=req.mbti,
        astro_focus=state.get("astro_focus", ""),
        issue_context=state.get("issue_context", ""),
        supplements=combined_supplements,
    )
    response = await get_light_llm().ainvoke([HumanMessage(content=prompt)])
    return {"root_logic": response.content}


async def combine_node(state: AgentState) -> dict:
    """
    最终合成回复节点（LLM 调用）。

    输入：所有前面节点的产出 + clarification_answers
    输出：reply

    将全部素材合成为朋友语气的最终回复。
    """
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
    return {"reply": response.content}
