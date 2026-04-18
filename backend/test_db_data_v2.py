import models
from database import SessionLocal
import json

db = SessionLocal()
lead = db.query(models.Prospecto).filter(models.Prospecto.id == 24).first()

def get_data(field):
    if not field: return {}
    if isinstance(field, str):
        try: return json.loads(field)
        except: return {}
    return field

audit = get_data(lead.audit_tecnico)
perf = audit.get("performance", {})
seo = audit.get("seo", {})

print("--- START DATA ---")
print(f"perf_loadTime: {perf.get('loadTime', 'N/A')}")
print(f"perf_totalSizeKB: {perf.get('totalSizeKB', 'N/A')}")
print(f"seo_h1: {seo.get('h1Count', 'N/A')}")
print(f"audit_keys: {list(audit.keys())}")
print("--- END DATA ---")

db.close()
