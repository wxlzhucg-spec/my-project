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
from .common.config import CORS_ORIGINS, DEBUG, ENABLE_TEST_ROUTES, HOST, PORT
from .core.graph import build_master_graph
from .common.middleware import RequestLoggingMiddleware
from .core.emotion import emotion_router
from .api.routers.chat import chat_router
from .api.routers.llm_models import llm_models_router
from .api.routers.fortune import fortune_router
from .api.routers.assessments import router as assessments_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(application: FastAPI):
    # 启动
    graph = build_master_graph()
    application.state.graph = graph

    # 预热 LLM 实例（避免首次请求冷启动）
    try:
        from .core.llm.llm import get_llm, get_reasoner_llm, get_light_llm
        get_light_llm()
        get_llm()
        get_reasoner_llm()
        logger.info("LLM 实例已预加载")
    except Exception as e:
        logger.warning("LLM 预加载失败，将在首次请求时创建: %s", e)

    level = logging.DEBUG if DEBUG else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logger.info("LangGraph 已编译（统一路由 + 三分支），等待请求… (test_routes=%s)", ENABLE_TEST_ROUTES)
    # 打印已注册路由
    if DEBUG or ENABLE_TEST_ROUTES:
        for r in application.routes:
            path = getattr(r, "path", None)
            if path is None:
                continue
            methods = getattr(r, "methods", None)
            logger.info("  路由 %s %s", ",".join(methods) if methods else "MOUNT", path)
    else:
        route_count = sum(1 for r in application.routes if getattr(r, "path", None))
        logger.info("已注册 %d 条路由", route_count)
    yield
    # 关闭
    logger.info("应用关闭")

def create_app() -> FastAPI:
    application = FastAPI(title="影子 AI", lifespan=lifespan)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    application.include_router(chat_router)
    application.include_router(llm_models_router)
    application.include_router(emotion_router)
    application.include_router(fortune_router, prefix="/api")
    application.include_router(assessments_router)

    if ENABLE_TEST_ROUTES:
        from .api.routers.pipeline_tests import register_pipeline_test_routes
        register_pipeline_test_routes(application)
        logger.info("测试路由已注册: /api/test/*")

    # 静态文件
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
    if os.path.isdir(static_dir):
        application.mount("/static", StaticFiles(directory=static_dir), name="static")

    @application.get("/health")
    async def health():
        return {"status": "ok", "version": "1.0.0", "service": "xinyu-shadow"}

    return application

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
