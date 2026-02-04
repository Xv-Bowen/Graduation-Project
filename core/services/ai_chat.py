from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from core.ai import AIServiceError, call_ai
from core.models import ChatLog


@dataclass
class AIChatPayload:
    provider: str
    deep_think: bool
    messages: list[dict]


def parse_ai_payload(payload: dict) -> AIChatPayload:
    provider = payload.get("provider") or "deepseek"
    deep_think = payload.get("deep_think") is True
    messages = payload.get("messages") or []
    if not isinstance(messages, list) or not messages:
        raise ValueError("消息格式不正确")
    cleaned = [
        msg
        for msg in messages
        if isinstance(msg, dict) and msg.get("role") in {"user", "assistant"} and msg.get("content")
    ]
    if not cleaned:
        raise ValueError("消息格式不正确")
    if len(cleaned) > settings.CHAT_HISTORY_LIMIT:
        cleaned = cleaned[-settings.CHAT_HISTORY_LIMIT :]
    for msg in cleaned:
        content = str(msg.get("content", ""))
        if len(content) > settings.AI_MAX_INPUT_CHARS:
            raise ValueError("内容过长")
    return AIChatPayload(provider=provider, deep_think=deep_think, messages=cleaned)


def contains_risk(text: str) -> bool:
    return any(keyword in text for keyword in settings.AI_RISK_KEYWORDS)


def build_messages(messages: list[dict]) -> list[dict]:
    system_message = {"role": "system", "content": settings.AI_SYSTEM_PROMPT}
    return [system_message] + messages


def generate_ai_reply(payload: AIChatPayload) -> str:
    model = settings.AI_REASONER_MODEL if payload.deep_think else settings.AI_CHAT_MODEL
    return call_ai(
        payload.provider,
        build_messages(payload.messages),
        model_override=model,
        max_tokens=settings.AI_MAX_TOKENS,
    )


def log_chat(provider: str, user, messages: list[dict], reply: str, risk: bool) -> None:
    ChatLog.objects.create(
        provider=provider,
        user=user,
        messages_json=messages,
        response_text=reply,
        risk_flag=risk,
    )
