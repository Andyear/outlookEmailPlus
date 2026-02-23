from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("system", __name__)
    bp.add_url_rule("/healthz", view_func=impl.healthz, methods=["GET"])
    bp.add_url_rule("/api/system/health", view_func=impl.api_system_health, methods=["GET"])
    bp.add_url_rule("/api/system/diagnostics", view_func=impl.api_system_diagnostics, methods=["GET"])
    bp.add_url_rule("/api/system/upgrade-status", view_func=impl.api_system_upgrade_status, methods=["GET"])
    return bp

