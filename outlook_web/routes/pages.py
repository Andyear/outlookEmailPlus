from __future__ import annotations

from typing import Callable, Optional

from flask import Blueprint


def create_blueprint(*, impl, csrf_exempt: Optional[Callable] = None) -> Blueprint:
    bp = Blueprint("pages", __name__)

    login_view = impl.login
    csrf_token_view = impl.get_csrf_token
    if csrf_exempt is not None:
        login_view = csrf_exempt(login_view)
        csrf_token_view = csrf_exempt(csrf_token_view)

    bp.add_url_rule("/login", view_func=login_view, methods=["GET", "POST"])
    bp.add_url_rule("/logout", view_func=impl.logout, methods=["GET"])
    bp.add_url_rule("/", view_func=impl.index, methods=["GET"])
    bp.add_url_rule("/api/csrf-token", view_func=csrf_token_view, methods=["GET"])
    return bp

