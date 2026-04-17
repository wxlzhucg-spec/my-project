# -*- coding: utf-8 -*-
"""
挂到现有 Flask 应用（5001）上即可打通小程序注册页。

用法示例：
    from register_routes import register_bp, init_register_db
    app.register_blueprint(register_bp)
    init_register_db(lambda: pymysql.connect(...))   # 或传入你的 get_conn

小程序请求：POST /register
JSON：{"phone":"152xxxx","password":"******","nickname":"xl"}
成功：{"code":0,"user_id":1,"openid":"p_152xxxx"}  （openid 为占位，便于后续 /emotion 校验）
"""
import re
import pymysql
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

register_bp = Blueprint("register", __name__)

_get_conn = None


def init_register_db(get_connection_callable):
    global _get_conn
    _get_conn = get_connection_callable


def _conn():
    if _get_conn is None:
        raise RuntimeError("请先调用 init_register_db(get_conn)")
    return _get_conn()


PHONE_RE = re.compile(r"^1\d{10}$")


@register_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""
    nickname = (data.get("nickname") or "").strip()
    if not PHONE_RE.match(phone):
        return jsonify(code=400, message="手机号格式错误"), 200
    if len(password) < 6:
        return jsonify(code=400, message="密码至少6位"), 200
    if not nickname:
        nickname = "用户" + phone[-4:]
    nickname = nickname[:32]
    open_id = "p_" + phone
    pwd_hash = generate_password_hash(password)

    try:
        cn = _conn()
        try:
            with cn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (open_id, phone, password_hash, nickname, terms_agreed_at, profile_completed)
                    VALUES (%s, %s, %s, %s, NOW(), 0)
                    """,
                    (open_id, phone, pwd_hash, nickname),
                )
                uid = cur.lastrowid
            cn.commit()
        finally:
            try:
                cn.close()
            except Exception:
                pass
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return jsonify(code=400, message="手机号已注册"), 200
        return jsonify(code=500, message="数据库错误"), 200
    except Exception as e:
        return jsonify(code=500, message=str(e) or "服务器错误"), 200

    return jsonify(code=0, message="ok", user_id=uid, openid=open_id), 200
