"""
ZAKARX CEO Agent
Revisa el estado completo del sitio y genera reporte semanal para Elias.
"""
import os, re, json, feedparser, requests
from gemini import ask
from datetime import datetime
from bs4 import BeautifulSoup

MONTHS_ES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']

PLACEHOLDERS = [
    ('573001234567', '❌ WhatsApp placeholder sin reemplazar'),
    ('TU_ID_FORMSPREE', '❌ Formspree ID sin configurar'),
    ('G-XXXXXXXXXX', '❌ Google Analytics sin activar'),
    ('$0 COP', '⚠️  Precio en $0 COP (verificar si es intencional)'),
]

def audit_html():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    issues = []
    for placeholder, msg in PLACEHOLDERS:
        if placeholder in html:
            issues.append(msg)

    soup = BeautifulSoup(html, 'lxml')

    # Verificar fecha de noticias
    news_date_el = soup.find(id='news-date')
    news_date = news_date_el.get_text(strip=True) if news_date_el else 'No encontrada'

    # Contar herramientas
    tool_cards = soup.find_all(class_='tool-card')
    tool_pills = soup.find_all(class_='tool-pill')

    # Verificar meta tags
    desc = soup.find('meta', attrs={'name': 'description'})
    desc_text = desc['content'] if desc else 'FALTANTE'

    return {
        'issues': issues,
        'news_date': news_date,
        'tool_cards_count': len(tool_cards),
        'tool_pills_count': len(tool_pills),
        'meta_description': desc_text[:100],
    }

def fetch_market_news():
    """Busca noticias del mercado pymes para el reporte"""
    news = []
    feeds = [
        "https://news.google.com/rss/search?q=software+pymes+Colombia+2025&hl=es-419&gl=CO&ceid=CO:es-419",
        "https://news.google.com/rss/search?q=digitalizacion+empresas+latinoamerica&hl=es-419&gl=CO&ceid=CO:es-419",
    ]
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                news.append(feed.entries[0].title)
        except:
            pass
    return news

def generate_report_with_gemini(audit, news):

    prompt = f"""Eres el agente CEO de ZAKARX, una suite digital para pymes colombianas.
El dueño es Elias (corrales.elias@gmail.com). Genera el reporte semanal.

AUDITORÍA DEL SITIO:
- Problemas encontrados: {audit['issues'] if audit['issues'] else ['Ninguno 🎉']}
- Fecha de noticias en el sitio: {audit['news_date']}
- Herramientas destacadas en portada: {audit['tool_cards_count']}
- Herramientas en pills: {audit['tool_pills_count']}
- Meta description actual: {audit['meta_description']}

NOTICIAS DEL MERCADO ESTA SEMANA:
{chr(10).join(f'- {n}' for n in news)}

Genera un reporte ejecutivo conciso con:
1. Estado general del sitio (semáforo: 🟢 Bien / 🟡 Atención / 🔴 Urgente)
2. Resumen de problemas a resolver (si hay)
3. Oportunidad de la semana basada en las noticias del mercado
4. Una recomendación de acción concreta para Elias
5. Métricas del sistema autónomo esta semana

Tono: directo, ejecutivo, orientado a acción. Máx 300 palabras."""

    issues_text = "\n".join(f"- {i}" for i in audit['issues']) if audit['issues'] else "- Ninguno 🎉"
    fallback = f"""## Estado del sitio: 🟡 Revisión manual recomendada

**Auditoría automática completada** (modo sin IA):

### Problemas detectados
{issues_text}

### Noticias del mercado esta semana
{chr(10).join(f'- {n}' for n in news[:3])}

### Recomendación
Revisar los problemas pendientes y mantener el sitio actualizado.
El sistema autónomo está funcionando correctamente."""
    return ask(prompt, fallback=fallback)

def write_report(audit, report_text):
    now = datetime.now()
    date_str = f"{now.day} de {MONTHS_ES[now.month-1]} de {now.year}"

    content = f"""# Reporte Semanal ZAKARX
**Generado:** {date_str} | **Agente:** CEO Bot

---

{report_text}

---

## 📋 Auditoría Técnica

| Elemento | Estado |
|----------|--------|
| Fecha noticias | {audit['news_date']} |
| Herramientas en portada | {audit['tool_cards_count']} tarjetas + {audit['tool_pills_count']} pills |
| Meta description | {audit['meta_description']}... |
{"".join(f"| {issue.split(' ', 1)[1] if ' ' in issue else issue} | {issue[:2]} Pendiente |" + chr(10) for issue in audit['issues'])}

---
*Reporte generado automáticamente por ZAKARX CEO Agent cada lunes*
*Para responder o dar instrucciones → corrales.elias@gmail.com*
"""
    with open('reporte-semanal.md', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    print("🔍 Auditando sitio...")
    audit = audit_html()

    if audit['issues']:
        print(f"  ⚠️  {len(audit['issues'])} problemas encontrados")
    else:
        print("  ✅ Sitio sin problemas")

    print("📰 Buscando noticias del mercado...")
    news = fetch_market_news()

    print("🤖 Generando reporte con Gemini...")
    report = generate_report_with_gemini(audit, news)

    print("📝 Escribiendo reporte-semanal.md...")
    write_report(audit, report)

    print("✅ CEO Agent completado — reporte-semanal.md actualizado")
