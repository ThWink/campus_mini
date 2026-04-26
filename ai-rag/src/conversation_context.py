# -*- coding: utf-8 -*-
from typing import Any, Dict, List

MAX_HISTORY_ITEMS = 6
MAX_CONTENT_CHARS = 500

WELCOME_MARKERS = [
    "你好！我是智能跑腿助手",
    "有什么可以帮你的吗",
]


def _clean_content(value: Any) -> str:
    return " ".join(str(value or "").split())[:MAX_CONTENT_CHARS]


def _display_role(role: str) -> str:
    if role in ["ai", "assistant"]:
        return "助手"
    return "用户"


def normalize_history(history: Any, limit: int = MAX_HISTORY_ITEMS) -> List[Dict[str, str]]:
    if not isinstance(history, list):
        return []

    normalized: List[Dict[str, str]] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip()
        if role not in ["user", "ai", "assistant"]:
            continue
        content = _clean_content(item.get("content"))
        if not content:
            continue
        if role in ["ai", "assistant"] and any(marker in content for marker in WELCOME_MARKERS):
            continue
        normalized.append({"role": role, "content": content})

    return normalized[-limit:]


def format_history(history: Any, limit: int = MAX_HISTORY_ITEMS) -> str:
    rows = normalize_history(history, limit)
    return "\n".join(f"{_display_role(row['role'])}：{row['content']}" for row in rows)


def build_contextual_query(message: str, history: Any, limit: int = MAX_HISTORY_ITEMS) -> str:
    current = _clean_content(message)
    prior = format_history(history, limit)
    if not prior:
        return current
    return f"历史对话：\n{prior}\n当前问题：{current}"
