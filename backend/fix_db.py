import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Prospecto, LeadStatus
from database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def fix_empties():
    db = SessionLocal()
    try:
        count = 0
        all_leads = db.query(Prospecto).all()
        for lead in all_leads:
            if not lead.estado or lead.estado == "":
                print(f"Fixing lead ID {lead.id}: setting empty estado to 'nuevo'")
                lead.estado = LeadStatus.nuevo
                count += 1
                
        if count > 0:
            db.commit()
            print(f"Fixed {count} leads in the database.")
        else:
            print("No empty estados found.")
            
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_empties()
