import pymysql
import os

# Configuración de conexión (Hardcoded como el resto del proyecto por ahora)
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "buscaclientes",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

def migrate():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            print("--- Iniciando Migración v2.6.0 (CRM & Pitch IA) ---")
            
            # Columnas a añadir
            # (Nombre, Tipo)
            columns_to_add = [
                ("pitch_ia", "TEXT"),
                ("fecha_envio", "DATETIME"),
                ("fecha_respuesta", "DATETIME"),
                ("fecha_venta", "DATETIME")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    query = f"ALTER TABLE prospectos ADD COLUMN {col_name} {col_type}"
                    cursor.execute(query)
                    print(f"✅ Columna '{col_name}' añadida con éxito.")
                except pymysql.err.InternalError as e:
                    if e.args[0] == 1060: # Duplicate column name
                        print(f"ℹ️ La columna '{col_name}' ya existe, omitiendo.")
                    else:
                        raise e
            
            connection.commit()
            print("--- Migración Finalizada con Éxito ---")
    finally:
        connection.close()

if __name__ == "__main__":
    migrate()
