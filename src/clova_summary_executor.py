import json
import http.client

try:
    from clovastudio_executor import CLOVAStudioExecutor
except:
    from src.clovastudio_executor import CLOVAStudioExecutor

class SummaryExecutor(CLOVAStudioExecutor):
    def __init__(self, api_key, api_key_primary_val, request_id, test_app_id, host='clovastudio.apigw.ntruss.com'):
        super().__init__(api_key, api_key_primary_val, request_id, test_app_id, host=host)
        self._end_point = '/testapp/v1/api-tools/summarization/v2'

    def _send_request(self, completion_request):
        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', f'{self._end_point}/{self._test_app_id}', json.dumps(completion_request), self._headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']['text']
        else:
            print(res["status"]["message"])
            return 'Error'


if __name__ == '__main__':
    import os
    
    from dotenv import load_dotenv
    
    from request_data import SummaryRequestData
    
    load_dotenv(override=True)
    API_KEY = os.getenv("KOOQOOO_API_KEY")
    API_KEY_PRIMARY_VAL = os.getenv("KOOQOOO_API_KEY_PRIMARY_VAL")
    REQUEST_ID = os.getenv("KOOQOOO_SUMMARY_REQUEST_ID")
    TEST_APP_ID = os.getenv("KOOQOOO_SUMMARY_APP_ID")
        
    
    summary_executor = SummaryExecutor(
        api_key=API_KEY,
        api_key_primary_val = API_KEY_PRIMARY_VAL,
        request_id=REQUEST_ID,
        test_app_id=TEST_APP_ID,
        host='clovastudio.apigw.ntruss.com',
    )

    texts = ["input text1", "input text2"]
    request_data = SummaryRequestData(texts=texts).to_dict()
    response_text = summary_executor.execute(request_data)
    
    print(request_data)
    print(response_text)