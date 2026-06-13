# 🌿 Smart Farming AI — Plant Disease Diagnosis System

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.10-orange)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38-red)](https://streamlit.io)
[![Accuracy](https://img.shields.io/badge/Accuracy-99.68%25-brightgreen)](https://huggingface.co/ankit2293/plant-disease-efficientnet)

**Live Demo → [smart-farming-ai-n4ewjrjcfzbvtq2vv6jnv7.streamlit.app](https://smart-farming-ai-n4ewjrjcfzbvtq2vv6jnv7.streamlit.app)**

**API Docs → [ankit2293-smart-farming-api.hf.space/docs](https://ankit2293-smart-farming-api.hf.space/docs)**

---

## 📌 Overview

An end-to-end AI pipeline that detects plant diseases from leaf images, estimates severity, and provides LLM-powered treatment recommendations — deployed live with FastAPI + Streamlit.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔬 Disease Detection | EfficientNet-B3 — 99.68% accuracy on 38 disease classes |
| 📊 Severity Estimation | OpenCV HSV-based infected area analysis |
| 💊 Treatment Plans | Groq LLM (Llama 3.3 70B) powered recommendations |
| 🗺️ Grad-CAM Heatmap | Explainable AI — visualize disease location |
| 🌤️ Weather & Risk | Real-time weather + disease outbreak risk |
| 💧 Irrigation Advisor | Smart water calculator for 10 crop types |
| 🌍 Multilingual | Responses in 6 Indian languages |
| 💬 Farming Chatbot | Multi-turn Q&A for farming advice |

---

## 📊 Model Performance

| Metric | Value |
|---|---|
| Validation Accuracy | 99.68% |
| Architecture | EfficientNet-B3 |
| Training Images | 37,997 |
| Classes | 38 diseases |
| Dataset | PlantVillage (54,305 images) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Model | PyTorch + EfficientNet-B3 (timm) |
| Severity | OpenCV HSV segmentation |
| Explainability | Grad-CAM |
| LLM | Groq API (Llama 3.3 70B) |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Weather | OpenWeather API |
| Translation | deep-translator |
| Model Hosting | HuggingFace Hub |
| Backend Deploy | HuggingFace Spaces |
| Frontend Deploy | Streamlit Cloud |

---

## 📁 Project Structure
smart-farming-ai/
├── api/
│   ├── main.py          # FastAPI endpoints
│   └── inference.py     # Model loading + prediction
├── src/
│   ├── model.py         # EfficientNet-B3 architecture
│   ├── train.py         # Training pipeline
│   ├── severity.py      # Severity estimator
│   ├── gradcam.py       # Grad-CAM heatmap
│   ├── weather.py       # Weather + disease risk
│   ├── irrigation.py    # Irrigation calculator
│   └── llm_agent.py     # LLM + chatbot
├── frontend/
│   └── app.py           # Streamlit UI
├── models/
│   └── class_names.json
├── notebooks/
│   └── 01_explore.ipynb
├── Dockerfile
└── requirements.txt

---

## ⚙️ Local Setup

```bash
# Clone
git clone https://github.com/ankit2293hub/smart-farming-ai.git
cd smart-farming-ai

# Setup
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add API keys
echo "GROQ_API_KEY=your_key" > .env
echo "OPENWEATHER_API_KEY=your_key" >> .env

# Run backend
uvicorn api.main:app --reload --port 8000

# Run frontend (new terminal)
streamlit run frontend/app.py
```

Open → **http://localhost:8501**

---

## 🚀 API Reference

### POST /predict
```bash
curl -X POST "https://ankit2293-smart-farming-api.hf.space/predict" \
  -F "file=@leaf.jpg"
```

Response:
```json
{
  "disease": "Tomato___Late_blight",
  "confidence": 0.9921,
  "severity": {"percentage": 34.2, "label": "Moderate"},
  "treatment": "1. Immediate Action: ..."
}
```

### POST /chat
```json
{
  "message": "How do I treat tomato blight?",
  "history": []
}
```

---

## 🏋️ Training

```bash
# Download dataset
kaggle datasets download -d abdallahalidev/plantvillage-dataset

# Explore data
jupyter notebook notebooks/01_explore.ipynb

# Train (Google Colab T4 GPU recommended)
python -m src.train
```

---

## 👤 Author

**Ankit Kumar**  
B.Tech CSE — SMVDU, Katra  
GitHub: [latentankit](https://github.com/latentankit)  
HuggingFace: [ankit2293](https://huggingface.co/ankit2293)

---

## 🙏 Acknowledgements

- PlantVillage Dataset — Hughes & Salathé (2015)
- EfficientNet — Tan & Le (2019)
- timm — Ross Wightman
- Groq — Fast LLM inference

---

⭐ Star this repo if you found it helpful!
