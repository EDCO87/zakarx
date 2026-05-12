"""
ZAKARX Social Media Agent
Genera posts listos para publicar en Instagram, LinkedIn y Twitter/X
basados en las noticias actuales del sitio y tendencias del mercado.
"""
import os, re, json, feedparser
from gemini import ask
from datetime import datetime
from bs4 import BeautifulSoup

MONTHS_ES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']

def extract_current_news(html):
    """Extrae las noticias actuales del div#news-grid"""
    soup = BeautifulSoup(html, 'lxml')
    grid = soup.find(id='news-grid')
    if not grid:
        return []
    news = []
    for card in grid.find_all('article', class_='news-card'):
        cat = card.find(class_='news-cat')
        title = card.find(class_='news-title')
        desc = card.find(class_='news-desc')
        news.append({
            'cat': cat.get_text(strip=True) if cat else '',
            'title': title.get_text(strip=True) if title else '',
            'desc': desc.get_text(strip=True) if desc else '',
        })
    return news

def fetch_trending():
    """Busca tendencias adicionales via RSS"""
    topics = []
    feeds = [
        "https://news.google.com/rss/search?q=emprendimiento+digital+Colombia+2025&hl=es-419&gl=CO&ceid=CO:es-419",
        "https://news.google.com/rss/search?q=pymes+latinoamerica+tecnologia&hl=es-419&gl=CO&ceid=CO:es-419",
    ]
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:3]:
                topics.append(e.title)
        except:
            pass
    return topics[:5]

def generate_posts_with_gemini(news, trends):

    news_text = "\n".join([f"- [{n['cat']}] {n['title']}: {n['desc']}" for n in news])
    trends_text = "\n".join([f"- {t}" for t in trends])

    now = datetime.now()
    date_str = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}"

    prompt = f"""Eres el social media manager de ZAKARX, una suite de 18 herramientas digitales para pymes colombianas y latinoamericanas.
Propuesta de valor clave: PAGO ÚNICO, SIN SUSCRIPCIONES. Compites contra Alegra y Siigo que cobran mensual.
Tono: cercano, emprendedor, latinoamericano, con energía — nunca corporativo frío.

NOTICIAS ACTUALES EN EL SITIO (fecha: {date_str}):
{news_text}

TENDENCIAS DEL MOMENTO:
{trends_text}

Genera 3 posts para redes sociales. Conecta el contenido de valor con ZAKARX de forma natural (no forzada).

Responde ÚNICAMENTE con JSON válido:
{{
  "instagram": {{
    "caption": "caption completo 150-200 palabras con emojis y hashtags al final (#pymes #emprendimiento #Colombia #ZAKARX #herramientasdigitales #emprendedoreslatam #negociosdigitales)",
    "slide1": "titular impactante (máx 40 chars)",
    "slide2": "punto de valor 1 (máx 60 chars)",
    "slide3": "punto de valor 2 (máx 60 chars)",
    "slide4": "punto de valor 3 (máx 60 chars)",
    "slide5": "CTA con ZAKARX (máx 60 chars)"
  }},
  "linkedin": "post completo de 200-300 palabras, tono profesional pero cercano, con datos si es posible, CTA al final",
  "twitter": {{
    "t1": "tweet 1/5 — hook fuerte (máx 240 chars)",
    "t2": "tweet 2/5 — punto clave (máx 240 chars)",
    "t3": "tweet 3/5 — punto clave (máx 240 chars)",
    "t4": "tweet 4/5 — dato o tip (máx 240 chars)",
    "t5": "tweet 5/5 — CTA ZAKARX (máx 240 chars)"
  }}
}}"""

    news_titles = " | ".join([n['title'] for n in news[:2]])
    fallback = json.dumps({
        "instagram": {
            "caption": f"💡 ¿Sabías que el 70% de las pymes en LATAM aún no usan herramientas digitales? Con ZAKARX tienes 18 herramientas en un solo pago. Sin mensualidades. Sin sorpresas. 🚀\n\n{news_titles}\n\n#pymes #emprendimiento #Colombia #ZAKARX #herramientasdigitales #emprendedoreslatam",
            "slide1": "¿Aún pagando mensual por tu software?",
            "slide2": "18 herramientas digitales para tu pyme",
            "slide3": "CRM, Facturación, IA y mucho más",
            "slide4": "Un solo pago. Para siempre.",
            "slide5": "Conoce ZAKARX — zakarx.netlify.app"
        },
        "linkedin": f"Las pymes latinoamericanas enfrentan un reto real: pagar suscripciones mensuales por herramientas digitales consume entre $500.000 y $2.000.000 COP al año.\n\nZAKARX ofrece una alternativa: 18 herramientas digitales con un único pago.\n\nEsta semana en el mercado pyme: {news_titles}\n\n¿Tu empresa ya está digitalizada? #pymes #Colombia #transformaciondigital #ZAKARX",
        "twitter": {
            "t1": "🧵 El mayor error de las pymes en LATAM: pagar suscripciones eternas por software que no necesitan.",
            "t2": "Alegra: $69.900/mes. Siigo: $179.000/mes. En 12 meses ya pagaste más de $2 millones.",
            "t3": "Con ZAKARX pagas UNA VEZ y tienes 18 herramientas para siempre. CRM, facturación, IA...",
            "t4": f"Noticia de la semana: {news_titles[:100]}...",
            "t5": "¿Listo para dejar las suscripciones? → zakarx.netlify.app #pymes #Colombia #ZAKARX"
        }
    }, ensure_ascii=False)
    raw = ask(prompt, fallback=fallback)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group(0) if match else raw)

def write_social_posts(posts, date_str):
    ig = posts['instagram']
    tw = posts['twitter']

    content = f"""# ZAKARX — Posts Redes Sociales
**Generado:** {date_str}

---

## 📸 INSTAGRAM

### Caption
{ig['caption']}

### Slides (Carrusel)
**Slide 1 — Portada:** {ig['slide1']}
**Slide 2:** {ig['slide2']}
**Slide 3:** {ig['slide3']}
**Slide 4:** {ig['slide4']}
**Slide 5 — CTA:** {ig['slide5']}

---

## 💼 LINKEDIN

{posts['linkedin']}

---

## 🐦 TWITTER/X — Hilo

**Tweet 1/5:** {tw['t1']}

**Tweet 2/5:** {tw['t2']}

**Tweet 3/5:** {tw['t3']}

**Tweet 4/5:** {tw['t4']}

**Tweet 5/5:** {tw['t5']}

---
*Generado automáticamente por ZAKARX Social Agent · {date_str}*
"""
    with open('social-posts.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    now = datetime.now()
    date_str = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}"

    print("📖 Leyendo noticias actuales del sitio...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    news = extract_current_news(html)
    print(f"  {len(news)} noticias encontradas")

    print("🔍 Buscando tendencias del momento...")
    trends = fetch_trending()
    print(f"  {len(trends)} tendencias encontradas")

    print("🤖 Generando posts con Gemini...")
    posts = generate_posts_with_gemini(news, trends)

    print("📝 Escribiendo social-posts.md...")
    write_social_posts(posts, date_str)

    print(f"✅ social-posts.md actualizado con 3 posts para {date_str}")
