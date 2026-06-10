FROM python:3.10.18-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

RUN mkdir -p api src models

COPY main.py api/main.py
COPY inference.py api/inference.py
COPY model.py src/model.py
COPY severity.py src/severity.py
COPY llm_agent.py src/llm_agent.py
COPY gradcam.py src/gradcam.py
COPY class_names.json models/class_names.json

RUN touch api/__init__.py src/__init__.py

EXPOSE 7860

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]