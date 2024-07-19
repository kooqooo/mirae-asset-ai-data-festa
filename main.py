import os
import json
from typing import List, Union, Dict
from uuid import uuid4

from dotenv import load_dotenv

from src.clova_completion_executor import CompletionExecutor
from src.clova_summary_executor import SummaryExecutor
from src.clova_sliding_window_executor import SlidingWindowExecutor
from src.prompt_template import Prompts
from utils.seoul_time import get_current_time_str, convert_for_file_name
from retrieval import retrieve_answer, prompt_path
from src.request_data import RequestData, SlidingWindowRequestData, SummaryRequestData

load_dotenv(override=True)
API_KEY = os.getenv("KOOQOOO_API_KEY")
API_KEY_PRIMARY_VAL = os.getenv("KOOQOOO_API_KEY_PRIMARY_VAL")
REQUEST_ID = os.getenv("REQUEST_ID")
TEST_APP_ID = os.getenv("TEST_APP_ID")
SLIDING_WINDOW_REQUEST_ID = os.getenv("KOOQOOO_SLI_WIN_REQUEST_ID")
SUMMARY_APP_ID = os.getenv("KOOQOOO_SUMMARY_APP_ID")
SUMMARY_REQUEST_ID = os.getenv("KOOQOOO_SUMMARY_REQUEST_ID")
path = os.path.abspath(os.path.dirname(__file__))

with open(prompt_path, "r", encoding="utf-8") as f:
    system_message = f.read()

completion_executor = CompletionExecutor(
    api_key=API_KEY,
    api_key_primary_val=API_KEY_PRIMARY_VAL,
    request_id=REQUEST_ID,
    test_app_id=TEST_APP_ID,
    stream=False
)

summary_executor = SummaryExecutor(
    api_key=API_KEY,
    api_key_primary_val=API_KEY_PRIMARY_VAL,
    request_id=SUMMARY_REQUEST_ID,
    test_app_id=SUMMARY_APP_ID,
    host='clovastudio.apigw.ntruss.com',
)

sliding_window_executor = SlidingWindowExecutor(
    api_key=API_KEY,
    api_key_primary_val=API_KEY_PRIMARY_VAL,
    request_id=SLIDING_WINDOW_REQUEST_ID,
)


class SessionState:
    def __init__(self):
        self.uuid: str = str(uuid4())
        self.created_at: str = get_current_time_str()
        self.title: str = ""
        self.preset_messages: Prompts = Prompts()
        self.chat_tokens: int = 0
        self.total_tokens: int = 0
        self.chat_log: Prompts = Prompts()
        self.turns = 10
        self.summary_messages: Prompts = Prompts()
        self.last_user_input: str = ""
        self.last_response: str = ""
        self.last_user_message: Prompts = Prompts()
        self.last_assistant_message: Prompts = Prompts()
        self.previous_messages: Prompts = Prompts()
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
            "last_user_input": self.last_user_input,
            "last_response": self.last_response,
            "last_user_message": self.last_user_message.to_dict(),
            "last_assistant_message": self.last_assistant_message.to_dict(),
            "previous_messages": self.previous_messages.to_dict(),
            "system_message": self.system_message.to_dict()
        }

    def __str__(self) -> str:
        return str(self.to_dict())

def save_log(session_state: SessionState):
    with open(
        os.path.join(path, "logs", f"{convert_for_file_name(session_state.created_at)}.json"), "w", encoding="utf-8") as f:
        json.dump(session_state.to_dict(), f, ensure_ascii=False, indent=4)

def main():
    # 세션 상태 초기화
    session_state = SessionState()
    
    while True:
        # 사용자 입력 받기
        print("'종료' 혹은 '그만' 입력하면 종료합니다.")
        user_input = input("사용자: ")
        if user_input in ["종료", "그만", "rmaks", "whdfy"]:
            break
        
        session_state.last_user_input = user_input
        session_state.chat_log.add_message("user", user_input)
        
        # 사용자 입력으로부터 답변 생성
        retrieved_answer = retrieve_answer(user_input)
        system_message_with_reference = Prompts.from_message("system", system_message + retrieved_answer)
        chat_log = system_message_with_reference + session_state.chat_log
        
        ### 여기 슬라이딩 윈도우 구현하기 ###
        sliding_window_request = SlidingWindowRequestData(messages=chat_log.to_dict()).to_dict()
        sliding_window_response = sliding_window_executor.execute(sliding_window_request)
        adjusted_messages = sliding_window_response["result"]["messages"]
        
        # 사용자 입력을 Clova Studio로 전송
        completion_request = RequestData(messages=adjusted_messages).to_dict()
        completion_response = completion_executor.invoke(completion_request)
        
        session_state.total_tokens += completion_response["result"]["outputLength"]
        session_state.chat_tokens += completion_response["result"]["outputLength"]
        
        # Clova Studio의 응답을 파싱하여 시스템 응답, 이를 chat_log에 추가
        session_state.last_response = completion_response["result"]["message"]["content"]
        session_state.chat_log.add_message("assistant", ''.join(session_state.last_response))
        print("=== Clova Studio 응답 ===")
        print(session_state.last_response)
        print()
        
        # 마지막 Clova Studio의 응답을 요약, 질문 생성용으로 사용 가능
        summary_request = SummaryRequestData(texts=[session_state.last_response]).to_dict()
        summary_response = summary_executor.execute(summary_request)
        print("=== 요약 ===")
        print(summary_response)
        print()
        print()
        
        save_log(session_state)
        
        # 턴 수 감소
        session_state.turns -= 1
        if session_state.turns == 0:
            # 턴이 종료된 경우에 대한 처리가 필요
            # 1. 이어 나가는 옵션 추가?
            # 2. 전체 대화 요약?
            
            # 전체 대화 내용을 요약
            summary_request = SummaryRequestData(texts=session_state.chat_log.to_list()).to_dict()
            # summary_response = summary_executor.execute(summary_request) # 토큰 절약을 위해 일시적 비활성화
            break
    

if __name__ == "__main__":
    main()