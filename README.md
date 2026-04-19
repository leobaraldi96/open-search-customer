# Busca Clientes App 🤖✨

> **Motor Híbrido de Prospección Inteligente y Auditoría Digital (Public Edition)**
>
> Una solución profesional diseñada para automatizar la auditoría de sitios web, extracción de leads desde Google Maps y detección de fallas críticas de negocio. El sistema utiliza una arquitectura distribuida que permite separar la gestión administrativa del motor de scraping pesado.

![Status](https://img.shields.io/badge/status-active-success)
![Engine](https://img.shields.io/badge/engine-playwright-orange)
![Audit](https://img.shields.io/badge/audit-deep-red)

[Busca-Clientes---CRM-Orquestador.webm](https://github.com/user-attachments/assets/1da798fc-01f5-4969-a61a-535f5c5b49c5)


---

## 📌 Visión General

Busca Clientes es un **Motor de Inteligencia de Negocios** que ayuda a agencias y consultores a prospectar mejor:

1.  **🪄 Importación Inteligente:** Prospección automática desde Google Maps. Extrae empresa, web, teléfono y dirección con un solo clic.
2.  **Scouting Técnico:** Recolección de Performance, SEO, UX, WHOIS y Stack Tecnológico.
3.  **Generación de Propuesta IA:** Creación automática de un "Prompt Maestro" blindado contra alucinaciones para generar pitches de venta potentes.
4.  **CRM de Prospección:** Gestión táctica del funnel de ventas (Contactado, Respondido, Venta).

---

## 🛠️ Arquitectura

El proyecto está dividido en tres componentes principales:

- **Frontend:** Dashboard "Luxury Obsidian" construido con Vanilla JS y Vite para máximo rendimiento.
- **Backend:** API en FastAPI (Python) que orquesta la base de datos y la lógica de negocio.
- **Worker Node:** Motor de scraping basado en Playwright para navegación real y extracción de datos.

### 🔄 Flujo de Trabajo
1. El usuario solicita un scouting desde el **Frontend**.
2. El **Backend** registra la solicitud y delega la tarea al **Worker**.
3. El **Worker** abre un navegador real, audita el sitio y extrae WHOIS/Performance.
4. El **Backend** procesa los resultados y genera el "Prompt Maestro" con IA.
5. El **Frontend** visualiza la auditoría lista para la venta.

---

## 🚀 Inicio Rápido

Para poner en marcha la aplicación, sigue estos pasos:

1.  Asegúrate de tener instalado **Python 3.12+**, **Node.js** y un servidor **MySQL/MariaDB** (como XAMPP).
2.  Instala las dependencias y configura tus variables de entorno siguiendo la **[Guía de Instalación Detallada (SETUP.md)](./SETUP.md)**.
3.  Instala Playwright: `python -m playwright install chromium`.

### Ejecución con un solo comando 🚀

Si estás en Windows, abre una terminal de PowerShell en la raíz y ejecuta:

```powershell
.\start-all.ps1
```

Este script iniciará automáticamente el Backend, el Worker y el Frontend.

---

## 🧠 El Corazón del Sistema: El Prompt Maestro

La potencia de esta herramienta no está solo en los datos, sino en cómo se le presentan a la Inteligencia Artificial.

### 📍 Localización y Estructura
Toda la lógica de persuasión reside en el archivo:
**`backend/core/prompts.py`**

Aquí es donde se construye el "Prompt Maestro". Este archivo contiene plantillas blindadas que toman los datos crudos de la auditoría (WHOIS, SEO, Performance) y los transforman en una estructura narrativa lógica que la IA puede entender sin "alucinar".

### 📋 Cómo usarlo (Método Actual)
Actualmente, el sistema funciona bajo un esquema de **copiar y pegar**:
1. Tras realizar una auditoría, el sistema genera un prompt denso y detallado.
2. Copias ese prompt desde el dashboard.
3. Lo pegas en tu chat de IA favorito (ChatGPT, Gemini, Claude).
4. La IA genera un speech de venta, un correo técnico o una propuesta completa basada en evidencia real.

> [!TIP]
> **Iteración Infinita:** El archivo `prompts.py` es totalmente maleable. Puedes editar las plantillas para adecuarlas a cualquier nicho de negocio, tono de voz o servicio específico que ofrezcas.

---

## 🚀 Próximamente: Automatización total con API

Estoy trabajando en una versión **Full Auto** que eliminará el paso de copiar y pegar. Esta actualización utilizará la **API de Google Gemini, Claude o ChatGPT** para consumir tokens directamente desde el servidor.

Esta versión está pensada para usuarios que:
- Cuentan con una API Key con créditos.
- Buscan automatizar la generación de cientos de propuestas en minutos.
- Quieren integrar el speech final directamente en su flujo de CRM.

---

## 📈 Roadmap y Funcionalidades

- [x] Importación Mágica desde Google Maps ✨.
- [x] Auditoría Profunda (WHOIS + Crawler + Extractor).
- [x] CRM Táctico integrado.
- [x] Estación de Comando (Prompt Maestro) para IA.
- [x] Dashboards de métricas en tiempo real.

---

## 📄 Documentación

- **[SETUP.md](./SETUP.md)** - Guía maestra de instalación y variables de entorno.
- **[Estructura SQL](./docs/setup/database_structure.sql)** - Script para inicializar la base de datos en MySQL/XAMPP.
- **[Arquitectura Detallada](./docs/architecture.md)** - Explicación profunda del diseño del sistema.
- **[Reglas de Oro](./docs/reglas_de_oro.md)** - Principios de desarrollo seguidos en este proyecto.

---

## 👤 Autoría y Filosofía

Este proyecto fue diseñado y desarrollado por **Leo Baraldi** como parte del ecosistema de herramientas de alto impacto del **Framework Baraldi**. 

Busca ser una pieza de ingeniería transparente que demuestre el poder de la automatización aplicada a la consultoría de negocios.

---

## 📄 Licencia y Uso Libre

Este software es **Open Source**. He decidido liberar este código para que la comunidad pueda aprender, iterar y construir sobre él.

**Puedes hacer lo que quieras con este código:**
- ✅ Usarlo para fines comerciales.
- ✅ Modificarlo y crear versiones derivadas.
- ✅ Distribuirlo libremente.
- ✅ Usarlo como base para tus propios productos.

*No se requiere permiso previo ni atribución obligatoria (aunque se agradece), el objetivo es que sea útil para tu crecimiento profesional.*

---
*Desarrollado con ❤️ por **Leo Baraldi** | Potenciado por el Framework Baraldi (Industrial Command Station)*
