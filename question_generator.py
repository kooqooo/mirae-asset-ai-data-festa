import os
import re
from typing import List

from dotenv import load_dotenv

from src.clova_completion_executor import CompletionExecutor
from src.session_state import SessionState
from src.prompt_template import Prompts
from src.request_data import RequestData
from retrieval import data_path


with open(os.path.join(data_path, "generate_question_prompt.txt"), "r", encoding="utf-8") as f:
    generate_question_prompt = f.read()

load_dotenv(override=True)
API_KEY = os.getenv("API_KEY")
API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
REQUEST_ID = os.getenv("REQUEST_ID")
TEST_APP_ID = os.getenv("TEST_APP_ID")

question_generator = CompletionExecutor(
    api_key=API_KEY,
    api_key_primary_val=API_KEY_PRIMARY_VAL,
    request_id=REQUEST_ID,
    test_app_id=TEST_APP_ID,
    stream=False
)

def extract_questions(text: str) -> List[str] | str:
    questions = re.findall(r'^\d+\.\s+(.+)$', text, re.MULTILINE)
    
    return questions if questions else text.strip()

def generate_questions(user_input: str, previous_user_inputs: Prompts) -> List[str]:
    messages = Prompts.from_message("system", generate_question_prompt)
    messages += previous_user_inputs
    messages.add_message("user", user_input)
    print("question_generator.py: generate_questions: messages.to_dict()")
    print(messages.to_dict())
    request_data = RequestData(messages=messages.to_dict(), temperature=0.5).to_dict()
    response = question_generator.execute(completion_request=request_data)

    return extract_questions(response["result"]["message"]["content"])


if __name__ == "__main__":
    previous_user_inputs = Prompts.from_message("user", "공동인증서 발급/재발급 어떻게 해?")
    user_input = "유효기한이 얼마야?"
    
    quesetions = generate_questions(user_input, previous_user_inputs)
    print(quesetions)

    # Ouput:
    # 1. 공동인증서 유효기간은 얼마나 돼? 
    # 2. 공동인증서 재발급 시 유효기간 초기화돼?
    # 3. 공동인증서 갱신하면 유효기간 연장 가능해?