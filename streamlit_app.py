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
import numpy as np
import io

# Add the current directory to Python path to import our RAG agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import RAG agent
try:
    from rag_agent import RAGAgent
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
    st.sidebar.markdown("🔍 **Global Search**")

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
        # Use session state to sync the text input with the selected demo query
        if 'search_query' not in st.session_state:
            st.session_state['search_query'] = ""
        
        # Update session state when demo query changes
        if selected_demo and selected_demo != st.session_state.get('last_selected_demo'):
            st.session_state['search_query'] = selected_demo
            st.session_state['last_selected_demo'] = selected_demo
        
        query = st.text_input("Search Orders", value=st.session_state['search_query'], key="search_input")
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
                st.info(f"🔍 API Response: {len(results) if results else 0} results found")
                if results and len(results) > 0:
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
                    
                    # ---- Results Table with Visual Elements ----
                    st.subheader("📋 Detailed Search Results")
                    
                    # Process results for better display
                    processed_results = []
                    for i, res in enumerate(results):
                        # Extract key information using regex
                        sentence = res['sentence']
                        
                        # Extract order number
                        order_match = re.search(r'Order\s+([^\s(]+)', sentence)
                        order_number = order_match.group(1) if order_match else "N/A"
                        
                        # Extract customer
                        customer_match = re.search(r'customer\s+([^\s,]+)', sentence, re.IGNORECASE)
                        customer = customer_match.group(1) if customer_match else "N/A"
                        
                        # Extract status
                        status_match = re.search(r'status:\s*([^,]+)', sentence, re.IGNORECASE)
                        status = status_match.group(1) if status_match else "N/A"
                        
                        # Extract date
                        date_match = re.search(r'(\d{2}-[A-Z]{3}-\d{2})', sentence)
                        date = date_match.group(1) if date_match else "N/A"
                        
                        # Calculate relevance percentage (inverse of score)
                        relevance = max(0, 100 - (res['score'] * 50))  # Convert score to percentage
                        
                        processed_results.append({
                            'Rank': i + 1,
                            'Order Number': order_number,
                            'Customer': customer,
                            'Status': status,
                            'Date': date,
                            'Relevance': relevance,
                            'Score': res['score'],
                            'Full Text': sentence
                        })
                    
                    # Create DataFrame
                    df = pd.DataFrame(processed_results)
                    
                    # ---- Result Details Dropdown ----
                    order_options = [f"{i+1}. {row['Order Number']} (Score: {row['Score']:.2f})" for i, row in enumerate(processed_results)]
                    selected_idx = st.selectbox(
                        "Select a result to view details",
                        options=list(range(len(order_options))),
                        format_func=lambda i: order_options[i],
                        index=0,
                        key="result_details_selectbox"
                    )
                    selected_row = df.iloc[selected_idx]

                    # ---- Custom CSS for Animations ----
                    st.markdown(
                        """
                        <style>
                        .fade-in {
                            animation: fadeIn 0.7s;
                        }
                        @keyframes fadeIn {
                            0% { opacity: 0; }
                            100% { opacity: 1; }
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    # ---- Animated Spinner for Order Details ----
                    with st.spinner("✨ Loading order details..."):
                        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
                        # Centered order details with analytics
                        center_col, side_col = st.columns([3, 1])
                        with center_col:
                            st.markdown("## 📝 Order Details")
                            # Parse the sentence into fields
                            record_pattern = re.compile(
                                r"Order (?P<order_number>[^ ]+) \(ID: (?P<order_id>[^)]+)\) for customer (?P<customer>[^ ]+) on (?P<date>[^,]+), status: (?P<status>[^,]+), line: (?P<line_id>[^,]+), item: (?P<item_id>[^,]+), qty: (?P<qty>[^,]+), price: (?P<price>[^,]+), billing: (?P<billing>[^,]+), delivery from: (?P<delivery>[^,]+), pricing status: (?P<pricing_status>.+)"
                            )
                            match = record_pattern.match(selected_row['Full Text'])
                            if match:
                                record = match.groupdict()
                                st.markdown(f"### 📝 Order {record['order_number']}")
                                st.markdown(f"**Order ID:** `{record['order_id']}`  |  **Customer:** `{record['customer']}`  |  **Date:** `{record['date']}`")
                                # Status badge
                                status = record['status']
                                if 'ACTIVE' in status.upper():
                                    st.markdown(f"**Status:** <span style='color: white; background: #28a745; border-radius: 6px; padding: 2px 8px;'>🟢 {status}</span>", unsafe_allow_html=True)
                                elif 'PAID' in status.upper():
                                    st.markdown(f"**Status:** <span style='color: white; background: #ffc107; border-radius: 6px; padding: 2px 8px;'>💰 {status}</span>", unsafe_allow_html=True)
                                elif 'TERMINATED' in status.upper():
                                    st.markdown(f"**Status:** <span style='color: white; background: #dc3545; border-radius: 6px; padding: 2px 8px;'>🔴 {status}</span>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"**Status:** <span style='color: white; background: #6c757d; border-radius: 6px; padding: 2px 8px;'>⚪ {status}</span>", unsafe_allow_html=True)
                                st.markdown(f"**Line:** `{record['line_id']}`  |  **Item:** `{record['item_id']}`  |  **Billing:** `{record['billing']}`  |  **Pricing Status:** `{record['pricing_status']}`")
                                # Quantity bar and relative analytics
                                try:
                                    qty = float(record['qty'])
                                    max_qty = df['Full Text'].apply(lambda s: float(record_pattern.match(s).group('qty')) if record_pattern.match(s) else 0).max()
                                    st.markdown(f"**Quantity:** {qty} (Max: {max_qty})")
                                    st.progress(min(qty / max_qty, 1.0))
                                    if qty == max_qty:
                                        st.markdown("<span style='color: #fff; background: #007bff; border-radius: 6px; padding: 2px 8px;'>🏆 Highest Quantity</span>", unsafe_allow_html=True)
                                except:
                                    st.markdown(f"**Quantity:** {record['qty']}")
                                # Price highlight and relative analytics
                                try:
                                    price = float(record['price'])
                                    max_price = df['Full Text'].apply(lambda s: float(record_pattern.match(s).group('price')) if record_pattern.match(s) else 0).max()
                                    st.markdown(f"**Price:** ₹{price} (Max: ₹{max_price})")
                                    st.progress(min(price / max_price, 1.0))
                                    if price == max_price:
                                        st.markdown("<span style='color: #fff; background: #28a745; border-radius: 6px; padding: 2px 8px;'>💰 Highest Price</span>", unsafe_allow_html=True)
                                except:
                                    st.markdown(f"**Price:** {record['price']}")
                                # Delivery
                                st.markdown(f"**Delivery:** <span style='color: #fff; background: #17a2b8; border-radius: 6px; padding: 2px 8px;'>🚚 {record['delivery']}</span>", unsafe_allow_html=True)
                                # Score analytics
                                score = selected_row['Score']
                                min_score = df['Score'].min()
                                max_score = df['Score'].max()
                                st.markdown(f"**Raw Score:** {score:.4f} (Best: {min_score:.4f}, Worst: {max_score:.4f})")
                                st.progress((max_score - score) / (max_score - min_score + 1e-6))
                                if score == min_score:
                                    st.markdown("<span style='color: #fff; background: #28a745; border-radius: 6px; padding: 2px 8px;'>🥇 Best Match</span>", unsafe_allow_html=True)
                                st.markdown(f"**Full Record:** {selected_row['Full Text']}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        with side_col:
                            with st.expander("📊 Search Analytics", expanded=False):
                                # Score Distribution Chart
                                scores = df['Score'].tolist()
                                fig = px.histogram(
                                    x=scores,
                                    nbins=10,
                                    title="Distribution of Search Result Scores",
                                    labels={'x': 'Relevance Score (Lower = Better)', 'y': 'Number of Results'}
                                )
                                fig.update_layout(showlegend=False)
                                st.plotly_chart(fig, use_container_width=True)
                                # Status Pie Chart
                                status_counts = df['Status'].value_counts()
                                if len(status_counts) > 0:
                                    fig_status = px.pie(
                                        values=status_counts.values, 
                                        names=status_counts.index,
                                        title="Order Status Distribution"
                                    )
                                    st.plotly_chart(fig_status, use_container_width=True)
                                # Relevance vs Rank scatter plot
                                fig_scatter = px.scatter(
                                    df, 
                                    x='Rank', 
                                    y='Relevance',
                                    title="Relevance vs Rank",
                                    labels={'Relevance': 'Relevance %', 'Rank': 'Result Rank'}
                                )
                                st.plotly_chart(fig_scatter, use_container_width=True)
                            
                            # ---- Query Insights ----
                            st.subheader("💡 Search Insights")
                            
                            insights = []
                            if len(results) > 0:
                                best_score = min([r['score'] for r in results])
                                if best_score < 0.9:
                                    insights.append("✅ **Excellent match found!** Your query was very specific and relevant.")
                                elif best_score < 1.1:
                                    insights.append("👍 **Good match found!** Your query returned relevant results.")
                                else:
                                    insights.append("⚠️ **Moderate match.** Consider refining your query for better results.")
                                
                                if len(set([r['record_id'] for r in results])) == len(results):
                                    insights.append("🎯 **Diverse results:** All results are from different orders.")
                                else:
                                    insights.append("📋 **Some duplicate orders:** Multiple results from the same order.")
                                
                                if any('ACTIVE' in r['sentence'].upper() for r in results):
                                    insights.append("🟢 **Active orders found:** Some results include currently active orders.")
                                
                                if any('PAID' in r['sentence'].upper() for r in results):
                                    insights.append("💰 **Payment information:** Results include payment-related data.")
                            
                            for insight in insights:
                                st.markdown(insight)
                else:
                    st.warning("🔍 No results found for your query. Try different keywords.")
                    st.info("💡 Try searching for: 'orders', 'customer', 'status', 'active', 'paid', etc.")
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
                    st.session_state['rag_agent'] = RAGAgent(tenant_id=tenant_id)
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

            # Callback to set the text input value
            def set_ai_query_input(value):
                st.session_state['ai_query_input'] = value

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
                    if st.button(
                        demo_query,
                        key=f"demo_ai_{i}",
                        on_click=set_ai_query_input,
                        args=(demo_query,)
                    ):
                        pass  # Button click handled by callback

            # ---- AI Response Generation ----
            if ai_search_button and ai_query.strip():
                with st.spinner("🤖 AI is analyzing your question..."):
                    try:
                        # Get last 3 turns of chat history for conversational awareness
                        history = st.session_state.get('ai_chat_history', [])
                        result = st.session_state['rag_agent'].generate_enhanced_response(ai_query, history=history, history_turns=3)
                        # Store the latest AI response for visualization ONLY after a new response
                        st.session_state['last_ai_response'] = result['response']
                        st.session_state['last_ai_query'] = ai_query
                        st.session_state['last_ai_context'] = result['context']
                        st.session_state['last_ai_table_data'] = result.get('table_data')
                        st.session_state['last_ai_viz_code'] = result.get('visualization_code')
                        st.session_state['last_ai_intent'] = result.get('intent')
                        st.session_state['show_visualization'] = False  # Reset visualization toggle on new response
                        
                        if result['status'] == 'success':
                            # ---- AI Response Display ----
                            st.markdown("---")
                            st.markdown("### 🤖 AI Response")
                            response_text = result['response']
                            # Clean the LLM response: remove HTML tags, code blocks, and collapse blank lines
                            import re
                            cleaned = re.sub(r'<[^>]+>', '', response_text)  # Remove HTML tags
                            cleaned = re.sub(r'```[\s\S]+?```', '', cleaned)  # Remove code blocks
                            cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)  # Collapse multiple blank lines
                            cleaned = cleaned.strip()
                            # Render as markdown, compact like chat history
                            st.markdown(f"**🤖 Answer**\n\n{cleaned}", unsafe_allow_html=False)
                            # Display table data if available
                            table_data = result.get('table_data')
                            if table_data and isinstance(table_data, str):
                                st.markdown('#### 📊 Data Table')
                                st.markdown(table_data)
                                # Try to parse as DataFrame for better display
                                try:
                                    import io
                                    df = pd.read_csv(io.StringIO(table_data), sep='|').dropna(axis=1, how='all')
                                    df.columns = [c.strip() for c in df.columns]
                                    st.dataframe(df)
                                except Exception as e:
                                    st.warning(f"Could not parse table data: {e}")
                            elif result.get('intent', {}).get('needs_table'):
                                st.info('Table was requested but could not be generated.')
                            # Optional: Show raw JSON in an expander for advanced users
                            json_match = re.search(r'```json\s*([\s\S]+?)\s*```', response_text)
                            if json_match:
                                with st.expander('Show Raw Data', expanded=False):
                                    st.code(json_match.group(1), language='json')
                            # Collapsible context
                            with st.expander("🔍 View AI's Context", expanded=False):
                                st.markdown("**Context used by AI:**")
                                st.code(result['context'], language='markdown')
                            # Model information
                            st.info(f"🤖 Model used: {result.get('model_used', 'Unknown')}")
                            # Add to chat history
                            if 'ai_chat_history' not in st.session_state:
                                st.session_state['ai_chat_history'] = []
                            st.session_state['ai_chat_history'].append({
                                'query': ai_query,
                                'response': result['response']
                            })
                        else:
                            st.error(f"❌ AI Error: {result['response']}")
                    except Exception as e:
                        st.error(f"❌ AI Assistant Error: {e}")
                        st.info("💡 This might be due to memory constraints. Consider using a cloud-based LLM.")

            # ---- Enhanced Visualization Section ----
            if st.session_state.get('last_ai_response'):
                if 'show_visualization' not in st.session_state:
                    st.session_state['show_visualization'] = False
                
                # Show visualization button if we have visualization code or table data
                last_ai_intent = st.session_state.get('last_ai_intent', {})
                has_viz_content = (st.session_state.get('last_ai_viz_code') or 
                                 st.session_state.get('last_ai_table_data') or
                                 (isinstance(last_ai_intent, dict) and last_ai_intent.get('needs_visualization')))
                
                if has_viz_content:
                    if st.button('📊 Visualize Data', key='visualize_data_btn'):
                        st.session_state['show_visualization'] = not st.session_state.get('show_visualization', False)
                    
                    if st.session_state.get('show_visualization', False):
                        st.markdown('#### 📊 Data Visualization')
                        
                        # First, try to execute AI-generated visualization code
                        viz_code = st.session_state.get('last_ai_viz_code')
                        if viz_code and isinstance(viz_code, str):
                            try:
                                # Create a safe execution environment
                                exec_globals = {
                                    'pd': pd,
                                    'px': px,
                                    'go': go,
                                    'st': st,
                                    'np': np
                                }
                                
                                # Execute the visualization code
                                exec(viz_code, exec_globals)
                                st.success("✅ AI-generated visualization executed successfully!")
                                
                            except Exception as e:
                                st.error(f"❌ Error executing AI visualization code: {e}")
                                st.code(viz_code, language='python')
                        
                        # If no AI visualization code, try to create visualizations from table data
                        elif st.session_state.get('last_ai_table_data'):
                            try:
                                # Parse table data
                                table_data = st.session_state.get('last_ai_table_data')
                                if not isinstance(table_data, str):
                                    st.warning("Table data is not in the expected string format.")
                                else:
                                    df = pd.read_csv(io.StringIO(table_data), sep='|').dropna(axis=1, how='all')
                                    df.columns = [c.strip() for c in df.columns]
                                    
                                    st.markdown('#### 📋 Data Table')
                                    st.dataframe(df)
                                    
                                    # Create automatic visualizations
                                    if len(df.columns) >= 2:
                                        # Try to identify numeric columns for charts
                                        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                                        
                                        if numeric_cols:
                                            # Create bar chart for first numeric column
                                            fig = px.bar(df, x=df.columns[0], y=numeric_cols[0], 
                                                       title=f"{numeric_cols[0]} by {df.columns[0]}")
                                            st.plotly_chart(fig, use_container_width=True)
                                        
                                        # Create a simple bar chart as fallback
                                        st.markdown('#### 📈 Simple Chart')
                                        st.bar_chart(df.set_index(df.columns[0]))
                                
                            except Exception as e:
                                st.error(f"❌ Error creating visualization from table data: {e}")
                        
                        # Fallback: try to extract data from response text
                        else:
                            def extract_table_or_json(response_text):
                                import pandas as pd
                                import re
                                import json
                                # Try to extract JSON block
                                json_match = re.search(r'```json\s*(\{[\s\S]+?\})\s*```', response_text)
                                if json_match:
                                    try:
                                        data = json.loads(json_match.group(1))
                                        df = pd.DataFrame(data)
                                        return df
                                    except Exception:
                                        pass
                                # Try to extract markdown table
                                table_match = re.search(r'(\|.+\|\n\|[-: ]+\|[\s\S]+?)(\n\n|$)', response_text)
                                if table_match:
                                    try:
                                        import io
                                        df = pd.read_csv(io.StringIO(table_match.group(1)), sep='|').dropna(axis=1, how='all')
                                        df.columns = [c.strip() for c in df.columns]
                                        return df
                                    except Exception:
                                        pass
                                return None
                            
                            response_text = st.session_state.get('last_ai_response', '')
                            df = extract_table_or_json(response_text)
                            if df is not None and not df.empty:
                                st.markdown('#### 📊 Extracted Data Visualization')
                                st.dataframe(df)
                                if len(df.columns) >= 2:
                                    st.bar_chart(df.set_index(df.columns[0]))
                            else:
                                st.info('No structured data found for visualization. Try asking for specific data in table format.')

            # ---- AI Chat History ----
            if 'ai_chat_history' in st.session_state and st.session_state['ai_chat_history']:
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
