from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("oauth", __name__)
    bp.add_url_rule("/api/oauth/auth-url", view_func=impl.api_get_oauth_auth_url, methods=["GET"])
    bp.add_url_rule("/api/oauth/exchange-token", view_func=impl.api_exchange_oauth_token, methods=["POST"])
    return bp

