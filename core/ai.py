import json
import os
import socket
import ssl
import urllib.error
import urllib.request

import certifi

from django.conf import settings


class AIServiceError(Exception):
    pass


def _get_provider(provider: str) -> dict:
    provider = (provider or "").lower().strip()
    config = settings.AI_PROVIDERS.get(provider)
    if not config:
        raise AIServiceError("未识别的 AI 服务商。")
    api_key = os.environ.get(config.get("api_key_env", ""), "").strip()
    if not api_key:
        raise AIServiceError("AI 服务尚未配置 API Key。")
    return {
        "provider": provider,
        "base_url": config["base_url"],
        "api_key": api_key,
        "model": config["model"],
    }


def call_ai(
    provider: str,
    messages: list,
    model_override: str | None = None,
    max_tokens: int | None = None,
) -> str:
    config = _get_provider(provider)
    model = model_override or config["model"]
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.4,
        "max_tokens": max_tokens or 1024,
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        config["base_url"],
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        },
        method="POST",
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    timeout = getattr(settings, "AI_TIMEOUT", 120)
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="ignore")
            data = json.loads(detail)
            if isinstance(data, dict):
                detail = data.get("error", {}).get("message") or data.get("message") or detail
        except Exception:
            detail = detail or ""
        message = f"AI 请求失败：{exc.code} {exc.reason}"
        if detail:
            message = f"{message}（{detail}）"
        raise AIServiceError(message) from exc
    except (urllib.error.URLError, socket.timeout, ssl.SSLError) as exc:
        detail = getattr(exc, "reason", "") or str(exc) or ""
        if isinstance(exc, socket.timeout):
            message = "AI 服务连接超时，请稍后重试。"
        else:
            message = "AI 服务无法连接，请稍后重试。"
        if detail:
            message = f"{message}（{detail}）"
        raise AIServiceError(message) from exc
    except Exception as exc:
        raise AIServiceError("AI 请求出现异常，请稍后重试。") from exc

    try:
        result = json.loads(raw)
        content = result["choices"][0]["message"]["content"]
        return content.strip()
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise AIServiceError("AI 返回数据解析失败，请检查服务商响应格式。") from exc
