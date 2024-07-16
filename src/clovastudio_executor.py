import json
import requests


class CLOVAStudioExecutor:
    def __init__(
        self, api_key, api_key_primary_val, request_id, test_app_id, host="https://clovastudio.stream.ntruss.com"
    ) -> None:
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id
        self._test_app_id = test_app_id
        self._headers = {
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,  # 없어도 작동 가능
            "Content-Type": "application/json; charset=utf-8",
        }

    def _send_request(self, completion_request, endpoint):
        return requests.post(
            f"{self._host}/testapp/v1/{endpoint}/{self._test_app_id}",
            headers=self._headers,
            json=completion_request,
        )

    def execute(self, completion_request, endpoint):
        response = self._send_request(completion_request, endpoint)
        if response.status_code == 200:
            return response.json()
        else:
            error_message = (
                f"status : {response.status_code}, message : {response.text}"
                if isinstance(response.json(), dict)
                else "Unknown error"
            )
            raise ValueError(f"오류 발생: HTTP {response.status_code}\n메시지: {error_message}")
