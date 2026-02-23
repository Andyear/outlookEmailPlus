from __future__ import annotations

from typing import Dict, List, Optional

import requests

from outlook_web import config
from outlook_web.repositories.settings import get_gptmail_api_key


def gptmail_request(
    method: str,
    endpoint: str,
    params: dict = None,
    json_data: dict = None,
) -> Optional[Dict]:
    """发送 GPTMail API 请求"""
    try:
        url = f"{config.get_gptmail_base_url()}{endpoint}"
        api_key = get_gptmail_api_key()
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=json_data, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=30)
        else:
            return None

        if response.status_code == 200:
            return response.json()
        return {"success": False, "error": f"API 请求失败: {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": f"请求异常: {str(e)}"}


def generate_temp_email(prefix: str = None, domain: str = None) -> Optional[str]:
    """生成临时邮箱地址"""
    json_data = {}
    if prefix:
        json_data["prefix"] = prefix
    if domain:
        json_data["domain"] = domain

    if json_data:
        result = gptmail_request("POST", "/api/generate-email", json_data=json_data)
    else:
        result = gptmail_request("GET", "/api/generate-email")

    if result and result.get("success"):
        return result.get("data", {}).get("email")
    return None


def get_temp_emails_from_api(email_addr: str) -> Optional[List[Dict]]:
    """从 GPTMail API 获取邮件列表"""
    result = gptmail_request("GET", "/api/emails", params={"email": email_addr})
    if result and result.get("success"):
        return result.get("data", {}).get("emails", [])
    return None


def get_temp_email_detail_from_api(message_id: str) -> Optional[Dict]:
    """从 GPTMail API 获取邮件详情"""
    result = gptmail_request("GET", f"/api/email/{message_id}")
    if result and result.get("success"):
        return result.get("data")
    return None


def delete_temp_email_from_api(message_id: str) -> bool:
    """从 GPTMail API 删除邮件"""
    result = gptmail_request("DELETE", f"/api/email/{message_id}")
    return bool(result and result.get("success", False))


def clear_temp_emails_from_api(email_addr: str) -> bool:
    """清空 GPTMail 邮箱的所有邮件"""
    result = gptmail_request("DELETE", "/api/emails/clear", params={"email": email_addr})
    return bool(result and result.get("success", False))

