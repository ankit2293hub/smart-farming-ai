import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert agricultural AI assistant 
specializing in plant diseases, crop management, and farming.

When given a disease and severity, provide:
1. Immediate Action (within 24-48 hours)
2. Short-term Treatment (1-2 weeks)
3. Long-term Prevention

Include both chemical and organic options.
Keep advice practical for smallholder farmers.
Be concise and clear."""

def get_treatment(disease: str, severity: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Disease: {disease}\nSeverity: {severity}\n\nProvide treatment plan."}
        ],
        max_tokens=600
    )
    return response.choices[0].message.content

def chat_with_bot(message: str, history: list) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=500
    )
    return response.choices[0].message.content
def translate_text(text: str, target_language: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        if target_language == "en":
            return text
        translated = GoogleTranslator(
            source='auto',
            target=target_language
        ).translate(text)
        return translated
    except Exception as e:
        return text  # Return original if translation fails