#!/bin/bash
# 影子 AI — 一键部署脚本
# 用法: 复制此脚本到服务器，然后执行 bash deploy.sh

set -e

SERVER_IP="43.143.169.226"
PROJECT_DIR="/opt/xinyu/shadow_server"
LOG_FILE="/var/log/shadow.log"
MYSQL_DB="xintujie"
MYSQL_USER="root"
MYSQL_PASS="010824Wy?"

echo "=== 影子 AI 部署脚本 ==="
echo ""

# 1. 进入项目目录
echo "[1/7] 进入项目目录..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo "错误: 项目目录不存在: $PROJECT_DIR"
    echo "请修改脚本中的 PROJECT_DIR 变量为实际路径"
    exit 1
fi
cd "$PROJECT_DIR"

# 2. 拉取最新代码
echo "[2/7] 拉取最新代码..."
if [ -d ".git" ]; then
    git pull origin main
else
    echo "警告: 不是 git 仓库，跳过 git pull"
fi

# 3. 安装依赖
echo "[3/7] 安装 Python 依赖..."
pip3 install -r requirements.txt -q

# 4. 创建数据库表
echo "[4/7] 创建 assessment_results 表..."
if command -v mysql &> /dev/null; then
    mysql -u "$MYSQL_USER" -p"$MYSQL_PASS" "$MYSQL_DB" < sql/create_assessment_results.sql 2>/dev/null || echo "  表可能已存在，跳过"
else
    echo "  警告: 未找到 mysql 命令，请手动执行 sql/create_assessment_results.sql"
fi

# 5. 停止旧服务
echo "[5/7] 停止旧服务..."
OLD_PID=$(pgrep -f "app.main" || true)
if [ -n "$OLD_PID" ]; then
    echo "  杀掉旧进程: $OLD_PID"
    kill "$OLD_PID" 2>/dev/null || true
    sleep 2
else
    echo "  没有找到运行中的旧进程"
fi

# 6. 启动新服务
echo "[6/7] 启动 Shadow 服务（绑定 80 端口）..."
nohup python3 -m app.main > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "  新进程 PID: $NEW_PID"
sleep 3

# 7. 验证
echo "[7/7] 验证服务..."
echo "  测试 /health..."
curl -s "http://$SERVER_IP/health" | head -c 200 || echo "  失败"

echo ""
echo "  测试 /api/assessments/submit..."
curl -s "http://$SERVER_IP/api/assessments/submit" \
    -X POST -H "Content-Type: application/json" \
    -d '{"user_id":1,"test_type":"holland","summary":"test","result_json":{}}' | head -c 200 || echo "  失败"

echo ""
echo "  测试 /api/fortune..."
curl -s "http://$SERVER_IP/api/fortune?user_id=1" | head -c 200 || echo "  失败"

echo ""
echo "=== 部署完成 ==="
echo "日志: tail -f $LOG_FILE"
echo ""
