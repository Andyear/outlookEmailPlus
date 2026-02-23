from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("scheduler", __name__)
    bp.add_url_rule("/api/scheduler/status", view_func=impl.api_get_scheduler_status, methods=["GET"])
    return bp
