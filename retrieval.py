"""
30회 반복 테스트 결과
(Query embedding 시간 포함)

ChromaDB 평균 소요 시간: 0.161336 sec
FAISS 평균 소요 시간:    0.137077 sec
"""
__import__("pysqlite3")
import os
from typing import List, Tuple

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma, FAISS, VectorStore
from langchain_community.embeddings import ClovaEmbeddings
from langchain.schema.document import Document

# from src.custom_langchain_clova_embedding import ClovaEmbeddings # Error: 42901 해결용

PATH = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(PATH, 'data')
prompt_path = os.path.join(data_path, 'system_prompt.txt')
chroma_path = os.path.join(data_path, 'chroma_db')
faiss_path = os.path.join(data_path, 'faiss_index')

load_dotenv(override=True)
embeddings = ClovaEmbeddings()

chroma = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
faiss = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

def retrieve_answer(query: str, vectorstore: VectorStore = faiss) -> str:
    result = vectorstore.similarity_search_with_score(query, k=1)
    return result[0][0].metadata["answer"]

def retrieve_answers(query: str, vectorstore: VectorStore = faiss, k: int = 4) -> list:
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [result[0].metadata["answer"] for result in results]

def retrieve_documents(query: str, vectorstore: VectorStore = faiss, k: int = 4) -> list:
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results

def extract_from_document(document: Tuple[Document, float]) -> str:
    return {
        "ids": document[0].metadata["ids"],
        "question": document[0].page_content,
        "answer": document[0].metadata["answer"],
        "score": document[1]
    }

def extract_from_documents(documents: list) -> list:
    return [extract_from_document(document) for document in documents]

if __name__ == "__main__":
    
    def print_answers(answers: list):
        for idx, answer in enumerate(answers):
            print()
            print(idx+1)
            print(answer)

    def print_documents(documents: List[tuple[Document, float]]):
        from pprint import pprint
        pprint(extract_from_documents(documents))
    
    query = "IRP에 대해서 알려줘"
    
    print(f"사용자의 질문: {query}")
    print()
    print("="*40, "ChromaDB", "="*40)
    answer = retrieve_answer(query, chroma)
    print(answer)
    
    answers = retrieve_answers(query, chroma)
    print_answers(answers)
    
    print("\n")
    print("="*40, "FAISS", "="*40)
    answer = retrieve_answer(query, faiss)
    print(answer)
    
    answers = retrieve_answers(query, faiss)
    print_answers(answers)

    print("\n")
    print("="*40, "Documents", "="*40)
    retrieved_documents = retrieve_documents(query, faiss)
    print_documents(retrieved_documents)
    
    
    # # Compare the average time taken to retrieve an answer from ChromaDB and FAISS
    # from time import time, sleep
    # from tqdm import tqdm
    
    # n = 30
    
    # chroma_time = 0
    # for _ in tqdm(range(n)):
    #     start = time()
    #     retrieve_answer(query, chroma)
    #     end = time()
    #     chroma_time += end - start
    #     sleep(1)    # Sleep for 1 second to avoid rate limiting
    # faiss_time = 0
    
    # for _ in tqdm(range(n)):
    #     start = time()
    #     retrieve_answer(query, faiss)
    #     end = time()
    #     faiss_time += end - start
    #     sleep(1)    # Sleep for 1 second to avoid rate limiting
    
    # average_chroma_time = chroma_time / n
    # average_faiss_time = faiss_time / n
    
    # print(f"ChromaDB 평균 소요 시간: {average_chroma_time:.6f} sec")
    # print(f"FAISS 평균 소요 시간: {average_faiss_time:.6f} sec")