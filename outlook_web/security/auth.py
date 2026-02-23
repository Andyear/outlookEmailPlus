from __future__ import annotations

import secrets
import time
from functools import wraps
from typing import Optional

from flask import g, jsonify, redirect, request, session, url_for

from outlook_web.db import get_db
from outlook_web.errors import build_error_payload

# 速率限制配置
MAX_LOGIN_ATTEMPTS = 5  # 最大失败次数
LOCKOUT_DURATION = 300  # 锁定时长（秒）- 5分钟
ATTEMPT_WINDOW = 600  # 失败计数窗口（秒）- 10分钟

# 导出二次验证 Token（持久化存储，支持重启/多进程）
EXPORT_VERIFY_TOKEN_TTL_SECONDS = 300  # 5 分钟有效期


def check_rate_limit(ip: str) -> tuple[bool, Optional[int]]:
    """
    检查 IP 是否被速率限制
    返回: (是否允许登录, 剩余锁定秒数)
    """
    current_time = time.time()
    db = get_db()

    try:
        row = db.execute(
            """
            SELECT count, last_attempt_at, locked_until_at
            FROM login_attempts
            WHERE ip = ?
            """,
            (ip,),
        ).fetchone()

        if not row:
            return True, None

        locked_until_at = row["locked_until_at"]
        if locked_until_at and current_time < locked_until_at:
            remaining = int(locked_until_at - current_time)
            return False, remaining

        last_attempt_at = row["last_attempt_at"]
        if last_attempt_at and (current_time - last_attempt_at > ATTEMPT_WINDOW):
            db.execute(
                """
                UPDATE login_attempts
                SET count = 0, last_attempt_at = ?, locked_until_at = NULL
                WHERE ip = ?
                """,
                (current_time, ip),
            )
            db.commit()
            return True, None

        count = row["count"] or 0
        if count >= MAX_LOGIN_ATTEMPTS:
            locked_until_at = current_time + LOCKOUT_DURATION
            db.execute(
                """
                UPDATE login_attempts
                SET locked_until_at = ?
                WHERE ip = ?
                """,
                (locked_until_at, ip),
            )
            db.commit()
            return False, LOCKOUT_DURATION

        return True, None
    except Exception:
        # 速率限制出错时，为避免误拒绝，默认放行
        return True, None


def record_login_failure(ip: str):
    """记录登录失败"""
    current_time = time.time()
    db = get_db()

    try:
        # 清理过期记录，避免无限增长
        db.execute(
            """
            DELETE FROM login_attempts
            WHERE last_attempt_at < ?
            """,
            (current_time - (ATTEMPT_WINDOW * 2),),
        )

        row = db.execute(
            """
            SELECT count, last_attempt_at
            FROM login_attempts
            WHERE ip = ?
            """,
            (ip,),
        ).fetchone()

        if not row:
            db.execute(
                """
                INSERT INTO login_attempts (ip, count, last_attempt_at, locked_until_at)
                VALUES (?, ?, ?, NULL)
                """,
                (ip, 1, current_time),
            )
        else:
            last_attempt_at = row["last_attempt_at"] or 0
            count = row["count"] or 0
            if current_time - last_attempt_at <= ATTEMPT_WINDOW:
                new_count = count + 1
            else:
                new_count = 1

            db.execute(
                """
                UPDATE login_attempts
                SET count = ?, last_attempt_at = ?
                WHERE ip = ?
                """,
                (new_count, current_time, ip),
            )

        db.commit()
    except Exception:
        pass


def reset_login_attempts(ip: str):
    """重置登录失败记录（登录成功时调用）"""
    db = get_db()
    try:
        db.execute("DELETE FROM login_attempts WHERE ip = ?", (ip,))
        db.commit()
    except Exception:
        pass


def login_required(f):
    """登录验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            if request.is_json or request.path.startswith("/api/"):
                trace_id_value = None
                try:
                    trace_id_value = getattr(g, "trace_id", None)
                except Exception:
                    trace_id_value = None
                error_payload = build_error_payload(
                    code="AUTH_REQUIRED",
                    message="请先登录",
                    err_type="AuthError",
                    status=401,
                    details="need_login",
                    trace_id=trace_id_value,
                )
                return jsonify({"success": False, "error": error_payload, "need_login": True}), 401
            return redirect(url_for("pages.login"))
        return f(*args, **kwargs)

    return decorated_function


def get_client_ip() -> str:
    """获取客户端 IP（兼容反向代理）"""
    try:
        client_ip = request.headers.get("X-Forwarded-For") or request.remote_addr
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        return client_ip or "unknown"
    except Exception:
        return "unknown"


def get_user_agent() -> str:
    try:
        return (request.headers.get("User-Agent") or "")[:300]
    except Exception:
        return ""


def issue_export_verify_token(client_ip: str, user_agent: str) -> str:
    """生成并持久化一次性导出验证 token"""
    db = get_db()
    now_ts = time.time()
    verify_token = secrets.token_urlsafe(32)
    expires_at = now_ts + EXPORT_VERIFY_TOKEN_TTL_SECONDS

    db.execute(
        """
        INSERT INTO export_verify_tokens (token, ip, user_agent, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (verify_token, client_ip, user_agent, expires_at, now_ts),
    )
    db.execute("DELETE FROM export_verify_tokens WHERE expires_at < ?", (now_ts,))
    db.commit()
    return verify_token


def consume_export_verify_token(verify_token: str) -> tuple[bool, str]:
    """校验并消费一次性导出验证 token（成功则删除）"""
    if not verify_token:
        return False, "需要二次验证"

    db = get_db()
    now_ts = time.time()

    try:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """
            SELECT expires_at
            FROM export_verify_tokens
            WHERE token = ?
            """,
            (verify_token,),
        ).fetchone()

        if not row:
            db.rollback()
            return False, "需要二次验证"

        expires_at = row["expires_at"] or 0
        if float(expires_at) < now_ts:
            db.execute("DELETE FROM export_verify_tokens WHERE token = ?", (verify_token,))
            db.commit()
            return False, "验证已过期，请重新验证"

        db.execute("DELETE FROM export_verify_tokens WHERE token = ?", (verify_token,))
        db.commit()
        return True, ""
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        return False, "验证失败，请重试"


def check_export_verify_token(verify_token: str) -> tuple[bool, str]:
    """校验一次性导出验证 token（不消费）"""
    if not verify_token:
        return False, "需要二次验证"

    db = get_db()
    now_ts = time.time()
    try:
        row = db.execute(
            """
            SELECT expires_at
            FROM export_verify_tokens
            WHERE token = ?
            """,
            (verify_token,),
        ).fetchone()
        if not row:
            return False, "需要二次验证"
        if float(row["expires_at"] or 0) < now_ts:
            return False, "验证已过期，请重新验证"
        return True, ""
    except Exception:
        return False, "验证失败，请重试"
