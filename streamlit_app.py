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
                        else:
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
                st.error(f"❌ Error {response.status_code}: {response.json().get('error', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"🔌 Connection failed: {e}")
            st.info("💡 Make sure the Flask API server is running on http://127.0.0.1:5000")

# ---- Always show results if present in session state ----
if 'last_results' in st.session_state and st.session_state['last_results']:
    results = st.session_state['last_results']
    query = st.session_state.get('last_query', '')
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
            else:
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
