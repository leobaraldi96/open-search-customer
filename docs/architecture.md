# Arquitectura y Definiciones Técnicas 🏛️ (v4.9.6)

## Orquestación Distribuida
El sistema separa la **Gestión de Datos** de la **Ejecución de Tareas**.

### 1. Orquestador (Windows / Python 8000)
- **Tecnología:** FastAPI.
- **Responsabilidad:** Recibir peticiones del Dashboard, persistir prospectos en MySQL y delegar auditorías al Worker de forma asíncrona (`BackgroundTasks`).
- **Estructura Modular (v5.0.0):** Desacoplamiento de la lógica de negocio en el directorio `backend/core/`.
- **Motor de Propuestas:** `backend/core/proposal_engine.py` centraliza la generación del Prompt Maestro.
- **Base de Datos:** MySQL gestionada vía SQLAlchemy (XAMPP).
- **Serialización:** Uso de `ensure_dict` y `ast.literal_eval` para manejar campos JSON compatibles con MySQL.

### 2. Worker Node (Nodo Motor / Python 8001)
- **Tecnología:** FastAPI + Playwright + BeautifulSoup + python-whois.
- **Responsabilidad:** Ejecutar el motor de **Auditoría Profunda** en 4 fases optimizadas:
    1. **WHOIS:** Datos legales y de registro del dominio (con soporte para .ar).
    2. **Crawler:** Rastreo recursivo inteligente (max 15 páginas).
    3. **Extractor:** Enriquecimiento de datos comerciales (WhatsApp, Redes).
    4. **Enriched Tech Analysis (v4.7.7):** Análisis de performance, UX (viewport, botones táctiles, scroll) y SEO (metatags) en el DOM (`domcontentloaded`).

### 3. Dashboard Ejecutivo (Vite 5173)
- **Tecnología:** Vanilla JS + CSS Glassmorphism.
- **Estación de Comando (v4.7.7):** Interfaz de alto rendimiento con modales de alta densidad. Implementa una **Cabecera Fija** para navegación por pestañas y un **Grid de 4 Columnas** para visualización técnica exhaustiva.

## Flujo de Estación de Comando (Intelligence Core v4.9.6)
El sistema utiliza un modelo de **Diagnóstico Estratégico de Negocios** que procesa la auditoría técnica bajo marcos de usabilidad senior.

1. **Auditoría Técnica & Scouting (v4.9.0):** El Worker ejecuta WHOIS, Crawler, Extractor y Wappalyzer In-Memory.
2. **Fase de Inteligencia Invisible (v4.9.5):** Se inyectan heurísticas de Krug y Nielsen en el prompt. Se activa el **Intelligence Shield** que valida la disonancia entre metadatos y navegación real (Anti-hallucination).
3. **Generación de Prompt Maestro (v4.9.6):** El sistema construye una narrativa de "Cluster de Fricción" (mezcla de 2-3 problemas graves) y exige un "Dato de Autoridad Inesperado" (Tech Stack/WHOIS) para el pitch.
4. **Procesamiento de IA Externo:** El usuario procesa el prompt en Gemini Web/App, obteniendo un diagnóstico sofisticado por vertical (Agro, B2B, etc.).
5. **Persistencia Atómica (Global Save):** Sincronización de Ficha + Pitch en una operación única.

## Reglas de Oro (Core Principles) 📜

1. **Datos Manuales Sagrados (#11):** La intervención humana en el pitch final es prioritaria sobre la automatización.
2. **Anti-Caché (#12):** Siempre forzar la auditoría fresca si el usuario lo solicita, ignorando estados previos.
3. **Sincronización Total (#13):** Toda métrica que mejore la visibilidad técnica en el informe crudo **DEBE** integrarse inmediatamente al Prompt Maestro. El "Cerebro" (IA) y los "Ojos" (Crawler) deben estar siempre en fase para maximizar la calidad del pitch.
4. **Profundidad Técnica (#16):** No ocultar la complejidad. El usuario (Leo) utiliza los datos RAW para validar la veracidad de la IA.
5. **Copiado Robusto (#5):** El sistema debe garantizar el copiado del prompt en entornos locales (HTTP) mediante fallbacks de texto.

---
**Nota sobre Estabilidad:** Esta arquitectura delegada garantiza que el sistema sea 100% operativo incluso sin una API Key de Google configurada en el servidor, utilizando la potencia del chat web de Gemini como motor de razonamiento externo. (v4.8.0)
