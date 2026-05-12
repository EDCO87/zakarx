"""
ZAKARX News Updater Agent
Busca noticias relevantes para pymes colombianas y actualiza las tarjetas en index.html.
Funciona con o sin acceso a Gemini API.
"""
import os, re, json, feedparser, requests
from gemini import ask
from datetime import datetime
from bs4 import BeautifulSoup

MONTHS_ES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']

UNSPLASH_IMAGES = [
    "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=600&h=168&fit=crop&q=80",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=168&fit=crop&q=80",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=168&fit=crop&q=80",
]

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=pymes+Colombia+tecnologia+2025&hl=es-419&gl=CO&ceid=CO:es-419",
    "https://news.google.com/rss/search?q=emprendimiento+fintech+latinoamerica&hl=es-419&gl=CO&ceid=CO:es-419",
    "https://news.google.com/rss/search?q=inteligencia+artificial+negocios+Colombia&hl=es-419&gl=CO&ceid=CO:es-419",
]

KEYWORD_CATS = [
    (['ia','inteligencia artificial','chatbot','automatizacion','machine learning'], 'IA & Tecnología'),
    (['fintech','finanzas','pago','credito','banco','inversion'],                   'Fintech'),
    (['emprendimiento','startup','emprendedor','negocio propio'],                   'Emprendimiento'),
    (['ecommerce','e-commerce','ventas online','tienda digital','marketplace'],     'E-commerce'),
    (['digital','software','app','herramienta','plataforma','tecnologia'],          'Digitalización'),
    (['colombia','bogota','medellin','cali','latinoamerica','latam'],               'Negocios LATAM'),
]

def guess_category(text: str) -> str:
    t = text.lower()
    for keywords, cat in KEYWORD_CATS:
        if any(k in t for k in keywords):
            return cat
    return 'Negocios LATAM'

def truncate(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 1].rsplit(' ', 1)[0] + '…'

def fetch_news():
    articles = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                e = feed.entries[0]
                summary_raw = e.get('summary', e.get('description', ''))
                soup = BeautifulSoup(summary_raw, 'lxml')
                summary = soup.get_text()[:300]
                articles.append({
                    'title':   e.title,
                    'summary': summary,
                    'source':  e.get('source', {}).get('title', 'Google News'),
                    'link':    e.get('link', '#'),
                })
        except Exception as ex:
            print(f"⚠️  Error en feed: {ex}")
    return articles[:3]

def format_no_ai(articles):
    """Formatea noticias sin IA usando lógica Python."""
    result = []
    for a in articles:
        combined = a['title'] + ' ' + a['summary']
        result.append({
            'cat':   guess_category(combined),
            'title': truncate(a['title'], 65),
            'desc':  truncate(a['summary'], 110) if a['summary'] else 'Lee más sobre este tema relevante para tu negocio.',
            'meta':  f"{a['source']} • hoy",
            'link':  a.get('link', '#'),
        })
    return result

def format_with_gemini(articles):
    articles_text = "\n".join(
        [f"{i+1}. TITULO: {a['title']}\n   RESUMEN: {a['summary']}\n   FUENTE: {a['source']}"
         for i, a in enumerate(articles)]
    )
    links = [a.get('link', '#') for a in articles]

    prompt = f"""Tienes estas 3 noticias recientes para pymes colombianas/latinoamericanas:

{articles_text}

Para cada noticia genera:
1. cat: categoría corta ("IA & Tecnología", "Fintech", "Emprendimiento", "Digitalización", "Negocios LATAM", "E-commerce")
2. title: título atractivo en español (máx 65 caracteres)
3. desc: descripción útil para dueños de pymes (máx 110 caracteres)
4. meta: fuente y tiempo (ej: "Forbes CO • hace 2 horas")

Responde ÚNICAMENTE con JSON válido:
[
  {{"cat":"...","title":"...","desc":"...","meta":"..."}},
  {{"cat":"...","title":"...","desc":"...","meta":"..."}},
  {{"cat":"...","title":"...","desc":"...","meta":"..."}}
]"""

    # Intentar con IA, si falla usar formateo básico
    fallback_json = json.dumps(format_no_ai(articles), ensure_ascii=False)
    raw = ask(prompt, fallback=fallback_json)
    match = re.search(r'\[.*\]', raw, re.DOTALL)
    result = json.loads(match.group(0) if match else raw)
    # Inyectar links (la IA no los modifica, los tomamos del RSS original)
    for i, item in enumerate(result):
        item['link'] = links[i] if i < len(links) else '#'
    return result

def replace_news_grid(html, new_content):
    """Reemplaza el contenido completo de div#news-grid contando divs anidados."""
    marker = 'id="news-grid"'
    start_idx = html.find(marker)
    if start_idx == -1:
        return html
    open_end = html.find('>', start_idx)
    depth, pos = 1, open_end + 1
    while pos < len(html) and depth > 0:
        next_open  = html.find('<div', pos)
        next_close = html.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return html[:open_end + 1] + new_content + html[next_close:]
            pos = next_close + 6
    return html

def update_html(articles_data):
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    cards_html = ""
    for i, a in enumerate(articles_data):
        img = UNSPLASH_IMAGES[i % len(UNSPLASH_IMAGES)]
        link = a.get('link', '#')
        cards_html += f'''
        <a class="news-card" href="{link}" target="_blank" rel="noopener noreferrer">
          <img class="news-card-img" src="{img}" alt="{a['title']}" loading="lazy">
          <div class="news-card-body">
            <span class="news-cat">{a['cat']}</span>
            <h3 class="news-title">{a['title']}</h3>
            <p class="news-desc">{a['desc']}</p>
            <span class="news-meta">{a['meta']}</span>
          </div>
        </a>'''

    html = replace_news_grid(html, cards_html + "\n      ")

    now = datetime.now()
    date_str = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}"
    html = re.sub(r'(<span id="news-date">)[^<]*(</span>)', f'\\g<1>{date_str}\\2', html)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    print("🔍 Buscando noticias...")
    articles = fetch_news()
    if not articles:
        print("❌ No se encontraron noticias. Abortando.")
        exit(1)
    print(f"✅ {len(articles)} noticias encontradas")

    print("🤖 Formateando...")
    formatted = format_with_gemini(articles)

    print("📝 Actualizando index.html...")
    update_html(formatted)
    print("✅ News Updater completado")
