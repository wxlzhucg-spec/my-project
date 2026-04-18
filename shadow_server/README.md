# 影子 AI (Shadow AI)

> 详细文档请参阅项目根目录 [README.md](../README.md)

## 快速开始

```bash
cp .env.example .env   # 编辑填入 DEEPSEEK_API_KEY 等
pip install -r requirements.txt
SHADOW_DEBUG=true uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## API 测试

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 主对话（传 open_id 自动补全用户信息）
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "open_id": "test_open_id_001",
    "emotion_keyword": "焦虑",
    "question": "工作压力太大"
  }'
```
