import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import re
import json
import sys
import os

# Add the current directory to Python path to import our RAG agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import RAG agent
try:
    from rag_agent_simple import SimpleRAGAgent
    RAG_AVAILABLE = True
except ImportError as e:
    st.warning(f"⚠️ RAG Agent not available: {e}")
    RAG_AVAILABLE = False

# ---- Setup and Branding ----
st.set_page_config(page_title="RecVue Global Search", page_icon=":mag:", layout="wide")

# Load and display logo
try:
    logo = Image.open("logo.jpg")
    st.sidebar.image(logo, width=120)
except:
    st.sidebar.image("🔍", width=120)

st.sidebar.title("Global Search")
st.sidebar.markdown("Multi-Tenant Semantic Search Demo")

# ---- Tenant Selection and Session State ----
tenant_id = st.sidebar.selectbox("Select Tenant", ["tenant_ABC", "tenant_XYZ"])
st.session_state["tenant_id"] = tenant_id

# ---- Navigation Tabs ----
tab1, tab2 = st.tabs(["🔍 Semantic Search", "🤖 AI Assistant"])

# ---- Tab 1: Original Semantic Search ----
with tab1:
    st.markdown(
        f"""
        <h1 style='text-align: center; color: #1f77b4;'>🔍 RecVue Global Search</h1>
        <p style='text-align: center; color: gray; font-size: 18px;'>Advanced Semantic Search with Visual Analytics</p>
        <p style='text-align: center; color: #666;'>Currently searching as <b>{tenant_id}</b></p>
        """,
        unsafe_allow_html=True
    )

    # ---- Demo Queries and Search Bar Sync ----
    demo_queries = [
        "High value orders over 5000",
        "Recent orders from last month",
        "Orders with status PAID",
        "Customer orders with billing issues",
        "Active orders for premium customers"
    ]

    col1, col2, col3 = st.columns([2, 5, 1])
    with col1:
        selected_demo = st.selectbox("Choose Demo Query", demo_queries, key="demo_query_selectbox")
    with col2:
        query = st.text_input("Search Orders", value=selected_demo if selected_demo else "")
    with col3:
        search_button = st.button("Search")

    # ---- Search Results Visualization ----
    if search_button and query.strip():
        with st.spinner("🔍 Searching through your data..."):
            try:
                url = f"http://127.0.0.1:5000/api/tenant/{tenant_id}/search"
                headers = {"X-Tenant-ID": tenant_id}
                response = requests.post(url, json={"query": query}, headers=headers)

                if response.status_code == 200:
                    results = response.json()
                    if results:
                        st.session_state['last_results'] = results
                        st.session_state['last_query'] = query

                    # ---- Results Summary ----
                    st.success(f"🎉 Found {len(results)} relevant results!")
                    
                    # Create metrics row
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Results", len(results))
                    with col2:
                        best_score = min([r['score'] for r in results])
                        st.metric("Best Match Score", f"{best_score:.4f}")
                    with col3:
                        avg_score = sum([r['score'] for r in results]) / len(results)
                        st.metric("Average Score", f"{avg_score:.4f}")
                    with col4:
                        st.metric("Query", query[:20] + "..." if len(query) > 20 else query)
                    
                    # Display results (simplified for brevity)
                    st.subheader("📋 Search Results")
                    for i, result in enumerate(results[:5]):  # Show top 5 results
                        st.markdown(f"**{i+1}.** {result['sentence'][:200]}...")
                        st.markdown(f"*Score: {result['score']:.4f}*")
                        st.divider()
                    
                else:
                    st.error(f"❌ Error {response.status_code}: {response.json().get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"🔌 Connection failed: {e}")
                st.info("💡 Make sure the Flask API server is running on http://127.0.0.1:5000")

# ---- Tab 2: AI Assistant with RAG ----
with tab2:
    st.markdown(
        f"""
        <h1 style='text-align: center; color: #28a745;'>🤖 AI Assistant</h1>
        <p style='text-align: center; color: gray; font-size: 18px;'>Ask questions in natural language and get AI-powered insights</p>
        <p style='text-align: center; color: #666;'>Currently assisting as <b>{tenant_id}</b></p>
        """,
        unsafe_allow_html=True
    )

    if not RAG_AVAILABLE:
        st.error("❌ RAG Agent is not available. Please ensure all dependencies are installed.")
        st.info("💡 Run: `pip install pyautogen chromadb sentence-transformers ollama fix-busted-json`")
    else:
        # Initialize RAG agent
        if 'rag_agent' not in st.session_state:
            try:
                with st.spinner("🤖 Initializing AI Assistant..."):
                    st.session_state['rag_agent'] = SimpleRAGAgent(tenant_id=tenant_id)
                st.success("✅ AI Assistant ready!")
            except Exception as e:
                st.error(f"❌ Failed to initialize AI Assistant: {e}")
                st.session_state['rag_agent'] = None

        if st.session_state.get('rag_agent'):
            # ---- AI Query Interface ----
            st.markdown("### 💬 Ask me anything about your orders...")
            
            # Sample AI queries
            ai_demo_queries = [
        "What are the highest value orders in the system?",
        "Show me all orders for customer 26",
        "Find orders with delivery issues",
        "Which orders are currently active?",
        "What's the average order value?",
        "Find orders from June 2021"
    ]

            col1, col2 = st.columns([3, 1])
            with col1:
                ai_query = st.text_input(
                    "Ask your question",
                    placeholder="e.g., 'What are the highest value orders?'",
                    key="ai_query_input"
                )
            with col2:
                ai_search_button = st.button("Ask AI", type="primary")

            # Show demo queries
            st.markdown("**💡 Try these example questions:**")
            demo_cols = st.columns(3)
            for i, demo_query in enumerate(ai_demo_queries):
                with demo_cols[i % 3]:
                    if st.button(demo_query, key=f"demo_ai_{i}"):
                        st.session_state['ai_query_input'] = demo_query
                        st.rerun()

            # ---- AI Response Generation ----
            if ai_search_button and ai_query.strip():
                with st.spinner("🤖 AI is analyzing your question..."):
                    try:
                        # Get AI response
                        result = st.session_state['rag_agent'].generate_response(ai_query)
                        
                        if result['status'] == 'success':
                            # ---- AI Response Display ----
                            st.markdown("---")
                            st.markdown("### 🤖 AI Response")
                            
                            # Response with styling
                            st.markdown(
                                f"""
                                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;'>
                                    <h4>💡 Answer:</h4>
                                    <p style='font-size: 16px; line-height: 1.6;'>{result['response']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Context information
                            with st.expander("🔍 View AI's Context", expanded=False):
                                st.markdown("**Context used by AI:**")
                                st.text(result['context'])
                            
                            # Model information
                            st.info(f"🤖 Model used: {result.get('model_used', 'Unknown')}")
                            
                        else:
                            st.error(f"❌ AI Error: {result['response']}")
                            
                    except Exception as e:
                        st.error(f"❌ AI Assistant Error: {e}")
                        st.info("💡 This might be due to memory constraints. Consider using a cloud-based LLM.")

            # ---- AI Chat History ----
            if 'ai_chat_history' not in st.session_state:
                st.session_state['ai_chat_history'] = []

            # Display chat history
            if st.session_state['ai_chat_history']:
                st.markdown("---")
                st.markdown("### 💬 Chat History")
                
                for i, chat_item in enumerate(st.session_state['ai_chat_history']):
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown("👤 **You:**")
                        with col2:
                            st.markdown(f"*{chat_item['query']}*")
                        
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown("🤖 **AI:**")
                        with col2:
                            st.markdown(chat_item['response'])
                        
                        if i < len(st.session_state['ai_chat_history']) - 1:
                            st.divider()

                # Clear chat button
                if st.button("🗑️ Clear Chat History"):
                    st.session_state['ai_chat_history'] = []
                    st.rerun()

# ---- Footer ----
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>🔍 <b>RecVue Global Search POC</b> | Powered by Semantic Search & AI</p>
        <p>💡 <i>Try both semantic search and natural language AI queries!</i></p>
    </div>
    """,
    unsafe_allow_html=True
) 