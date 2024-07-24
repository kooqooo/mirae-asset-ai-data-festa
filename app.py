import streamlit as st
from PIL import Image

from config import *
from src.clova_completion_executor import CompletionExecutor
from src.clova_summary_executor import SummaryExecutor
from src.clova_sliding_window_executor import SlidingWindowExecutor
from src.prompt_template import Prompts
from src.request_data import RequestData, SlidingWindowRequestData, SummaryRequestData
from src.session_state import SessionState
from utils.seoul_time import get_seoul_timestamp
from utils.streamlit_utils import Message, write_message, delete_session_state, save_log
from question_generator import generate_questions
from retrieval import prompt_path, retrieve_documents, extract_from_documents
from voting import get_most_frequent_document

# 페이지 설정
st.set_page_config(page_title="m.Talk 채팅상담", layout="centered")
st.markdown("<h1 style='text-align: center;'>💬 m.Talk 채팅상담</h1>", unsafe_allow_html=True)

# 챗봇 아이콘
chatbot_icon = Image.open(chatbot_icon_path)
st.image(chatbot_icon, width=180, caption="🚀 powered by HyperCLOVA")


# 세션 상태 초기화
if "chat_started" not in st.session_state:  # 채팅이 시작되었는지 여부
    st.session_state.chat_started = False
if "messages" not in st.session_state:      # 화면에 표시되는 메시지
    st.session_state.messages = []
if "chat_state" not in st.session_state:    # 내부 사용 메시지
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_message = f.read()
    st.session_state.system_message = system_message
    st.session_state.chat_state = SessionState(system_message)
if "completion_executor" not in st.session_state:
    st.session_state.completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
        stream=False
    )
if "summary_executor" not in st.session_state:
    st.session_state.summary_executor = SummaryExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=SUMMARY_REQUEST_ID,
        test_app_id=SUMMARY_APP_ID,
        host='clovastudio.apigw.ntruss.com',
    )
if "sliding_window_executor" not in st.session_state:
    st.session_state.sliding_window_executor = SlidingWindowExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=SLIDING_WINDOW_REQUEST_ID,
    )

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("처음으로"):
        delete_session_state()
        st.rerun()
with col2:
    if st.button("전화상담"):
        st.toast("1588-6800\n\n평일 08:00 ~ 18:00 (토, 일요일 및 공휴일 제외)", icon="📞")
with col3:
    st.button("채팅이력")
with col4:
    if st.button("요약하기"):
        if not st.session_state.chat_state.chat_log.messages:
            st.toast("대화가 없습니다.")
        else:
            texts = st.session_state.chat_state.chat_log.to_list()
            summary_request = SummaryRequestData(texts=texts).to_dict()
            summary_response = st.session_state.summary_executor.execute(summary_request)
            st.toast("[대화 요약]\n\n" + summary_response)
            
    
st.markdown("---")

# 채팅 히스토리 표시
for message in st.session_state.messages:
    write_message(message)


# 채팅이 시작되지 않았을 때만 옵션 버튼 표시
# TODO: 자주 묻는 질문에 대해서 적절한 답변 대응
if not st.session_state.chat_started:
    import json
    with open(faq_sample_data_path, "r", encoding="utf-8") as f:
        options = json.load(f)
    st.header("자주 묻는 질문")
    for option in options:
        if st.button(option["question"]):
            user_message = Message("user", option["question"], get_seoul_timestamp())
            st.session_state.messages.append(user_message)
            user_input = option["question"]
            assistant_message = Message(
                "assistant",
                option["answer"],
                get_seoul_timestamp()
            )
            st.session_state.messages.append(assistant_message)
            st.session_state.chat_state.title = option["question"]
            st.session_state.chat_state.chat_log.add_message("user", user_input)
            st.session_state.chat_state.chat_log.add_message("assistant", option["answer"])
            st.session_state.chat_started = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    init_assistant_message = Message(
        role="assistant",
        content="안녕하세요. 미래에셋증권 고객상담 챗봇 m.Talk입니다. 무엇을 도와드릴까요?",
        timestamp=get_seoul_timestamp()
    )
    write_message(init_assistant_message)

# 사용자 입력 처리
user_input = st.chat_input("텍스트를 입력해주세요")
if user_input:
    # 종료 명령어 처리 <- 나중에 버튼으로 대체
    if user_input in ["종료", "그만", "rmaks", "whdfy"]:
        delete_session_state()
        st.stop()
    user_message = Message("user", user_input, get_seoul_timestamp())
    st.session_state.messages.append(user_message)
    st.session_state.chat_state.chat_log.add_message("user", user_input)
    write_message(user_message)

    # 임시 메시지 표시
    with st.status("필요한 자료를 검색 중입니다.") as status:
        generated_questions = generate_questions(
            user_input=user_input,
            previous_user_inputs=st.session_state.chat_state.previous_user_inputs
        )
        st.session_state.chat_state.previous_user_inputs.add_message("user", user_input)
        
        retrieved_documents = retrieve_documents(user_input)
        documents_info = extract_from_documents(retrieved_documents)
        
        if isinstance(generated_questions, list):
            for question in generated_questions:
                retrieved_documents = retrieve_documents(question)
                documents_info += extract_from_documents(retrieved_documents)
        elif isinstance(generated_questions, str):
            retrieved_documents = retrieve_documents(generated_questions)
            documents_info += extract_from_documents(retrieved_documents)
        
        voted_document = get_most_frequent_document(documents_info)
        voted_answer = voted_document["answer"]
        
        status.update(label="적절한 답변을 준비하고 있습니다.", state="running")
        # 시스템 메시지에 답변 추가
        system_message_with_reference = Prompts.from_message("system", st.session_state.system_message + voted_answer)
        chat_log = system_message_with_reference + st.session_state.chat_state.chat_log
        
        # 슬라이딩 윈도우로 대화가 길어져도 맥락 유지하기
        sliding_window_request = SlidingWindowRequestData(messages=chat_log.to_dict()).to_dict()
        sliding_window_response = st.session_state.sliding_window_executor.execute(sliding_window_request)
        adjusted_messages = sliding_window_response["result"]["messages"]
        
        # 사용자 입력을 Clova Studio로 전송
        completion_request = RequestData(messages=adjusted_messages).to_dict()
        completion_response = st.session_state.completion_executor.invoke(completion_request)
        
        st.session_state.chat_state.total_tokens += completion_response["result"]["outputLength"]
        st.session_state.chat_state.chat_tokens += completion_response["result"]["outputLength"]
        
        # Clova Studio의 응답을 파싱하여 시스템 응답, 이를 chat_log에 추가
        st.session_state.chat_state.last_response = completion_response["result"]["message"]["content"]
        st.session_state.chat_state.chat_log.add_message("assistant", st.session_state.chat_state.last_response)

        # 프로세스 완료
        status.update(label="아래의 답변을 참고해주세요.", state="complete")

    response = st.session_state.chat_state.last_response
    assistant_message = Message("assistant", response, get_seoul_timestamp())
    st.session_state.messages.append(assistant_message)
    write_message(assistant_message)
    
    if not st.session_state.chat_started:
        st.session_state.chat_started = True
        if user_input:
            st.session_state.chat_state.title = user_input
        else:
            st.session_state.chat_state.title = st.session_state.chat_state.created_at
        save_log(st.session_state.chat_state, path)
        st.rerun()
    save_log(st.session_state.chat_state, path)
