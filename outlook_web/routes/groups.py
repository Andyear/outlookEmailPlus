from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("groups", __name__)
    bp.add_url_rule("/api/groups", view_func=impl.api_get_groups, methods=["GET"])
    bp.add_url_rule("/api/groups/<int:group_id>", view_func=impl.api_get_group, methods=["GET"])
    bp.add_url_rule("/api/groups", view_func=impl.api_add_group, methods=["POST"])
    bp.add_url_rule("/api/groups/<int:group_id>", view_func=impl.api_update_group, methods=["PUT"])
    bp.add_url_rule("/api/groups/<int:group_id>", view_func=impl.api_delete_group, methods=["DELETE"])
    bp.add_url_rule("/api/groups/<int:group_id>/export", view_func=impl.api_export_group, methods=["GET"])
    return bp

