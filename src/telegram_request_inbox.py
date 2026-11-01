"""Safely extract an authorized text request from a Telegram getUpdates payload."""
from __future__ import annotations

from parse_telegram_quran_request import parse_quran_request


def extract_authorized_request(update: dict, allowed_chat_id: str) -> dict:
    if not isinstance(update, dict) or not allowed_chat_id:
        raise ValueError("Telegram update and authorized chat ID are required.")
    message = update.get("message") or update.get("edited_message")
    if not isinstance(message, dict):
        raise ValueError("This Telegram update does not contain a text message.")
    chat = message.get("chat") or {}
    sender = message.get("from") or {}
    if str(chat.get("id", "")) != str(allowed_chat_id):
        raise PermissionError("Telegram chat is not authorized.")
    if not isinstance(message.get("text"), str):
        raise ValueError("Send a text request, for example: فيديو سورة الرحمن")
    request = parse_quran_request(message["text"])
    return {
        "update_id": int(update["update_id"]),
        "chat_id": str(chat["id"]),
        "user_id": str(sender.get("id", "")),
        "message_id": int(message["message_id"]),
        "request": request,
        "status": "authorized_request_parsed_only",
        "rendering_allowed": False,
        "telegram_delivery": False,
        "auto_publish": False,
    }
