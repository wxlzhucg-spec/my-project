# -*- coding: utf-8 -*-
"""
影子 AI — FastAPI 应用入口 (main.py)
"""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import CORS_ORIGINS, DEBUG, ENABLE_TEST_ROUTES, HOST, PORT
from .graph import build_graph
from .middleware import RequestLoggingMiddleware
from .routers.chat import chat_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(application: FastAPI):
    # 启动
    graph = build_graph()
    application.state.graph = graph
    level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger.info("LangGraph 已编译（主对话 + 情绪），等待请求… (test_routes=%s)", ENABLE_TEST_ROUTES)
    yield
    # 关闭
    logger.info("应用关闭")

def create_app() -> FastAPI:
    application = FastAPI(title="影子 AI", lifespan=lifespan)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    application.include_router(chat_router)

    if ENABLE_TEST_ROUTES:
        from .routers.pipeline_tests import register_pipeline_test_routes
        register_pipeline_test_routes(application)
        logger.info("测试路由已注册: /api/test/*")

    # 静态文件
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.isdir(static_dir):
        application.mount("/static", StaticFiles(directory=static_dir), name="static")

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    return application

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
