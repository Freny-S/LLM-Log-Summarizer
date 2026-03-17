import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Log Summarizer",
    page_icon="🔍",
    layout="wide"
)

def display_summary(result: dict):
    severity = result["severity"]
    color_map = {
       "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢" 
    }
    icon = color_map.get(severity, "⚪")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Severity", f"{icon} {severity}")
    with col2:
        st.metric("Resolved", "✅ Yes" if result["resolved"] else "❌ No")

    st.markdown("**Summary**")
    st.info(result["summary"])

    st.markdown("**Root Cause**")
    st.info(result["root_cause"])

    st.markdown("**Affected Services**")
    for service in (result["affected_services"]):
        st.code(service)


st.title("🔍 LLM Log Summarizer")
st.caption("Paste logs or upload a file to get instant AI-powered incident analysis.")

tab1, tab2 = st.tabs(["Paste Logs", "Upload File"])

# ---- Tab 1: Paste Logs ----
with tab1:
    st.subheader("Paste your logs below")
    logs_input = st.text_area(
        label="Logs",
        height=250,
        placeholder="2024-03-01 02:13:44 ERROR [kafka-consumer] broker timeout..."

    )

    if st.button("Analyze", key="analyze_paste"):
        if not logs_input.strip():
            st.warning("Please paste some logs first.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        f"{API_URL}/summarize",
                        json={"logs": logs_input}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        display_summary(result)
                    else:
                        st.error(f"API error: {response.status_code}")
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")


# ---- Tab 2: Upload file ----
with tab2:
    st.subheader("Upload a .log file")
    uploaded_file = st.file_uploader("Choose a .log file", type=["log"])

    if st.button("Analyze File", key="analyze_file"):
        if uploaded_file is None:
            st.warning("Please upload a file first.")
        else:
            with st.spinner("Analyzing all incidents..."):
                try:
                    response = requests.post(
                        f"{API_URL}/upload",
                        files={"file": (uploaded_file.name, uploaded_file, "text/plain")}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"Found {result['total_incidents']} incident(s)")
                        for i, incident in enumerate(result["incidents"], 1):
                            with st.expander(f"Incident {i} - {incident['severity']}"):
                                display_summary(incident)
                    else:
                        st.error(f"API error: {response.status_code}")
                except Exception as e:
                    st.error(f"Could not connect to API: {e}")