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