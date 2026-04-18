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
print("--- LATEST DATA ---")
print(json.dumps(audit, indent=2))
print("--- END DATA ---")

db.close()
