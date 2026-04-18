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

# Write to file explicitly with utf-8
with open("c:/xampp/htdocs/buscaclientes/backend/db_check_v6.txt", "w", encoding="utf-8") as f:
    f.write("--- LATEST DATA ---\n")
    f.write(json.dumps(audit, indent=2))
    f.write("\n--- END DATA ---\n")

db.close()
