from pydantic import BaseModel, HttpUrl
from typing import Optional, Union, Any
from datetime import datetime
from models import LeadStatus

class ProspectoBase(BaseModel):
    empresa: str
    url: Optional[str] = None

    # Datos de Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    contacto_clave: Optional[str] = None

    # Datos Enriquecidos
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None

    # Datos del Dueño
    nombre_dueno: Optional[str] = None
    cargo_dueno: Optional[str] = None
    email_dueno: Optional[str] = None
    telefono_dueno: Optional[str] = None
    fuente_contacto: Optional[str] = None

    # Redes Sociales
    redes_sociales: Optional[dict] = None

    # Auditoría
    falla_detectada: Optional[str] = None
    emails_hallados: Optional[str] = None
    telefonos_hallados: Optional[str] = None
    auditoria_texto: Optional[str] = None
    informe_detallado: Optional[dict] = None
    puntos_de_dolor: Optional[str] = None
    pitch_ia: Optional[str] = None
    pitch_curado: Optional[str] = None
    
    # Tracking de Ventas (CRM)
    fecha_envio: Optional[datetime] = None
    fecha_respuesta: Optional[datetime] = None
    fecha_venta: Optional[datetime] = None

    # Auditoría Técnica
    audit_tecnico: Optional[dict] = None
    tecnologias_detectadas: Optional[Union[list, dict, Any]] = None
    paginas_auditadas: Optional[int] = 0

    # WHOIS
    whois_data: Optional[dict] = None
    dominio_creado: Optional[datetime] = None
    dominio_expira: Optional[datetime] = None
    antiguedad_dominio: Optional[int] = None

    # Crawl
    urls_visitadas: Optional[list] = None

    # Observaciones Humanas
    observaciones_humanas: Optional[str] = None

    # Historial de Contacto e Ignorados
    emails_contactados: Optional[str] = None
    telefonos_contactados: Optional[str] = None
    telefonos_ignorados: Optional[str] = None
    emails_ignorados: Optional[str] = None

    estado: Optional[str] = LeadStatus.nuevo

class ProspectoCreate(ProspectoBase):
    pass

class ProspectoUpdate(BaseModel):
    empresa: Optional[str] = None
    url: Optional[str] = None

    # Contacto
    telefono: Optional[str] = None
    email: Optional[str] = None
    contacto_clave: Optional[str] = None

    # Datos Enriquecidos
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None

    # Dueño
    nombre_dueno: Optional[str] = None
    cargo_dueno: Optional[str] = None
    email_dueno: Optional[str] = None
    telefono_dueno: Optional[str] = None
    social_data: Optional[dict] = None # Alias para redes_sociales si es necesario
    fuente_contacto: Optional[str] = None

    # Redes
    redes_sociales: Optional[dict] = None

    # Auditoría
    falla_detectada: Optional[str] = None
    emails_hallados: Optional[str] = None
    telefonos_hallados: Optional[str] = None
    auditoria_texto: Optional[str] = None
    informe_detallado: Optional[dict] = None
    puntos_de_dolor: Optional[str] = None
    pitch_ia: Optional[str] = None
    pitch_curado: Optional[str] = None
    
    # Tracking de Ventas (CRM)
    fecha_envio: Optional[datetime] = None
    fecha_respuesta: Optional[datetime] = None
    fecha_venta: Optional[datetime] = None

    # Técnico
    audit_tecnico: Optional[dict] = None
    tecnologias_detectadas: Optional[Union[list, dict, Any]] = None
    paginas_auditadas: Optional[int] = None

    # WHOIS
    whois_data: Optional[dict] = None
    dominio_creado: Optional[datetime] = None
    dominio_expira: Optional[datetime] = None
    antiguedad_dominio: Optional[int] = None

    # Crawl
    urls_visitadas: Optional[list] = None

    # Observaciones Humanas
    observaciones_humanas: Optional[str] = None

    # Historial de Contacto e Ignorados
    emails_contactados: Optional[str] = None
    telefonos_contactados: Optional[str] = None
    telefonos_ignorados: Optional[str] = None
    emails_ignorados: Optional[str] = None

    estado: Optional[LeadStatus] = None

class ContactAction(BaseModel):
    tipo: str # 'email' o 'telefono'
    valor: str

class ProspectoOut(ProspectoBase):
    id: int
    creado_en: Optional[datetime]
    actualizado_en: Optional[datetime]

class MapsExtraction(BaseModel):
    empresa: Optional[str] = None
    url: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    google_maps_url: Optional[str] = None

    class Config:
        from_attributes = True
