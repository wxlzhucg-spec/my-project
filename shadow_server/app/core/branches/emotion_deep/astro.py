# -*- coding: utf-8 -*-
"""
影子 AI — 情绪深度分析：占星计算阶段 (astro.py)

【流程】astro_node → [ephemeris_node, search_node（并行）] → astro_insight_node
【功能】
  astro_node         : 计算本命星盘（纯本地计算，不调用 LLM）
  ephemeris_node     : 计算近7天星历摘要（纯本地计算）
  astro_insight_node : 提炼占星素材（LLM 轻量调用）
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage

from ....common.geocode import geocode
from ....common.models import AgentState
from ...llm.llm import get_light_llm
from ...prompts import get_astro_focus_prompt

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════
#  占星计算工具函数
# ══════════════════════════════════════════════════════════


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

        # 解析出生时间
        parts = birth_time.replace("/", "-").strip().split()
        date_str = parts[0]
        time_str = parts[1] if len(parts) > 1 else "12:00"

        # 地理编码
        lat, lon = geocode(birth_place)
        pos = GeoPos(lat, lon)

        # 构造 flatlib Datetime：Datetime(date, time, utcoffset)
        # date 格式: 'YYYY/MM/DD', time 格式: 'HH:MM'
        flat_date = FlatDatetime(
            date_str.replace("-", "/"),
            time_str,
            "+08:00",  # 默认东八区
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
    """将 Chart 对象格式化为标准版文字，供 LLM 分析使用。"""
    try:
        from flatlib import const

        # ── 星座中文映射 ──
        SIGN_ZH = {
            "Aries": "白羊座", "Taurus": "金牛座", "Gemini": "双子座",
            "Cancer": "巨蟹座", "Leo": "狮子座", "Virgo": "处女座",
            "Libra": "天秤座", "Scorpio": "天蝎座", "Sagittarius": "射手座",
            "Capricorn": "摩羯座", "Aquarius": "水瓶座", "Pisces": "双鱼座",
        }

        # ── 核心三要素：太阳、月亮、上升 ──
        sun = chart.getObject(const.SUN)
        moon = chart.getObject(const.MOON)
        asc = chart.getAngle(const.ASC)
        mc = chart.getAngle(const.MC)
        sun_h = chart.houses.getObjectHouse(sun)
        moon_h = chart.houses.getObjectHouse(moon)

        lines = ["【本命盘】"]
        lines.append("")
        lines.append("▶ 核心三元")
        lines.append(f"  太阳 {SIGN_ZH.get(sun.sign, sun.sign)} {sun.signlon:.1f}° · 第{sun_h.num()}宫")
        lines.append(f"  月亮 {SIGN_ZH.get(moon.sign, moon.sign)} {moon.signlon:.1f}° · 第{moon_h.num()}宫")
        lines.append(f"  上升 {SIGN_ZH.get(asc.sign, asc.sign)} {asc.signlon:.1f}°")

        # ── 其他行星 ──
        planet_defs = [
            (const.MERCURY, "水星"), (const.VENUS, "金星"), (const.MARS, "火星"),
            (const.JUPITER, "木星"), (const.SATURN, "土星"),
        ]
        lines.append("")
        lines.append("▶ 行星分布")
        for planet_id, name in planet_defs:
            obj = chart.getObject(planet_id)
            if obj:
                house = chart.houses.getObjectHouse(obj)
                retro = " 逆行" if obj.isRetrograde() else ""
                lines.append(
                    f"  {name} {SIGN_ZH.get(obj.sign, obj.sign)} {obj.signlon:.1f}° · 第{house.num()}宫{retro}"
                )

        # ── 南北交点 ──
        north = chart.getObject(const.NORTH_NODE)
        if north:
            north_h = chart.houses.getObjectHouse(north)
            lines.append("")
            lines.append("▶ 月交点")
            lines.append(
                f"  北交 {SIGN_ZH.get(north.sign, north.sign)} {north.signlon:.1f}° · 第{north_h.num()}宫 逆行"
            )
            # 南交 = 北交对宫
            south_sign_lon = (north.signlon + 180) % 360 if north.signlon > 0 else 0
            south_h_num = (north_h.num() + 6) % 12 or 12
            lines.append(
                f"  南交 对宫 · 第{south_h_num}宫 逆行"
            )

        # ── 中天 MC ──
        lines.append("")
        lines.append("▶ 重要角度")
        lines.append(f"  中天MC {SIGN_ZH.get(mc.sign, mc.sign)} {mc.signlon:.1f}°")

        # ── 元素与模式 ──
        elements = {"火象": 0, "土象": 0, "风象": 0, "水象": 0}
        modes = {"开创": 0, "固定": 0, "变动": 0}
        fire = ["Aries", "Leo", "Sagittarius"]
        earth = ["Taurus", "Virgo", "Capricorn"]
        air = ["Gemini", "Libra", "Aquarius"]
        water = ["Cancer", "Scorpio", "Pisces"]
        cardinal = ["Aries", "Cancer", "Libra", "Capricorn"]
        fixed = ["Taurus", "Leo", "Scorpio", "Aquarius"]
        mutable = ["Gemini", "Virgo", "Sagittarius", "Pisces"]

        for planet_id in [const.SUN, const.MOON, const.MERCURY, const.VENUS,
                          const.MARS, const.JUPITER, const.SATURN]:
            obj = chart.getObject(planet_id)
            if obj:
                s = obj.sign
                if s in fire: elements["火象"] += 1
                elif s in earth: elements["土象"] += 1
                elif s in air: elements["风象"] += 1
                elif s in water: elements["水象"] += 1
                if s in cardinal: modes["开创"] += 1
                elif s in fixed: modes["固定"] += 1
                elif s in mutable: modes["变动"] += 1

        lines.append("")
        lines.append("▶ 元素倾向")
        strong_e = max(elements, key=elements.get)
        weak_e = min(elements, key=elements.get)
        lines.append(f"  强势{strong_e}({elements[strong_e]}颗) 缺弱{weak_e}({elements[weak_e]}颗)")
        lines.append(f"  {', '.join(f'{k}{v}' for k,v in elements.items())}")

        lines.append("")
        lines.append("▶ 模式倾向")
        strong_m = max(modes, key=modes.get)
        lines.append(f"  主导{strong_m}({modes[strong_m]}颗)")
        lines.append(f"  {', '.join(f'{k}{v}' for k,v in modes.items())}")

        # ── 关键相位 ──
        ASPECT_DEFS = [
            (0, "合相", 10), (60, "六合", 6), (90, "刑克", 8),
            (120, "三合", 8), (180, "对冲", 10),
        ]
        planets_for_asp = [
            (chart.getObject(const.SUN), "太阳"),
            (chart.getObject(const.MOON), "月亮"),
            (chart.getObject(const.MERCURY), "水星"),
            (chart.getObject(const.VENUS), "金星"),
            (chart.getObject(const.MARS), "火星"),
            (chart.getObject(const.JUPITER), "木星"),
            (chart.getObject(const.SATURN), "土星"),
        ]
        aspects_found = []
        for i in range(len(planets_for_asp)):
            for j in range(i + 1, len(planets_for_asp)):
                p1, n1 = planets_for_asp[i]
                p2, n2 = planets_for_asp[j]
                diff = abs(p1.lon - p2.lon)
                if diff > 180:
                    diff = 360 - diff
                for angle, asp_name, max_orb in ASPECT_DEFS:
                    orb = abs(diff - angle)
                    if orb < max_orb:
                        aspects_found.append((n1, asp_name, n2, orb))
                        break

        lines.append("")
        lines.append("▶ 关键相位")
        if aspects_found:
            for n1, asp_name, n2, orb in sorted(aspects_found, key=lambda x: x[3]):
                orb_str = f"偏差{orb:.1f}°" if orb > 0 else "精准"
                lines.append(f"  {n1} {asp_name} {n2} ({orb_str})")
        else:
            lines.append("  无主要相位")

        return "\n".join(lines)
    except Exception as exc:
        logger.warning("星盘文本格式化失败: %s", exc)
        return "星盘格式化异常"


def _format_chart_context(chart) -> str:
    """将 Chart 对象格式化为精简上下文摘要，供 LLM prompt 使用。"""
    try:
        from flatlib import const

        SIGN_ZH = {
            "Aries": "白羊", "Taurus": "金牛", "Gemini": "双子",
            "Cancer": "巨蟹", "Leo": "狮子", "Virgo": "处女",
            "Libra": "天秤", "Scorpio": "天蝎", "Sagittarius": "射手",
            "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "双鱼",
        }

        sun = chart.getObject(const.SUN)
        moon = chart.getObject(const.MOON)
        asc = chart.getAngle(const.ASC)
        mc = chart.getAngle(const.MC)
        sun_h = chart.houses.getObjectHouse(sun)
        moon_h = chart.houses.getObjectHouse(moon)

        # 精简版：核心三元 + MC + 关键相位摘要
        parts = [
            f"太阳{SIGN_ZH.get(sun.sign, sun.sign)}{sun.signlon:.0f}°第{sun_h.num()}宫",
            f"月亮{SIGN_ZH.get(moon.sign, moon.sign)}{moon.signlon:.0f}°第{moon_h.num()}宫",
            f"上升{SIGN_ZH.get(asc.sign, asc.sign)}",
            f"MC{SIGN_ZH.get(mc.sign, mc.sign)}",
        ]

        # 加入逆行信息
        retro_planets = []
        for pid, pname in [(const.MERCURY,"水星"),(const.VENUS,"金星"),(const.MARS,"火星"),
                           (const.JUPITER,"木星"),(const.SATURN,"土星")]:
            obj = chart.getObject(pid)
            if obj and obj.isRetrograde():
                retro_planets.append(f"{pname}逆行")
        if retro_planets:
            parts.append("逆行: " + ",".join(retro_planets))

        # 关键相位摘要
        ASPECT_DEFS = [(0,"合",10),(60,"六合",6),(90,"刑",8),(120,"三合",8),(180,"冲",10)]
        planets_for_asp = [
            (chart.getObject(const.SUN), "日"), (chart.getObject(const.MOON), "月"),
            (chart.getObject(const.MERCURY), "水"), (chart.getObject(const.VENUS), "金"),
            (chart.getObject(const.MARS), "火"), (chart.getObject(const.JUPITER), "木"),
            (chart.getObject(const.SATURN), "土"),
        ]
        asp_strs = []
        for i in range(len(planets_for_asp)):
            for j in range(i + 1, len(planets_for_asp)):
                p1, n1 = planets_for_asp[i]
                p2, n2 = planets_for_asp[j]
                diff = abs(p1.lon - p2.lon)
                if diff > 180: diff = 360 - diff
                for angle, asp_name, max_orb in ASPECT_DEFS:
                    if abs(diff - angle) < max_orb:
                        asp_strs.append(f"{n1}{asp_name}{n2}")
                        break
        if asp_strs:
            parts.append("相位: " + " ".join(asp_strs[:5]))

        return "；".join(parts) + "。"
    except Exception:
        return "星盘数据暂不可用。"


def _compute_ephemeris(chart) -> str:
    """
    计算近7天星历摘要（flatlib 本地实时计算）。

    包含：
    - 当前行星位置总览
    - 行星换座（入星座）事件
    - 逆行变化
    - 本命盘与行运行星的关键相位（推运相位）
    """
    from datetime import datetime, timedelta

    try:
        from flatlib import const
        from flatlib.chart import Chart as FlatChart
        from flatlib.datetime import Datetime as FlatDatetime
        from flatlib.geopos import GeoPos

        SIGN_ZH = {
            "Aries": "白羊", "Taurus": "金牛", "Gemini": "双子",
            "Cancer": "巨蟹", "Leo": "狮子", "Virgo": "处女",
            "Libra": "天秤", "Scorpio": "天蝎", "Sagittarius": "射手",
            "Capricorn": "摩羯", "Aquarius": "水瓶", "Pisces": "双鱼",
        }

        today = datetime.now()
        end_day = today + timedelta(days=7)
        lat, lon = chart.pos.lat, chart.pos.lon
        pos = GeoPos(lat, lon)

        lines = ["【本周星历】"]
        lines.append(f"日期：{today.strftime('%Y-%m-%d')} 至 {end_day.strftime('%Y-%m-%d')}")
        lines.append("")

        # ── 1. 当前行星位置 ──
        today_chart = FlatChart(FlatDatetime(today.strftime('%Y/%m/%d'), '12:00', '+08:00'), pos)
        lines.append("▶ 当前行星位置")
        planet_order = [
            (const.SUN, "太阳"), (const.MOON, "月亮"), (const.MERCURY, "水星"),
            (const.VENUS, "金星"), (const.MARS, "火星"), (const.JUPITER, "木星"),
            (const.SATURN, "土星"),
        ]
        for pid, name in planet_order:
            obj = today_chart.getObject(pid)
            retro = " 逆行" if obj.isRetrograde() else ""
            lines.append(
                f"  {name} {SIGN_ZH.get(obj.sign, obj.sign)} {obj.signlon:.1f}°{retro}"
            )

        # ── 2. 行星换座事件 ──
        lines.append("")
        lines.append("▶ 行星换座")
        prev_signs = {}
        events = []
        for day_offset in range(8):
            d = today + timedelta(days=day_offset)
            t_chart = FlatChart(FlatDatetime(d.strftime('%Y/%m/%d'), '12:00', '+08:00'), pos)
            for pid, name in planet_order:
                obj = t_chart.getObject(pid)
                key = name
                curr = obj.sign
                if key in prev_signs and prev_signs[key] != curr:
                    events.append(
                        f"  {d.strftime('%m/%d')} {name} 入{SIGN_ZH.get(curr, curr)}"
                        f"（从{SIGN_ZH.get(prev_signs[key], prev_signs[key])}）"
                    )
                prev_signs[key] = curr
        if events:
            lines.extend(events)
        else:
            lines.append("  本周无行星换座")

        # ── 3. 逆行变化 ──
        lines.append("")
        lines.append("▶ 逆行动态")
        retro_planets_now = []
        prev_retro = {}
        retro_events = []
        for day_offset in range(8):
            d = today + timedelta(days=day_offset)
            t_chart = FlatChart(FlatDatetime(d.strftime('%Y/%m/%d'), '12:00', '+08:00'), pos)
            for pid, name in [(const.MERCURY, "水星"), (const.VENUS, "金星"),
                              (const.MARS, "火星"), (const.JUPITER, "木星"),
                              (const.SATURN, "土星")]:
                obj = t_chart.getObject(pid)
                key = name
                curr = obj.isRetrograde()
                if day_offset == 0 and curr:
                    retro_planets_now.append(name)
                if key in prev_retro and prev_retro[key] != curr:
                    status = "开始逆行 ↩" if curr else "恢复顺行 →"
                    retro_events.append(f"  {d.strftime('%m/%d')} {name} {status}")
                prev_retro[key] = curr
        if retro_planets_now:
            lines.append(f"  当前逆行：{'、'.join(retro_planets_now)}")
        else:
            lines.append("  当前无行星逆行")
        if retro_events:
            lines.extend(retro_events)

        # ── 4. 推运相位（行运行星与本命盘的关键相位）──
        lines.append("")
        lines.append("▶ 推运相位（行运→本命）")
        ASPECT_DEFS = [
            (0, "合", 8), (60, "六合", 5), (90, "刑", 7),
            (120, "三合", 7), (180, "冲", 8),
        ]
        # 本命关键点
        natal_points = [
            (chart.getObject(const.SUN), "本命太阳"),
            (chart.getObject(const.MOON), "本命月亮"),
            (chart.getAngle(const.ASC), "本命上升"),
        ]
        transits = []
        for natal_obj, natal_name in natal_points:
            for pid, name in planet_order:
                t_obj = today_chart.getObject(pid)
                diff = abs(t_obj.lon - natal_obj.lon)
                if diff > 180:
                    diff = 360 - diff
                for angle, asp_name, max_orb in ASPECT_DEFS:
                    orb = abs(diff - angle)
                    if orb < max_orb:
                        transits.append(
                            f"  行运{name} {asp_name} {natal_name} (偏差{orb:.1f}°)"
                        )
                        break
        if transits:
            lines.extend(transits[:8])  # 最多8条
        else:
            lines.append("  本周无显著推运相位")

        return "\n".join(lines)
    except Exception as exc:
        logger.warning("星历计算失败: %s", exc)
        return "星历数据暂不可用。"


# ══════════════════════════════════════════════════════════
#  DAG 节点
# ══════════════════════════════════════════════════════════


async def astro_node(state: AgentState) -> dict:
    """
    占星数据计算节点（纯本地计算，不调用 LLM）。
    同时计算本命星盘和近7天星历，避免 Chart 对象跨节点序列化。

    输入: request.birth_time, request.birth_place
    输出: astro_analysis, astro_context, ephemeris_summary
    """
    req = state["request"]
    logger.info("[astro_node] 计算本命星盘和近7天星历...")

    result = _compute_natal_chart(req.birth_time, req.birth_place)
    ephemeris = _compute_ephemeris(result["raw"])

    logger.info("[astro_node] 星盘+星历计算完成")
    return {
        "astro_analysis": result["text"],
        "astro_context": result["context"],
        "ephemeris_summary": ephemeris,
    }


async def ephemeris_node(state: AgentState) -> dict:
    """
    星历节点（已在 astro_node 中一并计算，此节点为透传/占位）。

    输入: ephemeris_summary（已由 astro_node 计算）
    输出: ephemeris_summary
    """
    summary = state.get("ephemeris_summary", "")
    if not summary:
        # 兜底：如果 astro_node 未计算，尝试用出生信息重新计算
        req = state["request"]
        result = _compute_natal_chart(req.birth_time, req.birth_place)
        summary = _compute_ephemeris(result["raw"])
    logger.info("[ephemeris_node] 星历数据就绪")
    return {"ephemeris_summary": summary}


async def astro_insight_node(state: AgentState) -> dict:
    """
    占星素材提炼节点（LLM 调用，轻量）。

    输入: astro_analysis, ephemeris_summary, request.*, supplements
    输出: astro_focus
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
