# -*- coding: utf-8 -*-
"""
API - 情绪记录 + 用户管理（与小程序 utils/api.js 一致）
- POST /emotion：openid, emotion_type, score, note?, date?, vitality?（0-100，可选，对应表 vitality）
- POST /user/register 成功：仅 { code, message }，不返回 user_id/openid

运行前设置环境变量，勿把密码写进代码：
  export MYSQL_HOST=127.0.0.1
  export MYSQL_USER=root
  export MYSQL_PASSWORD=你的密码
  export MYSQL_DATABASE=xintujie
"""
from __future__ import annotations

import hashlib
import os
from datetime import datetime

import pymysql
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


def _mysql_config():
    return {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "xintujie"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }


def get_db_connection():
    return pymysql.connect(**_mysql_config())


def _json_error_500(exc: BaseException):
    """统一 500 响应；服务器上 export XINYU_API_DEBUG=1 可在 JSON 里看到 error 便于排查。"""
    out = {"code": 500, "message": "服务器内部错误"}
    if os.getenv("XINYU_API_DEBUG", "").lower() in ("1", "true", "yes"):
        out["error"] = str(exc)
    return jsonify(out), 500


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _format_emotion(row):
    if row.get("date") and hasattr(row["date"], "strftime"):
        row["date"] = row["date"].strftime("%Y-%m-%d")
    for k in ("created_at", "updated_at"):
        if row.get(k) and hasattr(row[k], "strftime"):
            row[k] = row[k].strftime("%Y-%m-%d %H:%M:%S")


def _format_user(row):
    if not row:
        return row
    row = {k: v for k, v in row.items() if k != "password_hash"}
    for field in ("created_at", "updated_at", "last_login_at", "terms_agreed_at"):
        if row.get(field) and hasattr(row[field], "strftime"):
            row[field] = row[field].strftime("%Y-%m-%d %H:%M:%S")
    if row.get("birth_date") and hasattr(row["birth_date"], "strftime"):
        row["birth_date"] = row["birth_date"].strftime("%Y-%m-%d")
    return row


# ============ 情绪记录 API ============


@app.route("/emotion", methods=["GET"])
def get_emotion():
    openid = request.args.get("openid")
    date = request.args.get("date")

    if not openid:
        return jsonify({"code": 400, "message": "缺少openid参数"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if date:
            sql = "SELECT * FROM emotion_records WHERE openid = %s AND date = %s"
            cursor.execute(sql, (openid, date))
            row = cursor.fetchone()
            if row:
                _format_emotion(row)
                return jsonify({"code": 200, "message": "success", "data": row})
            return jsonify({"code": 404, "message": "未找到该日期的记录"}), 404

        sql = "SELECT * FROM emotion_records WHERE openid = %s ORDER BY date DESC"
        cursor.execute(sql, (openid,))
        rows = cursor.fetchall()
        for row in rows:
            _format_emotion(row)
        return jsonify({"code": 200, "message": "success", "data": rows, "count": len(rows)})
    except Exception as e:
        print(f"Error GET /emotion: {e}")
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/emotion", methods=["POST"])
def add_emotion():
    data = request.get_json() or {}
    openid = data.get("openid")
    emotion_type = data.get("emotion_type")
    score = data.get("score")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    note = data.get("note", "") or ""
    vitality_raw = data.get("vitality")
    if vitality_raw is None or vitality_raw == "":
        vitality_raw = data.get("vitality_score")

    if not openid:
        return jsonify({"code": 400, "message": "缺少openid"}), 400
    if emotion_type is None or emotion_type == "":
        return jsonify({"code": 400, "message": "缺少emotion_type"}), 400
    if score is None:
        return jsonify({"code": 400, "message": "缺少score"}), 400
    if not (isinstance(score, (int, float)) and 0 <= score <= 100):
        return jsonify({"code": 400, "message": "分数需为0-100之间的数字"}), 400

    vitality = None
    if vitality_raw is not None and vitality_raw != "":
        if not (isinstance(vitality_raw, (int, float)) and 0 <= vitality_raw <= 100):
            return jsonify({"code": 400, "message": "活力值需为0-100之间的数字"}), 400
        vitality = int(vitality_raw)

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO emotion_records (openid, date, emotion_type, score, vitality, note)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                emotion_type = VALUES(emotion_type),
                score = VALUES(score),
                vitality = VALUES(vitality),
                note = VALUES(note)
        """
        cursor.execute(sql, (openid, date, emotion_type, int(score), vitality, note))
        conn.commit()
        print(f"[EMOTION OK] openid={openid!r} date={date!r} rowcount={cursor.rowcount}", flush=True)
        return jsonify({"code": 200, "message": "success"})
    except Exception as e:
        print(f"Error POST /emotion: {e}")
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/emotion", methods=["DELETE"])
def delete_emotion():
    openid = request.args.get("openid")
    date = request.args.get("date")

    if not openid or not date:
        return jsonify({"code": 400, "message": "缺少必要参数"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "DELETE FROM emotion_records WHERE openid = %s AND date = %s"
        cursor.execute(sql, (openid, date))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({"code": 200, "message": "success"})
        return jsonify({"code": 404, "message": "未找到记录"}), 404
    except Exception as e:
        print(f"Error DELETE /emotion: {e}")
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============ 用户 API ============


@app.route("/user/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    password = data.get("password", "")
    terms_agreed = data.get("terms_agreed", False)

    if not phone or len(phone) != 11 or not phone.isdigit():
        return jsonify({"code": 400, "message": "请输入正确的11位手机号"}), 400
    if not password or len(password) < 6:
        return jsonify({"code": 400, "message": "密码至少6位"}), 400
    if not terms_agreed:
        return jsonify({"code": 400, "message": "请先同意用户协议"}), 400

    gender = data.get("gender", "unknown")
    if gender not in ("male", "female", "unknown"):
        return jsonify({"code": 400, "message": "gender 只允许 male/female/unknown"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        if cursor.fetchone():
            return jsonify({"code": 409, "message": "该手机号已注册"}), 409

        open_id = data.get("open_id")
        if open_id:
            cursor.execute("SELECT id FROM users WHERE open_id = %s", (open_id,))
            if cursor.fetchone():
                return jsonify({"code": 409, "message": "该微信已绑定其他账号"}), 409

        profile_completed = 1 if data.get("birth_date") else 0

        sql = """
            INSERT INTO users (phone, password_hash, nickname, avatar_url, gender,
                               birth_date, birth_time, birth_province, birth_city,
                               birth_district, mbti, open_id, union_id,
                               terms_agreed_at, profile_completed)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), %s)
        """
        cursor.execute(
            sql,
            (
                phone,
                _hash_password(password),
                data.get("nickname", "").strip(),
                data.get("avatar_url", "").strip(),
                gender,
                data.get("birth_date"),
                data.get("birth_time", "").strip(),
                data.get("birth_province", "").strip(),
                data.get("birth_city", "").strip(),
                data.get("birth_district", "").strip(),
                data.get("mbti", "").strip(),
                open_id,
                data.get("union_id"),
                profile_completed,
            ),
        )
        conn.commit()
        print(f"[REGISTER OK] user_id={cursor.lastrowid} phone={phone!r}", flush=True)

        return jsonify({"code": 200, "message": "注册成功"})
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error POST /user/register: {e}")
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/user/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    phone = data.get("phone", "").strip()
    password = data.get("password", "")

    if not phone or not password:
        return jsonify({"code": 400, "message": "手机号和密码不能为空"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 不在 SQL 里写 status=1：老库若没有 status 列会直接 500（Unknown column）
        cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"code": 401, "message": "手机号或密码错误"}), 401
        # 兼容：标准列为 password_hash；老表可能用 password 存哈希，缺列时用 .get 避免 KeyError→500
        stored_hash = user.get("password_hash")
        if stored_hash is None or stored_hash == "":
            stored_hash = user.get("password")
        if stored_hash is None or str(stored_hash) != _hash_password(password):
            return jsonify({"code": 401, "message": "手机号或密码错误"}), 401
        st = user.get("status")
        if st is not None and int(st) != 1:
            return jsonify({"code": 403, "message": "账号已禁用"}), 403

        try:
            cursor.execute("UPDATE users SET last_login_at = NOW() WHERE id = %s", (user["id"],))
            conn.commit()
        except Exception as upd_e:
            # 老表若无 last_login_at 列，UPDATE 会报错；不应导致整次登录 500
            print(f"[login] last_login_at 更新跳过: {upd_e}", flush=True)
            if conn:
                conn.rollback()

        return jsonify({"code": 200, "message": "登录成功", "data": _format_user(user)})
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error POST /user/login: {e}", flush=True)
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/user", methods=["GET"])
def get_user():
    user_id = request.args.get("id")
    open_id = request.args.get("open_id")
    phone = (request.args.get("phone") or "").strip()

    if not user_id and not open_id and not phone:
        return jsonify({"code": 400, "message": "请提供id、open_id或phone"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM users WHERE id = %s", (int(user_id),))
        elif phone:
            cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
        else:
            cursor.execute("SELECT * FROM users WHERE open_id = %s", (open_id,))

        user = cursor.fetchone()
        if not user:
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        return jsonify({"code": 200, "message": "success", "data": _format_user(user)})
    except Exception as e:
        print(f"Error GET /user: {e}")
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/user/profile", methods=["PUT"])
def update_profile():
    data = request.get_json() or {}
    user_id = data.get("id")
    phone = (data.get("phone") or "").strip()

    if not user_id and not phone:
        return jsonify({"code": 400, "message": "缺少用户ID或手机号"}), 400

    allowed_fields = [
        "nickname",
        "avatar_url",
        "gender",
        "birth_date",
        "birth_time",
        "birth_province",
        "birth_city",
        "birth_district",
        "mbti",
    ]
    updates = {k: v for k, v in data.items() if k in allowed_fields and v is not None}

    if not updates:
        return jsonify({"code": 400, "message": "没有需要更新的字段"}), 400

    if "gender" in updates and updates["gender"] not in ("male", "female", "unknown"):
        return jsonify({"code": 400, "message": "gender 只允许 male/female/unknown"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        target_user_id = None
        if user_id:
            cursor.execute("SELECT id FROM users WHERE id = %s", (int(user_id),))
        else:
            cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"code": 404, "message": "用户不存在"}), 404
        target_user_id = int(row["id"])

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [target_user_id]
        cursor.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
        conn.commit()

        cursor.execute("SELECT * FROM users WHERE id = %s", (target_user_id,))
        updated = cursor.fetchone()
        return jsonify({"code": 200, "message": "更新成功", "data": _format_user(updated)})
    except Exception as e:
        print(f"Error PUT /user/profile: {e}")
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/user/bind_wx", methods=["POST"])
def bind_wx():
    data = request.get_json() or {}
    user_id = data.get("id")
    open_id = data.get("open_id", "").strip()
    union_id = data.get("union_id", "").strip()

    if not user_id or not open_id:
        return jsonify({"code": 400, "message": "缺少必要参数"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE open_id = %s", (open_id,))
        existing = cursor.fetchone()
        if existing and existing["id"] != int(user_id):
            return jsonify({"code": 409, "message": "该微信已绑定其他账号"}), 409

        cursor.execute("SELECT id FROM users WHERE id = %s", (int(user_id),))
        if not cursor.fetchone():
            return jsonify({"code": 404, "message": "用户不存在"}), 404

        cursor.execute(
            "UPDATE users SET open_id = %s, union_id = %s WHERE id = %s",
            (open_id, union_id or None, int(user_id)),
        )
        conn.commit()
        return jsonify({"code": 200, "message": "绑定成功"})
    except Exception as e:
        print(f"Error POST /user/bind_wx: {e}")
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ============ 塔罗抽牌 API ============


@app.route("/tarot/draw", methods=["POST"])
def save_tarot_draw():
    """保存一次确认的塔罗抽牌（3 张牌 + 咨询意图）。"""
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "缺少 user_id"}), 400

    theme_tag_id = data.get("theme_tag_id") or None
    theme_tag_label = data.get("theme_tag_label") or None
    question_text = (data.get("question_text") or "").strip()

    cards = data.get("cards")
    if not cards or not isinstance(cards, list) or len(cards) < 3:
        return jsonify({"code": 400, "message": "cards 需为 3 张牌的数组"}), 400
    cards = cards[:3]

    draw_date = data.get("draw_date") or datetime.now().strftime("%Y-%m-%d")

    import json as _json

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO tarot_draws
                (user_id, theme_tag_id, theme_tag_label, question_text,
                 card1_idx, card1_name, card1_num,
                 card2_idx, card2_name, card2_num,
                 card3_idx, card3_name, card3_num,
                 cards_json, draw_date)
            VALUES (%s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s)
        """
        def _card(c):
            if isinstance(c, dict):
                return (
                    int(c.get("idx", c.get("index", 0))),
                    str(c.get("name", "")),
                    str(c.get("num", "")),
                )
            return (0, "", "")

        c1, c2, c3 = _card(cards[0]), _card(cards[1]), _card(cards[2])

        cursor.execute(sql, (
            int(user_id),
            theme_tag_id, theme_tag_label, question_text,
            c1[0], c1[1], c1[2],
            c2[0], c2[1], c2[2],
            c3[0], c3[1], c3[2],
            _json.dumps(cards, ensure_ascii=False),
            draw_date,
        ))
        conn.commit()
        draw_id = cursor.lastrowid
        print(f"[TAROT OK] draw_id={draw_id} user_id={user_id}", flush=True)
        return jsonify({"code": 200, "message": "success", "data": {"id": draw_id}})
    except Exception as e:
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.route("/tarot/draw", methods=["GET"])
def get_tarot_draws():
    """查询用户的塔罗抽牌历史。"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "缺少 user_id"}), 400

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM tarot_draws WHERE user_id = %s ORDER BY created_at DESC LIMIT 50",
            (int(user_id),),
        )
        rows = cursor.fetchall()
        for r in rows:
            if r.get("draw_date") and hasattr(r["draw_date"], "strftime"):
                r["draw_date"] = r["draw_date"].strftime("%Y-%m-%d")
            if r.get("created_at") and hasattr(r["created_at"], "strftime"):
                r["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            if r.get("cards_json") and isinstance(r["cards_json"], str):
                import json as _json
                try:
                    r["cards_json"] = _json.loads(r["cards_json"])
                except Exception:
                    pass
        return jsonify({"code": 200, "message": "success", "data": rows, "count": len(rows)})
    except Exception as e:
        print(f"Error GET /tarot/draw: {e}")
        return _json_error_500(e)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)
