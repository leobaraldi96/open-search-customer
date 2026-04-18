import sys
import os
import json

# Add backend to path to import database and models
sys.path.append(os.getcwd())

import database
import models

def fetch_samples():
    db = database.SessionLocal()
    try:
        # Fetch last 3 prospects with AI pitch
        prospects = db.query(models.Prospecto).filter(models.Prospecto.pitch_ia != None).order_by(models.Prospecto.id.desc()).limit(3).all()
        
        results = []
        for p in prospects:
            results.append({
                "empresa": p.empresa,
                "url": p.url,
                "audit": p.audit_tecnico,
                "pitch": p.pitch_ia
            })
        
        print(json.dumps(results, indent=2))
    finally:
        db.close()

if __name__ == "__main__":
    fetch_samples()
