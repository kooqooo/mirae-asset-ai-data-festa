# -*- coding: utf-8 -*-

import base64
import json
import http.client

try:
    from clovastudio_executor import CLOVAStudioExecutor  # src/clovastudio_executor.py
except:
    from src.clovastudio_executor import CLOVAStudioExecutor # 상위 디렉토리에서 실행 시

class TokenCalculationExecutor(CLOVAStudioExecutor):
    def __init__(
        self,
        api_key,
        api_key_primary_val,
        request_id,
        test_app_id="HCX-DASH-001",
        host="clovastudio.apigw.ntruss.com",
    ):
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host)
        
    def _send_request(self, completion_request):
        
        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', f'/v1/api-tools/chat-tokenize/{self._test_app_id}', json.dumps(completion_request), self._headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['messages']
        else:
            return 'Error'

    def get_total_tokens(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            total_token = 0
            messages = res['result']['messages']
            for message in messages:
                total_token += message['count']
            return total_token
        else:
            return 'Error'

if __name__ == '__main__':
    import os
    
    from dotenv import load_dotenv
    
    from prompt_template import Prompts
    
    load_dotenv(override=True)
    
    API_KEY = os.getenv("API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("REQUEST_ID")
    TEST_APP_ID = os.getenv("TEST_APP_ID")
    
    token_executor = TokenCalculationExecutor(
        api_key=API_KEY,
        api_key_primary_val=API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        host='clovastudio.apigw.ntruss.com',
    )

    preset_text = [
        ["system", "사용자의 질문에 답변합니다."],
        ["user", "경기도 용인시 기흥구 보정동 근처 맛집 추천해줘"]
    ]
    prompts = Prompts.from_messages(preset_text).to_dict()
    request_data = {"messages": prompts}
    # print(request_data)
    
    response_text = token_executor.execute(request_data)
    print(response_text)
    
    print(token_executor.get_total_tokens(request_data))
