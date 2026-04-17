# -*- coding: utf-8 -*-
"""
影子 AI — 后端应用包

【启动方式】
  cd shadow_server && uvicorn app.main:app --host 127.0.0.1 --port 8000

【对外 API】

  POST /api/chat           — 完整情感陪伴对话（星盘+LLM）
  POST /api/emotion        — 纯情绪分析（轻量级，不需出生信息）
  POST /api/emotion/detect — 仅情绪识别（最快）
  GET  /health             — 健康检查
"""
