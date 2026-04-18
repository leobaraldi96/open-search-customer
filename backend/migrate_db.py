import database
from sqlalchemy import text

def migrate():
    engine = database.engine
    with engine.connect() as conn:
        print("Iniciando migración de base de datos...")
        columns_to_add = [
            ("emails_contactados", "TEXT"),
            ("telefonos_contactados", "TEXT"),
            ("telefonos_ignorados", "TEXT"),
            ("emails_ignorados", "TEXT")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                # Comprobar si la columna ya existe para evitar errores
                result = conn.execute(text(f"SHOW COLUMNS FROM prospectos LIKE '{col_name}'"))
                if not result.fetchone():
                    print(f"Añadiendo columna: {col_name}...")
                    conn.execute(text(f"ALTER TABLE prospectos ADD COLUMN {col_name} {col_type} NULL"))
                    conn.commit()
                else:
                    print(f"La columna {col_name} ya existe. Saltando.")
            except Exception as e:
                print(f"Error al añadir {col_name}: {e}")
        
    print("Migración completada con éxito.")

if __name__ == "__main__":
    migrate()
