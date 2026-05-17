# -*- coding: utf-8 -*-
"""
影子 AI — 塔罗/专项会话持久化模块 (tarot_persist.py)

【职责】
  将 TAROT/ZODIAC/EMOTION_LOG 专项会话的完整数据持久化到 tarot_sessions 表：
  - 用户ID、会话ID、分类
  - 抽牌数据（塔罗牌快照）
  - AI 解读结果
  - 对话消息记录
  - 用户画像快照
"""
from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import text

from ..common.database import async_session_maker

logger = logging.getLogger(__name__)


def _extract_messages_from_result(result: dict) -> list[dict]:
    """从 LangGraph 结果中提取对话消息列表。"""
    messages = result.get("messages", [])
    out = []
    for msg in messages:
        role = "ai"
        msg_type = getattr(msg, "type", None) or ""
        if msg_type == "human":
            role = "user"
        elif msg_type == "ai":
            role = "ai"
        content = getattr(msg, "content", "")
        if content:
            out.append({"role": role, "content": content})
    return out


def _extract_draw_id(request_body: Any) -> Optional[int]:
    """从前端请求或 result 中提取 tarot_draws 关联 ID。"""
    # 前端可在请求中传入 draw_id，关联到 tarot_draws 记录
    draw_id = getattr(request_body, "draw_id", None)
    if draw_id:
        return int(draw_id)
    return None


async def save_tarot_session(
    user_id: Optional[int],
    session_id: str,
    category: str,
    request_body: Any,
    result: dict,
    phase: str,
    reply: str,
) -> Optional[int]:
    """
    将专项会话数据保存到 tarot_sessions 表。

    返回插入的记录 ID，失败返回 None。
    """
    if not user_id:
        logger.warning("[save_tarot_session] 缺少 user_id，跳过持久化")
        return None

    logger.info(
        "[save_tarot_session] 开始持久化: user_id=%s session=%s category=%s phase=%s",
        user_id, session_id, category, phase,
    )

    # 提取对话消息
    chat_messages = _extract_messages_from_result(result)
    logger.debug("[save_tarot_session] 提取到 %d 条消息", len(chat_messages))

    # 提取塔罗牌数据
    cards_json = None
    tarot_cards = getattr(request_body, "tarot_cards", None)
    if tarot_cards:
        cards_json = json.dumps(tarot_cards, ensure_ascii=False)
        logger.debug("[save_tarot_session] tarot_cards: %s", tarot_cards)
    else:
        logger.debug("[save_tarot_session] 无 tarot_cards")

    # 提取咨询问题
    question = getattr(request_body, "question", "") or ""
    logger.debug("[save_tarot_session] question: %s", question[:100])

    # 提取主题标签
    theme_tag_id = getattr(request_body, "theme_tag_id", None)
    theme_tag_label = getattr(request_body, "theme_tag_label", None)
    if theme_tag_id or theme_tag_label:
        logger.debug("[save_tarot_session] theme: id=%s label=%s", theme_tag_id, theme_tag_label)

    # 提取 draw_id 关联
    draw_id = _extract_draw_id(request_body)
    if draw_id:
        logger.debug("[save_tarot_session] draw_id: %s", draw_id)

    # 用户画像快照
    user_snapshot = None
    user_info = result.get("user_info")
    if user_info:
        safe_info = {k: v for k, v in user_info.items() if k not in ("password_hash",)}
        user_snapshot = json.dumps(safe_info, ensure_ascii=False, default=str)
        logger.debug("[save_tarot_session] user_snapshot 长度: %d", len(user_snapshot) if user_snapshot else 0)

    # 消息数
    message_count = len(chat_messages)

    try:
        async with async_session_maker() as session:
            db_result = await session.execute(
                text("""
                    INSERT INTO tarot_sessions
                        (user_id, draw_id, session_id, category,
                         cards_json, question, theme_tag_id, theme_tag_label,
                         ai_reply, phase, chat_messages, user_snapshot,
                         message_count)
                    VALUES
                        (:user_id, :draw_id, :session_id, :category,
                         :cards_json, :question, :theme_tag_id, :theme_tag_label,
                         :ai_reply, :phase, :chat_messages, :user_snapshot,
                         :message_count)
                """),
                {
                    "user_id": user_id,
                    "draw_id": draw_id,
                    "session_id": session_id,
                    "category": category,
                    "cards_json": cards_json,
                    "question": question[:512] if question else "",
                    "theme_tag_id": theme_tag_id,
                    "theme_tag_label": theme_tag_label,
                    "ai_reply": reply,
                    "phase": phase,
                    "chat_messages": json.dumps(chat_messages, ensure_ascii=False) if chat_messages else None,
                    "user_snapshot": user_snapshot,
                    "message_count": message_count
                },
            )
            await session.commit()
            # 获取插入的自增ID
            inserted_id = db_result.inserted_primary_key[0] if db_result.inserted_primary_key else None
            logger.info(
                "[save_tarot_session] 保存成功: id=%s user_id=%s session=%s category=%s",
                inserted_id, user_id, session_id, category,
            )
            return inserted_id
    except Exception as e:
        logger.error("[save_tarot_session] 保存失败: %s", e)
        return None


async def update_tarot_session_messages(
    session_id: str,
    messages: list[dict],
    reply: str,
    phase: str,
) -> bool:
    """
    更新已有的 tarot_session 记录（追加后续对话消息）。

    用于多轮对话时更新聊天记录。
    """
    try:
        async with async_session_maker() as session:
            await session.execute(
                text("""
                    UPDATE tarot_sessions
                    SET chat_messages = :chat_messages,
                        ai_reply = :ai_reply,
                        phase = :phase,
                        message_count = :message_count
                    WHERE session_id = :session_id
                """),
                {
                    "chat_messages": json.dumps(messages, ensure_ascii=False),
                    "ai_reply": reply,
                    "phase": phase,
                    "message_count": len(messages),
                    "session_id": session_id,
                },
            )
            await session.commit()
            logger.info("[update_tarot_session_messages] 更新成功: session=%s", session_id)
            return True
    except Exception as e:
        logger.error("[update_tarot_session_messages] 更新失败: %s", e)
        return False
