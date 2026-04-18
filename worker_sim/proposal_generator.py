import os
import random
import google.generativeai as genai
from dotenv import load_dotenv
from ai_utils import AIRateLimiter, get_best_model

# Cargar configuración de entorno
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("[WARNING] GOOGLE_API_KEY no encontrada. El generador usará plantillas estáticas.")

class ProposalGenerator:
    """
    Generador de propuestas comerciales avanzado (v2.7.0).
    Utiliza Gemini AI para humanizar el pitch y mimetizar el estilo de Leo Baraldi.
    """

    LANDINGS = {
        "agtech": "https://leobaraldi.com.ar/desarrollo-software-agropecuario-agtech/",
        "oil_gas": "https://leobaraldi.com.ar/ux-ui-desarrollo-industria-petrolera/",
        "diseno": "https://leobaraldi.com.ar/diseno/",
        "desarrollo": "https://leobaraldi.com.ar/desarrollo/",
        "general": "https://leobaraldi.com.ar/desarrollo-digital-a-medida/"
    }

    CONTACT_INFO = {
        "email": "hola@leobaraldi.com.ar",
        "tel": "+54 351 7543864",
        "linkedin": "https://www.linkedin.com/in/leobaraldi/",
        "cta_contact": "https://leobaraldi.com.ar/contacto/"
    }

    @staticmethod
    def _detect_best_landing(audit_data, url):
        text_to_scan = f"{url} {audit_data.get('puntos_de_dolor', '')}".lower()
        if any(kw in text_to_scan for kw in ["campo", "agtech", "agro", "siembra", "cosecha", "vaca", "granja"]):
            return ProposalGenerator.LANDINGS["agtech"]
        if any(kw in text_to_scan for kw in ["oil", "gas", "petrol", "drill", "refine", "energy", "vaca muerta"]):
            return ProposalGenerator.LANDINGS["oil_gas"]
        if any(kw in text_to_scan for kw in ["ux", "ui", "diseno", "design", "estetico", "interfaz"]):
            return ProposalGenerator.LANDINGS["diseno"]
        if any(kw in text_to_scan for kw in ["dev", "desarrollo", "software", "app", "web", "api"]):
            return ProposalGenerator.LANDINGS["desarrollo"]
        return ProposalGenerator.LANDINGS["general"]

    @staticmethod
    def generate_pitch(audit_data, company_name, url="", owner_name=None, past_edits=None, prospecto_id=None):
        """
        Punto de entrada principal. Intenta usar Gemini; si falla, usa el template v2.6.0.
        """
        best_landing = ProposalGenerator._detect_best_landing(audit_data, url)
        
        if GOOGLE_API_KEY:
            try:
                return ProposalGenerator._generate_pitch_ai(audit_data, company_name, url, owner_name, best_landing, past_edits, prospecto_id)
            except Exception as e:
                print(f"[ERROR Gemini] {e}. Usando fallback de plantilla.")
        
        return ProposalGenerator._generate_pitch_template(audit_data, company_name, url, owner_name, best_landing)

    @staticmethod
    def _generate_pitch_ai(audit_data, company_name, url, owner_name, best_landing, past_edits=None, prospecto_id=None):
        """Generación dinámica con Gemini AI (v2.8.0)."""
        # Esperar cuota antes de generar pitch
        AIRateLimiter.wait_if_needed(prospecto_id)
        
        model = genai.GenerativeModel(get_best_model())
        
        puntos_dolor = audit_data.get("puntos_de_dolor", "Fallas generales de UX y performance.")
        owner = owner_name if owner_name else "equipo"

        # Los past_edits van PRIMERO como marco de referencia de tono, no al final como apéndice
        estilo_context = ""
        if past_edits:
            estilo_context = f"""REFERENCIA DE ESTILO REAL (mensajes anteriores editados y aprobados por Leo):
---
{past_edits}
---
Matcheá exactamente este registro: mismo nivel de formalidad, misma longitud, mismo tipo de apertura.
No copies literalmente, pero sí el patrón: cómo arranca, cómo conecta el problema con el negocio y cómo cierra.\n\n"""

        system_prompt = f"""{estilo_context}Sos Leo Baraldi (https://leobaraldi.com.ar), experto Senior en Diseño de Producto y Estrategia Digital con más de 25 años de experiencia.

Escribís mensajes de primer contacto para potenciales clientes. Tu voz es cálida, directa y con autoridad natural — no vendés, mostrás lo que ves y proponés una charla.

CONTEXTO DEL PROSPECTO:
- Empresa: {company_name}
- Sitio web: {url}
- Responsable: {owner}
- Problemas detectados en el sitio: {puntos_dolor}

LO QUE TENÉS QUE COMUNICAR (sin decirlo literalmente):
→ Viste su sitio y notaste algo concreto que hoy le está costando dinero o confianza.
→ Eso tiene solución puntual, y vos sabés exactamente cómo.
→ No le pedís nada pesado: solo 15 minutos para explicarle qué viste.

REGLAS DURAS:
- NO abrir con "Hola, revisé tu sitio y encontré X problemas". Eso suena a spam.
- NO listar errores técnicos. Máximo un hallazgo, mencionado como impacto en el negocio (no como error).
- NO usar "Che", "copado", "bárbaro", "laburo", "genial".
- NO sonar corporativo. Nada de "Me dirijo a usted" ni eufemismos de ventas.
- SÍ usar español argentino muy sutil: "podés", "querés", "chequear" cuando caiga natural.
- El tono debe transmitir que ya sabés lo que necesitan, no que estás vendiendo.
- Incluir este link de portfolio como CTA natural (no como "hacé clic acá"): {best_landing}
- Longitud: máximo 3 párrafos. Ni uno más.

FIRMA OBLIGATORIA AL FINAL (no modificar):
Un abrazo,
Leo Baraldi
Diseñador de Producto & Strategist
📱 WhatsApp: {ProposalGenerator.CONTACT_INFO['tel']}
✉️ {ProposalGenerator.CONTACT_INFO['email']}
🌐 LinkedIn: {ProposalGenerator.CONTACT_INFO['linkedin']}
"""

        user_content = f"Escribí el mensaje para {company_name}. Dueño: {owner}."
        
        response = model.generate_content(system_prompt + "\n\n" + user_content)
        return response.text

    @staticmethod
    def _generate_pitch_template(audit_data, company_name, url, owner_name, best_landing):
        """Fallback estático v2.8.0 — tono humano, sin listar errores técnicos."""
        puntos_dolor = audit_data.get("puntos_de_dolor", "")
        owner = owner_name if owner_name else f"equipo de {company_name}"

        # Convertir el primer punto de dolor en un impacto de negocio, no en un error técnico
        primer_hallazgo = ""
        if puntos_dolor:
            lineas = [l.strip() for l in puntos_dolor.strip().split("\n") if l.strip()]
            if lineas:
                primer_hallazgo = f"Estuve mirando {url} y hay algo puntual que me llamó la atención: {lineas[0].lstrip('-•').strip().lower()}. Eso suele traducirse en consultas que no llegan."

        saludo = f"Hola {owner},"
        intro = primer_hallazgo if primer_hallazgo else f"Estuve mirando el sitio de {company_name} y hay un par de cosas que te podrían estar costando consultas sin que te des cuenta."
        propuesta = f"\n\nTengo algunas ideas concretas para resolverlo. Si te interesa, podemos charlar 15 minutos esta semana — sin compromiso.\n{best_landing}"
        firma = f"\n\nUn abrazo,\nLeo Baraldi\n{ProposalGenerator.CONTACT_INFO['tel']}\n{ProposalGenerator.CONTACT_INFO['email']}"
        return saludo + "\n\n" + intro + propuesta + firma

    @staticmethod
    def get_whatsapp_formatted(pitch):
        return pitch

    @staticmethod
    def get_email_formatted(pitch, company_name):
        # Asunto que genera curiosidad sin revelar el diagnóstico (evita spam filters)
        subjects = [
            f"Algo que vi en el sitio de {company_name}",
            f"Una observación sobre {company_name}",
            f"Consulta rápida — {company_name}",
        ]
        subject = random.choice(subjects)
        return {"subject": subject, "body": pitch}
