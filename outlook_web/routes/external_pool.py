from __future__ import annotations

from flask import Blueprint

from outlook_web.controllers import external_pool as external_pool_controller


def create_blueprint() -> Blueprint:
    bp = Blueprint("external_pool", __name__)
    bp.add_url_rule(
        "/api/external/pool/claim-random",
        view_func=external_pool_controller.api_external_pool_claim_random,
        methods=["POST"],
    )
    bp.add_url_rule(
        "/api/external/pool/claim-release",
        view_func=external_pool_controller.api_external_pool_claim_release,
        methods=["POST"],
    )
    bp.add_url_rule(
        "/api/external/pool/claim-complete",
        view_func=external_pool_controller.api_external_pool_claim_complete,
        methods=["POST"],
    )
    bp.add_url_rule(
        "/api/external/pool/stats",
        view_func=external_pool_controller.api_external_pool_stats,
        methods=["GET"],
    )
    return bp
