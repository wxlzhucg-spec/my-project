#!/bin/bash
# ============================================================
#  心语 (Xinyu) — 一键部署脚本
#  在服务器上运行: bash deploy.sh [init|update|restart|status|logs]
#
#  服务架构：
#    Nginx (80) → Flask API (5001)   用户/情绪/塔罗
#               → FastAPI Shadow (8000)  影子 AI 对话
# ============================================================

set -e

# ---- 配置 ----
APP_DIR="/opt/xinyu"
VENV_DIR="/opt/xinyu/venv"
REPO_URL="https://github.com/wxlzhucg-spec/my-project.git"
BRANCH="main"
FLASK_SERVICE="xinyu-flask"
SHADOW_SERVICE="xinyu-shadow"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---- 初始化（首次部署） ----
do_init() {
    log_info "===== 首次部署初始化 ====="

    # 1. 安装系统依赖
    log_info "安装系统依赖..."
    apt-get update -y
    apt-get install -y python3 python3-pip python3-venv nginx git

    # 2. 克隆代码
    if [ -d "$APP_DIR" ]; then
        log_warn "$APP_DIR 已存在，跳过克隆"
    else
        log_info "克隆代码仓库..."
        git clone -b $BRANCH $REPO_URL $APP_DIR
    fi

    # 3. 创建虚拟环境
    if [ -d "$VENV_DIR" ]; then
        log_warn "虚拟环境已存在，跳过"
    else
        log_info "创建 Python 虚拟环境..."
        python3 -m venv $VENV_DIR
    fi

    # 4. 安装 Python 依赖
    log_info "安装 Shadow AI 依赖..."
    $VENV_DIR/bin/pip install --upgrade pip
    $VENV_DIR/bin/pip install -r $APP_DIR/shadow_server/requirements.txt

    log_info "安装 Flask API 依赖..."
    $VENV_DIR/bin/pip install flask flask-cors pymysql

    # 5. 部署生产环境配置
    log_info "部署生产环境 .env..."
    cp $APP_DIR/shadow_server/deploy/.env.production $APP_DIR/shadow_server/.env

    # 6. 配置 systemd
    log_info "配置 systemd 服务..."
    cp $APP_DIR/shadow_server/deploy/xinyu-shadow.service /etc/systemd/system/
    cp $APP_DIR/shadow_server/deploy/xinyu-flask.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $SHADOW_SERVICE
    systemctl enable $FLASK_SERVICE

    # 7. 配置 Nginx
    log_info "配置 Nginx..."
    cp $APP_DIR/shadow_server/deploy/nginx_xinyu.conf /etc/nginx/sites-available/xinyu
    ln -sf /etc/nginx/sites-available/xinyu /etc/nginx/sites-enabled/xinyu
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx

    # 8. 启动服务
    log_info "启动后端服务..."
    systemctl start $FLASK_SERVICE
    systemctl start $SHADOW_SERVICE

    log_info "===== 部署完成！====="
    do_status
}

# ---- 更新代码并重启 ----
do_update() {
    log_info "===== 更新部署 ====="

    cd $APP_DIR

    # 拉取最新代码
    log_info "拉取最新代码..."
    git fetch origin $BRANCH
    git reset --hard origin/$BRANCH

    # 更新依赖
    log_info "更新 Python 依赖..."
    $VENV_DIR/bin/pip install -r $APP_DIR/shadow_server/requirements.txt --quiet
    $VENV_DIR/bin/pip install flask flask-cors pymysql --quiet

    # 更新 .env
    cp $APP_DIR/shadow_server/deploy/.env.production $APP_DIR/shadow_server/.env

    # 更新 systemd 配置
    cp $APP_DIR/shadow_server/deploy/xinyu-shadow.service /etc/systemd/system/
    cp $APP_DIR/shadow_server/deploy/xinyu-flask.service /etc/systemd/system/
    systemctl daemon-reload

    # 重启服务
    log_info "重启后端服务..."
    systemctl restart $FLASK_SERVICE
    systemctl restart $SHADOW_SERVICE

    # 重载 Nginx
    nginx -t && systemctl reload nginx

    log_info "===== 更新完成！====="
    do_status
}

# ---- 重启服务 ----
do_restart() {
    log_info "重启所有服务..."
    systemctl restart $FLASK_SERVICE
    systemctl restart $SHADOW_SERVICE
    systemctl reload nginx
    do_status
}

# ---- 查看状态 ----
do_status() {
    echo ""
    echo "===== Flask API ($FLASK_SERVICE) ====="
    systemctl status $FLASK_SERVICE --no-pager -l 2>/dev/null || echo "服务未安装"
    echo ""
    echo "===== Shadow AI ($SHADOW_SERVICE) ====="
    systemctl status $SHADOW_SERVICE --no-pager -l 2>/dev/null || echo "服务未安装"
    echo ""
    echo "===== Nginx ====="
    systemctl status nginx --no-pager -l 2>/dev/null || echo "Nginx 未安装"
    echo ""
    echo "===== API 健康检查 ====="
    curl -s http://127.0.0.1:8000/health 2>/dev/null && echo "" || echo "Shadow API 未响应"
    echo ""
    curl -s http://127.0.0.1:5001/user 2>/dev/null && echo "" || echo "Flask API 未响应"
    echo ""
    echo "===== 外部访问检查 ====="
    curl -s http://127.0.0.1/health 2>/dev/null && echo "" || echo "Nginx 代理未通"
    echo ""
}

# ---- 查看实时日志 ----
do_logs() {
    local svc="${2:-$SHADOW_SERVICE}"
    journalctl -u $svc -f
}

# ---- 主入口 ----
case "${1:-}" in
    init)   do_init ;;
    update) do_update ;;
    restart) do_restart ;;
    status) do_status ;;
    logs)   do_logs ;;
    *)
        echo "用法: bash deploy.sh [init|update|restart|status|logs]"
        echo ""
        echo "  init    - 首次部署（安装环境、克隆代码、启动服务）"
        echo "  update  - 更新代码并重启（日常发布用）"
        echo "  restart - 仅重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看实时日志（默认 Shadow，加 flask 看 Flask 日志）"
        ;;
esac
