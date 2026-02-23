from __future__ import annotations

from flask import Blueprint


def create_blueprint(*, impl) -> Blueprint:
    bp = Blueprint("temp_emails", __name__)
    bp.add_url_rule("/api/temp-emails", view_func=impl.api_get_temp_emails, methods=["GET"])
    bp.add_url_rule("/api/temp-emails/generate", view_func=impl.api_generate_temp_email, methods=["POST"])
    bp.add_url_rule("/api/temp-emails/<path:email_addr>", view_func=impl.api_delete_temp_email, methods=["DELETE"])
    bp.add_url_rule("/api/temp-emails/<path:email_addr>/messages", view_func=impl.api_get_temp_email_messages, methods=["GET"])
    bp.add_url_rule(
        "/api/temp-emails/<path:email_addr>/messages/<path:message_id>",
        view_func=impl.api_get_temp_email_message_detail,
        methods=["GET"],
    )
    bp.add_url_rule(
        "/api/temp-emails/<path:email_addr>/messages/<path:message_id>",
        view_func=impl.api_delete_temp_email_message,
        methods=["DELETE"],
    )
    bp.add_url_rule("/api/temp-emails/<path:email_addr>/clear", view_func=impl.api_clear_temp_email_messages, methods=["DELETE"])
    bp.add_url_rule("/api/temp-emails/<path:email_addr>/refresh", view_func=impl.api_refresh_temp_email_messages, methods=["POST"])
    return bp

