from ast import literal_eval
import json
import requests
from timeit import timeit

class CompletionExecutor:
    def __init__(
        self,
        api_key,
        api_key_primary_val,
        request_id,
        test_app_id,
        host="https://clovastudio.stream.ntruss.com"
    ) -> None:
        self.__host = host
        self.__api_key = api_key
        self.__api_key_primary_val = api_key_primary_val
        self.__request_id = request_id
        self.__test_app_id = test_app_id
        self.__headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self.__api_key,
            "X-NCP-APIGW-API-KEY": self.__api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.__request_id, # 없어도 작동 가능
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream",
        }

    def _post_request(self, completion_request, stream=False):
        return requests.post(
            f"{self.__host}/testapp/v1/chat-completions/{self.__test_app_id}",
            headers=self.__headers,
            json=completion_request,
            stream=stream,
        )

    def request(self, completion_request, stream=True):
        return self._post_request(completion_request, stream=stream)
    
    def execute(self, completion_request, response_type="stream"):
        # 길이가 가장 긴 문장을 반환, 테스트 결과 가장 빠른 속도를 보여서 채택
        final_answer = ""
 
        with self.request(completion_request) as r:
            if response_type == "stream":
                longest_line = ""
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            event_data = json.loads(decoded_line[len("data:"):])
                            message_content = event_data.get("message", {}).get("content", "")
                            if len(message_content) > len(longest_line):
                                longest_line = message_content
                final_answer = longest_line
            elif response_type == "single":
                final_answer = r.json()  # 가정: 단일 응답이 JSON 형태로 반환됨
        return final_answer
    
    def execute_pre_done(self, completion_request):
        # [DONE]이 나오기 이전의 문장을 반환
        response = self.request(completion_request)
 
        # 스트림에서 마지막 'data:' 라인을 찾기 위한 로직
        last_data_content = ""
 
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                if '"data":"[DONE]"' in decoded_line:
                    break
                if decoded_line.startswith("data:"):
                    last_data_content = json.loads(decoded_line[5:])["message"]["content"]
 
        return last_data_content

def parse_response(response: str) -> str:
    """
    실제 message의 content를 반환합니다.
    """
    response_dict = literal_eval(response[5:])  # "data:" 제거
    return response_dict["message"]["content"].replace("\\n", "\n")


class RequestData:
    """
    API 요청을 위한 데이터 클래스입니다.
    
    Args:
        messages: 프롬프트나 이전 대화 내용
        temperature (float): 생성 토큰에 대한 다양성 정도(설정값이 높을수록 다양한 문장 생성), 0.00 < temperature <= 1 (기본값: 0.50)
        topP (float): 생성 토큰 후보군을 누적 확률을 기반으로 샘플링, 0 < topP <= 1 (기본값: 0.8)
        topK (int): 생성 토큰 후보군에서 확률이 높은 k개를 후보로 지정하여 샘플링, 0 <= topK <= 128 (기본값: 0)
        repeatPenalty (float): 같은 토큰을 생성하는 것에 대한 패널티 정도(설정값이 높을수록 같은 결괏값을 반복 생성할 확률 감소), 0 < repeatPenalty <= 10 (기본값: 5.0)
        maxTokens (int): 생성 토큰 후보군에서 확률이 높은 k개를 후보로 지정하여 샘플링
        stopBefore (list[str]): 토큰 생성 중단 문자, (기본값: [])
        includeAiFilters (bool): 생성된 결괏값에 대해 욕설, 비하/차별/혐오, 성희롱 /음란 등 카테고리별로 해당하는 정도, (기본값: True)
        seed (int): 0일 때 일관성 수준이 랜덤 적용 (기본값: 0), 사용자 지정 seed 범위: 1 <= seed <= 4294967295
    """
    def __init__(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        topP: float = 0.8,
        topK: int = 0,
        maxTokens: int = 256,
        repeatPenalty: float = 5.0,
        stopBefore: list[str] = [],
        includeAiFilters: bool = True,
        seed: int = 0
    ) -> None:
        self.messages = messages
        self.topP = topP
        self.topK = topK
        self.maxTokens = maxTokens
        self.temperature = temperature
        self.repeatPenalty = repeatPenalty
        self.stopBefore = stopBefore
        self.includeAiFilters = includeAiFilters
        self.seed = seed


    def to_dict(self) -> dict:
        return {
            "messages": self.messages,
            "topP": self.topP,
            "topK": self.topK,
            "maxTokens": self.maxTokens,
            "temperature": self.temperature,
            "repeatPenalty": self.repeatPenalty,
            "stopBefore": self.stopBefore,
            "includeAiFilters": self.includeAiFilters,
            "seed": self.seed,
        }


if __name__ == "__main__":
    import os
    
    from dotenv import load_dotenv
    
    load_dotenv(override=True)
    API_KEY = os.getenv("API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("REQUEST_ID")
    TEST_APP_ID = os.getenv("TEST_APP_ID")

    preset_text = [
        {"role": "system", "content": "사용자의 질문에 답변합니다."},
        {"role": "user", "content": "경기도 용인시 기흥구 보정동 근처 맛집 추천해줘"}, # <- 맛없는 거 추천해줌
    ]

    request_data = RequestData(messages=preset_text).to_dict()

    completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )
    
    response = completion_executor.execute(request_data)
    print(response)