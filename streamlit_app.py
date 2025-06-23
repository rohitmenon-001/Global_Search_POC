import streamlit as st
import requests
from PIL import Image

# ---- Setup and Branding ----
st.set_page_config(page_title="RecVue Global Search", page_icon=":mag:", layout="wide")

# Load and display logo
logo = Image.open("logo.jpg")  # Ensure correct path
st.sidebar.image(logo, width=120)
st.sidebar.title("🔎 RecVue Copilot")
st.sidebar.markdown("Multi-Tenant Semantic Search Demo")

# ---- Tenant Selection and Session State ----
tenant_id = st.sidebar.selectbox("Select Tenant", ["tenant_ABC", "tenant_XYZ"])
st.session_state["tenant_id"] = tenant_id

st.markdown(
    f"""
    <h2 style='text-align: center;'>🔍 Semantic Search Panel</h2>
    <p style='text-align: center; color: gray;'>You are currently searching as <b>{tenant_id}</b></p>
    """,
    unsafe_allow_html=True
)

# ---- Search Box ----
query = st.text_input("Enter your search query:", placeholder="e.g. Order O1001 for customer C100...")

# ---- Search Action ----
if st.button("Search"):
    if not query.strip():
        st.warning("Please enter a valid query to search.")
    else:
        with st.spinner("Contacting Copilot..."):
            try:
                url = f"http://127.0.0.1:5000/api/tenant/{tenant_id}/search"
                headers = {"X-Tenant-ID": tenant_id}
                response = requests.post(url, json={"query": query}, headers=headers)

                if response.status_code == 200:
                    results = response.json()
                    if results:
                        st.success(f"✅ {len(results)} results found.")
                        for i, res in enumerate(results, 1):
                            with st.expander(f"{i}. Record ID: {res['record_id']}"):
                                st.markdown(f"📝 **Sentence:** {res['sentence']}")
                                st.markdown(f"📊 **Score:** `{res['score']:.4f}`")
                    else:
                        st.info("No relevant records matched your query.")
                else:
                    st.error(f"❌ Error {response.status_code}: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.exception(f"Connection failed: {e}")
