# -*- coding: utf-8 -*-
"""
每日个性化星座运势路由 — /api/fortune

输入：user_id 或 open_id（二选一）
输出：JSON { sign, status, ratings[], tabs[], cached }
缓存：同用户 + 同日期命中则直接返回，不重复消耗 LLM。
强制刷新：?force=1 跳过缓存重新生成。
"""

from __future__ import annotations

import json
import logging
import asyncio
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ...common.database import async_session_maker
from ...common.models import UserRequest
from ...core.llm.llm import get_llm
from .chat import _fill_user_from_db

logger = logging.getLogger(__name__)
router = APIRouter(tags=["每日运势"])

# ---------------------------------------------------------------------------
# 内部工具
# ---------------------------------------------------------------------------

def _safe_int(v: Any, fallback: int = 0) -> int:
    try:
        return int(v)
    except Exception:
        return fallback


def _sign_from_birthday(birth_date_str: Optional[str], birth_time_str: Optional[str] = None) -> str:
    """根据生日粗算太阳星座（仅用于兜底，优先用本命盘）。"""
    if not birth_date_str:
        return "神秘人"
    try:
        d = date.fromisoformat(str(birth_date_str).split("T")[0][:10])
    except Exception:
        return "神秘人"
    m, day = d.month, d.day
    if (m == 3 and day >= 21) or (m == 4 and day <= 19):   return "白羊座"
    if (m == 4 and day >= 20) or (m == 5 and day <= 20):   return "金牛座"
    if (m == 5 and day >= 21) or (m == 6 and day <= 20):   return "双子座"
    if (m == 6 and day >= 21) or (m == 7 and day <= 22):   return "巨蟹座"
    if (m == 7 and day >= 23) or (m == 8 and day <= 22):   return "狮子座"
    if (m == 8 and day >= 23) or (m == 9 and day <= 22):   return "处女座"
    if (m == 9 and day >= 23) or (m == 10 and day <= 22):  return "天秤座"
    if (m == 10 and day >= 23) or (m == 11 and day <= 21): return "天蝎座"
    if (m == 11 and day >= 22) or (m == 12 and day <= 21): return "射手座"
    if (m == 12 and day >= 22) or (m == 1 and day <= 19):  return "摩羯座"
    if (m == 1 and day >= 20) or (m == 2 and day <= 18):  return "水瓶座"
    return "双鱼座"


async def _query_existing_fortune(session: AsyncSession, user_id: int) -> Optional[Dict]:
    today = date.today().isoformat()
    stmt = text(
        "SELECT sign,status,ratings,tabs,created_at FROM daily_fortune "
        "WHERE user_id=:uid AND fortune_date=:today LIMIT 1"
    )
    row = (await session.execute(stmt, {"uid": user_id, "today": today})).fetchone()
    if not row:
        return None
    ratings = json.loads(row.ratings) if isinstance(row.ratings, str) else row.ratings
    tabs = json.loads(row.tabs) if isinstance(row.tabs, str) else row.tabs
    return {
        "sign": row.sign,
        "status": row.status,
        "ratings": ratings,
        "tabs": tabs,
        "cached": True,
    }


async def _save_fortune(session: AsyncSession, user_id: int, data: Dict):
    today = date.today().isoformat()
    upsert = text(
        "INSERT INTO daily_fortune (user_id,fortune_date,sign,status,ratings,tabs,created_at) "
        "VALUES (:uid,:today,:sign,:status,:ratings,:tabs,NOW()) "
        "ON DUPLICATE KEY UPDATE sign=VALUES(sign),status=VALUES(status),"
        "ratings=VALUES(ratings),tabs=VALUES(tabs),created_at=VALUES(created_at)"
    )
    await session.execute(upsert, {
        "uid": user_id,
        "today": today,
        "sign": data["sign"],
        "status": data["status"],
        "ratings": json.dumps(data["ratings"], ensure_ascii=False),
        "tabs": json.dumps(data["tabs"], ensure_ascii=False),
    })
    await session.commit()


async def _compute_natal_summary(birth_date: Optional[str], birth_time: Optional[str]) -> str:
    """调用星盘模块获取本命盘摘要文本。失败时返回空字符串，不影响主流程。"""
    try:
        from ...core.branches.emotion_deep.astro import natal_chart_to_text
        loop = asyncio.get_event_loop()
        summary = await loop.run_in_executor(
            None, lambda: natal_chart_to_text(birth_date=birth_date, birth_time=birth_time)
        )
        return summary or ""
    except Exception as e:
        logger.warning("[fortune] 本命盘计算跳过: %s", e)
        return ""


async def _compute_ephemeris_text(d: date) -> str:
    """调用星历模块获取当日行星星历文本。失败时返回空字符串。"""
    try:
        from ...core.branches.emotion_deep.astro import ephemeris_to_text
        loop = asyncio.get_event_loop()
        txt = await loop.run_in_executor(None, lambda: ephemeris_to_text(target_date=d))
        return txt or ""
    except Exception as e:
        logger.warning("[fortune] 星历计算跳过: %s", e)
        return ""


_FORTUNE_PROMPT = """你是一个温暖、有洞察力的占星师，擅长把星象翻译成朋友般的日常提醒。你的文字让人感觉被关心、被看见。

【用户信息】
星座：{sign}
MBTI：{mbti}

【本命盘核心】
{natal}

【今日星历 ({today})】
{ephemeris}

请为这位用户生成今日个性化运势，严格按以下 JSON 格式输出（不要输出其他文字）：

{{
  "status": "一句话状态（12字以内），温暖自然，像朋友对你说的第一句话，带一点小期待和关心",
  "ratings": [
    {{"label":"综合","val":N}},
    {{"label":"爱情","val":N}},
    {{"label":"工作","val":N}},
    {{"label":"财富","val":N}}
  ],
  "tabs": [
    {{"label":"综合运势","content":"120-160字。分三层写：①先用1-2句温暖的话接住今天的状态，让ta觉得被理解；②再写2-3句具体描述今天的节奏和关键点，像朋友在提醒你注意什么；③最后1-2句给一个温柔的方向感或小鼓励。用句号分隔短句，读起来有呼吸感"}},
    {{"label":"感情运势","content":"100-140字。分三层写：①先用1句共情的话打开，不管是单身还是有伴侣都能代入；②再写2-3句具体的场景或细节提示，温柔不鸡汤，可以点到某个具体时刻；③最后1句暖心的收尾。整体语气像闺蜜/兄弟在私下跟你聊感情"}},
    {{"label":"工作运势","content":"100-140字。分三层写：①先用1句点出今天工作上的整体感觉；②再写2-3句具体到一件事或一个心态调整，让人有抓手；③最后1句轻松的鼓励或小提示。不说教，像过来人给的小贴士"}},
    {{"label":"财富运势","content":"90-120字。分两层写：①先用1-2句点出今天的财运节奏，是适合保守还是可以小试；②再给1个实用小建议，具体到今天可以做什么（比如"中午前处理那笔转账"），最后1句让人安心的收尾"}}
  ]
}}

核心原则（非常重要）：
1. 温度第一！每段开头都要有情绪温度，不是冷冰冰的分析，而是"我懂你"的感觉
2. 短句为王！每句不超过30字，用句号分隔，读起来有节奏感
3. 有层次感！每段内容都分层次递进：先共情→再说具体→最后给方向，像一段完整的小故事
4. 零占星术语！不要出现"三合""刑""冲""拱""入座""逆行""推运"等词
5. 用生活化表达替代：能量好→状态在线；压力大→事情有点多；适合沟通→今天说话特别顺
6. val 为 1-5 整数，真实反映星象，不要全给4-5分
7. 像微信聊天语气："今天适合…""小心…""有个小提醒""不过别担心…"
8. 不要emoji，不要「」「」等装饰符号
9. 具体胜于抽象！说"下午三点那场会议你可以大胆发言"胜过"今天适合表达自己"
"""


def _parse_fortune_json(raw: str) -> Optional[Dict]:
    """从 LLM 返回中提取 JSON；容忍前后多余文字。"""
    s = raw.strip()
    # 尝试直接解析
    if s.startswith("{"):
        try:
            return json.loads(s)
        except Exception:
            pass
    # 尝试找第一个 { ... } 块
    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(s[start : end + 1])
        except Exception:
            pass
    return None


# ---------------------------------------------------------------------------
# 请求模型 & 入口
# ---------------------------------------------------------------------------

class FortuneResponse(BaseModel):
    sign: str
    status: str
    ratings: List[Dict[str, Any]]
    tabs: List[Dict[str, str]]
    cached: bool = False


@router.get("/fortune", response_model=FortuneResponse)
async def get_daily_fortune(
    user_id: Optional[int] = Query(None, description="用户数据库 ID"),
    open_id: Optional[str] = Query(None, description="微信 open_id"),
    force: int = Query(0, description="设为 1 时跳过缓存重新生成"),
):
    if not user_id and not open_id:
        raise HTTPException(status_code=400, detail="需提供 user_id 或 open_id")

    uid: Optional[int] = None

    # 1) 确定用户 ID + 填充资料
    req = UserRequest(user_id=user_id, open_id=open_id, question="每日运势")
    req = await _fill_user_from_db(req)
    uid = req.user_id
    if not uid:
        # _fill_user_from_db 没有查到用户时，uid 仍为 None
        if user_id:
            uid = user_id
        else:
            raise HTTPException(status_code=404, detail="未找到用户信息")

    sign = _sign_from_birthday(req.birth_time, None)
    mbti = str(req.mbti or "")

    # 2) 缓存命中（非强制刷新时直接返回）
    async with async_session_maker() as session:
        if not force:
            cached = await _query_existing_fortune(session, uid)
            if cached:
                return FortuneResponse(**cached)

    # 3) 计算本命盘 + 当日星历
    natal, eph = "", ""
    if req.birth_time:
        natal = await _compute_natal_summary(req.birth_time, None)
    eph = await _compute_ephemeris_text(date.today())

    # 5) LLM 生成
    prompt = _FORTUNE_PROMPT.format(
        sign=sign,
        mbti=mbti,
        natal=natal or "(暂无本命盘数据)",
        ephemeris=eph or "(今日星历暂不可用)",
        today=date.today().isoformat(),
    )

    llm = get_llm()
    raw_reply = ""

    # 流式读取完整回复
    async for chunk in llm.astream(prompt):
        token = getattr(chunk, "content", "")
        if isinstance(token, list):
            token = "".join(getattr(t, "text", str(t)) for t in token)
        raw_reply += str(token)

    data = _parse_fortune_json(raw_reply)
    if not data:
        raise HTTPException(status_code=502, detail="运势生成失败，LLM 返回格式异常")

    # 字段校验与兜底
    data.setdefault("sign", sign)
    data.setdefault("status", "今天慢慢来，一切刚刚好")
    data.setdefault("ratings", [
        {"label": "综合", "val": 3},
        {"label": "爱情", "val": 3},
        {"label": "工作", "val": 3},
        {"label": "财富", "val": 3},
    ])
    data.setdefault("tabs", [
        {"label": "综合运势", "content": "今天的节奏偏柔和，不用急着赶路。上午可能会有些小琐碎找上门，不过别烦，一件件来就好。下午状态会慢慢回来，适合做一些需要耐心的事。晚上给自己留一点独处的时间，你会觉得这一天其实挺充实的。"},
        {"label": "感情运势", "content": "不管身边有没有人，今天都值得好好照顾自己的感受。如果心里有话想对某个人说，白天比晚上更适合开口。单身的朋友不用刻意寻找什么，做让自己舒服的事，吸引力自然会来。"},
        {"label": "工作运势", "content": "今天工作上的节奏不快不慢，正好适合查漏补缺。之前搁置的小事可以顺手处理掉，清完之后心里会踏实很多。如果遇到拿不准的决定，不用今天一定给答案，放一放反而更清晰。"},
        {"label": "财富运势", "content": "今天花钱前多想一秒就够了，不需要太紧张。如果有固定的账单或转账，上午处理完会更安心。小额的消费可以随心，但大额的决定再等一天也不迟。"},
    ])

    # 4) 写入缓存
    try:
        async with async_session_maker() as session:
            await _save_fortune(session, uid, data)
    except Exception as e:
        logger.warning("[fortune] 缓存写入失败(不影响返回): %s", e)

    return FortuneResponse(sign=data["sign"], status=data["status"], ratings=data["ratings"], tabs=data["tabs"], cached=False)


# 兼容旧引用名
fortune_router = router
