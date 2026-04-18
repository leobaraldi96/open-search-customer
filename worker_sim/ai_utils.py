import time
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importar modelos de forma dinámica para evitar circulares
sys.path.append(os.path.join(os.getcwd(), '..', 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'backend')) # Para ejecución desde raíz

class AIRateLimiter:
    """
    Controlador de tasa para llamadas a IA. 
    Asegura que no se superen X solicitudes en Y segundos.
    Por defecto: 2 solicitudes por minuto (60s).
    """
    _last_calls = []
    _limit_rpm = 2
    _window_seconds = 60

    @classmethod
    def wait_if_needed(cls, prospecto_id: int = None):
        """
        Espera si hemos superado el límite de llamadas en la ventana de tiempo.
        Si se provee prospecto_id, cambia su estado en DB a 'esperando_saldo'.
        """
        now = datetime.now()
        # Limpiar llamadas viejas fuera de la ventana
        cls._last_calls = [call for call in cls._last_calls if now - call < timedelta(seconds=cls._window_seconds)]

        if len(cls._last_calls) >= cls._limit_rpm:
            # Calcular cuánto falta
            wait_time = (cls._last_calls[0] + timedelta(seconds=cls._window_seconds) - now).total_seconds()
            
            if wait_time > 0:
                print(f"\n[AI Rate Limiter] Límite alcanzado (2 RPM). Esperando {wait_time:.1f}s...")
                
                # Opcional: Actualizar estado en DB si tenemos el ID
                if prospecto_id:
                    cls._set_db_status(prospecto_id, "esperando_saldo")
                
                time.sleep(wait_time + 1) # +1s de margen
                
                # Volver a poner en investigando tras la espera
                if prospecto_id:
                    cls._set_db_status(prospecto_id, "investigando")
        
        # Registrar la llamada actual
        cls._last_calls.append(datetime.now())

    @staticmethod
    def _set_db_status(prospecto_id: int, status: str):
        """Helper para actualizar estado en DB directamente desde el worker."""
        try:
            from database import SessionLocal
            import models
            db = SessionLocal()
            p = db.query(models.Prospecto).get(prospecto_id)
            if p:
                p.estado = status
                db.commit()
            db.close()
        except Exception as e:
            print(f"[Limiter] Error actualizando DB: {e}")

def get_best_model():
    """Centraliza la elección del modelo operativo. Pro para inteligencia estratégica si el token count es bajo."""
    return "gemini-1.5-pro"
