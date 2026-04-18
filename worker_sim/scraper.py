import re
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

# Importar nuevos módulos de auditoría profunda
from whois_lookup import extract_whois_data, extract_contact_hints
from site_crawler import crawl_website
from business_extractor import extract_business_data
from proposal_generator import ProposalGenerator


async def scrape_website(url: str, prospecto_id: int = None):
    """
    Auditoría web profunda de 4 fases:
    1. WHOIS Lookup - Datos del dominio
    2. Site Crawling - Recorrido multi-página
    3. Business Extraction - Datos de contacto y negocio
    4. Análisis Técnico UX/UI - Métricas de performance y usabilidad
    """
    if not url.startswith("http"):
        url = "https://" + url

    print(f"\n{'='*60}")
    print(f"[AUDITORÍA PROFUNDA] Iniciando: {url}")
    print('='*60)

    # ========== FASE 1: WHOIS LOOKUP ==========
    print("\n[FASE 1/4] Consultando WHOIS...")
    try:
        whois_data = extract_whois_data(url)
        whois_hints = extract_contact_hints(whois_data)
        print(f"✓ WHOIS completado - Registrante: {whois_data.get('registrante') or 'N/A'}")
    except Exception as e:
        print(f"✗ Error WHOIS: {e}")
        whois_data = {"error": str(e)}
        whois_hints = {}

    # ========== FASE 2: SITE CRAWLING ==========
    print("\n[FASE 2/4] Crawling del sitio (hasta 15 páginas)...")
    try:
        crawl_results = await crawl_website(url, max_pages=15)
        print(f"✓ Crawling completado - {crawl_results['total_pages']} páginas recorridas")
        print(f"  Emails encontrados: {len(crawl_results['emails_found'])}")
        print(f"  Teléfonos encontrados: {len(crawl_results['phones_found'])}")
    except Exception as e:
        print(f"✗ Error Crawling: {e}")
        crawl_results = {"pages": [], "total_pages": 0, "emails_found": [], "phones_found": []}

    # ========== FASE 3: BUSINESS DATA EXTRACTION (Traditional) ==========
    print("\n[FASE 3/4] Extrayendo datos de negocio (Scraping tradicional)...")
    business_data = {
        "nombre_dueno": None,
        "cargo_dueno": None,
        "email_dueno": None,
        "telefono_dueno": None,
        "telefono_empresa": None,
        "direccion": None,
        "ciudad": None,
        "provincia": None,
        "redes_sociales": {},
        "fuente_datos": []
    }

    # Procesar cada página para extraer datos de negocio (Sin IA en esta fase)
    for page in crawl_results.get("pages", []):
        if page.get("has_contact_info") or any(x in page["url"].lower() for x in ["about", "nosotros", "contact", "team", "equipo"]):
            try:
                page_business = extract_business_data(
                    html=page.get("html", ""),
                    url=page["url"],
                    page_title=page.get("title", "")
                )

                # Merge datos de negocio
                for key in ["nombre_dueno", "cargo_dueno", "email_dueno", "telefono_dueno", "telefono_empresa"]:
                    if page_business.get(key) and not business_data.get(key):
                        business_data[key] = page_business[key]

                if page_business.get("direccion") and not business_data["direccion"]:
                    business_data["direccion"] = page_business["direccion"]
                    business_data["ciudad"] = page_business.get("ciudad")
                    business_data["provincia"] = page_business.get("provincia")

                if page_business.get("redes_sociales"):
                    business_data["redes_sociales"].update(page_business["redes_sociales"])

            except Exception as e:
                print(f"  ⚠ Error extrayendo datos de {page['url']}: {e}")
                continue

    print(f"✓ Datos base completados. La IA procesará el análisis final al terminar.")

    # ========== FASE 4: ANÁLISIS TÉCNICO PROFUNDO (Home Page) ==========
    print("\n[FASE 4/4] Análisis técnico profundo (Home Page)...")
    
    try: # Try general de Fase 4 + Master Call
        # Inicialización DE VALORES POR DEFECTO
        tech_analysis = {
            "performance": {"loadTime": 0, "totalSizeKB": 0, "resourcesCount": 0},
            "seo": {"h1Count": 0, "imagesSinAlt": 0, "description": ""},
            "ux": {"smallOnesCount": 0, "hasHScroll": False, "menuItemsCount": 0, "formsCount": 0, "formsWithoutLabelsCount": 0, "lowContrastCount": 0},
            "tech_stack": [],
            "score_tecnico": 0,
            "ssl": "NO"
        }

        pilares = {
            "Seguridad": {"estado": "desconocido", "detalle": "No analizado"},
            "Performance": {"estado": "desconocido", "detalle": "No analizado"},
            "SEO": {"estado": "desconocido", "detalle": "No analizado"},
            "Accesibilidad": {"estado": "desconocido", "detalle": "No analizado"},
            "UX/UI": {"estado": "desconocido", "detalle": "No analizado"}
        }
        
        puntos_dolor = []
        html_content = ""
        access_error = None

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800},
                    ignore_https_errors=True
                )
                page = await context.new_page()

                try:
                    # IMPLEMENTACIÓN v4.8.1: Stealth Mode
                    # Usar headers más humanos para saltar WAFs básicos
                    await context.set_extra_http_headers({
                        "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "none",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1"
                    })

                    # INYECCIÓN STEALTH (Ocultar huella de WebDriver y Canvas)
                    await context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                        Object.defineProperty(navigator, 'languages', { get: () => ['es-AR', 'es', 'en-US', 'en'] });
                        // Spoof simple de WebGL vendor
                        const getParameter = WebGLRenderingContext.prototype.getParameter;
                        WebGLRenderingContext.prototype.getParameter = function(parameter) {
                            if (parameter === 37445) return 'Intel Inc.';
                            if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                            return getParameter.apply(this, arguments);
                        };
                    """)

                    start_time = asyncio.get_event_loop().time()
                    
                    # Llamada a PageSpeed en background (Concurrencia)
                    from pagespeed_api import fetch_pagespeed_data
                    pagespeed_task = asyncio.create_task(fetch_pagespeed_data(url))

                    # wait_until="networkidle" es más seguro para challenges pero puede tardar. 
                    # Usamos domcontentloaded + un sleep generoso.
                    response = await page.goto(url, timeout=60000, wait_until="domcontentloaded")
                    
                    # RETRASO DE EVASIÓN (Stealth v4.8.1)
                    # 5 segundos permiten que los retos de "Checking your browser" se resuelvan
                    await asyncio.sleep(5)

                    html_raw = await page.content()
                    
                    # === INTEGRACIÓN WAPPALYZER (IN-MEMORY) ===
                    try:
                        from Wappalyzer import Wappalyzer, WebPage
                        wappalyzer = Wappalyzer.latest()
                        headers = response.headers if response else {}
                        webpage = WebPage(url, html=html_raw, headers=headers)
                        wapp_result = wappalyzer.analyze_with_categories(webpage)
                        
                        tech_stack_dict = {}
                        for tech_name, details in wapp_result.items():
                            version = details.get('version') or details.get('versions') or ''
                            # Normalizar: si version es lista tomar el primero
                            if isinstance(version, list):
                                version = version[0] if version else ''
                            tech_stack_dict[tech_name] = {
                                "categories": details.get('categories', []),
                                "version": version.strip() if version else ''
                            }
                        
                        tech_analysis["tech_stack"] = tech_stack_dict
                        print(f"✓ Wappalyzer: detectadas {len(tech_stack_dict)} tecnologías en memoria")
                    except Exception as e:
                        print(f"  ⚠ Error Wappalyzer: {e}")
                    
                    # LIMPIEZA DE HTML v2 (Detox Estratégico)
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html_raw, "html.parser")
                    # Eliminar ruido técnico puro pero conservar arquitectura
                    for s in soup(["script", "style", "svg", "iframe", "noscript"]):
                        s.extract()
                    
                    # Limpiar atributos basura de TODAS las etiquetas pero mantener los estratégicos
                    atribs_a_conservar = ['alt', 'title', 'aria-label', 'role', 'href', 'id', 'name']
                    for tag in soup.find_all(True):
                        atribs_actuales = list(tag.attrs.keys())
                        for attr in atribs_actuales:
                            if attr not in atribs_a_conservar:
                                del tag[attr]
                                
                    html_content = str(soup)[:6000] # Un poco más de contexto para el modelo Pro

                    # Performance Detallada
                    performance_metrics = await page.evaluate("""() => {
                        const nav = performance.getEntriesByType('navigation')[0] || {};
                        const paint = performance.getEntriesByType('paint');
                        const fcp = paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0;
                        return {
                            loadTime: Math.round(fcp || nav.domContentLoadedEventEnd - nav.startTime) || 0,
                            totalSizeKB: Math.round(performance.getEntriesByType('resource').reduce((acc, r) => acc + (r.transferSize || 0), 0) / 1024),
                            resourcesCount: performance.getEntriesByType('resource').length
                        };
                    }""")
                    
                    # Esperar resultado de PageSpeed Insights API (timeout total en pagespeed configurado a 60s)
                    try:
                        pagespeed_results = await pagespeed_task
                        if pagespeed_results:
                            performance_metrics.update(pagespeed_results)
                        else:
                            performance_metrics.update({"score": 0, "lcp": None, "cls": None, "inp": None, "data_origin": "error"})
                    except Exception as e:
                        print(f"  ⚠ PageSpeed Task Error: {e}")
                        performance_metrics.update({"score": 0, "lcp": None, "cls": None, "inp": None, "data_origin": "error"})
                        
                    tech_analysis["performance"].update(performance_metrics)

                    # SEO & Schema (Implementando enseñanzas del skill seo-audit)
                    seo_data = await page.evaluate("""() => {
                        const getMeta = (n) => document.querySelector(`meta[name="${n}"], meta[property="${n}"]`)?.content || null;
                        const schemaNodes = document.querySelectorAll('script[type="application/ld+json"]');
                        const schemas = Array.from(schemaNodes).map(s => {
                            try { return JSON.parse(s.innerText)['@type'] || 'Custom'; } catch(e) { return 'Invalid'; }
                        });
                        
                        return {
                            h1Count: document.querySelectorAll('h1').length,
                            h1Text: Array.from(document.querySelectorAll('h1')).map(h => h.innerText.trim()).join(' | '),
                            imagesSinAlt: Array.from(document.querySelectorAll('img')).filter(img => !img.alt).length,
                            imagesTotal: document.querySelectorAll('img').length,
                            description: getMeta('description'),
                            descriptionLen: getMeta('description')?.length || 0,
                            title: document.title,
                            author: getMeta('author') || getMeta('copyright'),
                            keywords: getMeta('keywords'),
                            location: getMeta('geo.placename') || getMeta('business:contact_data:locality'),
                            lat: getMeta('geo.position')?.split(';')[0] || getMeta('ICBM')?.split(',')[0],
                            lng: getMeta('geo.position')?.split(';')[1] || getMeta('ICBM')?.split(',')[1],
                            hasSchema: schemas.length > 0,
                            schemaTypes: schemas.slice(0, 5)
                        };
                    }""")
                    tech_analysis["seo"].update(seo_data)

                    # UX & Accessibility (Métricas de impacto visual)
                    ux_data = await page.evaluate("""() => {
                        const buttons = Array.from(document.querySelectorAll('button, a, input[type="submit"]'));
                        return {
                            smallOnesCount: buttons.filter(el => {
                                const r = el.getBoundingClientRect();
                                return r.width > 0 && (r.width < 44 || r.height < 44);
                            }).length,
                            hasHScroll: document.documentElement.scrollWidth > document.documentElement.clientWidth,
                            menuItemsCount: document.querySelectorAll('nav a, header a, .menu a').length,
                            formsCount: document.querySelectorAll('form').length,
                            formsWithoutLabelsCount: Array.from(document.querySelectorAll('form')).filter(f => {
                                const inputs = f.querySelectorAll('input:not([type="hidden"]), textarea, select');
                                const labels = f.querySelectorAll('label');
                                return inputs.length > labels.length;
                            }).length,
                            lowContrastCount: 0 // Requiere análisis visual o computacional pesado
                        };
                    }""")
                    tech_analysis["ux"].update(ux_data)

                    # Pilares v3.0 (Lógica de Negocio Leo Baraldi)
                    is_insecure = not page.url.startswith("https")
                    tech_analysis["ssl"] = "SÍ" if not is_insecure else "NO"
                    
                    pilares["Seguridad"] = {
                        "estado": "critico" if is_insecure else "bueno", 
                        "detalle": "⚠️ SIN SSL: Riesgo de seguridad y penalización Google." if is_insecure else "✅ SSL Activo. Conexión cifrada detectada."
                    }
                    
                    p_time = tech_analysis["performance"]['loadTime']
                    pilares["Performance"] = {
                        "estado": "critico" if p_time > 5000 else ("alerta" if p_time > 2500 else "bueno"), 
                        "detalle": f"{'🐌 LENTA' if p_time > 2500 else '⚡ RÁPIDA'}: {p_time}ms carga total. {tech_analysis['performance']['totalSizeKB']}KB en {tech_analysis['performance']['resourcesCount']} recursos."
                    }
                    
                    s_h1 = tech_analysis["seo"]['h1Count']
                    s_desc = tech_analysis["seo"]['descriptionLen']
                    pilares["SEO"] = {
                        "estado": "critico" if s_h1 != 1 or s_desc < 100 else "bueno", 
                        "detalle": f"{s_h1} H1 | {'❌ Sin meta description' if s_desc < 10 else '✅ Meta OK'}. {tech_analysis['seo']['imagesSinAlt']} imágenes sin alt text."
                    }
                    
                    ux_small = tech_analysis["ux"]['smallOnesCount']
                    pilares["Accesibilidad"] = {
                        "estado": "critico" if ux_small > 10 else ("alerta" if ux_small > 0 else "bueno"), 
                        "detalle": f"{ux_small} botones pequeños | {tech_analysis['ux']['formsWithoutLabelsCount']} formularios sin labels."
                    }
                    
                    ux_scroll = tech_analysis["ux"]['hasHScroll']
                    pilares["UX/UI"] = {
                        "estado": "critico" if ux_scroll else "bueno", 
                        "detalle": f"{'❌ Desbordes horizontales' if ux_scroll else '✅ Estructura Adaptativa'}. Menú: {tech_analysis['ux']['menuItemsCount']} items."
                    }

                except Exception as e:
                    print(f"  ⚠ Playwright Timeout/Error: {e}")
                    access_error = str(e)
                    puntos_dolor.append(f"⚠️ Sitio inaccesible (Timeout 60s).")
                    for k in pilares: pilares[k] = {"estado": "critico", "detalle": "⚠️ Error de conexión"}

                await browser.close()
        except Exception as e:
            print(f"  ⚠ Error inicializando Playwright: {e}")
            access_error = str(e)

        # ========== FASE FINAL: MASTER AI CALL (DESACTIVADA v3.2) ==========
        print("\n[SCREAPER] Auditoría técnica completada. El orquestador generará el Prompt Maestro.")
        
        # Consolidamos los pilares técnicos para la visualización inicial
        informe_detallado_final = {"pilares": pilares}
        
        all_emails = set(crawl_results.get("emails_found", []))
        all_phones = set(crawl_results.get("phones_found", []))
        is_incomplete = len(all_emails) == 0 and len(all_phones) == 0

        urls_track = []
        for p in crawl_results.get("pages", []):
            if p.get("url"): urls_track.append(p["url"])

        # Mapeo manual de datos hallados al objeto final
        return {
            "status": "success" if not access_error else "partial",
            "url_auditada": url,
            "urls_visitadas": urls_track,
            "paginas_recorridas": crawl_results.get('total_pages', 0),
            "telefono": business_data.get("telefono_empresa") or (list(all_phones)[0] if all_phones else None),
            "whatsapp": business_data.get("whatsapp"),
            "email": business_data.get("email_dueno") or (list(all_emails)[0] if all_emails else None),
            "emails_encontrados": sorted(list(all_emails)),       # ← NUEVO: lista completa
            "telefonos_encontrados": sorted(list(all_phones)),    # ← NUEVO: lista completa
            "nombre_dueno": business_data.get("nombre_dueno"),
            "direccion": business_data.get("direccion"),
            "redes_sociales": business_data.get("redes_sociales", {}),
            "whois_data": whois_data,
            "audit_tecnico": tech_analysis,
            "informe_detallado": informe_detallado_final,
            "puntos_de_dolor": "⚠️ Auditoría técnica lista. Generá el prompt para el análisis estratégico.",
            "pitch_ia": "", # Se llenará manualmente vía Prompt Maestro
            "falla_encontrada": access_error if access_error else f"Análisis técnico completado",
            "is_incomplete": is_incomplete
        }

    except Exception as e:
        import traceback
        print(f"\n[ERROR CRÍTICO] {e}")
        print(traceback.format_exc())
        return {"status": "error", "falla_encontrada": str(e)[:50]}



def _build_partial_response(url, whois_data, crawl_results, business_data, error_msg):
    """Construye respuesta parcial cuando el sitio no carga pero tenemos datos de crawling/WHOIS."""

    puntos_dolor = [f"⚠️ El sitio no respondió completamente: {error_msg}"]

    if whois_data.get("antiguedad_anios") and whois_data["antiguedad_anios"] > 5:
        puntos_dolor.append(f"💡 El dominio tiene {whois_data['antiguedad_anios']} años. Probablemente sea un negocio establecido que necesita modernización.")

    # Consolidar datos disponibles
    all_emails = set(crawl_results.get("emails_found", []))
    all_phones = set(crawl_results.get("phones_found", []))
    is_incomplete = len(all_emails) == 0 and len(all_phones) == 0

    return {
        "status": "partial",
        "falla_encontrada": f"⚠️ Sitio inaccesible: {error_msg}",
        "url_auditada": url,
        "paginas_recorridas": crawl_results.get("total_pages", 0),
        "emails_encontrados": list(all_emails) if all_emails else None,
        "telefonos_encontrados": list(all_phones) if all_phones else None,
        "telefono": list(all_phones)[0] if all_phones else None,
        "email": list(all_emails)[0] if all_emails else None,
        "nombre_dueno": business_data.get("nombre_dueno") if business_data.get("nombre_dueno") else None,
        "direccion": business_data.get("direccion") if business_data.get("direccion") else None,
        "whois_data": whois_data if whois_data else None,
        "puntos_de_dolor": "\n\n".join(puntos_dolor) if puntos_dolor else None,
        "informe_detallado": {
            "pilares": {
                "Accesibilidad": {"estado": "desconocido", "detalle": "No se pudo analizar - sitio inaccesible"},
                "Performance": {"estado": "desconocido", "detalle": "No se pudo analizar"}
            }
        } if not is_incomplete else None,
        "is_incomplete": is_incomplete
    }


# Mantener backward compatibility
import asyncio

if __name__ == "__main__":
    # Prueba
    async def test():
        result = await scrape_website("https://ejemplo.com")
        print("\n" + "="*60)
        print("RESULTADO COMPLETO")
        print("="*60)
        print(f"Status: {result['status']}")
        print(f"Páginas: {result['paginas_recorridas']}")
        print(f"Dueño: {result.get('nombre_dueno')}")
        print(f"Teléfono: {result.get('telefono')}")
        print(f"Dirección: {result.get('direccion')}")

    asyncio.run(test())
