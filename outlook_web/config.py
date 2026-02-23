from __future__ import annotations

import os


def _getenv(key: str, default: str | None = None) -> str | None:
    value = os.getenv(key)
    if value is None:
        return default
    value = value.strip()
    return value if value != "" else default


def require_secret_key() -> str:
    secret_key = _getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable is required. "
            "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    return secret_key


def get_database_path() -> str:
    return _getenv("DATABASE_PATH", "data/outlook_accounts.db") or "data/outlook_accounts.db"


def get_login_password_default() -> str:
    return _getenv("LOGIN_PASSWORD", "admin123") or "admin123"


def get_gptmail_base_url() -> str:
    return _getenv("GPTMAIL_BASE_URL", "https://mail.chatgpt.org.uk") or "https://mail.chatgpt.org.uk"


def get_gptmail_api_key_default() -> str:
    return _getenv("GPTMAIL_API_KEY", "gpt-test") or "gpt-test"


def get_oauth_client_id() -> str:
    return _getenv("OAUTH_CLIENT_ID", "24d9a0ed-8787-4584-883c-2fd79308940a") or "24d9a0ed-8787-4584-883c-2fd79308940a"


def get_oauth_redirect_uri() -> str:
    return _getenv("OAUTH_REDIRECT_URI", "http://localhost:8080") or "http://localhost:8080"


def env_true(key: str, default: bool) -> bool:
    """
    与旧实现保持一致：只有值为 'true'（忽略大小写）才视为 True；其它值均为 False。
    """
    value = _getenv(key, "true" if default else "false") or ("true" if default else "false")
    return value.lower() == "true"


def get_scheduler_autostart_default() -> bool:
    return env_true("SCHEDULER_AUTOSTART", True)

