import os
from dotenv import load_dotenv, find_dotenv

# Cargar configuración de entorno
load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────

LANDINGS = {
    "agtech":          "https://leobaraldi.com.ar/desarrollo-software-agropecuario-agtech/",
    "oil_gas":         "https://leobaraldi.com.ar/ux-ui-desarrollo-industria-petrolera/",
    "manufactura":     "https://leobaraldi.com.ar/desarrollo-de-software-industrial-y-diseno-ux-para-manufactura/",
    "constructoras":   "https://leobaraldi.com.ar/desarrollo-de-software-para-constructoras-y-gestion-de-obra/",
    "diseno_uxui":     "https://leobaraldi.com.ar/diseno-ux-ui-productos-digitales/",
    "diseno":          "https://leobaraldi.com.ar/diseno/",
    "desarrollo":      "https://leobaraldi.com.ar/desarrollo/",
    "ecommerce":       "https://leobaraldi.com.ar/desarrollo-digital-a-medida/",
    "ia_auto":         "https://leobaraldi.com.ar/desarrollo/",
    "branding":        "https://leobaraldi.com.ar/diseno/",
    "capacitacion":    "https://leobaraldi.com.ar/contactame/",
    "general":         "https://leobaraldi.com.ar/desarrollo-digital-a-medida/",
    "contacto":        "https://leobaraldi.com.ar/contactame/",
}

# Firma simplificada (solo cierre, el resto va en el template del mailer)
FIRMA = "Un abrazo,"


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _format_val(val, default="N/A"):
    """Convierte None, vacío y bool a string limpio.
    Nota: el chequeo de bool debe ir ANTES del chequeo de falsiness
    porque False es falsy y sería capturado por 'if not val'.
    """
    if isinstance(val, bool):
        return "SÍ" if val else "NO"
    if val is None or val == "None" or val == "":
        return default
    return str(val)


def _detect_landing(audit_data: dict, url: str) -> str:
    """
    Detecta el CTA más adecuado por keywords en URL y pain points.
    Fallback: 'general'.
    """
    text = f"{url} {audit_data.get('puntos_de_dolor', '')}".lower()
    if any(kw in text for kw in ["campo", "agtech", "agro", "siembra", "cosecha", "granja", "cultivo", "ganaderia"]):
        return LANDINGS["agtech"]
    if any(kw in text for kw in ["oil", "gas", "petrol", "drill", "refine", "vaca muerta", "energia", "mineria"]):
        return LANDINGS["oil_gas"]
    if any(kw in text for kw in ["manufactura", "industrial", "fabrica", "planta", "maquinaria", "industria", "autopart"]):
        return LANDINGS["manufactura"]
    if any(kw in text for kw in ["construct", "obra", "inmobili", "arquitect", "edificio", "developer", "proptech", "fideicomiso"]):
        return LANDINGS["constructoras"]
    if any(kw in text for kw in ["tienda", "ecommerce", "e-commerce", "woocommerce", "shop", "venta online", "carrito"]):
        return LANDINGS["ecommerce"]
    if any(kw in text for kw in ["inteligencia artificial", " ia ", "automatiz", "bot", "chatbot", "crm", "flujo"]):
        return LANDINGS["ia_auto"]
    if any(kw in text for kw in ["marca", "identidad", "branding", "logo", "comunicacion", "imagen corporativa"]):
        return LANDINGS["branding"]
    if any(kw in text for kw in ["capacitacion", "mentoria", "formacion", "equipo", "entrenamiento"]):
        return LANDINGS["capacitacion"]
    if any(kw in text for kw in ["ux", "ui", "diseno", "design", "interfaz", "experiencia de usuario", "producto digital"]):
        return LANDINGS["diseno_uxui"]
    if any(kw in text for kw in ["dev", "desarrollo", "software", "app", "web", "api", "saas", "startup"]):
        return LANDINGS["desarrollo"]
    return LANDINGS["general"]


def _extract_scraping(audit_data: dict) -> dict:
    """
    Extrae campos del scraping con fallback case-insensitive.
    Devuelve un dict con valores ya formateados como string.
    """
    perf  = audit_data.get("performance") or audit_data.get("Performance") or {}
    seo   = audit_data.get("seo")         or audit_data.get("SEO")         or {}
    ux    = audit_data.get("ux")          or audit_data.get("UX")          or {}
    whois = audit_data.get("whois_data")  or audit_data.get("Whois")       or {}
    stack = audit_data.get("tech_stack")  or audit_data.get("Tech Stack")  or []

    if isinstance(stack, list):
        stack_str = ", ".join(stack) if stack else "N/A"
    elif isinstance(stack, dict):
        category_map = {}
        for tech, cats in stack.items():
            if not cats: cats = ["Other"]
            for c in cats:
                category_map.setdefault(c, []).append(tech)
        stack_parts = [f"{cat}: {', '.join(techs)}" for cat, techs in category_map.items()]
        stack_str = " | ".join(stack_parts) if stack_parts else "N/A"
    else:
        stack_str = _format_val(stack)

    # Ratios y nuevos campos v4.8.0
    imgs_total = seo.get("imagesTotal") or "N/A"
    imgs_ratio = f"{seo.get('imagesSinAlt', 0)} sin ALT de {imgs_total} totales"
    
    forms_total = ux.get("formsCount") or 0
    forms_ratio = f"{ux.get('formsWithoutLabelsCount', 0)} sin labels de {forms_total} totales"

    # SSL / HTTPS — campo crítico de seguridad
    security = audit_data.get("security") or audit_data.get("Security") or {}
    ssl_val = security.get("hasSSL") or security.get("ssl") or security.get("https")
    if ssl_val is None:
        # Fallback: inferir desde la propia URL analizada
        ssl_val = None  # se resolverá en build_prompt con la url real
    ssl_str = _format_val(ssl_val) if ssl_val is not None else "NO DETECTADO"
    ssl_expiry = _format_val(security.get("sslExpiry") or security.get("cert_expiry"))
    ssl_issuer = _format_val(security.get("sslIssuer") or security.get("cert_issuer"))

    # Responsive / Viewport
    viewport_ok = ux.get("hasViewportMeta") or ux.get("responsive") or ux.get("viewportMeta")
    responsive_str = _format_val(viewport_ok)

    # Contactos extra del scraping raw
    extra = audit_data.get("extra_contacts") or audit_data.get("contacts") or {}
    scraping_emails = ", ".join(extra.get("emails", [])) if extra.get("emails") else "No detectados"
    scraping_phones = ", ".join(extra.get("phones", []) + extra.get("whatsapps", [])) if (extra.get("phones") or extra.get("whatsapps")) else "No detectados"

    return {
        "title":           _format_val(seo.get("title")),
        "author":          _format_val(seo.get("author")),
        "load_time":       _format_val(perf.get("loadTime")        or perf.get("tiempoCarga")),
        "total_size":      _format_val(perf.get("totalSizeKB")     or perf.get("tamanoTotal")),
        "resources":       _format_val(perf.get("resourcesCount")  or perf.get("recursosCount")),
        "h1_count":        _format_val(seo.get("h1Count")          or seo.get("etiquetasH1")),
        "h1_text":         _format_val(seo.get("h1Text"), "No detectados"),
        "author":          _format_val(seo.get("author")           or seo.get("author_meta")),
        "imgs_ratio":      imgs_ratio,
        "meta_desc":       _format_val(seo.get("description")      or seo.get("metaDescription")),
        "has_schema":      _format_val(seo.get("hasSchema")),
        "schema_info":     ", ".join(seo.get("schemaTypes", [])) if seo.get("schemaTypes") else "Ninguno",
        "small_btns":      _format_val(ux.get("smallOnesCount")    or ux.get("botonesPequenos")),
        "h_scroll":        _format_val(ux.get("hasHScroll")        or ux.get("scrollHorizontal")),
        "forms_ratio":     forms_ratio,
        "location":        _format_val(seo.get("location")),
        "coords":          f"Lat: {seo.get('lat', 'N/A')} | Lng: {seo.get('lng', 'N/A')}",
        "domain_age":      _format_val(whois.get("antiguedad_anios") or whois.get("antiguedad")),
        "stack":           stack_str,
        "google_score":    _format_val(perf.get("score"), "N/A"),
        "lcp":             _format_val(perf.get("lcp"), "N/A"),
        "cls":             _format_val(perf.get("cls"), "N/A"),
        "inp":             _format_val(perf.get("inp"), "N/A"),
        "data_origin":     _format_val(perf.get("data_origin"), "N/A"),
        # Seguridad
        "ssl":             ssl_str,
        "ssl_expiry":      ssl_expiry,
        "ssl_issuer":      ssl_issuer,
        # UX adicional
        "responsive":      responsive_str,
        # Contactos del scraping
        "scraping_emails": scraping_emails,
        "scraping_phones": scraping_phones,
    }


# ─────────────────────────────────────────────
# GENERADOR PRINCIPAL
# ─────────────────────────────────────────────

from core.prompts import MASTER_PROMPT_TEMPLATE

def build_prompt(
    audit_data: dict,
    company_name: str,
    url: str = "",
    owner_name: str = None,
    email: str = None,
    phone: str = None,
    address: str = None,
    urls_visitadas: list = None,
    redes_sociales: dict = None,
    observaciones_humanas: str = None,
) -> str:
    """
    Genera el prompt v5.1 (Modular + Observaciones Humanas) listo para pegar en Gemini Web.
    """
    s = _extract_scraping(audit_data)
    
    # Formatear traza y redes sociales
    trace_str = ", ".join(urls_visitadas[:5]) if urls_visitadas else "Solo Home Page"
    social_str = ", ".join([f"{k}: {v}" for k, v in redes_sociales.items()]) if redes_sociales else "No detectadas"

    # Inferir SSL desde la URL si el scraper no lo proveyó
    ssl_display = s["ssl"]
    if ssl_display == "NO DETECTADO":
        if url.startswith("https://"):
            ssl_display = "SÍ (inferido por URL)"
        elif url.startswith("http://"):
            ssl_display = "NO — URL en HTTP plano ⚠️"

    # Observaciones Humanas — fallback si no hay input
    obs_text = observaciones_humanas.strip() if observaciones_humanas and observaciones_humanas.strip() else "Sin observaciones adicionales del auditor en esta revisión."

    # Inyección de datos en el template modular
    prompt = MASTER_PROMPT_TEMPLATE.format(
        url=url,
        company_name=company_name,
        owner=_format_val(owner_name),
        p_email=_format_val(email),
        p_phone=_format_val(phone),
        p_addr=_format_val(address),
        ssl_display=ssl_display,
        ssl_expiry=s["ssl_expiry"],
        ssl_issuer=s["ssl_issuer"],
        title=s["title"],
        author=s["author"],
        google_score=s["google_score"],
        data_origin=s["data_origin"],
        lcp=s["lcp"],
        cls=s["cls"],
        inp=s["inp"],
        load_time=s["load_time"],
        total_size=s["total_size"],
        resources=s["resources"],
        h1_count=s["h1_count"],
        h1_text=s["h1_text"],
        imgs_ratio=s["imgs_ratio"],
        meta_desc=s["meta_desc"],
        has_schema=s["has_schema"],
        schema_info=s["schema_info"],
        responsive=s["responsive"],
        small_btns=s["small_btns"],
        h_scroll=s["h_scroll"],
        forms_ratio=s["forms_ratio"],
        scraping_emails=s["scraping_emails"],
        scraping_phones=s["scraping_phones"],
        location=s["location"],
        coords=s["coords"],
        domain_age=s["domain_age"],
        stack=s["stack"],
        social_str=social_str,
        trace_str=trace_str,
        observaciones_humanas=obs_text,
        FIRMA=FIRMA
    )

    return prompt.strip()


if __name__ == "__main__":
    # Ejemplo de uso
    sample_audit = {
        "performance": {"loadTime": 1136, "totalSizeKB": 264, "resourcesCount": 59, "score": 85, "data_origin": "LH"},
        "seo": {"h1Count": 15, "imagesSinAlt": 16, "description": "Residencia para adultos en Córdoba."},
        "ux": {"smallOnesCount": 23, "hasHScroll": False},
        "security": {"hasSSL": True, "sslExpiry": "2026-12-01", "sslIssuer": "Let's Encrypt"},
    }

    prompt = build_prompt(
        audit_data=sample_audit,
        company_name="Casa Sabia",
        url="https://www.casasabia.com.ar/",
    )

    print(prompt)
