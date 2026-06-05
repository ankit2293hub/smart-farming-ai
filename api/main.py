import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Smart Farming AI", version="1.0")

app.add_middleware(CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])

# Load models at startup
from api.inference import predict_disease
from src.severity import estimate_severity
from src.llm_agent import get_treatment, chat_with_bot

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@app.get("/")
def root():
    return {"status": "Smart Farming AI is running 🌿"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # Save uploaded image to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Run all 3 stages
    disease, confidence, top3 = predict_disease(tmp_path)
    severity  = estimate_severity(tmp_path)
    treatment = get_treatment(disease, severity["label"])

    os.remove(tmp_path)

    return {
        "disease"         : disease,
        "confidence"      : confidence,
        "top3_predictions": top3,
        "severity"        : severity,
        "treatment"       : treatment
    }

@app.post("/chat")
def chat(req: ChatRequest):
    response = chat_with_bot(req.message, req.history)
    return {"response": response}
@app.post("/gradcam")
async def gradcam(file: UploadFile = File(...)):
    import json
    import torch
    from src.gradcam import generate_gradcam
    from src.model import PlantDiseaseClassifier
    import base64
    import cv2

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    with open('models/class_names.json') as f:
        classes = json.load(f)

    model = PlantDiseaseClassifier(num_classes=38, pretrained=False).to(device)
    ckpt  = torch.load('models/best_model.pth', map_location=device)
    model.load_state_dict(ckpt['model_state_dict'])

    overlay, cam = generate_gradcam(model, tmp_path, 0, device)
    os.remove(tmp_path)

    # Convert to base64 to send over API
    _, buffer = cv2.imencode('.jpg', cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    img_base64 = base64.b64encode(buffer).decode('utf-8')

    return {"heatmap": img_base64}