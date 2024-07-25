import os
import json
from datetime import datetime

import streamlit as st
from src.session_state import SessionState
from utils.seoul_time import convert_for_file_name

class Message():
    def __init__(self, role: str, content: str, timestamp: str):
        self.role = role
        self.content = content
        self.timestamp = timestamp
        
    def __repr__(self):
        return f"{self.role = }\n{self.content = }\n{self.timestamp}"
    
    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }
        
def write_message(message: Message):
    with st.chat_message(message.role):
        col1, col2 = st.columns([0.9, 0.1])
        with col1:
            st.write(message.content)
        with col2:
            st.write(message.timestamp)

def delete_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]

def save_log(session_state: SessionState, path: str):
    logs_path = os.path.join(path, "logs")
    
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)
    
    log_file_path = os.path.join(logs_path, f"{convert_for_file_name(session_state.created_at)}.json")
    
    # 로그 파일 저장
    with open(log_file_path, "w", encoding="utf-8") as f:
        json.dump(session_state.to_dict(), f, ensure_ascii=False, indent=4)