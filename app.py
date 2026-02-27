import streamlit as st
import os

# Import our modularized backend components
from src.auth import login_ui
from src.database import store_chat_history, get_recent_chats
from src.document_processor import get_combined_text
from src.rag_engine import get_text_chunks, get_vectorstore, document_agent_stream
from src.web_search import web_agent


def handle_userinput(question):
    vectorstore = st.session_state.get('vectorstore')
    if vectorstore is None:
        st.warning("Please process documents first.")
        return
    
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # 2. Assistant Stream Placeholder
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            stream_gen, confidence = document_agent_stream(vectorstore, question)
            
            # Stream the document answer
            for chunk in stream_gen:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
                
        except Exception as e:
            st.error(f"Groq error: {e}")
            full_response, confidence = "Sorry, I am unable to generate a response at this time.", 0.0

        low_conf = confidence < 0.65  
        short_answer = len(full_response.strip()) < 120
        keywords = any(
            x in full_response.lower() 
            for x in ["don't know", "not found", "sorry", "unable to", "unfortunately", "couldn't", "no relevant context", "not available", "doesn't provide"]
        )

        # 3. Fallback to Web Search
        if low_conf or short_answer or keywords:
            message_placeholder.markdown(full_response + "\n\n*Low confidence in document answer. Searching the web...* ⏳")
            web_answer, web_conf = web_agent(question)
            
            if web_conf > confidence:
                full_response = web_answer
                confidence = web_conf
                
        # 4. Finalize
        message_placeholder.markdown(full_response)
        st.caption(f"Confidence Score: {confidence}")
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Save to Firebase DB
    user_id = st.session_state.user['localId']
    store_chat_history(user_id, question, full_response)
    
def main():
    st.set_page_config(page_title="RAG ChatBot", page_icon="🤖")
    
    # Check Auth
    authenticated = login_ui()
    if not authenticated:
        return
    
    user_id = st.session_state.user['localId']
    
    # Init Session State variables
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.header("🤖 Document RAG Chatbot")
     
    with st.sidebar:
        st.subheader("Your documents")
        uploaded_files = st.file_uploader(
            "Upload your files here 📂", 
            type=["pdf", "txt", "docx" ,".png", ".jpg", ".jpeg"], 
            accept_multiple_files=True
        )
        
        if st.button("Process Documents", type="primary"):
            if not uploaded_files:
                st.warning("Please upload at least one file before processing.")
            else:
                with st.spinner("Processing documents into vectorspace..."):
                    raw_text = get_combined_text(uploaded_files)
                    text_chunks = get_text_chunks(raw_text)
                    st.session_state.vectorstore = get_vectorstore(text_chunks)
                    
                st.success("✅ Processing complete! Ask your question.")
                
        # Display DB Chat History
        st.divider()
        st.subheader("Recent Chat History (DB)")
        history = get_recent_chats(user_id)
        for i, chat in enumerate(reversed(history), 1):
            st.markdown(f"**You:** {chat['question']}")
            ans = chat['answer']
            if len(ans) > 60: ans = ans[:60] + "..."
            st.markdown(f"🤖 {ans}")
            st.divider()

    # Render Stream Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if question := st.chat_input("Ask a question about your documents..."):
        handle_userinput(question)

if __name__=="__main__":
    main()