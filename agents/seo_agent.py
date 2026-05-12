"""
ZAKARX SEO Agent
Actualiza meta tags, description, keywords y OG tags en index.html
según tendencias de búsqueda actuales para pymes colombianas.
"""
import os, re, json, feedparser
import anthropic
from datetime import datetime

TREND_FEEDS = [
    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=CO",
    "https://news.google.com/rss/search?q=herramientas+digitales+pymes+Colombia&hl=es-419&gl=CO&ceid=CO:es-419",
    "https://news.google.com/rss/search?q=software+empresas+pequenas+latinoamerica&hl=es-419&gl=CO&ceid=CO:es-419",
]

def fetch_trending_topics():
    topics = []
    for url in TREND_FEEDS:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:5]:
                topics.append(e.title)
        except Exception as ex:
            print(f"⚠️  Feed error: {ex}")
    return topics[:15]

def generate_seo_with_claude(topics, current_html):
    client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])

    # Extraer meta tags actuales del HTML
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', current_html)
    keywords_match = re.search(r'<meta name="keywords" content="([^"]*)"', current_html)
    current_desc = desc_match.group(1) if desc_match else ""
    current_kw = keywords_match.group(1) if keywords_match else ""

    prompt = f"""Eres un experto en SEO para software B2B latinoamericano.

CONTEXTO:
- Sitio: ZAKARX — Suite digital para pymes colombianas y latinoamericanas
- Propuesta de valor: 18 herramientas en pago único, sin suscripciones
- Competidores: Alegra, Siigo, Loggro (cobran mensual)
- Herramientas: CRM, Facturador, Chatbot IA, Inventario, Gastos, Contratos, etc.

DESCRIPCIÓN ACTUAL:
{current_desc}

KEYWORDS ACTUALES:
{current_kw}

TEMAS TRENDING HOY EN COLOMBIA:
{chr(10).join(f'- {t}' for t in topics[:10])}

Genera meta tags optimizados que:
1. Incorporen keywords trending relevantes para el negocio
2. Mantengan la propuesta de valor (pago único, sin suscripciones)
3. Sean naturales y no spam
4. description: máx 155 caracteres
5. keywords: 15-20 keywords separadas por coma
6. og:description: máx 200 caracteres (más descriptivo)

Responde ÚNICAMENTE con JSON válido:
{{
  "description": "...",
  "keywords": "...",
  "og_description": "...",
  "og_title": "ZAKARX — Suite Digital para Pymes | Pago Único"
}}"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group(0) if match else raw)

def update_html(seo_data, html):
    # Actualizar description
    if seo_data.get('description'):
        html = re.sub(
            r'(<meta name="description" content=")[^"]*(")',
            f'\\g<1>{seo_data["description"]}\\2', html
        )

    # Actualizar keywords
    if seo_data.get('keywords'):
        if re.search(r'<meta name="keywords"', html):
            html = re.sub(
                r'(<meta name="keywords" content=")[^"]*(")',
                f'\\g<1>{seo_data["keywords"]}\\2', html
            )
        else:
            html = html.replace(
                '</head>',
                f'  <meta name="keywords" content="{seo_data["keywords"]}">\n</head>'
            )

    # Actualizar OG tags
    if seo_data.get('og_description'):
        if re.search(r'<meta property="og:description"', html):
            html = re.sub(
                r'(<meta property="og:description" content=")[^"]*(")',
                f'\\g<1>{seo_data["og_description"]}\\2', html
            )
    if seo_data.get('og_title'):
        if re.search(r'<meta property="og:title"', html):
            html = re.sub(
                r'(<meta property="og:title" content=")[^"]*(")',
                f'\\g<1>{seo_data["og_title"]}\\2', html
            )

    return html

if __name__ == '__main__':
    print("🔍 Buscando tendencias de búsqueda...")
    topics = fetch_trending_topics()
    print(f"  {len(topics)} temas encontrados")

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    print("🤖 Generando SEO optimizado con Claude...")
    seo_data = generate_seo_with_claude(topics, html)
    print(f"  Description: {seo_data.get('description', '')[:60]}...")

    print("📝 Actualizando meta tags en index.html...")
    updated_html = update_html(seo_data, html)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(updated_html)

    # Guardar log SEO
    now = datetime.now()
    log = f"""# SEO Update — {now.strftime('%d/%m/%Y')}

## Meta tags actualizados
**Description:** {seo_data.get('description','')}
**Keywords:** {seo_data.get('keywords','')}
**OG Description:** {seo_data.get('og_description','')}

## Trending topics usados
{chr(10).join(f'- {t}' for t in topics[:8])}

---
*Generado por ZAKARX SEO Agent*
"""
    with open('reporte-seo.md', 'w', encoding='utf-8') as f:
        f.write(log)

    print("✅ SEO Agent completado")
