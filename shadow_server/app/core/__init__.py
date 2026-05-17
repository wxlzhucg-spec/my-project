# -*- coding: utf-8 -*-
"""
影子 AI — 核心业务逻辑 (core/)

模块说明：
  router.py    : 分类路由器（识别意图 + 分发到分支）
  graph.py     : LangGraph DAG 组装
  prompts.py   : Prompt 模板集合
  branches/    : 各路由分支的节点实现
    general.py       : 普通聊天
    specialist.py    : 专项分析（塔罗/星座/情绪记录）
    web_search.py    : 联网问答
    emotion_deep/    : 情绪深度分析（4阶段）
      prepare_and_clarify.py : 追问阶段
      astro.py               : 占星计算阶段
      analyze.py             : 分析阶段
      generate.py            : 生成阶段
  emotion/     : 独立情绪分析 API
  llm/         : LLM 实例管理
"""
from .graph import build_graph, build_master_graph

__all__ = ["build_graph", "build_master_graph"]
