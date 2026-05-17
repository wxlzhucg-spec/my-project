# -*- coding: utf-8 -*-
"""
影子 AI — LangGraph DAG 组装 (graph.py)

【职责】将 router + branches 中的节点组装为可执行的 DAG。
【不包含】节点实现逻辑（在 branches/ 中），路由分发逻辑（在 router.py 中）。
"""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..common.config import SHADOW_SQLITE_PATH, SHADOW_USE_SQLITE_SAVER
from ..common.models import AgentState
from .router import route_after_prepare, route_after_refine, route_after_router, router_node
from .branches.general import generate_node
from .branches.specialist import specialist_node
from .branches.web_search import web_search_node
from .branches.emotion_deep import (
    analyze_node,
    astro_insight_node,
    astro_node,
    clarify_node,
    combine_node,
    draft_node,
    ephemeris_node,
    prepare_node,
    refine_node,
    search_node,
)

logger = logging.getLogger(__name__)


def _build_checkpointer():
    """按环境变量创建 LangGraph checkpointer。"""
    if not SHADOW_USE_SQLITE_SAVER:
        return MemorySaver()

    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
    except ImportError as exc:
        raise RuntimeError(
            "已启用 SHADOW_USE_SQLITE_SAVER，但缺少 langgraph-checkpoint-sqlite 依赖"
        ) from exc

    db_path = Path(SHADOW_SQLITE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    logger.info("SQLite checkpointer 已启用: %s", db_path)
    return SqliteSaver(conn)


def build_graph(checkpointer=None):
    """
    构建并编译旧版情绪深度分析 DAG，保留兼容入口。
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("prepare_node", prepare_node)
    workflow.add_node("clarify_node", clarify_node)
    workflow.add_node("astro_node", astro_node)
    workflow.add_node("ephemeris_node", ephemeris_node)
    workflow.add_node("astro_insight_node", astro_insight_node)
    workflow.add_node("search_node", search_node)
    workflow.add_node("analyze_node", analyze_node)
    workflow.add_node("combine_node", combine_node)

    workflow.set_entry_point("prepare_node")
    workflow.add_conditional_edges(
        "prepare_node",
        route_after_prepare,
        {"clarify": "clarify_node", "analyze": "astro_node"},
    )
    workflow.add_edge("clarify_node", END)
    workflow.add_edge("astro_node", "ephemeris_node")
    workflow.add_edge("astro_node", "search_node")
    workflow.add_edge("ephemeris_node", "astro_insight_node")
    workflow.add_edge("astro_insight_node", "analyze_node")
    workflow.add_edge("search_node", "analyze_node")
    workflow.add_edge("analyze_node", "combine_node")
    workflow.add_edge("combine_node", END)

    return workflow.compile(checkpointer=checkpointer or _build_checkpointer())


def build_master_graph(checkpointer=None):
    """
    构建统一路由 + 四条独立分支的 master graph。

    分支说明：
      specialist    → specialist_node → END
      web           → web_search_node → generate_node → END
      general       → generate_node → END
      emotion_deep  → prepare_node → clarify/astro → ... → combine_node → END
    """
    workflow = StateGraph(AgentState)

    # ── 注册所有节点 ──
    workflow.add_node("router_node", router_node)
    workflow.add_node("specialist_node", specialist_node)
    workflow.add_node("web_search_node", web_search_node)
    workflow.add_node("generate_node", generate_node)
    workflow.add_node("prepare_node", prepare_node)
    workflow.add_node("clarify_node", clarify_node)
    workflow.add_node("astro_node", astro_node)
    workflow.add_node("ephemeris_node", ephemeris_node)
    workflow.add_node("astro_insight_node", astro_insight_node)
    workflow.add_node("search_node", search_node)
    workflow.add_node("analyze_node", analyze_node)
    workflow.add_node("draft_node", draft_node)
    workflow.add_node("refine_node", refine_node)
    workflow.add_node("combine_node", combine_node)

    # ── 入口 → router ──
    workflow.set_entry_point("router_node")
    workflow.add_conditional_edges(
        "router_node",
        route_after_router,
        {
            "specialist": "specialist_node",
            "general": "generate_node",
            "web": "web_search_node",
            "emotion_deep": "prepare_node",
        },
    )

    # ── specialist 分支 ──
    workflow.add_edge("specialist_node", END)

    # ── web 分支 ──
    workflow.add_edge("web_search_node", "generate_node")
    workflow.add_edge("generate_node", END)

    # ── emotion_deep 分支 ──
    workflow.add_conditional_edges(
        "prepare_node",
        route_after_prepare,
        {"clarify": "clarify_node", "analyze": "astro_node"},
    )
    workflow.add_edge("clarify_node", END)
    workflow.add_edge("astro_node", "ephemeris_node")
    workflow.add_edge("astro_node", "search_node")
    workflow.add_edge("ephemeris_node", "astro_insight_node")
    workflow.add_edge("astro_insight_node", "analyze_node")
    workflow.add_edge("search_node", "analyze_node")
    workflow.add_edge("analyze_node", "draft_node")
    workflow.add_edge("draft_node", "refine_node")
    workflow.add_conditional_edges(
        "refine_node",
        route_after_refine,
        {"refine": "refine_node", "combine": "combine_node"},
    )
    workflow.add_edge("combine_node", END)

    return workflow.compile(checkpointer=checkpointer or _build_checkpointer())
