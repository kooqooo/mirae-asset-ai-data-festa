import streamlit as st
from PIL import Image
import datetime

from config import *
from src.clova_completion_executor import CompletionExecutor
from src.clova_summary_executor import SummaryExecutor
from src.clova_sliding_window_executor import SlidingWindowExecutor
from src.prompt_template import Prompts
from src.request_data import RequestData, SlidingWindowRequestData, SummaryRequestData
from src.session_state import SessionState
from utils.seoul_time import get_seoul_timestamp
from utils.streamlit_utils import Message, write_message, delete_session_state
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


# 채팅 히스토리 표시
for message in st.session_state.messages:
    write_message(message)


# 채팅이 시작되지 않았을 때만 옵션 버튼 표시
# TODO: 자주 묻는 질문에 대해서 적절한 답변 대응
if not st.session_state.chat_started:
    options = [
        "신규 상장종목 거래방법 안내",
        "개인 투자용 국채 안내",
        "보안매체 발급",
        "계좌비밀번호 재등록 안내",
        "IRP(퇴직연금) 계좌개설",
        "개인연금계약이전 안내",
    ]
    for option in options:
        if st.button(option):
            user_message = Message("user", option, get_seoul_timestamp())
            st.session_state.messages.append(user_message)
            
            assistant_message = Message(
                "assistant",
                f"{option}에 대해 안내해 드리겠습니다. 어떤 점이 궁금하신가요?",
                get_seoul_timestamp()
            )
            st.session_state.messages.append(assistant_message)
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
    write_message(user_message)

    response = f"'{user_input}'에 대한 답변입니다. 추가 질문이 있으시면 말씀해 주세요."
    assistant_message = Message("assistant", response, get_seoul_timestamp())
    st.session_state.messages.append(assistant_message)
    write_message(assistant_message)
    
    if not st.session_state.chat_started:
        st.session_state.chat_started = True
        st.rerun()

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("처음으로"):
        delete_session_state()
        st.rerun()
with col2:
    st.button("전화상담")
with col3:
    st.button("1:1 문의")
with col4:
    st.button("채팅이력")
with col5:
    st.button("요약하기")