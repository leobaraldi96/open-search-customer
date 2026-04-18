import models
from database import SessionLocal
import json

db = SessionLocal()
lead = db.query(models.Prospecto).filter(models.Prospecto.id == 24).first()

print(f"ID: {lead.id}")
print(f"Empresa: {lead.empresa}")
print(f"Audit Tecnico Type: {type(lead.audit_tecnico)}")
print(f"Audit Tecnico Content: {lead.audit_tecnico}")

if isinstance(lead.audit_tecnico, str):
    try:
        data = json.loads(lead.audit_tecnico)
        print("Successfully parsed as JSON")
        print(f"Performance: {data.get('performance')}")
    except:
        print("Failed to parse as JSON")
else:
    print(f"Performance: {lead.audit_tecnico.get('performance') if lead.audit_tecnico else 'N/A'}")

db.close()
