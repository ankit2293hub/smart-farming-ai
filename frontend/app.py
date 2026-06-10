import streamlit as st
import requests
from PIL import Image
import os

st.set_page_config(
    page_title="🌿 Smart Farming AI",
    page_icon="🌿",
    layout="wide"
)

API_URL = os.getenv("API_URL", "https://ankit2293-smart-farming-api.hf.space")

st.title("🌿 Smart Farming AI System")
st.markdown("Complete AI-powered farming assistant — disease detection, weather, irrigation & more.")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔬 Diagnose Plant",
    "🗺️ Grad-CAM",
    "🌤️ Weather & Risk",
    "💧 Irrigation",
    "💬 Farming Chatbot"
])

# ==================== TAB 1 — DIAGNOSE ====================
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
            st.image(img, caption="Uploaded Leaf", width=300)
            analyze = st.button("🔍 Analyze", type="primary", use_container_width=True)
        else:
            st.info("👆 Upload a leaf image to get started")
            analyze = False

    with col2:
        if uploaded and analyze:
            with st.spinner("🧠 Analyzing leaf..."):
                try:
                    buf   = uploaded.getvalue()
                    files = {"file": ("leaf.jpg", buf, "image/jpeg")}
                    resp  = requests.post(
                        f"{API_URL}/predict",
                        files=files,
                        timeout=60
                    )
                    if resp.status_code == 503:
                        st.warning("⚠️ Backend waking up — wait 30 seconds and try again.")
                    else:
                        resp.raise_for_status()
                        result = resp.json()

                        st.subheader("📊 Diagnosis Results")
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            name = result["disease"].replace("___", " — ").replace("_", " ")
                            st.metric("Disease", name)
                        with m2:
                            conf = result["confidence"] * 100
                            st.metric("Confidence", f"{conf:.1f}%")
                        with m3:
                            sev   = result["severity"]
                            icons = {"Mild": "🟢", "Moderate": "🟡", "Severe": "🔴"}
                            icon  = icons.get(sev["label"], "⚪")
                            st.metric("Severity", f"{icon} {sev['label']} ({sev['percentage']}%)")

                        st.subheader("🔝 Top 3 Predictions")
                        for i, pred in enumerate(result["top3_predictions"]):
                            pname = pred["disease"].replace("___", " — ").replace("_", " ")
                            pconf = pred["confidence"] * 100
                            st.progress(pred["confidence"], text=f"{i+1}. {pname} — {pconf:.1f}%")

                        st.subheader("💊 Treatment Plan")
                        st.markdown(result["treatment"])

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Wait 30 seconds and try again.")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Backend is loading — try again.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.info("Upload a leaf image and click Analyze.")

# ==================== TAB 2 — GRAD-CAM ====================
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
            with st.spinner("Generating heatmap... (may take 30-60 seconds)"):
                try:
                    import base64
                    import io

                    files = {"file": ("leaf.jpg", uploaded_gc.getvalue(), "image/jpeg")}
                    resp  = requests.post(
                        f"{API_URL}/gradcam",
                        files=files,
                        timeout=120
                    )
                    if resp.status_code == 503:
                        st.warning("⚠️ Backend waking up — wait 30 seconds and try again.")
                    else:
                        resp.raise_for_status()
                        result   = resp.json()
                        img_data = base64.b64decode(result["heatmap"])
                        img      = Image.open(io.BytesIO(img_data))

                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(uploaded_gc, caption="Original", width=300)
                        with col2:
                            st.image(img, caption="Grad-CAM Heatmap", width=300)

                        st.info("🔴 Red = disease area | 🔵 Blue = healthy tissue")

                except requests.exceptions.Timeout:
                    st.error("❌ Timed out. Backend is loading — try again in 30 seconds.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    else:
        st.info("Upload a leaf image to generate heatmap.")

# ==================== TAB 3 — WEATHER ====================
with tab3:
    st.subheader("🌤️ Weather & Disease Risk")
    st.markdown("Get real-time weather and disease risk for your location.")

    col1, col2 = st.columns([1, 2])
    with col1:
        city = st.text_input("Enter your city", placeholder="e.g. Mumbai, Delhi, Katra")
        if st.button("🌍 Get Weather", type="primary"):
            if city:
                with st.spinner("Fetching weather..."):
                    try:
                        weather_key = os.getenv("OPENWEATHER_API_KEY", "")
                        if not weather_key:
                            st.error("❌ Weather API key not configured in secrets.")
                        else:
                            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}&units=metric"
                            r   = requests.get(url, timeout=10)
                            d   = r.json()

                            if d.get("cod") != 200:
                                st.error(f"❌ City not found: {city}")
                            else:
                                temp     = d["main"]["temp"]
                                humidity = d["main"]["humidity"]

                                risks = {}
                                risks["Late Blight"]      = "🔴 High" if humidity > 80 and 10 < temp < 24 else "🟡 Medium" if humidity > 70 and 10 < temp < 24 else "🟢 Low"
                                risks["Powdery Mildew"]   = "🔴 High" if 20 < temp < 30 and humidity < 60 else "🟡 Medium" if 15 < temp < 30 and humidity < 70 else "🟢 Low"
                                risks["Rust"]             = "🔴 High" if humidity > 75 and 15 < temp < 25 else "🟡 Medium" if humidity > 65 and 15 < temp < 25 else "🟢 Low"
                                risks["Bacterial Blight"] = "🔴 High" if humidity > 80 and temp > 28 else "🟡 Medium" if humidity > 70 and temp > 25 else "🟢 Low"

                                st.session_state["weather"] = {
                                    "city"        : d["name"],
                                    "temperature" : temp,
                                    "humidity"    : humidity,
                                    "description" : d["weather"][0]["description"],
                                    "wind_speed"  : d["wind"]["speed"],
                                    "feels_like"  : d["main"]["feels_like"],
                                    "disease_risk": risks
                                }
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
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
            st.markdown(f"**Conditions:** {w['description'].capitalize()}")
            st.subheader("⚠️ Disease Risk Today")
            for disease, risk in w["disease_risk"].items():
                st.markdown(f"**{disease}:** {risk}")
        else:
            st.info("Enter a city and click Get Weather.")

# ==================== TAB 4 — IRRIGATION ====================
with tab4:
    st.subheader("💧 Smart Irrigation Advisor")
    st.markdown("Calculate exactly how much water your crop needs today.")

    CROP_WATER_NEEDS = {
        "Tomato"     : {"base": 5.0, "stages": {"seedling": 2.5, "growing": 5.0, "flowering": 6.5, "fruiting": 5.5}},
        "Potato"     : {"base": 4.5, "stages": {"seedling": 2.0, "growing": 4.5, "flowering": 6.0, "fruiting": 4.0}},
        "Corn"       : {"base": 5.5, "stages": {"seedling": 3.0, "growing": 5.5, "flowering": 7.0, "fruiting": 5.0}},
        "Apple"      : {"base": 4.0, "stages": {"seedling": 1.0, "growing": 4.0, "flowering": 5.0, "fruiting": 4.5}},
        "Grape"      : {"base": 3.5, "stages": {"seedling": 1.0, "growing": 3.5, "flowering": 4.5, "fruiting": 4.0}},
        "Wheat"      : {"base": 4.0, "stages": {"seedling": 2.0, "growing": 4.0, "flowering": 5.5, "fruiting": 3.5}},
        "Rice"       : {"base": 8.0, "stages": {"seedling": 6.0, "growing": 8.0, "flowering": 9.0, "fruiting": 7.0}},
        "Pepper"     : {"base": 4.5, "stages": {"seedling": 2.5, "growing": 4.5, "flowering": 5.5, "fruiting": 4.5}},
        "Strawberry" : {"base": 3.5, "stages": {"seedling": 2.0, "growing": 3.5, "flowering": 4.5, "fruiting": 4.0}},
        "Soybean"    : {"base": 4.5, "stages": {"seedling": 2.5, "growing": 4.5, "flowering": 6.0, "fruiting": 4.5}},
    }

    col1, col2 = st.columns(2)
    with col1:
        crop      = st.selectbox("🌱 Crop", list(CROP_WATER_NEEDS.keys()))
        stage     = st.selectbox("📅 Growth Stage", ["seedling", "growing", "flowering", "fruiting"])
        soil_type = st.selectbox("🌍 Soil Type", ["Loamy", "Sandy", "Clay", "Silt"])
        area      = st.number_input("📐 Farm Area (hectares)", min_value=0.1, value=1.0, step=0.1)

    with col2:
        temperature = st.slider("🌡️ Temperature (°C)", 0, 50, 25)
        humidity    = st.slider("💧 Humidity (%)", 0, 100, 60)
        rainfall    = st.slider("🌧️ Rainfall (mm)", 0.0, 50.0, 0.0, step=0.5)

    if st.button("💧 Calculate Irrigation", type="primary"):
        crop_data  = CROP_WATER_NEEDS.get(crop, {"base": 4.5, "stages": {}})
        base_need  = crop_data["stages"].get(stage, crop_data["base"])

        temp_factor     = 1.3 if temperature > 35 else 1.15 if temperature > 30 else 0.8 if temperature < 15 else 1.0
        humidity_factor = 0.85 if humidity > 80 else 1.2 if humidity < 40 else 1.0
        soil_factors    = {"Sandy": 1.3, "Loamy": 1.0, "Clay": 0.8, "Silt": 0.9}
        soil_factor     = soil_factors.get(soil_type, 1.0)

        daily_need   = base_need * temp_factor * humidity_factor * soil_factor
        net_need     = max(0, daily_need - rainfall)
        area_m2      = area * 10000
        total_liters = net_need * area_m2
        total_cubic  = total_liters / 1000

        if net_need == 0:
            schedule  = "No irrigation needed today — rainfall is sufficient"
            frequency = "Check tomorrow"
        elif net_need < 2:
            schedule  = "Light irrigation recommended"
            frequency = "Every 3-4 days"
        elif net_need < 4:
            schedule  = "Moderate irrigation needed"
            frequency = "Every 2 days"
        else:
            schedule  = "Heavy irrigation required"
            frequency = "Daily"

        st.subheader("📊 Irrigation Recommendation")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Daily Need", f"{round(daily_need, 2)} mm")
        with m2:
            st.metric("Net Need", f"{round(net_need, 2)} mm")
        with m3:
            st.metric("Total Water", f"{round(total_liters):,} L")
        st.success(f"📋 {schedule}")
        st.info(f"🔄 Frequency: {frequency}")
        st.info(f"⏰ Best Time: Early morning (5-7 AM) or evening (6-8 PM)")
        st.metric("Total (cubic meters)", f"{round(total_cubic, 2)} m³")

# ==================== TAB 5 — CHATBOT ====================
with tab5:
    st.subheader("💬 Ask the Farming Assistant")
    st.markdown("Ask anything about plant diseases, treatments, or farming practices.")

    languages = {
        "English": "en",
        "Hindi":   "hi",
        "Tamil":   "ta",
        "Telugu":  "te",
        "Punjabi": "pa",
        "Bengali": "bn"
    }
    lang_name = st.selectbox("🌍 Response Language", list(languages.keys()))
    lang_code = languages[lang_name]

    if "messages" not in st.session_state:
        st.session_state.messages    = []
        st.session_state.api_history = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about farming, diseases, treatments..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.api_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": prompt,
                            "history": st.session_state.api_history[:-1]
                        },
                        timeout=60
                    )
                    if resp.status_code == 503:
                        st.warning("⚠️ Backend waking up — wait 30 seconds and try again.")
                    else:
                        resp.raise_for_status()
                        bot_reply = resp.json()["response"]

                        if lang_code != "en":
                            try:
                                from deep_translator import GoogleTranslator
                                bot_reply = GoogleTranslator(
                                    source='auto',
                                    target=lang_code
                                ).translate(bot_reply)
                            except Exception:
                                st.caption("⚠️ Translation unavailable — showing English")

                        st.markdown(bot_reply)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": bot_reply}
                        )
                        st.session_state.api_history.append(
                            {"role": "assistant", "content": bot_reply}
                        )

                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to API. Wait 30 seconds and retry.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")