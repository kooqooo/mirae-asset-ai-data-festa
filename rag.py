import os
from typing import Optional

from dotenv import load_dotenv

from src.clova_completion_executor import CompletionExecutor
from src.prompt_template import Prompts
from src.request_data import RequestData
from retrieval import retrieve_answer, retrieve_answers

load_dotenv(override=True)
API_KEY = os.getenv("API_KEY")
API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
REQUEST_ID = os.getenv("REQUEST_ID")
TEST_APP_ID = os.getenv("TEST_APP_ID")


def append_reference_to_system_prompt(query: str) -> Prompts:
    reference = retrieve_answer(query)
    # 이 부분에 reference가 너무 긴 경우 처리하는 프로세스가 필요함
    # 적절한 토큰 수 사용
    system_prompt_with_reference = f"{system_prompt_text}\nreference: {reference}"
    system_prompt = Prompts.from_message("system", system_prompt_with_reference)
    return system_prompt

def rag_executor(
        query: str,
        previous_prompts: Optional[Prompts] = None,
    ) -> str:
    system_prompt = append_reference_to_system_prompt(query)
    query_prompts = Prompts.from_message("user", query)

    if previous_prompts is not None:
        prompts = system_prompt + previous_prompts + query_prompts
    else:
        prompts = system_prompt + query_prompts

    # 적절한 토큰 수 사용이 필요함
    request_data = RequestData(messages=prompts.to_dict(), maxTokens=1000).to_dict()
    answer = completion_executor.execute(request_data)

    return answer

if __name__ == "__main__":
    completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )

    with open("data/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt_text = f.read()
        
    print(rag_executor("계좌 개설 방법 알려줘"))