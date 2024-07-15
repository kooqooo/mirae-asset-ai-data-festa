from ast import literal_eval
import json
import requests
from http import HTTPStatus

from request_data import RequestData  # src/request_data.py
from clovastudio_executor import CLOVAStudioExecutor  # src/clovastudio_executor.py


class CompletionExecutor(CLOVAStudioExecutor):
    def __init__(
        self,
        api_key,
        api_key_primary_val,
        request_id,
        test_app_id="HCX-DASH-001",
        host="https://clovastudio.stream.ntruss.com",
        stream=True,
    ) -> None:
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host)
        self._test_app_id = test_app_id
        self._stream = stream
        self._headers["Accept"] = "text/event-stream" if self._stream else "application/json"
        self._end_point = "chat-completions"

    def _send_request(self, completion_request, stream=True):
        return requests.post(
            f"{self._host}/testapp/v1/{self._end_point}/{self._test_app_id}",
            headers=self._headers,
            json=completion_request,
            stream=stream,
        )

    def request(self, completion_request, stream=True):
        return self._send_request(completion_request, stream=stream)

    def execute(self, completion_request, stream=True):
        # 길이가 가장 긴 문장을 반환, 테스트 결과 가장 빠른 속도를 보여서 채택
        final_answer = ""

        with self.request(completion_request) as r:
            if stream:
                longest_line = ""
                for line in r.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        if decoded_line.startswith("data:"):
                            event_data = json.loads(decoded_line[len("data:") :])
                            message_content = event_data.get("message", {}).get("content", "")
                            if len(message_content) > len(longest_line):
                                longest_line = message_content
                final_answer = longest_line
            elif not stream:
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

    def execute_all(self, completion_request, stream=True):
        # 모든 응답을 반환, 스트림 출력 지원
        # parse_stream_response() 또는 parse_non_stream_response()를 사용하여 content 부분만 추출이 필요
        with self.request(completion_request) as r:
            if stream:
                if r.status_code == HTTPStatus.OK:
                    response_data = ""
                    for line in r.iter_lines():
                        if line:
                            decoded_line = line.decode("utf-8")
                            # 실시간 출력 부분
                            if decoded_line.startswith("data:"):
                                data = json.loads(line[5:])
                                if "message" in data and "content" in data["message"]:
                                    print(data["message"]["content"], end="", flush=True)
                            response_data += decoded_line + "\n"
                    return response_data
                else:
                    print(f"오류 발생: HTTP {r.status_code}, 메시지: {r.text}")
                    # raise ValueError(f"오류 발생: HTTP {r.status_code}, 메시지: {r.text}")
            else:
                if r.status_code == HTTPStatus.OK:
                    return r.json()
                else:
                    print(f"오류 발생: HTTP {r.status_code}, 메시지: {r.text}")
                    # raise ValueError(f"오류 발생: HTTP {r.status_code}, 메시지: {r.text}")


def parse_response(response: str | dict) -> str:
    """
    실제 message의 content를 반환합니다.
    """
    if isinstance(response, str):
        response = literal_eval(response[5:])  # "data:" 제거
    return response["message"]["content"].replace("\\n", "\n")


# 스트리밍 응답에서 content 부분만 추출
def parse_stream_response(response):
    """
    stream=True로 설정한 execute_all()에서 사용합니다.
    """
    content_parts = []
    for line in response.splitlines():
        if line.startswith("data:"):
            data = json.loads(line[5:])
            if "message" in data and "content" in data["message"]:
                content_parts.append(data["message"]["content"])
    content = content_parts[-1] if content_parts else ""
    return content.strip()


# 논스트리밍 응답에서 content 부분만 추출
def parse_non_stream_response(response: str | dict) -> str:
    """
    stream=False로 설정한 execute_all()에서 사용합니다.
    """
    if isinstance(response, str):
        response = literal_eval(response)
    result = response.get("result", {})
    message = result.get("message", {})
    content = message.get("content", "")
    return content.strip()


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
        {"role": "user", "content": "경기도 용인시 기흥구 보정동 근처 맛집 추천해줘"},  # <- 맛없는 거 추천해줌
    ]

    request_data = RequestData(messages=preset_text).to_dict()

    completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )

    print("execute(), stream=True")
    response = completion_executor.execute(request_data)
    print(response)

    print()
    print("execute_all(), stream=True")
    response = completion_executor.execute_all(request_data)
    print(parse_stream_response(response))

    non_stream_completion_executor = CompletionExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
        stream=False,
    )
    print()
    print("execute_all(), stream=False")
    response = non_stream_completion_executor.execute_all(request_data, stream=False)
    print(parse_non_stream_response(response))
