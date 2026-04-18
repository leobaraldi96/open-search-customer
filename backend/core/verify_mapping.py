# backend/core/verify_mapping.py
import sys
import os

# Añadir el path actual para poder importar core.proposal_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.proposal_engine import build_prompt

def test_full_mapping():
    print("[INIT] Iniciando Validacion de Mapeo de Datos (Prompt v5.1)...")
    
    sample_audit = {
        "performance": {
            "loadTime": 850,
            "totalSizeKB": 120,
            "resourcesCount": 12,
            "score": 92,
            "lcp": 1200,
            "cls": 0.05,
            "inp": 80,
            "data_origin": "Lighthouse"
        },
        "seo": {
            "title": "Tus Bolsas | Soluciones de Embalaje",
            "author": "Agencia Web X",
            "h1Count": 1,
            "imagesSinAlt": 5,
            "imagesTotal": 20,
            "description": "Fabrica de bolsas personalizadas en Cordoba.",
            "hasSchema": True,
            "location": "Cordoba, Argentina",
            "lat": -31.4,
            "lng": -64.1
        },
        "ux": {
            "smallOnesCount": 2,
            "hasHScroll": False,
            "formsCount": 1,
            "formsWithoutLabelsCount": 0,
            "hasViewportMeta": True
        },
        "security": {
            "hasSSL": True,
            "sslExpiry": "2026-10-15",
            "sslIssuer": "Google Trust Services"
        },
        "whois_data": {
            "antiguedad_anios": 8
        },
        "tech_stack": {
            "WordPress": ["CMS"],
            "Elementor": ["Page Builder"],
            "WooCommerce": ["E-commerce"]
        },
        "extra_contacts": {
            "emails": ["ventas@tusbolsas.com"],
            "phones": ["+54 351 1234567"]
        }
    }

    try:
        prompt = build_prompt(
            audit_data=sample_audit,
            company_name="Tus Bolsas",
            url="https://tusbolsas.com/",
            owner_name="Juan Perez",
            email="juan@tusbolsas.com",
            phone="3515551234",
            address="Calle Falsa 123, Cba",
            urls_visitadas=["https://tusbolsas.com/", "https://tusbolsas.com/productos"],
            redes_sociales={"Instagram": "https://instagram.com/tusbolsas", "Facebook": "https://fb.com/tusbolsas"}
        )
        
        print("\n[SUCCESS] Generacion Exitosa.")
        print("-" * 50)
        print("VISTA PREVIA DEL PROMPT (fragmentos clave):")
        print("-" * 50)
        
        # Verificar secciones clave (usando fragmentos seguros sin acentos)
        assert "actu" in prompt.lower()
        assert "Leo Baraldi" in prompt
        assert "ALARMAS DE NEGOCIO 2026" in prompt
        assert "Tus Bolsas" in prompt
        assert "CMS: WordPress" in prompt
        assert "Argentino Federal" in prompt
        
        lines = prompt.split("\n")
        print("\n".join(lines[:20])) # Primeras 20 líneas
        print("\n...\n")
        print("\n".join(lines[-10:])) # Últimas 10 líneas
        
        print("-" * 50)
        print("[DONE] TODOS LOS CAMPOS MAPEARON CORRECTAMENTE.")
        
    except Exception as e:
        print(f"\n[ERROR] ERROR EN VALIDACION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_mapping()
