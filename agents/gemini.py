"""
Wrapper para la API REST de Gemini.
Prueba varios modelos en orden hasta que uno responda correctamente.
"""
import os, requests

MODELS = [
    ("v1",    "gemini-pro"),
    ("v1beta","gemini-1.5-flash"),
    ("v1beta","gemini-1.5-flash-latest"),
    ("v1beta","gemini-1.5-pro"),
    ("v1beta","gemini-2.0-flash-lite"),
]

def ask(prompt: str) -> str:
    api_key = os.environ['GEMINI_API_KEY']
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    errors = []

    for version, model in MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/{version}"
            f"/models/{model}:generateContent?key={api_key}"
        )
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"✅ Gemini OK con modelo: {model}")
                return text
            errors.append(f"{model}: HTTP {r.status_code} — {r.text[:120]}")
        except Exception as e:
            errors.append(f"{model}: {e}")

    raise RuntimeError("Ningún modelo de Gemini respondió:\n" + "\n".join(errors))
