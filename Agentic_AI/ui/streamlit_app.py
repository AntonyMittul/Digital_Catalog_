import streamlit as st
import requests

# Try to read from secrets, else use fallback
try:
    BACKEND = st.secrets["backend_url"]
except Exception:
    BACKEND = "http://localhost:8000"  # fallback default

st.title("Agentic AI Catalog")
st.write(f"Using backend: {BACKEND}")

# Example usage of BACKEND in API call
try:
    response = requests.get(f"{BACKEND}/health")
    if response.status_code == 200:
        st.success("Backend is running!")
    else:
        st.warning("Backend reachable but not healthy.")
except Exception as e:
    st.error(f"Failed to connect to backend: {e}")
