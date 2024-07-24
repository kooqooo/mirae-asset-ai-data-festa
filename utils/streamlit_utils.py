import streamlit as st

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
