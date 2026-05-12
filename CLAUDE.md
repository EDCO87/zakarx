# ZAKARX — Suite Digital para Pymes Latinoamericanas

## Descripción del proyecto
ZAKARX es una suite de 18 herramientas digitales para pymes colombianas y latinoamericanas. El dueño es Elias (corrales.elias@gmail.com). El posicionamiento principal es **pago único, sin suscripciones**, compitiendo contra Alegra, Siigo y Loggro que cobran mensual.

## Archivos del proyecto
| Archivo | Descripción |
|---|---|
| `index.html` | Landing page principal (antes llamado zakarx.html) |
| `herramientas.html` | Catálogo de las 18 herramientas con filtros |
| `precios.html` | Página de planes y precios |
| `herramienta.html` | Página universal para cada herramienta (lee el parámetro `?tool=crm` de la URL) |

## Stack técnico
- HTML/CSS/JS puro — sin frameworks
- Fuentes: Syne (títulos) + DM Sans (cuerpo) via Google Fonts
- Seguridad: CSP meta tags, X-Frame-Options DENY, anti-XSS

## Design tokens (CSS variables)
```css
--bg: #ffffff
--accent: #00dcc8        /* cyan principal */
--accent-dark: #00b8a6
--accent-light: #e0faf8
--gold: #f5c842
--border: #e8eaf2
--text: #0a0b14
--text2: #4a4d60
--text3: #8b8fa8
```

## Las 18 herramientas
**Ventas:** CRM Liviano, Cotizaciones Automáticas, Facturador Simple, Reportes de Ventas  
**Operaciones:** Panel de Métricas, Generador de Contratos, Kanban de Tareas, Base de Conocimiento, Encuestas y NPS, Calculadora ROI  
**IA:** Chatbot IA, Generador de Contenido IA, Propuestas Comerciales IA, Analizador de Reseñas, Correos de Ventas IA, Resumidor de Reuniones  
**Seguridad:** Auditor de Contraseñas, Suite de Seguridad  

## Precios actuales
Los precios están en **$0 COP** temporalmente (el dueño los actualiza cuando esté listo).  
Precios de referencia del mercado colombiano:
- Starter: $249.000 COP (pago único)
- Pro: $549.000 COP (pago único)
- Enterprise: Desde $999.000 COP

Competidores: Alegra $69.900–$149.900/mes · Siigo desde $179.000/mes · Loggro desde $179.000/mes  
Argumento de venta: *"3 meses de Siigo = ZAKARX Pro para siempre"*

## Estructura del navbar
- Barra de urgencia: `position:fixed; top:0; z-index:1001` (fondo oscuro)
- Navbar: `position:fixed; top:40px; z-index:1000` (fondo blanco)
- Hero padding-top: 130px

## Links internos
- Todos los links entre páginas usan rutas relativas (`index.html`, `herramientas.html`, etc.)
- Links rotos desactivados con `href="#"`: guia.html, privacidad.html, terminos.html, y las 18 páginas individuales de herramientas
- WhatsApp: `https://wa.me/573001234567` (número placeholder — reemplazar con número real)
- Formulario contacto: Formspree — reemplazar `TU_ID_FORMSPREE` con ID real

## Pendientes del dueño (no tocar con código)
1. Reemplazar número WhatsApp `573001234567` con número real
2. Reemplazar `TU_ID_FORMSPREE` con ID real de Formspree
3. Agregar NIT real en el footer de precios.html
4. Activar Google Analytics (reemplazar `G-XXXXXXXXXX`)
5. Crear favicon.ico y og-image.png (1200×630px)
6. Definir precios finales y actualizar los $0 COP
7. Agregar testimoniales reales
8. Crear guia.html, privacidad.html, terminos.html cuando estén listos

## Pendientes técnicos
- Crear páginas individuales para cada herramienta (actualmente todas van a herramienta.html con ?tool=ID)
- Agregar extensión de Chrome del dueño como sección en index.html (pendiente info del dueño)
- Crear guia.html, privacidad.html, terminos.html

## Hosting
- Netlify (plan gratuito)
- Para actualizar: arrastrar la carpeta con los 4 archivos al panel Deploys en Netlify
- Dominio propio pendiente: comprar en Namecheap o Porkbun (~$10 USD/año) y conectar en Netlify

## Decisiones de diseño tomadas
- Fondo blanco, tipografía bold, sin colores oscuros de fondo en hero
- Badge flotante "IA activada / Claude Sonnet" removido del hero
- Precios con tachado del precio anterior y porcentaje de descuento
- Popup de captura de leads aparece a los 8 segundos (una vez por usuario via localStorage)
- Barra de urgencia fija en la parte superior
