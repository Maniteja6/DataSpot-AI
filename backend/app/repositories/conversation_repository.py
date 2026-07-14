from __future__ import annotations
import threading
from app.models.chat_message import ChatMessage


class ConversationRepository:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._messages: dict[str, list[ChatMessage]] = {}

    def add_message(self, conversation_id: str, message: ChatMessage) -> None:
        with self._lock:
            self._messages.setdefault(conversation_id, []).append(message)

    def get_history(self, conversation_id: str, limit: int = 20) -> list[ChatMessage]:
        return self._messages.get(conversation_id, [])[-limit:]


conversation_repository = ConversationRepository()
