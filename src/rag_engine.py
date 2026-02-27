import streamlit as st
import os
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

# Init Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY)

# Text Splitter
def get_text_chunks(raw_text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    return text_splitter.split_text(raw_text)

# Embeddings Cache
@st.cache_resource(show_spinner="Loading Embedding Model...")
def get_embeddings_model():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5", 
        model_kwargs={"device": "cpu"}
    )

def get_vectorstore(text_chunks):
    """Creates an in-memory ChromaDB vector store for the user session."""
    embeddings = get_embeddings_model()
    vectorstore = Chroma.from_texts(
        texts=text_chunks,
        embedding=embeddings
    ) 
    return vectorstore

def calculate_confidence(question: str, context_chunks: list) -> float:
    if not context_chunks:
        return 0.0
    try:
        embeddings = get_embeddings_model()
        q_emb = embeddings.embed_query(question)
        emb_list = [embeddings.embed_query(c) for c in context_chunks]
        
        sims = cosine_similarity([q_emb], emb_list)[0]
        best_sim = max(sims)
        return round(float(best_sim), 2)
    except Exception:
        return 0.0

def call_groq_stream(prompt: str, model: str = "llama-3.1-8b-instant"):
    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide factual, clear, and concise answers based on the context."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"--- Groq Error --- {e}"

def document_agent_stream(vectorstore, question: str):
    """Retrieves document context and streams the LLM completion."""
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(question)
        context_chunks = [d.page_content for d in docs]
        context = "\n".join(context_chunks) if context_chunks else "No relevant context found."
        
        prompt = (
            f"Use only the provided context if relevant.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}"
        )
        
        confidence = calculate_confidence(question, context_chunks)
        stream_generator = call_groq_stream(prompt)
        
        return stream_generator, confidence
    except Exception as e:
        return (chunk for chunk in [f"--- Document Agent Error --- {e}"]), 0.0
