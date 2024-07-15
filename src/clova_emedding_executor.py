# -*- coding: utf-8 -*-
import base64
import json
import http.client

from clovastudio_executor import CLOVAStudioExecutor


class EmbeddingExecutor(CLOVAStudioExecutor):
    def __init__(
        self,
        api_key,
        api_key_primary_val,
        request_id,
        test_app_id,
        host="https://clovastudio.apigw.ntruss.com",
    ) -> None:
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host)
        self._test_app_id = test_app_id
        self._end_point = "embedding"

    def _send_request(self, completion_request):
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-NCP-CLOVASTUDIO-API-KEY": self._api_key,
            "X-NCP-APIGW-API-KEY": self._api_key_primary_val,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self._request_id,
        }
        conn = http.client.HTTPSConnection(self._host)
        conn.request(
            "POST",
            f"/testapp/v1/api-tools/{self._end_point}/clir-emb-dolphin/{self._test_app_id}",
            json.dumps(completion_request),
            headers,
        )
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding="utf-8"))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res["status"]["code"] == "20000":
            return res["result"]["embedding"]
        else:
            return "Error"


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv(override=True)

    API_KEY = os.getenv("API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("REQUEST_ID_EMBEDDING")
    TEST_APP_ID = os.getenv("TEST_APP_ID_EMBEDDING")

    embedding_executor = EmbeddingExecutor(
        host="clovastudio.apigw.ntruss.com",  # 현재 상태에서 https 붙이면 에러 발생
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )
    request_data = json.loads(
        """{
  "text" : "input text"
}""",
        strict=False,
    )
    response_text = embedding_executor.execute(request_data)
    print(request_data)
    print(len(response_text))
