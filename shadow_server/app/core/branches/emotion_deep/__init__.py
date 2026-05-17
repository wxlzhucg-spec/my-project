# -*- coding: utf-8 -*-
"""
影子 AI — 情绪深度分析分支

【路由】router_node → EMOTION_DEEP → prepare_node → ... → combine_node → END
【流程】4个阶段：
  1. 追问阶段: prepare_node → clarify_node
  2. 占星阶段: astro_node → ephemeris_node → astro_insight_node
  3. 分析阶段: search_node → analyze_node
  4. 生成阶段: draft_node → refine_node → combine_node
"""
from .prepare_and_clarify import prepare_node, clarify_node
from .astro import astro_node, ephemeris_node, astro_insight_node
from .analyze import search_node, analyze_node
from .generate import draft_node, refine_node, combine_node

__all__ = [
    "prepare_node", "clarify_node",
    "astro_node", "ephemeris_node", "astro_insight_node",
    "search_node", "analyze_node",
    "draft_node", "refine_node", "combine_node",
]
