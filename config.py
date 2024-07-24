import os
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("KOOQOOO_API_KEY")
API_KEY_PRIMARY_VAL = os.getenv("KOOQOOO_API_KEY_PRIMARY_VAL")
REQUEST_ID = os.getenv("REQUEST_ID")
TEST_APP_ID = os.getenv("TEST_APP_ID")
SLIDING_WINDOW_REQUEST_ID = os.getenv("KOOQOOO_SLI_WIN_REQUEST_ID")
SUMMARY_APP_ID = os.getenv("KOOQOOO_SUMMARY_APP_ID")
SUMMARY_REQUEST_ID = os.getenv("KOOQOOO_SUMMARY_REQUEST_ID")


path = os.path.abspath(os.path.dirname(__file__))
prompt_path = os.path.join(path, "data", "system_prompt.txt")
chatbot_icon_path = os.path.join(path, "data", "chatbot_icon.png")
faq_sample_data_path = os.path.join(path, "data", "faq_sample_data.json")