import json
import http.client
import requests
 
try:
    from clovastudio_executor import CLOVAStudioExecutor
except:
    from src.clovastudio_executor import CLOVAStudioExecutor


class SlidingWindowExecutor(CLOVAStudioExecutor):
    def __init__(self, api_key, api_key_primary_val, request_id, test_app_id='HCX-DASH-001', host='https://clovastudio.apigw.ntruss.com'):
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host)
        self._end_point = 'sliding/chat-messages'
        self._test_app_id = test_app_id
        
    def execute(self, completion_request):
        response = requests.post(
            f"{self._host}/v1/api-tools/{self._end_point}/{self._test_app_id}",
            headers=self._headers,
            json=completion_request,
        )

        if response.status_code == 200:
            return response.json()
        else:
            error_message = (
                f"status : {response.status_code}, message : {response.text}"
                if isinstance(response.json(), dict)
                else "Unknown error"
            )
            raise ValueError(f"오류 발생: HTTP {response.status_code}\n메시지: {error_message}")
        
if __name__ == "__main__":
    import os
    
    from dotenv import load_dotenv
    
    from prompt_template import Prompts
    from request_data import SlidingWindowRequestData
    load_dotenv(override=True)
    
    API_KEY = os.getenv('KOOQOOO_API_KEY') # 키 수정 필요
    API_KEY_PRIMARY_VAL = os.getenv('KOOQOOO_API_KEY_PRIMARY_VAL')
    REQUEST_ID = os.getenv('KOOQOOO_SLI_WIN_REQUEST_ID')
    TEST_APP_ID = os.getenv('TEST_APP_ID')
    
    
    sliding_window_executor = SlidingWindowExecutor(API_KEY, API_KEY_PRIMARY_VAL, REQUEST_ID)
    
    preset_text = [
        ["system", "사용자의 질문에 답변합니다."],
        ["user", "경기도 용인시 기흥구 보정동 근처 맛집 추천해줘"]
    ]
    
    prompts = Prompts.from_messages(preset_text).to_dict()
    request_data = SlidingWindowRequestData(messages=prompts).to_dict()
    print(request_data)
    print(sliding_window_executor.execute(request_data))