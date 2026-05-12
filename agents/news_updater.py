"""
ZAKARX News Updater Agent
Busca noticias relevantes para pymes colombianas y actualiza las tarjetas en index.html
"""
import os, re, json, feedparser, requests
from google import genai
from datetime import datetime
from bs4 import BeautifulSoup

MONTHS_ES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']

UNSPLASH_IMAGES = [
    "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&h=168&fit=crop&q=80",  # IA
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=168&fit=crop&q=80",  # finanzas
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=168&fit=crop&q=80",    # negocios
]

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=pymes+Colombia+tecnologia+2025&hl=es-419&gl=CO&ceid=CO:es-419",
    "https://news.google.com/rss/search?q=emprendimiento+fintech+latinoamerica&hl=es-419&gl=CO&ceid=CO:es-419",
    "https://news.google.com/rss/search?q=inteligencia+artificial+negocios+pequenos+Colombia&hl=es-419&gl=CO&ceid=CO:es-419",
]

def fetch_news():
    articles = []
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; ZakarxBot/1.0)'}
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                e = feed.entries[0]
                # Limpiar HTML del summary
                summary_raw = e.get('summary', e.get('description', ''))
                soup = BeautifulSoup(summary_raw, 'lxml')
                summary = soup.get_text()[:300]
                articles.append({
                    'title': e.title,
                    'summary': summary,
                    'source': e.get('source', {}).get('title', 'Noticias'),
                })
        except Exception as ex:
            print(f"⚠️  Error en feed {url}: {ex}")
    return articles[:3]

def format_with_gemini(articles):
    client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
    articles_text = "\n".join(
        [f"{i+1}. TITULO: {a['title']}\n   RESUMEN: {a['summary']}\n   FUENTE: {a['source']}"
         for i, a in enumerate(articles)]
    )
    prompt = f"""Tienes estas 3 noticias recientes relevantes para pymes colombianas y latinoamericanas:

{articles_text}

Para cada noticia genera:
1. cat: categoría corta (ej: "IA & Tecnología", "Fintech", "Emprendimiento", "Digitalización", "Negocios LATAM", "E-commerce")
2. title: título atractivo en español (máx 65 caracteres, sin comillas extras)
3. desc: descripción útil y concisa para dueños de pymes (máx 110 caracteres)
4. meta: fuente y tiempo aproximado (ej: "El Tiempo • hace 3 horas")

Responde ÚNICAMENTE con JSON válido (sin markdown, sin explicaciones):
[
  {{"cat":"...","title":"...","desc":"...","meta":"..."}},
  {{"cat":"...","title":"...","desc":"...","meta":"..."}},
  {{"cat":"...","title":"...","desc":"...","meta":"..."}}
]"""

    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    raw = response.text.strip()
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    return json.loads(match.group(0) if match else raw)

def update_html(articles_data):
    html_path = 'index.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    cards_html = "\n"
    for i, a in enumerate(articles_data):
        img = UNSPLASH_IMAGES[i % len(UNSPLASH_IMAGES)]
        cards_html += f'''        <article class="news-card">
          <img class="news-card-img" src="{img}" alt="{a['title']}" loading="lazy">
          <div class="news-card-body">
            <span class="news-cat">{a['cat']}</span>
            <h3 class="news-title">{a['title']}</h3>
            <p class="news-desc">{a['desc']}</p>
            <span class="news-meta">{a['meta']}</span>
          </div>
        </article>\n'''

    html = re.sub(
        r'(<div[^>]*id="news-grid"[^>]*>).*?(</div>)',
        f'\\1{cards_html}      \\2',
        html, flags=re.DOTALL
    )

    now = datetime.now()
    date_str = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}"
    html = re.sub(r'(<span id="news-date">)[^<]*(</span>)', f'\\g<1>{date_str}\\2', html)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    print("🔍 Buscando noticias...")
    articles = fetch_news()
    if not articles:
        print("❌ No se encontraron noticias. Abortando.")
        exit(1)
    print(f"✅ {len(articles)} noticias encontradas")

    print("🤖 Formateando con Gemini...")
    formatted = format_with_gemini(articles)

    print("📝 Actualizando index.html...")
    update_html(formatted)
    print("✅ News Updater completado")
