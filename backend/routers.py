from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import json
import ast

def ensure_dict(field):
    """Asegura que un campo JSON de la base de datos sea un diccionario Python."""
    if not field: return {}
    if isinstance(field, dict): return field
    if isinstance(field, str):
        # Intentar JSON estándar primero
        try:
            return json.loads(field)
        except:
            # Intentar literal_eval de Python (para MySQL que guarda con comillas simples)
            try:
                return ast.literal_eval(field)
            except:
                return {}
    return field
from typing import List
import httpx
from datetime import datetime
import asyncio

import time
from playwright.sync_api import sync_playwright
import models, schemas
from database import get_db
from core.proposal_engine import build_prompt

router = APIRouter(
    prefix="/api/prospectos",
    tags=["prospectos"]
)

@router.get("/", response_model=List[schemas.ProspectoOut])
def read_prospectos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    prospectos = db.query(models.Prospecto).offset(skip).limit(limit).all()
    return prospectos

@router.get("/{prospecto_id}", response_model=schemas.ProspectoOut)
def read_prospecto(prospecto_id: int, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if db_prospecto is None:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    return db_prospecto

@router.post("/", response_model=schemas.ProspectoOut)
def create_prospecto(prospecto: schemas.ProspectoCreate, db: Session = Depends(get_db)):
    db_prospecto = models.Prospecto(**prospecto.model_dump())
    db.add(db_prospecto)
    db.commit()
    db.refresh(db_prospecto)
    return db_prospecto

@router.put("/{prospecto_id}", response_model=schemas.ProspectoOut)
def update_prospecto(prospecto_id: int, prospecto: schemas.ProspectoUpdate, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    update_data = prospecto.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prospecto, key, value)
        
    db.commit()
    db.refresh(db_prospecto)
    return db_prospecto

@router.patch("/{id}/analysis")
@router.post("/{id}/analysis") 
def update_analysis(id: int, audit_update: dict, db: Session = Depends(get_db)):
    """
    v4.6.0: Guardado Global. Actualiza cualquier campo del prospecto + pitch.
    """
    print(f"[GLOBAL SAVE] ID: {id}. Campos: {list(audit_update.keys())}")
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    # 1. Actualizar dinámicamente cualquier campo permitido
    for key, value in audit_update.items():
        if hasattr(db_prospecto, key) and key not in ["id", "creado_en"]:
            setattr(db_prospecto, key, value)
            
    # 2. Sincronización especial para el pitch (asegurar redundancia)
    new_pitch = audit_update.get("pitch_curado") or audit_update.get("pitch_ia")
    if new_pitch:
        db_prospecto.pitch_ia = new_pitch # Mantener sincronizados v4.6.0
        
    # 3. Cambio de estado automático SOLO si no se envió un estado manual
    manual_state = audit_update.get("estado")
    if not manual_state:
        if new_pitch and len(new_pitch) > 50:
            db_prospecto.estado = models.LeadStatus.analizado
    else:
        print(f"[MANUAL STATE] Forzando estado: {manual_state}")
        db_prospecto.estado = manual_state

    db.commit()
    return {"status": "success", "id": id, "received": list(audit_update.keys())}

@router.get("/{id}/prompt")
def get_master_prompt(id: int, db: Session = Depends(get_db)):
    """
    v3.2: Genera y devuelve el Prompt Maestro basado en los datos crudos del lead.
    """
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    from core.proposal_engine import build_prompt
    
    # Consolidar datos para el prompt (v4.9.1 - Fix SSL + extra_contacts)
    audit_tecnico = ensure_dict(db_prospecto.audit_tecnico)
    whois = ensure_dict(db_prospecto.whois_data)
    
    # LOGS DE DEPURACIÓN (vía Consola Uvicorn)
    print(f"\n[DEBUG PROMPT] Prospecto ID: {id} - {db_prospecto.empresa}")
    print(f"  - Keys en Audit Técnico: {list(audit_tecnico.keys()) if audit_tecnico else 'Vacio'}")
    if audit_tecnico:
        print(f"  - Performance Data: {audit_tecnico.get('performance') or audit_tecnico.get('Performance')}")
        print(f"  - Security Data:    {audit_tecnico.get('security') or audit_tecnico.get('Security')}")
        print(f"  - Extra Contacts:   {audit_tecnico.get('extra_contacts') or audit_tecnico.get('contacts')}")
    
    audit_data = {
        "performance":    audit_tecnico.get("performance")    or audit_tecnico.get("Performance")    or {},
        "seo":            audit_tecnico.get("seo")            or audit_tecnico.get("SEO")            or {},
        "ux":             audit_tecnico.get("ux")             or audit_tecnico.get("UX")             or {},
        # ✅ FIX v4.9.1: security y extra_contacts faltaban — SSL siempre llegaba como "NO DETECTADO"
        "security":       audit_tecnico.get("security")       or audit_tecnico.get("Security")       or {},
        "extra_contacts": audit_tecnico.get("extra_contacts") or audit_tecnico.get("contacts")      or {},
        "whois_data":     whois,
        "tech_stack":     db_prospecto.tecnologias_detectadas,
        "puntos_de_dolor": db_prospecto.puntos_de_dolor or "No detectados",
    }
    
    prompt = build_prompt(
        audit_data, 
        db_prospecto.empresa, 
        db_prospecto.url, 
        db_prospecto.nombre_dueno,
        db_prospecto.email,
        db_prospecto.telefono,
        db_prospecto.direccion,
        urls_visitadas=db_prospecto.urls_visitadas,
        redes_sociales=db_prospecto.redes_sociales,
        observaciones_humanas=db_prospecto.observaciones_humanas,
    )
    
    return {"prompt": prompt}

@router.delete("/{prospecto_id}")
def delete_prospecto(prospecto_id: int, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
    db.delete(db_prospecto)
    db.commit()
    return {"message": "Prospecto eliminado exitosamente"}

async def run_audit_in_background(prospecto_id: int, url: str):
    from database import SessionLocal
    db = SessionLocal()
    
    # Notificamos al simulador del Mac Pro (Worker)
    # Primero, obtenemos el prospecto para asegurar que tenemos la URL más reciente y para la actualización posterior
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        # Si el prospecto no existe, no hay nada que auditar o actualizar
        db.close()
        return

    try:
        # Damos 180 segundos (3 minutos) de timeout para auditorías profundas
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post("http://127.0.0.1:8001/auditar", json={
                "url": db_prospecto.url,
                "prospecto_id": prospecto_id
            })
            if response.status_code == 200:
                result = response.json()
            else:
                result = {
                    "status": "error", 
                    "falla_encontrada": f"Worker error ({response.status_code})",
                    "error": response.text
                }
    except Exception as e:
        result = {
            "error": str(e), 
            "status": "error", 
            "falla_encontrada": f"Error de conexión: {str(e)[:50]}"
        }

    # Actualizamos el prospecto en base al resultado del Worker
    if db_prospecto:
        if result.get("status") in ["success", "partial"]:
            # Siempre actualizar el estado al recibir resultados exitosos o parciales
            is_incomplete = result.get("is_incomplete", False)
            db_prospecto.estado = models.LeadStatus.incompleto if is_incomplete else models.LeadStatus.analizado
            
            if result.get("falla_encontrada"):
                db_prospecto.falla_detectada = result.get("falla_encontrada")
            else:
                db_prospecto.falla_detectada = None # Limpiar si éxito total

            # Auditoría Técnica (Solo si hay nuevos datos)
            if result.get("informe_detallado"):
                db_prospecto.informe_detallado = result.get("informe_detallado")
            
            if result.get("audit_tecnico"):
                db_prospecto.audit_tecnico = result.get("audit_tecnico")
                db_prospecto.tecnologias_detectadas = result.get("audit_tecnico", {}).get("tech_stack")

            if result.get("urls_visitadas"):
                db_prospecto.urls_visitadas = result.get("urls_visitadas")
            
            if result.get("paginas_recorridas") is not None:
                db_prospecto.paginas_auditadas = result.get("paginas_recorridas")
            
            if result.get("puntos_de_dolor"):
                db_prospecto.puntos_de_dolor = result.get("puntos_de_dolor")

            # --- NUEVO: Motor de Humanización IA (Solo si tenemos nuevos puntos de dolor) ---
            if result.get("puntos_de_dolor"):
                try:
                    # ✅ FIX v4.9.1: pasar audit_tecnico completo (security, seo, ux, performance)
                    audit_tecnico_bg = ensure_dict(db_prospecto.audit_tecnico)
                    whois_bg = ensure_dict(db_prospecto.whois_data)
                    audit_data_bg = {
                        "performance":    audit_tecnico_bg.get("performance")    or audit_tecnico_bg.get("Performance")    or {},
                        "seo":            audit_tecnico_bg.get("seo")            or audit_tecnico_bg.get("SEO")            or {},
                        "ux":             audit_tecnico_bg.get("ux")             or audit_tecnico_bg.get("UX")             or {},
                        "security":       audit_tecnico_bg.get("security")       or audit_tecnico_bg.get("Security")       or {},
                        "extra_contacts": audit_tecnico_bg.get("extra_contacts") or audit_tecnico_bg.get("contacts")      or {},
                        "whois_data":     whois_bg,
                        "tech_stack":     db_prospecto.tecnologias_detectadas,
                        "puntos_de_dolor": db_prospecto.puntos_de_dolor,
                    }
                    
                    # Generar Pitch / Prompt completo con todos los datos técnicos
                    new_pitch = build_prompt(
                        audit_data=audit_data_bg,
                        company_name=db_prospecto.empresa or "Prospecto",
                        url=db_prospecto.url,
                        owner_name=db_prospecto.nombre_dueno,
                        email=db_prospecto.email,
                        phone=db_prospecto.telefono,
                        address=db_prospecto.direccion,
                        urls_visitadas=db_prospecto.urls_visitadas,
                        redes_sociales=db_prospecto.redes_sociales,
                    )
                    if new_pitch:
                        db_prospecto.pitch_ia = new_pitch
                        print(f"[IA] Prompt completo generado para {db_prospecto.empresa}")
                except Exception as ia_err:
                    print(f"[IA ERROR] Falló generación del prompt: {ia_err}")
            
            # Emails y Teléfonos Hallados (Como sugerencia, no pisan el principal)
            ignorados_m = (db_prospecto.emails_ignorados or "").split(",")
            ignorados_m = [m.strip() for m in ignorados_m if m.strip()]
            
            if result.get("emails_encontrados"):
                emails = result.get("emails_encontrados", [])
                if isinstance(emails, list):
                    emails = [m for m in emails if m not in ignorados_m]
                    db_prospecto.emails_hallados = ", ".join(emails)
                else:
                    db_prospecto.emails_hallados = str(emails)

            ignorados_t = (db_prospecto.telefonos_ignorados or "").split(",")
            ignorados_t = [t.strip() for t in ignorados_t if t.strip()]

            if result.get("telefonos_encontrados"):
                telefonos = result.get("telefonos_encontrados", [])
                if isinstance(telefonos, list):
                    telefonos = [t for t in telefonos if t not in ignorados_t]
                    db_prospecto.telefonos_hallados = ", ".join(telefonos)
                else:
                    db_prospecto.telefonos_hallados = str(telefonos)

            # Datos de Contacto: PRIORIDAD MANUAL (Solo llenar si está vacío)
            # v5.0: Se prioriza el WhatsApp directo sobre el teléfono general
            def is_empty(val):
                return val is None or str(val).strip() == "" or str(val).strip() == "None"

            # Prioridad 1: WhatsApp directo hallado en links
            if result.get("whatsapp") and is_empty(db_prospecto.telefono):
                db_prospecto.telefono = str(result.get("whatsapp"))
                db_prospecto.fuente_contacto = "whatsapp_link"
            
            # Prioridad 2: Teléfono detectado (si el 1 falló)
            if result.get("telefono") and is_empty(db_prospecto.telefono):
                db_prospecto.telefono = str(result.get("telefono"))
            
            if result.get("email") and is_empty(db_prospecto.email):
                db_prospecto.email = str(result.get("email"))
            
            if result.get("direccion") and is_empty(db_prospecto.direccion):
                db_prospecto.direccion = str(result.get("direccion"))
            
            if result.get("nombre_dueno") and is_empty(db_prospecto.nombre_dueno):
                db_prospecto.nombre_dueno = str(result.get("nombre_dueno"))
                if is_empty(db_prospecto.contacto_clave):
                    db_prospecto.contacto_clave = str(result.get("nombre_dueno"))
            
            if result.get("whois_data"):
                whois_data = result.get("whois_data")
                db_prospecto.whois_data = whois_data
                
                # Mapear campos planos para facilitar filtros y reportes
                try:
                    if whois_data.get("creacion"):
                        db_prospecto.dominio_creado = datetime.fromisoformat(whois_data["creacion"])
                    if whois_data.get("expiracion"):
                        db_prospecto.dominio_expira = datetime.fromisoformat(whois_data["expiracion"])
                    if whois_data.get("antiguedad_anios"):
                        db_prospecto.antiguedad_dominio = int(whois_data["antiguedad_anios"])
                except Exception as e:
                    print(f"[WHOIS PARSE ERROR] {e}")
            
            if result.get("paginas_recorridas"):
                db_prospecto.paginas_auditadas = result.get("paginas_recorridas", 0)
            
            if result.get("urls_visitadas"):
                db_prospecto.urls_visitadas = result.get("urls_visitadas")
        
        else:
            # Si hay error total, volvemos a 'nuevo' para permitir RE-AUDITAR
            db_prospecto.falla_detectada = result.get("falla_encontrada", "Error de conexión")
            db_prospecto.estado = models.LeadStatus.nuevo
            print(f"[WORKER ERROR] No se actualizaron datos para {db_prospecto.empresa} debido a falla. Estado reseteado a NUEVO.")
        
        db.commit()
    db.close()

@router.post("/{prospecto_id}/iniciar-auditoria")
async def start_audit(prospecto_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    if not db_prospecto.url:
        raise HTTPException(status_code=400, detail="El prospecto no tiene URL configurada.")

    # Cambiamos estado temporal "investigando"
    db_prospecto.estado = models.LeadStatus.investigando
    db.commit()
    db.refresh(db_prospecto)

    # Lanzamos el ping asíncrono en background simulando delegar a la Mac
    background_tasks.add_task(run_audit_in_background, prospecto_id, db_prospecto.url)

    return {"message": "Bot enviado", "prospecto": db_prospecto}

@router.post("/{prospecto_id}/guardar-pitch")
def guardar_pitch(prospecto_id: int, data: dict, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    # Guardar Pitch
    if "pitch" in data:
        db_prospecto.pitch_curado = data.get("pitch")
    
    # Guardar Ediciones Manuales de Contacto (Ficha de Lead)
    if "empresa" in data:
        db_prospecto.empresa = data.get("empresa")
    if "nombre_dueno" in data:
        db_prospecto.nombre_dueno = data.get("nombre_dueno")
        db_prospecto.contacto_clave = data.get("nombre_dueno")
    if "email" in data:
        db_prospecto.email = data.get("email")
    if "telefono" in data:
        db_prospecto.telefono = data.get("telefono")
    if "direccion" in data:
        db_prospecto.direccion = data.get("direccion")
        
    db_prospecto.actualizado_en = datetime.utcnow()
    db.commit()
    db.refresh(db_prospecto)
    return {"status": "success", "message": "Cambios guardados exitosamente."}

# ENDPOINTS DE TRACKING CRM (v2.6.0)

@router.post("/{prospecto_id}/track/enviado")
def track_enviado(prospecto_id: int, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    db_prospecto.estado = models.LeadStatus.contactado
    db_prospecto.fecha_envio = datetime.utcnow()
    db.commit()
    return {"status": "success", "estado": "contactado", "fecha": db_prospecto.fecha_envio}

@router.post("/{prospecto_id}/track/respondido")
def track_respondido(prospecto_id: int, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    db_prospecto.estado = models.LeadStatus.respondido
    db_prospecto.fecha_respuesta = datetime.utcnow()
    db.commit()
    return {"status": "success", "estado": "respondido", "fecha": db_prospecto.fecha_respuesta}

@router.post("/{prospecto_id}/track/venta")
def track_venta(prospecto_id: int, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == prospecto_id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    db_prospecto.estado = models.LeadStatus.ganado
    db_prospecto.fecha_venta = datetime.utcnow()
    db.commit()
    return {"status": "success", "estado": "ganado", "fecha": db_prospecto.fecha_venta}

@router.post("/{id}/marcar-contacto")
async def marcar_contacto(id: int, action: schemas.ContactAction, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    if action.tipo == "email":
        current = (db_prospecto.emails_contactados or "").split(",")
        current = [item.strip() for item in current if item.strip()]
        if action.valor not in current:
            current.append(action.valor)
            db_prospecto.emails_contactados = ",".join(current)
    else:
        current = (db_prospecto.telefonos_contactados or "").split(",")
        current = [item.strip() for item in current if item.strip()]
        if action.valor not in current:
            current.append(action.valor)
            db_prospecto.telefonos_contactados = ",".join(current)
            
    db.commit()
    return {"status": "ok"}

@router.post("/{id}/remover-hallazgo")
async def remover_hallazgo(id: int, action: schemas.ContactAction, db: Session = Depends(get_db)):
    db_prospecto = db.query(models.Prospecto).filter(models.Prospecto.id == id).first()
    if not db_prospecto:
        raise HTTPException(status_code=404, detail="Prospecto no encontrado")
    
    if action.tipo == "email":
        # Remover de hallados
        hallados = (db_prospecto.emails_hallados or "").split(",")
        hallados = [item.strip() for item in hallados if item.strip() and item.strip() != action.valor]
        db_prospecto.emails_hallados = ",".join(hallados)
        # Añadir a ignorados
        ignorados = (db_prospecto.emails_ignorados or "").split(",")
        ignorados = [item.strip() for item in ignorados if item.strip()]
        if action.valor not in ignorados:
            ignorados.append(action.valor)
            db_prospecto.emails_ignorados = ",".join(ignorados)
    else:
        # Remover de hallados
        hallados = (db_prospecto.telefonos_hallados or "").split(",")
        hallados = [item.strip() for item in hallados if item.strip() and item.strip() != action.valor]
        db_prospecto.telefonos_hallados = ",".join(hallados)
        # Añadir a ignorados
        ignorados = (db_prospecto.telefonos_ignorados or "").split(",")
        ignorados = [item.strip() for item in ignorados if item.strip()]
        if action.valor not in ignorados:
            ignorados.append(action.valor)
            db_prospecto.telefonos_ignorados = ",".join(ignorados)
            
    db.commit()
    return {"status": "ok"}

def _sync_extract_maps(url: str):
    """Lógica síncrona de extracción para evitar conflictos de event loop en Windows."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Contexto con User Agent humano
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # Navegación rápida: no esperar a que toda la red se calme (Maps nunca lo hace)
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            
            # 🍪 GESTIÓN DE COOKIES INMEDIATA
            try:
                # Buscar botón de aceptar rápidamente
                consent_selector = '#L2AGLb, button[aria-label="Aceptar todo"], button[aria-label="Accept all"], button[jsname="b3VHJd"]'
                page.wait_for_selector(consent_selector, timeout=3000)
                page.click(consent_selector)
            except:
                pass # Si no hay cartel, seguimos
            
            # Esperar específicamente al contenedor de información
            name_sel = 'h1.DUwDvf.lfPIob'
            page.wait_for_selector(name_sel, timeout=15000)
            
            # Pequeña pausa para que los datos secundarios (web/tel) se rendericen
            time.sleep(1.5) 
            
            # Selectores estables
            web_sel = 'a[data-item-id="authority"]'
            phone_sel = 'button[data-item-id^="phone:tel:"]'
            addr_sel = 'button[data-item-id="address"]'
            
            empresa = page.inner_text(name_sel)
            
            web_elem = page.query_selector(web_sel)
            web_url = web_elem.get_attribute("href") if web_elem else None
            
            phone_elem = page.query_selector(phone_sel)
            telefono = (phone_elem.get_attribute("aria-label")) if phone_elem else None
            if telefono: telefono = telefono.replace("Teléfono: ", "").replace("Phone: ", "").strip()
            
            addr_elem = page.query_selector(addr_sel)
            direccion = (addr_elem.get_attribute("aria-label")) if addr_elem else None
            if direccion: direccion = direccion.replace("Dirección: ", "").replace("Address: ", "").strip()
            
            return {
                "empresa": empresa,
                "url": web_url.split('?')[0].rstrip('/') if web_url else None,
                "telefono": telefono,
                "direccion": direccion,
                "google_maps_url": url
            }
        except Exception as e:
            print(f"Error en Maps Extract Interno: {e}")
            raise e
        finally:
            browser.close()

@router.post("/extract-maps", response_model=schemas.MapsExtraction)
async def extract_maps(data: dict):
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL no proporcionada")
    
    try:
        # Ejecutar la lógica síncrona en un hilo separado
        # Esto soluciona el NotImplementedError de asyncio en Windows
        extracted = await asyncio.to_thread(_sync_extract_maps, url)
        return extracted
    except Exception as e:
        print(f"Error en endpoint extract-maps: {e}")
        raise HTTPException(status_code=500, detail=f"Error en extracción: {str(e)}")
