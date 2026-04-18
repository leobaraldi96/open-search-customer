import pymysql
import os

def migrate():
    try:
        # Usar los mismos parámetros que el orquestador
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="buscaclientes",
            autocommit=True
        )
        cursor = conn.cursor()
        
        # 1. Agregar columna pitch_curado if not exists
        try:
            cursor.execute("ALTER TABLE prospectos ADD COLUMN pitch_curado TEXT NULL AFTER puntos_de_dolor")
            print("Columna 'pitch_curado' agregada.")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("La columna 'pitch_curado' ya existe.")
            else:
                print(f"Error al agregar pitch_curado: {e}")

        # 2. Actualizar ENUM de estado para incluir 'incompleto'
        try:
            # En MySQL el ENUM se redefine con la lista completa
            cursor.execute("ALTER TABLE prospectos MODIFY COLUMN estado ENUM('nuevo', 'investigando', 'contactado', 'incompleto', 'reunion', 'ganado', 'perdido') DEFAULT 'nuevo'")
            print("Tipo ENUM 'estado' actualizado con 'incompleto'.")
        except Exception as e:
            print(f"Error al actualizar ENUM: {e}")

        cursor.close()
        conn.close()
        print("Migración completada exitosamente.")
    except Exception as e:
        print(f"Falla crítica en la migración: {e}")

if __name__ == "__main__":
    migrate()
