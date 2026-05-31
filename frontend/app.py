import streamlit as st
import requests
from PIL import Image
import io

# Page config
st.set_page_config(
    page_title="🌿 Plant Doctor AI",
    page_icon="🌿",
    layout="wide"
)

API_URL = "https://smart-farming-ai-ajge.onrender.com"

# Header
st.title("🌿 Plant Disease Diagnosis System")
st.markdown("Upload a leaf image to detect disease, severity and get treatment recommendations.")

# Tabs
tab1, tab2 = st.tabs(["🔬 Diagnose Plant", "💬 Farming Chatbot"])

# ==================== TAB 1 — DIAGNOSE ====================
with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Upload Leaf Image")
        uploaded = st.file_uploader(
            "Choose a leaf photo",
            type=["jpg", "jpeg", "png"]
        )

        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption="Uploaded Leaf", use_column_width=True)
            analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)
        else:
            st.info("👆 Upload a leaf image to get started")
            analyze = False

    with col2:
        if uploaded and analyze:
            with st.spinner("🧠 Analyzing leaf..."):
                try:
                    # Send to API
                    files = {"file": (uploaded.name, uploaded.getvalue(), "image/jpeg")}
                    response = requests.post(f"{API_URL}/predict", files=files)
                    result = response.json()

                    # Disease result
                    st.subheader("📊 Diagnosis Results")

                    # Metrics row
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        disease_name = result["disease"].replace("___", " — ").replace("_", " ")
                        st.metric("Disease", disease_name)
                    with m2:
                        conf = result["confidence"] * 100
                        st.metric("Confidence", f"{conf:.1f}%")
                    with m3:
                        sev = result["severity"]
                        icons = {"Mild": "🟢", "Moderate": "🟡", "Severe": "🔴", "Unknown": "⚪"}
                        icon = icons.get(sev["label"], "⚪")
                        st.metric("Severity", f"{icon} {sev['label']} ({sev['percentage']}%)")

                    # Top 3 predictions
                    st.subheader("🔝 Top 3 Predictions")
                    for i, pred in enumerate(result["top3_predictions"]):
                        name = pred["disease"].replace("___", " — ").replace("_", " ")
                        conf = pred["confidence"] * 100
                        st.progress(pred["confidence"], text=f"{i+1}. {name} — {conf:.1f}%")

                    # Treatment
                    st.subheader("💊 Treatment Plan")
                    st.markdown(result["treatment"])

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Make sure the FastAPI server is running on port 8000")

        elif not uploaded:
            st.info("Upload a leaf image on the left to see diagnosis results here.")

# ==================== TAB 2 — CHATBOT ====================
with tab2:
    st.subheader("💬 Ask the Farming Assistant")
    st.markdown("Ask anything about plant diseases, treatments, or farming practices.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.api_history = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about farming, diseases, treatments..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.api_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": prompt,
                            "history": st.session_state.api_history[:-1]
                        }
                    )
                    bot_reply = response.json()["response"]
                    st.markdown(bot_reply)

                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    st.session_state.api_history.append({"role": "assistant", "content": bot_reply})

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")