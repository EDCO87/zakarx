"""Wrapper minimalista para la API REST de Gemini — sin SDKs."""
import os, requests

def ask(prompt: str) -> str:
    api_key = os.environ['GEMINI_API_KEY']
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
