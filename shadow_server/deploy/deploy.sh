#!/bin/bash
# ============================================================
#  心语 (Xinyu) — 一键部署脚本
#  用法: bash deploy.sh [init|update|restart|status]
#
#  架构：Nginx(80) → Flask(5001) + FastAPI Shadow(8000)
#  自动部署：git push → GitHub Actions → SSH → deploy.sh update
#  兼容：Ubuntu(apt) / CentOS/OpenCloudOS(yum)
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

# ---- 检测包管理器 ----
pkg_install() {
    if command -v apt-get &>/dev/null; then
        apt-get update -y && apt-get install -y "$@"
    elif command -v yum &>/dev/null; then
        yum install -y "$@"
    elif command -v dnf &>/dev/null; then
        dnf install -y "$@"
    else
        log_error "找不到包管理器 (apt/yum/dnf)"
        exit 1
    fi
}

# ---- 首次部署 ----
do_init() {
    log_info "===== 首次部署 ====="

    # 安装系统依赖
    log_info "安装系统依赖..."
    # CentOS 需要先装 EPEL 才有 nginx
    if command -v yum &>/dev/null; then
        yum install -y epel-release 2>/dev/null || true
    fi
    pkg_install python3 python3-pip git nginx

    # python3-venv 在 CentOS 上可能叫 python3-virtualenv 或用 pip 装
    if python3 -m venv --help &>/dev/null; then
        log_info "venv 可用"
    else
        log_info "安装 venv..."
        pip3 install virtualenv 2>/dev/null || pkg_install python3-virtualenv 2>/dev/null || true
    fi

    if [ -d "$APP_DIR" ]; then
        log_warn "$APP_DIR 已存在，跳过克隆"
    else
        log_info "克隆代码..."
        git clone -b $BRANCH $REPO_URL $APP_DIR
    fi

    if [ -d "$VENV_DIR" ]; then
        log_warn "虚拟环境已存在"
    else
        log_info "创建虚拟环境..."
        python3 -m venv $VENV_DIR || virtualenv $VENV_DIR
    fi

    log_info "安装 Python 依赖..."
    $VENV_DIR/bin/pip install --upgrade pip
    $VENV_DIR/bin/pip install -r $APP_DIR/shadow_server/requirements.txt
    $VENV_DIR/bin/pip install flask flask-cors pymysql

    log_info "部署配置..."
    cp $APP_DIR/shadow_server/deploy/.env.production $APP_DIR/shadow_server/.env

    # systemd 服务
    log_info "配置 systemd..."
    cp $APP_DIR/shadow_server/deploy/xinyu-shadow.service /etc/systemd/system/
    cp $APP_DIR/shadow_server/deploy/xinyu-flask.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable $SHADOW_SERVICE $FLASK_SERVICE

    # Nginx — CentOS 用 conf.d，Ubuntu 用 sites-available
    log_info "配置 Nginx..."
    if [ -d /etc/nginx/sites-available ]; then
        cp $APP_DIR/shadow_server/deploy/nginx_xinyu.conf /etc/nginx/sites-available/xinyu
        ln -sf /etc/nginx/sites-available/xinyu /etc/nginx/sites-enabled/xinyu
        rm -f /etc/nginx/sites-enabled/default
    else
        # CentOS: 放 conf.d
        cp $APP_DIR/shadow_server/deploy/nginx_xinyu.conf /etc/nginx/conf.d/xinyu.conf
        # 删除默认冲突配置
        rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true
    fi
    nginx -t && systemctl enable nginx && systemctl reload nginx

    # 启动后端
    log_info "启动服务..."
    systemctl start $FLASK_SERVICE
    systemctl start $SHADOW_SERVICE

    log_info "===== 部署完成 ====="
    do_status
}

# ---- 更新部署 ----
do_update() {
    log_info "===== 更新部署 ====="
    cd $APP_DIR

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
