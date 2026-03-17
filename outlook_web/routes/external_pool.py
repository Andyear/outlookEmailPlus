from __future__ import annotations

from typing import Callable, Optional

from flask import Blueprint

from outlook_web.controllers import external_pool as external_pool_controller


def create_blueprint(csrf_exempt: Optional[Callable] = None) -> Blueprint:
    bp = Blueprint("external_pool", __name__)
    handlers = [
        (
            "/api/external/pool/claim-random",
            external_pool_controller.api_external_pool_claim_random,
            ["POST"],
        ),
        (
            "/api/external/pool/claim-release",
            external_pool_controller.api_external_pool_claim_release,
            ["POST"],
        ),
        (
            "/api/external/pool/claim-complete",
            external_pool_controller.api_external_pool_claim_complete,
            ["POST"],
        ),
        (
            "/api/external/pool/stats",
            external_pool_controller.api_external_pool_stats,
            ["GET"],
        ),
    ]

    for path, handler, methods in handlers:
        view_func = csrf_exempt(handler) if csrf_exempt else handler
        bp.add_url_rule(path, view_func=view_func, methods=methods)
    return bp
