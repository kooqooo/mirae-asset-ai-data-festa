from collections import Counter
from typing import List, Tuple, Dict

from langchain_core.documents.base import Document
from tqdm import tqdm

from src.session_state import SessionState
from question_generator import generate_questions
from retrieval import retrieve_documents, extract_from_documents, retrieve_answer


def get_lowest_score_document(documents_with_scores: List[Dict]) -> Document:
    document = None
    max_score = float("inf")
    for doc in documents_with_scores:
        if doc["score"] < max_score:
            document = doc
            max_score = doc["score"]
    return document

def get_most_frequent_document(documents_with_scores: List[Dict]) -> Document:
    document = None
    counter = Counter([doc["ids"] for doc in documents_with_scores])
    max_count = max(counter.values())
    min_score = float("inf")
    for doc in documents_with_scores:
        if counter[doc["ids"]] == max_count:
            score = sum([d["score"] for d in documents_with_scores if d["ids"] == doc["ids"]])
            if score < min_score:
                document = doc
                min_score = score
    return document, counter, min_score
    

if __name__ == "__main__":
    
    session_state = SessionState("system_message")
    
    user_input = "해외 주식 거래 어떻게 해?"
    generated_questions = generate_questions(
        user_input=user_input,
        previous_user_inputs=session_state.previous_user_inputs
    )
    
    retrieved_answer = retrieve_answer(user_input)
    retrieved_documents = retrieve_documents(user_input)

    documents_info = extract_from_documents(retrieved_documents)
    print("="*80)
    print("Question:", user_input)
    print(documents_info)
    
    if isinstance(generated_questions, list):
        for question in tqdm(generated_questions):
            retrieved_documents = retrieve_documents(question)
            documents_info += extract_from_documents(retrieved_documents)
            print("="*80)
            print("Question:", question)
            for doc in retrieved_documents:
                print(doc)
                print()
    elif isinstance(generated_questions, str):
        retrieved_documents = retrieve_documents(generated_questions)
        documents_info += extract_from_documents(retrieved_documents)
    
    print("=== get_lowest_score_document ===")
    document = get_lowest_score_document(documents_info)
    print(document)
    
    print("=== get_most_frequent_document ===")
    document = get_most_frequent_document(documents_info)
    print(document)