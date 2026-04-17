# 影子 AI (Shadow AI) — 情感陪伴后端

> 基于星盘 + LLM 的情感陪伴 AI，提供深度情感分析和个性化建议。

## 项目结构

```
shadow_server/
├── README.md               ← 本文件
├── .gitignore              ← Git 忽略规则
├── .env.example            ← 环境变量模板
├── .env                    ← 实际环境变量（不提交到 Git）
├── requirements.txt        ← Python 依赖
├── app/                    ← 核心代码包
│   ├── __init__.py         ← 包入口
│   ├── main.py             ← FastAPI 应用入口 + 路由
│   ├── config.py           ← 配置管理
│   ├── models.py           ← 数据模型
│   ├── llm.py              ← LLM 工厂（DeepSeek 单例）
│   ├── astro_engine.py     ← 占星计算引擎
│   ├── nodes.py            ← 主对话流水线节点
│   ├── prompts.py          ← Prompt 模板
│   ├── graph.py            ← LangGraph DAG
│   └── emotion_api.py      ← 情绪分析独立 API
└── static/                 ← 静态资源
    └── test_panel.html     ← 前端测试面板
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY
```

### 3. 启动服务

```bash
# 开发模式（带调试路由）
SHADOW_DEBUG=true uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 测试

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 主对话 API
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "birth_time": "1995-06-15 14:30",
    "birth_place": "甘肃省天水市武山县",
    "mbti": "INFP",
    "blood_type": "A",
    "emotion_keyword": "焦虑",
    "question": "工作压力太大"
  }'

# 情绪分析 API
curl -X POST http://127.0.0.1:8000/api/emotion \
  -H "Content-Type: application/json" \
  -d '{
    "text": "最近总觉得自己做什么都不对",
    "context": "工作中被领导批评了",
    "mbti": "INFP"
  }'
```

## API 端点

| 方法 | 路径 | 说明 | LLM 调用 |
|------|------|------|-----------|
| POST | `/api/chat` | 完整情感陪伴对话 | 4次 |
| POST | `/api/emotion` | 完整情绪分析 | 3次 |
| POST | `/api/emotion/detect` | 仅情绪识别 | 1次 |
| GET | `/health` | 健康检查 | 0次 |
| POST | `/api/test/node` | 单节点测试 | 0-1次 |
| POST | `/api/test/prompt` | Prompt 预览 | 0次 |

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPSEEK_API_KEY` | (空) | DeepSeek API 密钥，**必填** |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/v1` | API 地址 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 模型名称 |
| `SHADOW_HOST` | `127.0.0.1` | 监听地址 |
| `SHADOW_PORT` | `8000` | 监听端口 |
| `SHADOW_DEBUG` | `false` | 调试模式 |
| `SHADOW_CHAT_TIMEOUT_SECONDS` | `180` | 超时秒数 |

## 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **LLM**: DeepSeek (via langchain-openai)
- **流水线**: LangGraph (有向无环图)
- **占星**: flatlib + geopy (Nominatim)
- **数据校验**: Pydantic v2
