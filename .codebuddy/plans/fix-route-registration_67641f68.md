---
name: fix-route-registration
overview: 修复 main.py 中缺失的 emotion_router 注册，并添加完整的路由健康检查测试方案
todos:
  - id: fix-emotion-router
    content: 在 main.py 中 import 并 include emotion_router
    status: completed
  - id: add-route-logging
    content: 在 lifespan 启动阶段添加已注册路由的日志输出
    status: completed
    dependencies:
      - fix-emotion-router
---

## 产品概述

测试并修复 shadow_server/app/main.py 中的路由注册问题，确保所有已定义的路由端点均正确可访问。

## 核心功能

- 修复 `emotion_router` 未在 main.py 中注册的 bug（POST /api/emotion 和 POST /api/emotion/detect 当前不可访问）
- 添加启动时路由注册日志，方便后续验证所有路由是否正确挂载

## 技术栈

- Python + FastAPI（现有项目栈）
- LangGraph + LangChain（现有依赖）

## 实现方案

在 main.py 的 `create_app()` 中补充 import 并注册 `emotion_router`，同时在 lifespan 启动阶段打印所有已注册路由，便于一眼验证。

## 修改文件

```
shadow_server/app/
├── main.py  # [MODIFY] import emotion_router 并 include_router；启动时打印路由列表
```

## 实现细节

1. **修复 emotion_router 注册**：在 main.py 顶部 import `emotion_router`，在 `create_app()` 中调用 `application.include_router(emotion_router)`
2. **启动路由日志**：在 lifespan 的 yield 之前，遍历 `application.routes` 打印每个路由的 path 和 methods，方便启动时一眼确认

## 注意事项

- emotion_router 的 prefix 已在 emotion_api.py 中定义为 `/api/emotion`，无需在 include_router 时重复指定
- 路由日志只需在 DEBUG 或 ENABLE_TEST_ROUTES 模式下打印完整列表，生产环境仅打印路由数量即可