import os

from dotenv import load_dotenv
from langchain_community.embeddings import ClovaEmbeddings


load_dotenv(override=True)
CLOVA_EMB_API_KEY = os.getenv("CLOVA_EMB_API_KEY")
CLOVA_EMB_APIGW_API_KEY = os.getenv("CLOVA_EMB_APIGW_API_KEY")
# REQUEST_ID = os.getenv("REQUEST_ID_EMBEDDING")
CLOVA_EMB_APP_ID = os.getenv("CLOVA_EMB_APP_ID")

embeddings = ClovaEmbeddings()

document_text = ["This is a test doc1.", "This is a test doc2."]
document_result = embeddings.embed_documents(document_text)

print(f"몇 개의 문서가 있는가? -> {len(document_text)}")
print(f"임베딩 결과를 가지는 리스트에는 몇개의 임베딩이 있는가? -> {len(document_result)}")
print(f"각 임베딩 벡터의 길이는? -> {len(document_result[0])}")
