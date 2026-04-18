# 心途 (Xinyu) — 情感陪伴 App

> 基于星盘 + LLM 的情感陪伴 AI，提供深度情感分析和个性化建议。

## 项目架构

```
xinyu_v1/
├── xinyu/                    ← 微信小程序前端 (uni-app / Vue 2)
│   ├── pages/                ← 页面组件
│   ├── server/               ← Flask API (用户/情绪/塔罗)
│   │   ├── flask_api.py      ← Flask 主文件
│   │   └── *.sql             ← 数据库迁移脚本
│   └── utils/                ← 工具函数
│
├── shadow_server/            ← 影子 AI 后端 (FastAPI + LangGraph)
│   ├── app/
│   │   ├── main.py           ← FastAPI 入口
│   │   ├── config.py         ← 配置（从 .env 读取）
│   │   ├── models.py         ← Pydantic 模型
│   │   ├── database.py       ← SQLAlchemy 异步数据库
│   │   ├── nodes.py          ← LangGraph 节点
│   │   ├── graph.py          ← LangGraph DAG
│   │   ├── llm.py            ← DeepSeek LLM 单例
│   │   ├── prompts.py        ← Prompt 模板
│   │   ├── geocode.py        ← 地理编码
│   │   └── routers/
│   │       └── chat.py       ← /api/chat 路由
│   ├── deploy/
│   │   ├── deploy.sh         ← 一键部署脚本
│   │   ├── nginx_xinyu.conf  ← Nginx 配置
│   │   ├── xinyu-flask.service   ← Flask systemd
│   │   ├── xinyu-shadow.service  ← Shadow systemd
│   │   └── .env.production   ← 生产环境变量
│   └── .env.example          ← 环境变量模板
│
└── .github/workflows/
    └── deploy.yml            ← GitHub Actions 自动部署
```

## 服务器架构

```
客户端 (微信小程序)
    ↓ HTTPS
Nginx (80)
    ├── /user/*, /emotion/*, /tarot/*  → Flask API (127.0.0.1:5001)
    ├── /api/*, /health, /static/*     → Shadow AI (127.0.0.1:8000)
    └── /                              → 状态 JSON
    ↓
MySQL (xintujie 库)
    ├── users            ← 用户信息 (含 open_id, blood_type)
    ├── emotion_records  ← 情绪记录
    └── tarot_draws      ← 塔罗抽牌
```

## 本地 → 服务器更新流程

### 方式一：自动部署（推荐）

```bash
# 1. 本地修改代码后，提交并推送
git add .
git commit -m "描述你的改动"
git push origin main

# 2. GitHub Actions 自动触发：
#    SSH → cd /opt/xinyu → git pull → deploy.sh update
#    约 30 秒后生效
```

### 方式二：手动部署

```bash
# SSH 登录服务器
ssh root@43.143.169.226

# 拉取最新代码 + 重启服务
cd /opt/xinyu
bash shadow_server/deploy/deploy.sh update

# 或仅重启
bash shadow_server/deploy/deploy.sh restart

# 查看状态
bash shadow_server/deploy/deploy.sh status
```

### 方式三：手动逐步操作

```bash
ssh root@43.143.169.226
cd /opt/xinyu
git stash --include-untracked
git pull origin main
cp shadow_server/deploy/.env.production shadow_server/.env
systemctl restart xinyu-flask
systemctl restart xinyu-shadow
```

## 本地开发

### Shadow AI 后端

```bash
cd shadow_server
pip install -r requirements.txt
cp .env.example .env   # 编辑填入 DEEPSEEK_API_KEY 等
SHADOW_DEBUG=true uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Flask API

```bash
cd xinyu/server
pip install flask flask-cors pymysql
export MYSQL_HOST=127.0.0.1
export MYSQL_DATABASE=xintujie
python flask_api.py
```

## API 端点

### Flask API (端口 5001)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/user/register` | 用户注册 |
| POST | `/user/login` | 用户登录 |
| GET  | `/user` | 查询用户 (id/open_id/phone) |
| PUT  | `/user/profile` | 更新用户资料 |
| POST | `/user/bind_wx` | 绑定微信 |
| GET/POST/DELETE | `/emotion` | 情绪记录 CRUD |
| POST/GET | `/tarot/draw` | 塔罗抽牌 |

### Shadow AI (端口 8000)

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 情感陪伴对话（支持 open_id 自动补全） |
| GET  | `/health` | 健康检查 |

## 数据库配置

- 主机: 43.143.169.226:3306
- 库名: **xintujie**（不是 xinyu）
- users 表关键字段: open_id, phone, birth_date, birth_time, birth_province, birth_city, birth_district, mbti, blood_type

## 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DEEPSEEK_API_KEY` | (空) | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/v1` | API 地址 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | 模型名称 |
| `MYSQL_HOST` | `43.143.169.226` | MySQL 主机 |
| `MYSQL_DATABASE` | `xintujie` | 数据库名 |
| `SHADOW_DEBUG` | `false` | 调试模式 |
| `SHADOW_PORT` | `8000` | Shadow 端口 |

## 技术栈

- **前端**: uni-app + Vue 2 (微信小程序)
- **Flask API**: Flask + PyMySQL
- **Shadow AI**: FastAPI + Uvicorn + LangGraph + DeepSeek
- **数据库**: MySQL 8
- **部署**: Nginx + systemd + GitHub Actions
