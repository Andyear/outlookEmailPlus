from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("settings", __name__)
    bp.add_url_rule("/api/settings/validate-cron", view_func=impl.api_validate_cron, methods=["POST"])
    bp.add_url_rule("/api/settings", view_func=impl.api_get_settings, methods=["GET"])
    bp.add_url_rule("/api/settings", view_func=impl.api_update_settings, methods=["PUT"])
    return bp

