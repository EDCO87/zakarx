"""
ZAKARX Competitor Agent
Monitorea precios de Alegra, Siigo y Loggro y actualiza el texto comparativo en index.html
"""
import os, re, json, requests
from gemini import ask
from bs4 import BeautifulSoup
from datetime import datetime

COMPETITORS = {
    'Alegra':  'https://alegra.com/precios/',
    'Siigo':   'https://siigo.com/planes-y-precios/',
    'Loggro':  'https://loggro.com/precios/',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'
}

def scrape_price_page(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        # Extraer texto relevante (precios suelen estar en .price, .plan, h2, h3)
        text_chunks = []
        for tag in soup.find_all(['h1','h2','h3','p','span','div'], limit=200):
            t = tag.get_text(strip=True)
            if t and ('$' in t or 'mes' in t.lower() or 'plan' in t.lower() or 'precio' in t.lower()):
                text_chunks.append(t[:120])
        return ' | '.join(text_chunks[:20])
    except Exception as ex:
        return f"[Error al leer página: {ex}]"

def analyze_with_gemini(scraped_data):
    data_text = "\n".join([f"{name}: {text}" for name, text in scraped_data.items()])

    prompt = f"""Analiza estos datos de precios de competidores de software para pymes en Colombia:

{data_text}

Extrae los precios mensuales más relevantes de cada competidor en pesos colombianos (COP).
Si no encuentras un precio específico, indica "precio no disponible".

Genera un JSON con este formato exacto:
{{
  "alegra_precio": "desde $XX.XXX/mes",
  "siigo_precio": "desde $XX.XXX/mes",
  "loggro_precio": "desde $XX.XXX/mes",
  "argumento": "3 meses de [competidor más barato] = ZAKARX Pro para siempre",
  "urgency_text": "texto corto de urgencia comparativo (máx 80 caracteres)"
}}

Responde ÚNICAMENTE con JSON válido, sin markdown."""

    fallback = json.dumps({
        "alegra_precio": "desde $69.900/mes",
        "siigo_precio": "desde $179.000/mes",
        "loggro_precio": "desde $179.000/mes",
        "argumento": "3 meses de Alegra = ZAKARX Pro para siempre",
        "urgency_text": "Alegra cobra $69.900/mes. ZAKARX: pago único."
    }, ensure_ascii=False)
    raw = ask(prompt, fallback=fallback)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group(0) if match else raw)

def update_html(data):
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Actualizar barra de urgencia si contiene texto comparativo
    if data.get('urgency_text'):
        html = re.sub(
            r'(Alegra cobra)[^<]*(\d+)',
            lambda m: m.group(0),  # Mantener si no hay patrón claro
            html
        )

    # Actualizar precios de competidores en la sección de pricing si existen
    if data.get('alegra_precio') and 'precio no disponible' not in data['alegra_precio']:
        html = re.sub(r'Alegra \$[\d\.\,]+–?\$?[\d\.\,]*/mes', f"Alegra {data['alegra_precio']}", html)
    if data.get('siigo_precio') and 'precio no disponible' not in data['siigo_precio']:
        html = re.sub(r'Siigo desde \$[\d\.\,]+/mes', f"Siigo {data['siigo_precio']}", html)
    if data.get('loggro_precio') and 'precio no disponible' not in data['loggro_precio']:
        html = re.sub(r'Loggro desde \$[\d\.\,]+/mes', f"Loggro {data['loggro_precio']}", html)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # Guardar reporte de competidores
    now = datetime.now()
    report = f"""# Reporte Competidores — {now.strftime('%d/%m/%Y')}

## Precios encontrados
- **Alegra:** {data.get('alegra_precio', 'N/D')}
- **Siigo:** {data.get('siigo_precio', 'N/D')}
- **Loggro:** {data.get('loggro_precio', 'N/D')}

## Argumento de venta sugerido
{data.get('argumento', 'Ver reporte anterior')}

---
*Generado automáticamente por ZAKARX Competitor Agent*
"""
    with open('reporte-competidores.md', 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == '__main__':
    print("🔍 Monitoreando precios de competidores...")
    scraped = {}
    for name, url in COMPETITORS.items():
        print(f"  → {name}...")
        scraped[name] = scrape_price_page(url)

    print("🤖 Analizando con Gemini...")
    data = analyze_with_gemini(scraped)
    print(f"  Alegra: {data.get('alegra_precio')}")
    print(f"  Siigo:  {data.get('siigo_precio')}")
    print(f"  Loggro: {data.get('loggro_precio')}")

    print("📝 Actualizando index.html y reporte...")
    update_html(data)
    print("✅ Competitor Agent completado")
