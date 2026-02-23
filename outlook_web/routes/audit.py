from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("audit", __name__)
    bp.add_url_rule("/api/audit-logs", view_func=impl.api_get_audit_logs, methods=["GET"])
    return bp
