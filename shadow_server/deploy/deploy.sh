#!/bin/bash
# ============================================================
#  心语 (Xinyu) — 一键部署脚本
#  用法: bash deploy.sh [init|update|restart|status|logs]
#
#  架构：Nginx(80) → Flask(5001) + FastAPI Shadow(8000)
#  自动部署：git push → GitHub Actions → SSH → deploy.sh update
# ============================================================

set -e

APP_DIR="/opt/xinyu"
VENV_DIR="/opt/xinyu/venv"
REPO_URL="https://github.com/wxlzhucg-spec/my-project.git"
BRANCH="main"
FLASK_SERVICE="xinyu-flask"
SHADOW_SERVICE="xinyu-shadow"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ---- 首次部署 ----
do_init() {
    log_info "===== 首次部署 ====="

    apt-get update -y
    apt-get install -y python3 python3-pip python3-venv nginx git

    if [ -d "$APP_DIR" ]; then
        log_warn "$APP_DIR 已存在，跳过克隆"
    else
        git clone -b $BRANCH $REPO_URL $APP_DIR
    fi

    if [ -d "$VENV_DIR" ]; then
        log_warn "虚拟环境已存在"
    else
        python3 -m venv $VENV_DIR
    fi

    $VENV_DIR/bin/pip install --upgrade pip
    $VENV_DIR/bin/pip install -r $APP_DIR/shadow_server/requirements.txt
    $VENV_DIR/bin/pip install flask flask-cors pymysql

    cp $APP_DIR/shadow_server/deploy/.env.production $APP_DIR/shadow_server/.env

    cp $APP_DIR/shadow_server/deploy/xinyu-shadow.service /etc/systemd/system/
    cp $APP_DIR/shadow_server/deploy/xinyu-flask.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $SHADOW_SERVICE $FLASK_SERVICE

    cp $APP_DIR/shadow_server/deploy/nginx_xinyu.conf /etc/nginx/sites-available/xinyu
    ln -sf /etc/nginx/sites-available/xinyu /etc/nginx/sites-enabled/xinyu
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx

    systemctl start $FLASK_SERVICE
    systemctl start $SHADOW_SERVICE

    log_info "===== 部署完成 ====="
    do_status
}

# ---- 更新部署（日常用 / CI 自动触发）----
do_update() {
    log_info "===== 更新部署 ====="

    cd $APP_DIR

    # 安装 git（首次 init 可能未执行到）
    which git >/dev/null 2>&1 || apt-get install -y git

    log_info "拉取最新代码..."
    git fetch origin $BRANCH
    git reset --hard origin/$BRANCH

    log_info "更新依赖..."
    $VENV_DIR/bin/pip install -q -r $APP_DIR/shadow_server/requirements.txt
    $VENV_DIR/bin/pip install -q flask flask-cors pymysql

    log_info "更新配置..."
    cp $APP_DIR/shadow_server/deploy/.env.production $APP_DIR/shadow_server/.env
    cp $APP_DIR/shadow_server/deploy/xinyu-shadow.service /etc/systemd/system/
    cp $APP_DIR/shadow_server/deploy/xinyu-flask.service /etc/systemd/system/
    systemctl daemon-reload

    log_info "重启服务..."
    systemctl restart $FLASK_SERVICE
    systemctl restart $SHADOW_SERVICE
    nginx -t 2>/dev/null && systemctl reload nginx 2>/dev/null || true

    log_info "===== 更新完成 ====="
    do_status
}

# ---- 仅重启 ----
do_restart() {
    systemctl restart $FLASK_SERVICE
    systemctl restart $SHADOW_SERVICE
    systemctl reload nginx 2>/dev/null || true
    do_status
}

# ---- 状态 ----
do_status() {
    echo ""
    echo "===== Flask API ====="
    systemctl status $FLASK_SERVICE --no-pager -l 2>/dev/null | head -5 || echo "未安装"
    echo ""
    echo "===== Shadow AI ====="
    systemctl status $SHADOW_SERVICE --no-pager -l 2>/dev/null | head -5 || echo "未安装"
    echo ""
    echo "===== 健康检查 ====="
    curl -s http://127.0.0.1/health 2>/dev/null && echo "" || echo "Nginx 未通"
}

case "${1:-}" in
    init)   do_init ;;
    update) do_update ;;
    restart) do_restart ;;
    status) do_status ;;
    *) echo "用法: bash deploy.sh [init|update|restart|status]" ;;
esac
