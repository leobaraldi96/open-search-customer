import models
from database import SessionLocal
import json
from proposal_engine import ProposalGenerator

db = SessionLocal()
lead = db.query(models.Prospecto).filter(models.Prospecto.id == 24).first()

def ensure_dict(field):
    if not field: return {}
    if isinstance(field, str):
        try: return json.loads(field)
        except: return {}
    return field

audit_tecnico = ensure_dict(lead.audit_tecnico)
whois = ensure_dict(lead.whois_data)

audit_data = {
    "performance": audit_tecnico.get("performance", {}),
    "seo": audit_tecnico.get("seo", {}),
    "ux": audit_tecnico.get("ux", {}),
    "whois_data": whois,
    "puntos_de_dolor": lead.puntos_de_dolor or "No detectados",
    "email": lead.email,
    "telefono": lead.telefono,
    "direccion": lead.direccion
}

print("--- EXECUTING BUILD_MANUAL_PROMPT ---")
prompt = ProposalGenerator.build_manual_prompt(
    audit_data, 
    lead.empresa, 
    lead.url, 
    lead.nombre_dueno, 
    "https://leobaraldi.com.ar/test"
)
print(prompt)
print("--- END ---")

db.close()
