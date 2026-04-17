# -*- coding: utf-8 -*-
"""
影子 AI — LangGraph DAG 构建 (graph.py)

【职责】
  构建主对话流水线的有向无环图 (DAG)。

【DAG 结构】

  prepare_node ──(条件路由)──┬── "clarify" ──→ clarify_node → END
                              │
                              └── "analyze" ──→ astro_node ──┬─→ ephemeris_node
                                                               │       │
                                                               │       ↓
                                                               │   astro_insight_node ──┐
                                                               │                        │
                                                               └─→ search_node ─────┐  │
                                                                                      ↓  ↓
                                                                               analyze_node
                                                                                    │
                                                                              combine_node
                                                                                    │
                                                                                   END
"""
from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from .models import AgentState
from .nodes import (
    analyze_node,
    astro_insight_node,
    astro_node,
    clarify_node,
    combine_node,
    ephemeris_node,
    prepare_node,
    search_node,
)


def _route_after_prepare(state: AgentState) -> str:
    """
    条件路由：判断走追问分支还是分析分支。

    追问逻辑：
      - 如果 request.supplements 为空 → 追问
      - 如果 request.supplements 有值且 clarification_round >= 1 → 分析（只追问1轮）
    
    clarification_round 由 prepare_node 更新。
    """
    req = state.get("request")
    has_supplements = bool(req and req.supplements and req.supplements.strip())
    round_num = state.get("clarification_round", 0)
    
    # 只进行1轮追问
    MAX_ROUNDS = 1
    
    if has_supplements and round_num >= MAX_ROUNDS:
        return "analyze"
    else:
        return "clarify"


def build_graph(checkpointer=None):
    """
    构建并编译主对话流水线 DAG。

    流程说明：
      第一轮（无 supplements）：
        prepare_node → clarify_node → END
        前端收到 phase=clarifying，展示追问，等待用户回答

      第二轮（有 supplements）：
        prepare_node → astro_node → [ephemeris_node, search_node（并行）]
        ephemeris_node → astro_insight_node
        [astro_insight_node, search_node] → analyze_node
        analyze_node → combine_node → END
        前端收到 phase=complete，展示最终分析

    Args:
        checkpointer: 状态检查器，默认 MemorySaver。

    Returns:
        编译后的 CompiledGraph
    """
    workflow = StateGraph(AgentState)

    # ── 注册全部节点 ──
    workflow.add_node("prepare_node", prepare_node)
    workflow.add_node("clarify_node", clarify_node)
    workflow.add_node("astro_node", astro_node)
    workflow.add_node("ephemeris_node", ephemeris_node)
    workflow.add_node("astro_insight_node", astro_insight_node)
    workflow.add_node("search_node", search_node)
    workflow.add_node("analyze_node", analyze_node)
    workflow.add_node("combine_node", combine_node)

    # ── 入口 ──
    workflow.set_entry_point("prepare_node")

    # ── 条件路由：追问 vs 分析 ──
    workflow.add_conditional_edges(
        "prepare_node",
        _route_after_prepare,
        {
            "clarify": "clarify_node",
            "analyze": "astro_node",
        },
    )

    # ── 追问分支 ──
    workflow.add_edge("clarify_node", END)

    # ── 分析分支 ──
    workflow.add_edge("astro_node", "ephemeris_node")
    workflow.add_edge("astro_node", "search_node")

    # 串行链：ephemeris → astro_insight
    workflow.add_edge("ephemeris_node", "astro_insight_node")

    # 合流：astro_insight + search → analyze
    workflow.add_edge("astro_insight_node", "analyze_node")
    workflow.add_edge("search_node", "analyze_node")

    # analyze → combine → END
    workflow.add_edge("analyze_node", "combine_node")
    workflow.add_edge("combine_node", END)

    # ── 编译 ──
    if checkpointer is None:
        checkpointer = MemorySaver()

    return workflow.compile(checkpointer=checkpointer)
