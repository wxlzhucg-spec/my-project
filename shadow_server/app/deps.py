# -*- coding: utf-8 -*-
"""
影子 AI — FastAPI 依赖注入 (deps.py)

【职责】
  提供路由级别的依赖项，如获取 LangGraph 实例。
"""
from typing import Any

from fastapi import HTTPException, Request


def get_chat_graph(request: Request) -> Any:
    graph = getattr(request.app.state, "graph", None)
    if graph is None:
        raise HTTPException(status_code=503, detail="主对话引擎未初始化，请稍后重试")
    return graph
