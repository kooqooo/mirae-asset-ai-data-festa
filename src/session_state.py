from uuid import uuid4
from src.prompt_template import Prompts
from utils.seoul_time import get_current_time_str

class SessionState:
    def __init__(self, system_message: str):
        self.uuid: str = str(uuid4())
        self.created_at: str = get_current_time_str()
        self.title: str = ""
        self.preset_messages: Prompts = Prompts()
        self.chat_tokens: int = 0
        self.total_tokens: int = 0
        self.chat_log: Prompts = Prompts()
        self.turns = 10
        self.summary_messages: Prompts = Prompts()
        self.last_response: str = ""
        self.system_message: Prompts = Prompts.from_message("system", system_message)
    
    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "created_at": self.created_at,
            "title": self.title,
            "preset_messages": self.preset_messages.to_dict(),
            "chat_tokens": self.chat_tokens,
            "total_tokens": self.total_tokens,
            "chat_log": self.chat_log.to_dict(),
            "turns": self.turns,
            "summary_messages": self.summary_messages.to_dict(),
            "last_response": self.last_response,
            "system_message": self.system_message.to_dict()
        }

    def __str__(self) -> str:
        return str(self.to_dict())