import streamlit as st
from google.cloud.firestore_v1.base_query import FieldFilter
from firebase_config import db
from datetime import datetime

def store_chat_history(user_id, question, answer):
    user_ref = db.collection("chat_history").document(user_id)
    doc = user_ref.get()
    
    chat_entry = {
        "question": question,
        "answer": answer,
        "timestamp": datetime.now().isoformat()
    }
    
    if doc.exists:
        history = doc.to_dict().get("history", [])
        history.append(chat_entry)
        if len(history) > 5:
            history = history[-5:]
        user_ref.update({"history": history})
    else:
        user_ref.set({"history": [chat_entry]})

def get_recent_chats(user_id):
    user_ref = db.collection("chat_history").document(user_id)
    doc = user_ref.get()
    
    if doc.exists:
        return doc.to_dict().get("history", [])
    return []
