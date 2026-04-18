import models
from database import SessionLocal
import json
import logging

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

with open("c:/xampp/htdocs/buscaclientes/backend/final_results.txt", "w") as f:
    f.write("--- RESULTS START ---\n")
    f.write(f"perf_loadTime: {perf.get('loadTime', 'N/A')}\n")
    f.write(f"perf_totalSizeKB: {perf.get('totalSizeKB', 'N/A')}\n")
    f.write(f"perf_resourcesCount: {perf.get('resourcesCount', 'N/A')}\n")
    f.write(f"seo_h1: {seo.get('h1Count', 'N/A')}\n")
    f.write(f"seo_imagesSinAlt: {seo.get('imagesSinAlt', 'N/A')}\n")
    f.write(f"ux_small: {ux.get('smallOnesCount', 'N/A')}\n")
    f.write(f"ux_scroll: {ux.get('hasHScroll', 'N/A')}\n")
    f.write(f"audit_keys: {list(audit.keys())}\n")
    f.write("--- RESULTS END ---\n")

db.close()
