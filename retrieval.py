"""
30회 반복 테스트 결과
(Query embedding 시간 포함)

ChromaDB 평균 소요 시간: 0.161336 sec
FAISS 평균 소요 시간:    0.137077 sec
"""

import os

from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma, FAISS, VectorStore
from langchain_community.embeddings import ClovaEmbeddings

# from src.clova_completion_executor import CompletionExecutor
from src.prompt_template import Prompts

PATH = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(PATH, 'data')
prompt_path = os.path.join(data_path, 'system_prompt.txt')
chroma_path = os.path.join(data_path, 'chroma_db')
faiss_path = os.path.join(data_path, 'faiss_index')

load_dotenv(override=True)
embeddings = ClovaEmbeddings()

chroma = Chroma(persist_directory=chroma_path, embedding_function=embeddings)
faiss = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)

def retrieve_answer(query: str, vectorstore: VectorStore) -> str:
    result = vectorstore.similarity_search_with_score(query, k=1)
    return result[0][0].metadata["answer"]

def retrieve_answers(query: str, vectorstore: VectorStore, k: int = 4) -> list:
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [result[0].metadata["answer"] for result in results]

if __name__ == "__main__":
    
    def print_answers(answers: list):
        for idx, answer in enumerate(answers):
            print()
            print(idx+1)
            print(answer)
    
    query = "계좌 개설 방법 알려줘"
    
    print("="*10, "ChromaDB", "="*10)
    answer = retrieve_answer(query, chroma)
    print(answer)
    
    answers = retrieve_answers(query, chroma)
    print_answers(answers)
    
    print("="*10, "FAISS", "="*10)
    answer = retrieve_answer(query, faiss)
    print(answer)
    
    answers = retrieve_answers(query, faiss)
    print_answers(answers)
    
    
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