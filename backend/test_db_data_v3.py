import models
from database import SessionLocal
import json
import logging

# Disable sqlalchemy logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

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
ux = audit.get("ux", {})

print("--- RESULTS START ---")
print(f"perf_loadTime: {perf.get('loadTime', 'N/A')}")
print(f"perf_totalSizeKB: {perf.get('totalSizeKB', 'N/A')}")
print(f"perf_resourcesCount: {perf.get('resourcesCount', 'N/A')}")
print(f"seo_h1: {seo.get('h1Count', 'N/A')}")
print(f"seo_imagesSinAlt: {seo.get('imagesSinAlt', 'N/A')}")
print(f"ux_small: {ux.get('smallOnesCount', 'N/A')}")
print(f"ux_scroll: {ux.get('hasHScroll', 'N/A')}")
print(f"audit_keys: {list(audit.keys())}")
print("--- RESULTS END ---")

db.close()
