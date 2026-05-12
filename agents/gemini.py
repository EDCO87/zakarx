"""
Wrapper para Gemini API con fallback a formateo básico sin IA.
Si la API falla, los agentes siguen funcionando con lógica Python pura.
"""
import os, requests

MODELS = [
    ("v1beta", "gemini-2.0-flash"),
    ("v1beta", "gemini-2.0-flash-lite"),
    ("v1beta", "gemini-1.5-flash"),
    ("v1",     "gemini-pro"),
]

def ask(prompt: str, fallback: str = None) -> str:
    """
    Llama a Gemini. Si falla, retorna `fallback` si se provee,
    o lanza excepción si no hay fallback.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        if fallback is not None:
            return fallback
        raise RuntimeError("GEMINI_API_KEY no configurada")

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for version, model in MODELS:
        url = (
            f"https://generativelanguage.googleapis.com/{version}"
            f"/models/{model}:generateContent?key={api_key}"
        )
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                text = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"✅ Gemini OK ({model})")
                return text
        except Exception:
            pass

    print("⚠️  Gemini no disponible — usando modo sin IA")
    if fallback is not None:
        return fallback
    raise RuntimeError("API no disponible y no se proporcionó fallback")
