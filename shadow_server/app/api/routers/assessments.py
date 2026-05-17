# -*- coding: utf-8 -*-
"""
影子 AI — 心理测评 API 路由 (assessments.py)
"""
from __future__ import annotations
import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text

from ...common.database import async_session_maker

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assessments", tags=["assessments"])

VALID_TYPES = {"mbti", "enneagram", "holland", "mh", "depression", "intimacy"}


# ── Request / Response ──────────────────────────────────────────────

class AssessmentSubmit(BaseModel):
    user_id: int = Field(..., description="用户 ID")
    test_type: str = Field(..., description="测评类型: mbti/enneagram/holland/mh/depression/intimacy")
    summary: str = Field("", description="主结果标签: 如 INFP / 安全型 / 心理健康良好")
    result_json: dict = Field(..., description="完整测评结果 JSON")
    answers_json: Optional[list] = Field(None, description="原始答案列表")
    score_json: Optional[dict] = Field(None, description="原始得分")
    question_count: int = Field(0, description="题目数量")
    duration_sec: Optional[int] = Field(None, description="作答耗时(秒)")


class AssessmentResponse(BaseModel):
    code: int = 0
    msg: str = "ok"
    data: Optional[dict] = None


class AssessmentListResponse(BaseModel):
    code: int = 0
    msg: str = "ok"
    data: Optional[list] = None


# ── POST /api/assessments/submit ─ 提交/更新测评结果 ─────────────

@router.post("/submit", response_model=AssessmentResponse)
async def submit_assessment(body: AssessmentSubmit):
    """提交或更新测评结果（同一用户同一类型仅保留最新一条）"""
    if body.test_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的测评类型: {body.test_type}")

    result_str = json.dumps(body.result_json, ensure_ascii=False)
    answers_str = json.dumps(body.answers_json, ensure_ascii=False) if body.answers_json else None
    score_str = json.dumps(body.score_json, ensure_ascii=False) if body.score_json else None

    async with async_session_maker() as session:
        # UPSERT: 存在则更新，不存在则插入
        sql = text("""
            INSERT INTO assessment_results
                (user_id, test_type, summary, result_json, answers_json, score_json, question_count, duration_sec)
            VALUES
                (:uid, :ttype, :summary, :rjson, :ajson, :sjson, :qcount, :dur)
            ON DUPLICATE KEY UPDATE
                summary       = VALUES(summary),
                result_json   = VALUES(result_json),
                answers_json  = VALUES(answers_json),
                score_json    = VALUES(score_json),
                question_count = VALUES(question_count),
                duration_sec  = VALUES(duration_sec)
        """)
        await session.execute(sql, {
            "uid": body.user_id,
            "ttype": body.test_type,
            "summary": body.summary,
            "rjson": result_str,
            "ajson": answers_str,
            "sjson": score_str,
            "qcount": body.question_count,
            "dur": body.duration_sec,
        })
        await session.commit()

    logger.info("[assessment] 用户 %d 提交 %s 测评: %s", body.user_id, body.test_type, body.summary)
    return AssessmentResponse(data={"test_type": body.test_type, "summary": body.summary})


# ── GET /api/assessments/query ─ 查询单类测评结果 ─────────────────

@router.get("/query", response_model=AssessmentResponse)
async def query_assessment(
    user_id: int = Query(..., description="用户 ID"),
    test_type: str = Query(..., description="测评类型"),
):
    """查询某用户某类测评的最新结果"""
    if test_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的测评类型: {test_type}")

    async with async_session_maker() as session:
        sql = text("""
            SELECT id, user_id, test_type, summary, result_json, answers_json,
                   score_json, question_count, duration_sec, created_at, updated_at
            FROM assessment_results
            WHERE user_id = :uid AND test_type = :ttype
        """)
        row = await session.execute(sql, {"uid": user_id, "ttype": test_type})
        r = row.mappings().first()

    if not r:
        return AssessmentResponse(code=1, msg="暂无数据", data=None)

    data = dict(r)
    # 解析 JSON 字符串
    for key in ("result_json", "answers_json", "score_json"):
        if data.get(key) and isinstance(data[key], str):
            try:
                data[key] = json.loads(data[key])
            except Exception:
                pass
    return AssessmentResponse(data=data)


# ── GET /api/assessments/list ─ 查询用户所有测评结果 ───────────────

@router.get("/list", response_model=AssessmentListResponse)
async def list_assessments(
    user_id: int = Query(..., description="用户 ID"),
):
    """查询某用户所有测评结果概要"""
    async with async_session_maker() as session:
        sql = text("""
            SELECT test_type, summary, question_count, created_at, updated_at
            FROM assessment_results
            WHERE user_id = :uid
            ORDER BY FIELD(test_type, 'mbti', 'enneagram', 'holland', 'intimacy', 'mh', 'depression')
        """)
        row = await session.execute(sql, {"uid": user_id})
        results = [dict(r) for r in row.mappings().all()]
    return AssessmentListResponse(data=results)
