from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("tags", __name__)
    bp.add_url_rule("/api/tags", view_func=impl.api_get_tags, methods=["GET"])
    bp.add_url_rule("/api/tags", view_func=impl.api_add_tag, methods=["POST"])
    bp.add_url_rule("/api/tags/<int:tag_id>", view_func=impl.api_delete_tag, methods=["DELETE"])
    return bp

