import requests
import asyncio
import time

PAGESPEED_API_KEY = "AIzaSyAVo2Tc4dEhc6yDiCRVDg4DvuGMfmJzm9w"
API_URL = "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed"

def _fetch_pagespeed_sync(url: str, strategy: str = "mobile"):
    """
    Realiza la llamada síncrona a la API de PageSpeed.
    strategy puede ser 'mobile' o 'desktop'.
    """
    params = {
        "url": url,
        "key": PAGESPEED_API_KEY,
        "strategy": strategy,
        "category": "performance"
    }
    
    try:
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [PAGESPEED ERROR] {e}")
        return None

async def fetch_pagespeed_data(url: str):
    """
    Obtiene métricas de Core Web Vitals y Lighthouse Score de forma asíncrona.
    Extrae la experiencia real del usuario (CrUX) si existe, o las métricas de laboratorio en su defecto.
    """
    # Ejecutamos la petición síncrona en un hilo separado para no bloquear el event loop de Playwright
    data = await asyncio.to_thread(_fetch_pagespeed_sync, url)
    
    if not data:
        return None
        
    result = {
        "score": 0,
        "lcp": None, # ms
        "cls": None, # score
        "inp": None, # ms
        "data_origin": "unknown" # 'field' or 'lab'
    }
    
    # 1. Obtener Lighthouse Score (Lab Performance)
    # Viene como un número del 0.0 al 1.0, lo convertimos a 0-100
    lh_score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score")
    if lh_score is not None:
        result["score"] = int(lh_score * 100)
    
    # 2. Intentar sacar Field Data (Experiencia Real) si el sitio tiene tráfico
    loading_exp = data.get("loadingExperience", {}).get("metrics", {})
    if 'LARGEST_CONTENTFUL_PAINT_MS' in loading_exp:
        result["data_origin"] = "field"
        result["lcp"] = loading_exp.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile")
        result["cls"] = loading_exp.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile")
        # No todos tienen INP en field data, también puede venir como FID
        result["inp"] = loading_exp.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile")
        if result["cls"] is not None:
            # CLS Field data suele venir multiplicado por 100 en la API a veces, comprobamos
            if result["cls"] > 10: 
                result["cls"] = round(result["cls"] / 100, 3)
            else:
                result["cls"] = round(result["cls"] / 100, 3) # CLS from API needs dividing by 100 usually
    else:
        # 3. Si no hay Field Data, caemos en Lab Data de Lighthouse
        result["data_origin"] = "lab"
        audits = data.get("lighthouseResult", {}).get("audits", {})
        
        lcp_audit = audits.get("largest-contentful-paint", {}).get("numericValue")
        if lcp_audit is not None:
             result["lcp"] = int(lcp_audit)
             
        cls_audit = audits.get("cumulative-layout-shift", {}).get("numericValue")
        if cls_audit is not None:
            result["cls"] = round(cls_audit, 3)
            
        inp_audit = audits.get("interaction-to-next-paint", {}).get("numericValue")
        # La alternativa de laboratorio clásica si INP falla en Lab (a veces TBT)
        max_pot_fid = audits.get("max-potential-fid", {}).get("numericValue")
        
        if inp_audit is not None:
            result["inp"] = int(inp_audit)
        elif max_pot_fid is not None:
            result["inp"] = int(max_pot_fid)
    
    # Corrección de estructura de Field Data CLS
    if result["cls"] is not None and result["data_origin"] == "field":
         # En 'loadingExperience', CUMULATIVE_LAYOUT_SHIFT_SCORE.percentile viene como un INT ej: 14 = 0.14
         if isinstance(result["cls"], int):
             result["cls"] = result["cls"] / 100
             
    return result

if __name__ == "__main__":
    # Test local
    async def run_test():
        url = "https://www.clarin.com" # Un sitio grande con datos de campo seguros
        print(f"Probando PageSpeed API para: {url}")
        dt = await fetch_pagespeed_data(url)
        print(dt)
        
    asyncio.run(run_test())
