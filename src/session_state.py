from uuid import uuid4
from src.prompt_template import Prompts
from utils.seoul_time import get_current_time_str


class SessionState:
    def __init__(self, system_message: str):
        self.uuid: str = str(uuid4())
        self.created_at: str = get_current_time_str()
        self.title: str = ""
        self.turns = 10
        self.chat_tokens: int = 0
        self.total_tokens: int = 0
        self.system_message: Prompts = Prompts.from_message("system", system_message)
        self.previous_user_inputs: Prompts = Prompts()
        self.chat_log: Prompts = Prompts()
        self.summary_messages: Prompts = Prompts()
        self.last_response: str = ""
    
    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "created_at": self.created_at,
            "title": self.title,
            "total_tokens": self.total_tokens,
            "chat_log": self.chat_log.to_dict(),
            "summary_messages": self.summary_messages.to_dict(),
        }

    def __repr__(self) -> str:
        return str(self.__dict__)

if __name__ == "__main__":
    print(SessionState("안녕하세요!"))