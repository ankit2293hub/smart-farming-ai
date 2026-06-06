import streamlit as st
import requests
from PIL import Image
import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Safe imports for cloud
try:
    from src.weather import get_weather
    from src.irrigation import calculate_irrigation, CROP_WATER_NEEDS
    FEATURES_AVAILABLE = True
except Exception:
    FEATURES_AVAILABLE = False
st.set_page_config(
    page_title="🌿 Smart Farming AI",
    page_icon="🌿",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("🌿 Smart Farming AI System")
st.markdown("Complete AI-powered farming assistant.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔬 Diagnose Plant",
    "🗺️ Grad-CAM",
    "🌤️ Weather & Risk",
    "💧 Irrigation",
    "💬 Farming Chatbot"
])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Upload Leaf Image")
        uploaded = st.file_uploader(
            "Choose a leaf photo",
            type=["jpg", "jpeg", "png"],
            key="diagnose"
        )
        if uploaded:
            img = Image.open(uploaded)
            st.image(img, caption="Uploaded Leaf", use_container_width=True)
            analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)
        else:
            st.info("👆 Upload a leaf image to get started")
            analyze = False

    with col2:
        if uploaded and analyze:
            with st.spinner("🧠 Analyzing leaf..."):
                try:
                    buf = uploaded.getvalue()
                    files = {"file": ("leaf.jpg", buf, "image/jpeg")}
                    response = requests.post(f"{API_URL}/predict", files=files)
                    result = response.json()

                    st.subheader("📊 Diagnosis Results")
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

                    st.subheader("🔝 Top 3 Predictions")
                    for i, pred in enumerate(result["top3_predictions"]):
                        name = pred["disease"].replace("___", " — ").replace("_", " ")
                        conf = pred["confidence"] * 100
                        st.progress(pred["confidence"], text=f"{i+1}. {name} — {conf:.1f}%")

                    st.subheader("💊 Treatment Plan")
                    st.markdown(result["treatment"])

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.info("Upload a leaf image and click Analyze.")

with tab2:
    st.subheader("🗺️ Grad-CAM Disease Heatmap")
    st.markdown("See exactly which part of the leaf the AI is looking at.")

    uploaded_gc = st.file_uploader(
        "Upload leaf image for heatmap",
        type=["jpg", "jpeg", "png"],
        key="gradcam"
    )

    if uploaded_gc:
        if st.button("🔥 Generate Heatmap", type="primary"):
            with st.spinner("Generating heatmap..."):
                try:
                    import base64
                    from PIL import Image
                    import io

                    files = {"file": ("leaf.jpg", uploaded_gc.getvalue(), "image/jpeg")}
                    response = requests.post(f"{API_URL}/gradcam", files=files)
                    result = response.json()

                    # Decode base64 image
                    img_data = base64.b64decode(result["heatmap"])
                    img = Image.open(io.BytesIO(img_data))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(uploaded_gc, caption="Original", width=400)
                    with col2:
                        st.image(img, caption="Grad-CAM Heatmap", width=400)

                    st.info("🔴 Red = disease area | 🔵 Blue = healthy tissue")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("Upload a leaf image to generate heatmap.")
with tab3:
    st.subheader("🌤️ Weather & Disease Risk")

    col1, col2 = st.columns([1, 2])
    with col1:
        city = st.text_input(
            "Enter your city",
            placeholder="e.g. Mumbai, Delhi, Katra"
        )
        if st.button("🌍 Get Weather", type="primary"):
            if city:
                with st.spinner("Fetching weather..."):
                    weather = get_weather(city)
                    if "error" in weather:
                        st.error(f"❌ {weather['error']}")
                    else:
                        st.session_state["weather"] = weather
            else:
                st.warning("Please enter a city name")

    with col2:
        if "weather" in st.session_state:
            w = st.session_state["weather"]
            st.subheader(f"📍 {w['city']}")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("🌡️ Temperature", f"{w['temperature']}°C",
                          f"Feels {w['feels_like']}°C")
            with m2:
                st.metric("💧 Humidity", f"{w['humidity']}%")
            with m3:
                st.metric("💨 Wind", f"{w['wind_speed']} m/s")
            st.markdown(
                f"**Conditions:** {w['description'].capitalize()}"
            )
            st.subheader("⚠️ Disease Risk Today")
            for disease, risk in w["disease_risk"].items():
                st.markdown(f"**{disease}:** {risk}")

with tab4:
    st.subheader("💧 Smart Irrigation Advisor")

    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("🌱 Crop", list(CROP_WATER_NEEDS.keys()))
        stage = st.selectbox(
            "📅 Growth Stage",
            ["seedling", "growing", "flowering", "fruiting"]
        )
        soil_type = st.selectbox(
            "🌍 Soil Type",
            ["Loamy", "Sandy", "Clay", "Silt"]
        )
        area = st.number_input(
            "📐 Farm Area (hectares)",
            min_value=0.1, value=1.0, step=0.1
        )

    with col2:
        temperature = st.slider("🌡️ Temperature (°C)", 0, 50, 25)
        humidity    = st.slider("💧 Humidity (%)", 0, 100, 60)
        rainfall    = st.slider("🌧️ Rainfall (mm)", 0.0, 50.0, 0.0, step=0.5)

    if st.button("💧 Calculate Irrigation", type="primary"):
        result = calculate_irrigation(
            crop, stage, temperature, humidity, rainfall, area, soil_type
        )
        st.subheader("📊 Irrigation Recommendation")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Daily Need", f"{result['daily_need_mm']} mm")
        with m2:
            st.metric("Net Need", f"{result['net_need_mm']} mm")
        with m3:
            st.metric("Total Water", f"{result['total_liters']:,} L")
        st.success(f"📋 {result['schedule']}")
        st.info(f"🔄 Frequency: {result['frequency']}")
        st.info(f"⏰ Best Time: {result['best_time']}")

with tab5:
    st.subheader("💬 Ask the Farming Assistant")

    languages = {
        "English": "en",
        "Hindi":   "hi",
        "Tamil":   "ta",
        "Telugu":  "te",
        "Punjabi": "pa",
        "Bengali": "bn"
    }
    lang_name = st.selectbox(
        "🌍 Response Language",
        list(languages.keys())
    )
    lang_code = languages[lang_name]

    if "messages" not in st.session_state:
        st.session_state.messages    = []
        st.session_state.api_history = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about farming, diseases, treatments..."):
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )
        st.session_state.api_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

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

                    if lang_code != "en":
                        from src.llm_agent import translate_text
                        bot_reply = translate_text(bot_reply, lang_code)

                    st.markdown(bot_reply)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": bot_reply}
                    )
                    st.session_state.api_history.append(
                        {"role": "assistant", "content": bot_reply}
                    )

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")