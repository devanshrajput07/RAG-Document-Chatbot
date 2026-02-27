import os
import requests
from rank_bm25 import BM25Okapi

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

def perform_web_search(query: str, num_results: int = 5) -> list:
    if not SERPAPI_API_KEY:
        print("SERPAPI_API_KEY not found.")
        return []
    
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("organic_results", [])
        return [res.get("snippet", "") for res in results if "snippet" in res]
    except Exception as e:
        print(f"Error calling SerpAPI: {e}")
        return []

def web_agent(question: str) -> tuple:   
    search_results = perform_web_search(question)
    if not search_results:
        return "I could not find relevant information on the web.", 0.0

    tokenized_corpus = [doc.split(" ") for doc in search_results]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = question.split(" ")
    scores = bm25.get_scores(tokenized_query)
    
    best_idx = scores.argmax()
    best_snippet = search_results[best_idx]
    
    max_score = float(max(scores))
    confidence_score = min(max_score / 2.0, 0.95)
    
    answer = f"[Web Search Result]: {best_snippet}"
    return answer, round(confidence_score, 2)
