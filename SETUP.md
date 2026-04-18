# 🚀 Guía de Instalación - Busca Clientes

Bienvenido a **Busca Clientes**, una plataforma híbrida diseñada para la prospección inteligente de leads, auditoría técnica y generación de propuestas personalizadas mediante IA.

Este proyecto está diseñado para ejecutarse localmente. Sigue estos pasos para ponerlo en marcha.

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:
- **Python 3.10+**
- **Node.js 18+** y npm
- **XAMPP** o un servidor MySQL/MariaDB local.
- Una **Google API Key** (para Gemini y opcionalmente PageSpeed).

---

## 🛠️ Paso 1: Configuración de la Base de Datos

1. Abre el panel de control de **XAMPP** e inicia **MySQL**.
2. Entra en `http://localhost/phpmyadmin`.
3. Crea una nueva base de datos llamada `buscaclientes`.
4. Importa el archivo situado en: `docs/setup/database_structure.sql`.
   - Este archivo creará la tabla `prospectos` e insertará 2 registros de ejemplo.

---

## ⚙️ Paso 2: Variables de Entorno

1. En la raíz del proyecto, busca el archivo `.env.example`.
2. Renómbralo a `.env`.
3. Completa los valores:
   - `DATABASE_URL`: Por defecto es `mysql+pymysql://root:@localhost:3306/buscaclientes`.
   - `GOOGLE_API_KEY`: Tu clave de Google AI Studio (Gemini).
   - `PAGESPEED_API_KEY`: Tu clave de Google PageSpeed API.

---

## 🐍 Paso 3: Configuración del Backend y Worker

El proyecto usa Python para la lógica de servidor y el motor de scraping. Recomendamos usar entornos virtuales.

### Backend (Orquestador)
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### Worker Node (Scraper)
```bash
cd worker_sim
# Puedes usar el mismo venv o uno nuevo
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 💻 Paso 4: Configuración del Frontend (Dashboard)

El dashboard está construido con Vite y React.

```bash
cd frontend
npm install
```

---

## 🏃 Paso 5: Ejecución

Debes iniciar los tres componentes simultáneamente. Puedes usar varias pestañas de la terminal:

1. **Backend**: `cd backend && uvicorn main:app --port 8000 --reload`
2. **Worker**: `cd worker_sim && uvicorn main:app --port 8001 --reload`
3. **Frontend**: `cd frontend && npm run dev`

Accede a la aplicación en: **`http://localhost:5173`**

---

## 🚀 Ejecución Rápida (Recomendado)

Si estás en Windows, puedes iniciar todos los servicios (Backend, Worker y Frontend) simultáneamente con un solo comando. Abre una terminal de PowerShell en la raíz del proyecto y ejecuta:

```powershell
.\start-all.ps1
```

Este script abrirá las terminales necesarias de forma automática, dejando la aplicación funcional y lista para usar.

---

## 📝 Notas
- El **Backend** se encarga de la base de datos y la orquestación.
- El **Worker** realiza el scraping pesado usando Playwright.
- El **Frontend** es la interfaz "Luxury Obsidian" para gestionar tus leads.
