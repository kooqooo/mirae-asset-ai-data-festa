# -*- coding: utf-8 -*-
import base64
import json
import http.client


from clovastudio_executor import CLOVAStudioExecutor
from request_data import SegmentationRequestData


class CompletionExecutor(CLOVAStudioExecutor):
    def __init__(self, api_key, api_key_primary_val, request_id, test_app_id, host):
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host)
        self._end_point = "segmentation"

    def _send_request(self, completion_request):
        conn = http.client.HTTPSConnection(self._host)
        conn.request(
            "POST",
            f"/testapp/v1/api-tools/{self._end_point}/{self._test_app_id}",
            json.dumps(completion_request),
            self._headers,
        )
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding="utf-8"))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        print(res)
        if res["status"]["code"] == "20000":
            return res["result"]["topicSeg"]
        else:
            return "Error"


if __name__ == "__main__":
    import os

    from dotenv import load_dotenv

    load_dotenv(override=True)

    API_KEY = os.getenv("API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("SEG_REQUEST_ID")
    TEST_APP_ID = os.getenv("SEG_TEST_APP_ID")
    print(TEST_APP_ID)

    completion_executor = CompletionExecutor(
        host="clovastudio.apigw.ntruss.com",
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
    )

    request_data = SegmentationRequestData(text=["input text", "input text2"]).to_dict()
    response_text = completion_executor.execute(request_data)
    print(response_text)