import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import re
import json

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

# ---- Header ----
st.markdown(
    f"""
    <h1 style='text-align: center; color: #1f77b4;'>🔍 RecVue Global Search</h1>
    <p style='text-align: center; color: gray; font-size: 18px;'>Advanced Semantic Search with Visual Analytics</p>
    <p style='text-align: center; color: #666;'>Currently searching as <b>{tenant_id}</b></p>
    """,
    unsafe_allow_html=True
)

# ---- Search Interface ----
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    query = st.text_input(
        "🔍 Enter your search query:", 
        placeholder="e.g. High value orders for customer C100, Recent active orders, Orders with billing issues...",
        help="Try natural language queries - the system understands meaning, not just keywords!"
    )

with col2:
    search_button = st.button("🚀 Search", type="primary", use_container_width=True)

with col3:
    if st.button("🎲 Demo Queries", use_container_width=True):
        demo_queries = [
            "High value orders over 5000",
            "Recent orders from last month", 
            "Orders with status PAID",
            "Customer orders with billing issues",
            "Active orders for premium customers"
        ]
        query = st.selectbox("Choose a demo query:", demo_queries)

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
                    
                    # ---- Score Distribution Chart ----
                    st.subheader("📊 Relevance Score Distribution")
                    scores = [r['score'] for r in results]
                    fig = px.histogram(
                        x=scores, 
                        nbins=10,
                        title="Distribution of Search Result Scores",
                        labels={'x': 'Relevance Score (Lower = Better)', 'y': 'Number of Results'}
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    
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
                    
                    # Display results with visual elements
                    for _, row in df.iterrows():
                        with st.container():
                            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 3])
                            
                            with col1:
                                # Rank with color coding
                                if row['Rank'] == 1:
                                    st.markdown(f"🥇 **#{row['Rank']}**")
                                elif row['Rank'] == 2:
                                    st.markdown(f"🥈 **#{row['Rank']}**")
                                elif row['Rank'] == 3:
                                    st.markdown(f"🥉 **#{row['Rank']}**")
                                else:
                                    st.markdown(f"**#{row['Rank']}**")
                            
                            with col2:
                                st.markdown(f"**Order:** {row['Order Number']}")
                                st.markdown(f"**Customer:** {row['Customer']}")
                            
                            with col3:
                                # Status with color coding
                                status = row['Status']
                                if 'ACTIVE' in status.upper():
                                    st.markdown(f"🟢 **{status}**")
                                elif 'PAID' in status.upper():
                                    st.markdown(f"💰 **{status}**")
                                elif 'TERMINATED' in status.upper():
                                    st.markdown(f"🔴 **{status}**")
                                else:
                                    st.markdown(f"⚪ **{status}**")
                                
                                st.markdown(f"**Date:** {row['Date']}")
                            
                            with col4:
                                # Relevance progress bar
                                relevance = row['Relevance']
                                st.markdown(f"**Relevance:** {relevance:.1f}%")
                                
                                # Color-coded progress bar
                                if relevance >= 80:
                                    color = "green"
                                elif relevance >= 60:
                                    color = "orange"
                                else:
                                    color = "red"
                                
                                st.progress(relevance / 100)
                            
                            with col5:
                                # Expandable full text
                                with st.expander("📄 View Details"):
                                    st.markdown(f"**Full Record:** {row['Full Text']}")
                                    st.markdown(f"**Raw Score:** {row['Score']:.4f}")
                            
                            st.divider()
                    
                    # ---- Search Analytics ----
                    st.subheader("📈 Search Analytics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Status distribution
                        status_counts = df['Status'].value_counts()
                        if len(status_counts) > 0:
                            fig_status = px.pie(
                                values=status_counts.values, 
                                names=status_counts.index,
                                title="Order Status Distribution"
                            )
                            st.plotly_chart(fig_status, use_container_width=True)
                    
                    with col2:
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
                    st.warning("🔍 No relevant records found for your query.")
                    st.info("💡 **Tips:** Try using different keywords, synonyms, or more general terms.")
                    
            else:
                st.error(f"❌ Error {response.status_code}: {response.json().get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"🔌 Connection failed: {e}")
            st.info("💡 Make sure the Flask API server is running on http://127.0.0.1:5000")

# ---- Footer ----
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>🔍 <b>RecVue Global Search POC</b> | Powered by Semantic Search & Vector Embeddings</p>
        <p>💡 <i>Try natural language queries - the system understands meaning, not just keywords!</i></p>
    </div>
    """,
    unsafe_allow_html=True
)
