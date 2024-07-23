import streamlit as st

from src.session_state import SessionState

stst = st.session_state

if "messages" not in stst:
    stst["messages"] = [{"role": "assistant", "content": "나는 말을 두 번 따라하는 앵무새 입니다."}]
    
if "chat_state" not in stst:
    stst["chat_state"] = SessionState("안녕하세요!")

chat_history = [
    {
        "title" : "Hello",
        "message" : "Hi, how can I help you today?",
    },
    {
        "title" : "Question",
        "message" : "How do I apply for a passport?",
    },
    {
        "title" : "Answer",
        "message" : "You can apply for a passport by visiting the nearest passport office.",
    },
]
tiles = [item["title"] for item in chat_history]

with st.sidebar:
    st.title("📚 NLP App")
    st.markdown("---")
    st.subheader("NLP Tasks")
    for title in tiles:
        if st.button(title):
            st.write([item["message"] for item in chat_history if item["title"] == title][0])

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by HyperCLOVA X")

for msg in stst.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if user_input := st.chat_input():
    stst.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    response = {"role": "assistant", "content": user_input + " " + user_input}
    stst.messages.append(response)
    st.chat_message(response["role"]).write(response["content"])
st.markdown("---")