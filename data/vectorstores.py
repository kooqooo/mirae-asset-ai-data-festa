import json
import os

from langchain.schema.document import Document


PATH = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(PATH, "faq_data.json")

with open(json_path, "r", encoding="utf-8") as f:
    faq = json.load(f)

documents = [
    Document(
        page_content=document["question"],
        metadata={
            "ids": idx,
            "category": document["category"],
            "answer": document["answer"],
        },
    )
    for idx, document in enumerate(faq)
]


if __name__ == "__main__":

    def _print(docs: list[Document]):
        for idx, doc in enumerate(docs):
            score = None
            this = "->" if idx == 0 else "  "
            if type(doc) == tuple:
                doc, score = doc
            print(f"{this} content : {doc.page_content}")
            print(f"{this} metadata : {doc.metadata}") if doc.metadata else None
            print(f"{this} score : {score}") if score is not None else None
            print()
        print()

    from time import time, sleep
    from dotenv import load_dotenv
    from chromadb import Client
    from chromadb.config import Settings

    # from langchain_community.embeddings import ClovaEmbeddings
    from langchain_community.vectorstores import Chroma, FAISS
    from tqdm import tqdm

    from src.custom_langchain_clova_embedding import ClovaEmbeddings

    load_dotenv(override=True)
    CLOVA_EMB_API_KEY = os.getenv("CLOVA_EMB_API_KEY")
    CLOVA_EMB_APIGW_API_KEY = os.getenv("CLOVA_EMB_APIGW_API_KEY")
    # REQUEST_ID = os.getenv("REQUEST_ID_EMBEDDING")
    CLOVA_EMB_APP_ID = os.getenv("CLOVA_EMB_APP_ID")

    embeddings = ClovaEmbeddings()

    query = "계좌 비밀번호를 알아내는 방법은 무엇인가요?"
    query_vector = embeddings.embed_query(query)

    # # Chroma 저장용 설정
    # chroma = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=os.path.join(PATH, "chroma_db"))
    
    # Chroma 저장 안하는 방법
    chroma = Chroma.from_documents(documents=documents, embedding=embeddings)

    start = time()
    print(f"{type(chroma.embeddings) = }")
    chroma_similarity_search_with_score = chroma.similarity_search_with_score(query)
    chroma_similarity_search_with_relevance_scores = (
        chroma.similarity_search_with_relevance_scores(query)
    )
    end = time()
    print(f"Chroma: {end - start:.6f} sec")

    print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    _print(chroma_similarity_search_with_score)
    _print(chroma_similarity_search_with_relevance_scores)

    FAISS_INDEX_PATH = os.path.join(PATH, "faiss_index")
    faiss = FAISS.from_documents(documents=documents, embedding=embeddings)
    start = time()
    print(f"{type(faiss.embeddings) = }")

    faiss_similarity_search_with_score = faiss.similarity_search_with_score(query)
    faiss_similarity_search_with_relevance_scores = (
        faiss.similarity_search_with_relevance_scores(query)
    )
    end = time()
    print(f"FAISS: {end - start:.6f} sec")

    print(f"/** <{query}>와 유사도가 높은 답은 '->'로 표시 **/")
    _print(faiss_similarity_search_with_score)
    _print(faiss_similarity_search_with_relevance_scores)

    # faiss.save_local(FAISS_INDEX_PATH) # 저장 할 경우 이 코드 수행
