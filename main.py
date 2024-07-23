import os
import json
from time import sleep

from dotenv import load_dotenv
from tqdm import tqdm

from src.clova_completion_executor import CompletionExecutor
from src.clova_summary_executor import SummaryExecutor
from src.clova_sliding_window_executor import SlidingWindowExecutor
from src.prompt_template import Prompts
from src.request_data import RequestData, SlidingWindowRequestData, SummaryRequestData
from src.session_state import SessionState
from utils.seoul_time import convert_for_file_name
from question_generator import generate_questions
from retrieval import prompt_path, retrieve_documents, extract_from_documents, retrieve_answer
from voting import get_lowest_score_document, get_most_frequent_document
from config import *

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


def save_log(session_state: SessionState):
    logs_path = os.path.join(path, "logs")
    
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    
    log_file_path = os.path.join(logs_path, f"{convert_for_file_name(session_state.created_at)}.json")
    
    # 로그 파일 저장
    with open(log_file_path, "w", encoding="utf-8") as f:
        json.dump(session_state.to_dict(), f, ensure_ascii=False, indent=4)

def main():
    # 세션 상태 초기화
    session_state = SessionState(system_message=system_message)
    
    while True:
        # 사용자 입력 받기
        print("'종료' 혹은 '그만' 입력하면 종료합니다.")
        user_input = input("사용자: ")
        if user_input in ["종료", "그만", "rmaks", "whdfy"]:
            break
        
        generated_questions = generate_questions(
            user_input=user_input,
            previous_user_inputs=session_state.previous_user_inputs
        )
        session_state.chat_log.add_message("user", user_input)
        session_state.previous_user_inputs.add_message("user", user_input)

        # 사용자 입력으로부터 답변 생성
        retrieved_documents = retrieve_documents(user_input)
        documents_info = extract_from_documents(retrieved_documents)

        # 생성된 질문으로 부터 답변 생성
        if isinstance(generated_questions, list):
            for question in tqdm(generated_questions):
                retrieved_documents = retrieve_documents(question)
                documents_info += extract_from_documents(retrieved_documents)
        elif isinstance(generated_questions, str):
            retrieved_documents = retrieve_documents(generated_questions)
            documents_info += extract_from_documents(retrieved_documents)
        
        voted_document = get_most_frequent_document(documents_info)
        voted_answer = voted_document[0]["answer"]
        
        system_message_with_reference = Prompts.from_message("system", system_message + voted_answer)
        chat_log = system_message_with_reference + session_state.chat_log
        
        # 슬라이딩 윈도우로 대화가 길어져도 맥락 유지하기
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
        session_state.chat_log.add_message("assistant", session_state.last_response)
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