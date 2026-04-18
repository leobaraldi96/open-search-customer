import './style.css';

// Adaptable para acceder desde la Mac, iPad o red local usando la IP de esta PC
const API_BASE_URL = `http://${window.location.hostname}:8000/api/prospectos`;

// Elementos del DOM
const leadsBody = document.getElementById('leadsBody');
const leadCount = document.getElementById('leadCount');
const prospectForm = document.getElementById('prospectForm');

// Estado Local (v4.7.0)
let currentPage = 1;
const LEADS_PER_PAGE = 6;
let allLeads = [];
let currentLeadData = null; // Nivel 1: datos del lead activo en el modal

// Polling dinámico
let pollingInterval = null;

function startPolling() {
    if (pollingInterval) return;
    console.log("[POLLING] Activado...");
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch(API_BASE_URL + '/');
            const leads = await response.json();
            leads.sort((a, b) => new Date(b.creado_en) - new Date(a.creado_en));
            allLeads = leads;

            const hasActiveLead = leads.some(l => l.estado === 'investigando' || l.estado === 'esperando_saldo');
            if (!hasActiveLead) stopPolling();

            renderLeads(leads);
            updateMetrics(leads);
        } catch (e) {
            console.error("Error en polling:", e);
        }
    }, 3000);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
        console.log("[POLLING] Detenido.");
    }
}

async function fetchLeads() {
    try {
        const response = await fetch(API_BASE_URL + '/');
        if (!response.ok) throw new Error('Error listando prospectos');
        const leads = await response.json();
        leads.sort((a, b) => new Date(b.creado_en) - new Date(a.creado_en));
        allLeads = leads;

        renderLeads(leads);
        updateMetrics(leads);

        if (leads.some(l => l.estado === 'investigando' || l.estado === 'esperando_saldo')) {
            startPolling();
        }
    } catch (error) {
        console.error("Error conexión:", error);
        if (leadsBody) leadsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--neon-pink);">Error de conexión.</td></tr>`;
    }
}

// Helper: Limpiar teléfono para WhatsApp - Formato Argentina (v4.9.6)
function sanitizePhone(num) {
    if (!num) return '';
    // Eliminar todo lo que no sea dígito
    let clean = num.toString().replace(/\D/g, '');
    // Normalización Argentina:
    // Formato local 0351... → 549351... (agrega 54 + 9)
    if (clean.startsWith('0') && clean.length >= 10) {
        clean = '549' + clean.slice(1);
    }
    // Formato +54 351... (sin 9 de móvil) → 549351...
    // Ej: 543514751500 (12 dígitos) → 5493514751500 (13 dígitos)
    if (clean.startsWith('54') && clean.length === 12 && clean[2] !== '9') {
        clean = '549' + clean.slice(2);
    }
    return clean;
}

function renderLeads(leads) {
    if (!leadCount || !leadsBody) return;
    leadCount.textContent = `${leads.length} prospectos`;

    // Paginación (v4.7.0)
    const startIndex = (currentPage - 1) * LEADS_PER_PAGE;
    const paginatedLeads = leads.slice(startIndex, startIndex + LEADS_PER_PAGE);

    leadsBody.innerHTML = '';

    if (leads.length === 0) {
        leadsBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted);">Sin leads registrados.</td></tr>`;
        return;
    }

    paginatedLeads.forEach(lead => {
        const telRaw = lead.telefono || lead.telefono_dueno || (lead.telefonos_hallados ? lead.telefonos_hallados.split(',')[0] : null);
        const telSanitized = sanitizePhone(telRaw);
        const contactoDisplay = lead.nombre_dueno || lead.contacto_clave || 'Desconocido';
        const contactoBadge = (lead.telefono || lead.email) ? `<span style="color: var(--accent-emerald); font-size: 0.875rem; font-weight:700;">PRO</span>` : '';

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-primary);">${lead.empresa}</div>
                ${telRaw ? `
                    <a href="https://wa.me/${telSanitized}" target="_blank" title="WhatsApp" style="font-size: 0.875rem; color: var(--accent-indigo); text-decoration: none; display: flex; align-items: center; gap: 4px; margin-top: 4px; font-weight: 500;">
                        <span style="color: var(--accent-emerald);">●</span> ${telRaw}
                    </a>
                ` : ''}
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 6px; opacity: 0.7; letter-spacing: 0.05em;">
                    ${new Date(lead.creado_en).toLocaleDateString('es-AR')}
                </div>
            </td>
            <td><a href="${lead.url || '#'}" target="_blank" style="color: var(--accent-indigo); text-decoration: none; font-size: 0.875rem; font-weight: 600;">${lead.url ? new URL(lead.url).hostname : 'N/A'}</a></td>
            <td>
                <div style="font-size: 0.875rem; color: var(--text-secondary); max-width: 220px; font-style: italic;">
                    ${lead.falla_detectada || '—'}
                </div>
            </td>
            <td>
                <span class="state-tag state-${lead.estado}">
                    ${lead.estado ? lead.estado.replace('_', ' ') : 'N/A'}
                </span>
            </td>
            <td>
                <div class="actions-cell" style="display:flex; gap:8px;">
                    ${(lead.url && lead.estado !== 'investigando') ? `
                        <button onclick="iniciarAuditoria(${lead.id})" class="premium-btn secondary" style="padding: 6px 12px; font-size: 0.875rem; width: auto;">
                            AUDITAR
                        </button>` : ''}
                    ${(lead.estado === 'analizado' || lead.puntos_de_dolor || lead.pitch_ia) ? `
                        <button onclick="openReport(${lead.id})" class="premium-btn" style="padding: 6px 12px; font-size: 0.875rem; width: auto; background: var(--accent-emerald); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);">INFORME</button>` : ''}
                    <button onclick="deleteLead(${lead.id})" style="background: rgba(244, 63, 94, 0.1); border: 1px solid rgba(244, 63, 94, 0.3); color: var(--accent-rose); padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.875rem;">X</button>
                </div>
            </td>
        `;
        leadsBody.appendChild(tr);
    });

    renderPagination(leads.length);
}

// Función de Paginación (v5.1.0)
function renderPagination(totalItems) {
    const totalPages = Math.ceil(totalItems / LEADS_PER_PAGE);
    let paginationDiv = document.getElementById('paginationControls');
    if (!paginationDiv) {
        paginationDiv = document.createElement('div');
        paginationDiv.id = 'paginationControls';
        paginationDiv.className = 'pagination-container';
        if (leadsBody && leadsBody.parentElement) {
            leadsBody.parentElement.parentElement.appendChild(paginationDiv);
        }
    }
    if (totalPages <= 1) {
        if (paginationDiv) paginationDiv.style.display = 'none';
        return;
    }
    paginationDiv.style.display = 'flex';
    paginationDiv.innerHTML = `
        <button class="pagination-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>← Anterior</button>
        <span class="page-info">Página <span>${currentPage}</span> de ${totalPages}</span>
        <button class="pagination-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>Siguiente →</button>
    `;
}

window.changePage = (newPage) => {
    const totalPages = Math.ceil(allLeads.length / LEADS_PER_PAGE);
    if (newPage < 1 || newPage > totalPages) return;
    currentPage = newPage;
    renderLeads(allLeads);
};

function updateMetrics(leads) {
    const statsTotal = document.getElementById('statsTotal');
    const statsContactados = document.getElementById('statsContactados');
    const statsRespondidos = document.getElementById('statsRespondidos');
    const statsConversion = document.getElementById('statsConversion');
    if (!statsTotal) return;
    const total = leads.length;
    const contactados = leads.filter(l => ['contactado', 'enviado', 'respondido', 'reunion', 'ganado'].includes(l.estado)).length;
    const respondidos = leads.filter(l => ['respondido', 'reunion', 'ganado'].includes(l.estado)).length;
    const ganados = leads.filter(l => l.estado === 'ganado').length;

    // Cálculos de porcentajes
    const respPerc = total > 0 ? ((respondidos / total) * 100).toFixed(1) : 0;
    const conversion = contactados > 0 ? ((ganados / contactados) * 100).toFixed(1) : 0;

    statsTotal.textContent = total;
    statsContactados.textContent = contactados;
    statsRespondidos.textContent = `${respondidos} (${respPerc}%)`;
    statsConversion.textContent = `${conversion}%`;
}

// Helper: Asegurar que un campo sea objeto usable
function parseSafe(val) {
    if (!val) return {};
    if (typeof val === 'object') return val;
    try { return JSON.parse(val); } catch (e) { return {}; }
}

// LÓGICA DE MODAL E INFORME (v4.8.1)
const reportModal = document.getElementById('reportModal');
let currentLeadId = null;

window.openReport = async (id) => {
    currentLeadId = id;
    try {
        const response = await fetch(`${API_BASE_URL}/${id}?t=${Date.now()}`);
        const lead = await response.json();
        currentLeadData = lead; // Nivel 1: guardar datos del lead activo

        const versionStr = lead.audit_tecnico ? "v4.9.0" : "v4.0";
        const informe = parseSafe(lead.informe_detallado);
        const auditTech = parseSafe(lead.audit_tecnico);
        const whois = parseSafe(lead.whois_data);
        const seo = auditTech.seo || auditTech.SEO || {};
        const ux = auditTech.ux || auditTech.UX || {};
        const perf = auditTech.performance || auditTech.Performance || {};
        const pitchContenido = lead.pitch_curado || "";

        const pageTitle = seo.title || "";
        const isBlocked = pageTitle.includes("Checking your browser") || pageTitle.includes("Just a moment");
        const wafWarning = isBlocked ? `<div style="background:rgba(255,50,50,0.1); border:1px solid var(--neon-pink); color:var(--neon-pink); padding:8px; border-radius:4px; font-size:0.875rem; margin-bottom:10px;">⚠️ ACCESO LIMITADO: Protección anti-bot detectada.</div>` : "";

        reportModal.innerHTML = `
            <div class="modal-content glass-panel" style="max-height: 94vh; display: flex; flex-direction: column; padding: 0;">
                <!-- HEADER PREMIUM -->
                <div class="modal-header-top" style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid var(--glass-border); padding: 1.5rem 2rem; background: var(--bg-deep);">
                    <div style="display: flex; align-items: center; gap: 1rem;">
                        <div style="width:40px; height:40px; background: var(--accent-indigo); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:1.2rem; box-shadow: 0 0 20px var(--glass-glow);">📊</div>
                        <div>
                            <h2 style="margin:0; font-size: 1.25rem;">${lead.empresa || 'Auditoría'}</h2>
                            <span style="font-size: 0.875rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.1em; font-weight:700;">Baraldi Intelligence Core 2026</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <span style="font-size: 0.875rem; color: var(--text-muted); font-weight: 800; letter-spacing: 0.05em;">ESTADO CRM:</span>
                        <select id="crmStateSelect" class="premium-btn secondary" style="width: auto; padding: 6px 16px; font-size: 0.875rem; background: var(--bg-obsidian); border-color: var(--accent-indigo); color: var(--accent-indigo); outline:none;">
                            <option value="analizado" ${lead.estado === 'analizado' ? 'selected' : ''}>📊 ANALIZADO</option>
                            <option value="contactado" ${lead.estado === 'contactado' ? 'selected' : ''}>🎯 CONTACTADO</option>
                            <option value="respondido" ${lead.estado === 'respondido' ? 'selected' : ''}>💬 RESPONDIDO</option>
                            <option value="ganado" ${lead.estado === 'ganado' ? 'selected' : ''}>💰 GANADO</option>
                        </select>
                        <button onclick="saveAllChanges(${lead.id})" class="premium-btn" style="width: auto; padding: 8px 24px; font-size: 0.875rem; background: var(--accent-emerald);">GUARDAR</button>
                        <button onclick="closeModal()" class="premium-btn secondary" style="width: auto; padding: 8px 15px; border:none; font-size: 1.2rem; cursor:pointer;">✖</button>
                    </div>
                </div>

                <div class="modal-scroll-area" style="padding: 2rem; overflow-y: auto;">
                    ${wafWarning}
                    <div class="matrix-grid" style="display: grid; gap: 2.5rem; align-items: start;">
                        
                        <!-- COLUMNA 1: DIAGNÓSTICO TÉCNICO (Evidencia) -->
                        <div class="diagnostic-column">
                            <h3 style="font-size: 0.875rem; text-transform: uppercase; color: var(--accent-indigo); margin-bottom: 1.5rem; letter-spacing: 0.05em; display:flex; align-items:center; gap:10px;">
                                <span style="width:16px; height:2px; background:var(--accent-indigo);"></span> Matriz de Evidencia & Autoridad
                            </h3>
                            
                            <!-- TARJETAS DE MÉTRICAS CLAVE -->
                            <div class="pillars-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem;">
                                <div class="metric-card">
                                    <span class="metric-label">Antigüedad Domain</span>
                                    <div style="display:flex; justify-content:space-between; align-items:end;">
                                        <span class="metric-value">${(whois.antiguedad_anios !== null && whois.antiguedad_anios !== undefined) ? whois.antiguedad_anios : (lead.antiguedad_dominio || 'N/D')} Años</span>
                                        <span style="font-size: 0.875rem; font-weight:700; color: var(--accent-indigo);">${whois.registrar ? whois.registrar.split(' ')[0].substring(0, 12) : 'REGISTRAR'}</span>
                                    </div>
                                </div>
                                <div class="metric-card">
                                    <span class="metric-label">Eficiencia (Peso)</span>
                                    <div style="display:flex; justify-content:space-between; align-items:end;">
                                        <span class="metric-value" style="color: ${perf.totalSizeKB > 2000 ? 'var(--accent-rose)' : 'var(--text-primary)'}">${perf.totalSizeKB || 0} KB</span>
                                        <span style="font-size: 0.875rem; color: var(--text-muted); font-weight:700;">${perf.resourcesCount || 0} RECURSOS</span>
                                    </div>
                                </div>
                                <div class="metric-card">
                                    <span class="metric-label">SSL & Seguridad</span>
                                    <div style="display:flex; justify-content:space-between; align-items:end;">
                                        <span class="metric-value" style="color: ${auditTech.ssl === 'SÍ' ? 'var(--accent-emerald)' : 'var(--accent-rose)'}">${auditTech.ssl === 'SÍ' ? 'PROTEGIDO' : 'INSEGURO'}</span>
                                        <span style="font-size: 0.875rem; font-weight:700; color: var(--text-muted);">${whois.dnssec ? 'DNSSEC' : 'BÁSICO'}</span>
                                    </div>
                                </div>
                                <div class="metric-card">
                                    <span class="metric-label">Performance Core</span>
                                    <div style="display:flex; justify-content:space-between; align-items:end;">
                                        <span class="metric-value" style="color: ${perf.score >= 80 ? 'var(--accent-emerald)' : (perf.score >= 50 ? 'var(--accent-amber)' : 'var(--accent-rose)')}">${perf.score || 0}%</span>
                                        <span style="font-size: 0.875rem; color: var(--text-muted); font-weight:700;">LIGHTHOUSE</span>
                                    </div>
                                </div>
                            </div>

                            <!-- ALARMAS DE NEGOCIO -->
                            <section style="margin-bottom: 2rem;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
                                    <h3 style="font-size: 0.875rem; text-transform: uppercase; color: var(--accent-rose); margin:0; letter-spacing: 0.05em; display:flex; align-items:center; gap:10px;">
                                        <span style="width:16px; height:2px; background:var(--accent-rose);"></span> Alarmas Estratégicas detectadas
                                    </h3>
                                    ${whois.expiracion ? (() => {
                                        const exp = new Date(whois.expiracion);
                                        const today = new Date();
                                        const dd = String(exp.getDate()).padStart(2, '0');
                                        const mm = String(exp.getMonth() + 1).padStart(2, '0');
                                        const yyyy = exp.getFullYear();
                                        const dateStr = `${dd}/${mm}/${yyyy}`;
                                        
                                        let months = (exp.getFullYear() - today.getFullYear()) * 12 + (exp.getMonth() - today.getMonth());
                                        let days = exp.getDate() - today.getDate();
                                        if (days < 0) {
                                            months--;
                                            const lastDayPrevMonth = new Date(exp.getFullYear(), exp.getMonth(), 0).getDate();
                                            days += lastDayPrevMonth;
                                        }
                                        
                                        let timeText = "";
                                        if (months > 0) timeText += `${months}m `;
                                        if (days > 0) timeText += `${days}d`;
                                        const remaining = (months < 0) ? "Vencido" : `Falta ${timeText.trim()}`;
                                        
                                        return `<span style="font-size: 0.875rem; background: rgba(244, 63, 94, 0.1); color: var(--accent-rose); padding: 4px 10px; border-radius: 6px; font-weight:700; white-space: nowrap;">EXP: ${dateStr} (${remaining})</span>`;
                                    })() : ''}
                                </div>
                                ${(() => {
                const alarmas = [];

                // 🕰️ ALARMA DOMINIO NUEVO (Riesgo de volatilidad)
                const age = whois.antiguedad_anios !== null ? whois.antiguedad_anios : lead.antiguedad_dominio;
                if (age !== null && age !== undefined && age < 2) {
                    alarmas.push({
                        icon: '🌱', nivel: 'MEDIA',
                        titulo: 'Dominio Reciente — Falta de Autoridad',
                        desc: `El dominio tiene solo ${age} año(s). Esto indica un negocio nuevo o una marca que cambió de sitio recientemente, lo cual afecta el posicionamiento orgánico histórico.`
                    });
                }

                // 🔒 ALARMA SSL
                if (auditTech.ssl === 'NO' || auditTech.ssl === 'Vencido') {
                    alarmas.push({
                        icon: '🔓', nivel: 'ALTA',
                        titulo: 'Sitio sin HTTPS — Barrera de Confianza',
                        desc: 'El certificado SSL está ausente. Los navegadores modernos muestran "Sitio no seguro". Esto destruye la conversión antes de que el prospecto lea una sola línea.'
                    });
                }

                // 📱 ALARMA PERFORMANCE
                if (perf.score && perf.score < 40) {
                    alarmas.push({
                        icon: '🐌', nivel: 'ALTA',
                        titulo: `Performance Crítica — ${perf.score}/100`,
                        desc: `Velocidad de carga inaceptable. El LCP es de ${perf.lcp || 'N/D'}ms. Google penaliza activamente sitios con este rendimiento en dispositivos móviles.`
                    });
                }

                // 🔍 ALARMA SEO ESTRUCTURAL
                if ((seo.h1Count || 0) === 0) {
                    alarmas.push({
                        icon: '🔍', nivel: 'ALTA',
                        titulo: 'Invisibilidad SEO — Sin H1 detectado',
                        desc: 'El sitio no tiene un título principal definido. Google no sabe de qué trata el negocio. Es como un local sin cartel en la calle.'
                    });
                }

                // ⚖️ ALARMA PESO (EFICIENCIA)
                if (perf.totalSizeKB > 4000) {
                    alarmas.push({
                        icon: '⚖️', nivel: 'MEDIA',
                        titulo: `Sitio Sobrecargado — ${Math.round(perf.totalSizeKB / 1024)}MB`,
                        desc: `La home es extremadamente pesada. Esto agota los datos móviles del cliente y aumenta la tasa de rebote instantáneo.`
                    });
                }

                if (alarmas.length === 0) {
                    return `<div style="padding: 1rem; color: var(--accent-emerald); font-size: 0.875rem; background: rgba(16,185,129,0.05); border: 1px solid rgba(16,185,129,0.2); border-radius: 12px;">✅ Sin fallas críticas evidentes en el primer análisis.</div>`;
                }

                return alarmas.map(a => `
                                        <div style="margin-bottom: 0.75rem; padding: 1rem 1.25rem; background: rgba(244, 63, 94, 0.04); border: 1px solid rgba(244, 63, 94, 0.2); border-left: 4px solid ${a.nivel === 'ALTA' ? 'var(--accent-rose)' : 'var(--accent-amber)'}; border-radius: 12px;">
                                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 0.4rem;">
                                                <h4 style="font-size: 0.875rem; color: var(--text-primary); margin:0; display:flex; align-items:center; gap:6px;">${a.icon} ${a.titulo}</h4>
                                                <span style="font-size: 0.875rem; font-weight:800; letter-spacing:0.08em; color: ${a.nivel === 'ALTA' ? 'var(--accent-rose)' : 'var(--accent-amber)'};">${a.nivel}</span>
                                            </div>
                                            <p style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5; margin:0;">${a.desc}</p>
                                        </div>
                                    `).join('');
            })()}
                            </section>

                            <!-- ESTRATEGIA SEO & METADATOS (EVIDENCIA 360) -->
                            <section style="margin-bottom: 2rem;">
                                <h3 style="font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; letter-spacing: 0.05em; display:flex; align-items:center; gap:10px;">
                                    <span style="width:16px; height:2px; background:var(--text-muted);"></span> Estrategia SEO & Metadatos
                                </h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                                    <div class="info-card" style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; border: 1px solid var(--glass-border);">
                                        <div style="font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">Titulares Primarios (H1)</div>
                                        <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.4;">${seo.h1Text || 'No detectados o vacíos'}</div>
                                    </div>
                                    <div class="info-card" style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 12px; border: 1px solid var(--glass-border);">
                                        <div style="font-size: 0.875rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">Huella de Construcción & Propiedad</div>
                                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                                            <div style="margin-bottom: 4px; color: var(--accent-emerald);"><strong>Titular:</strong> ${whois.registrante || whois.organizacion || 'Privado / No detectado'}</div>
                                            <div style="margin-bottom: 4px;"><strong>Autor:</strong> ${seo.author || 'Genérico'}</div>
                                            <div style="margin-bottom: 4px;"><strong>Schema:</strong> ${seo.hasSchema ? (seo.schemaTypes || []).join(', ') : 'Ninguno'}</div>
                                            <div><strong>Localización:</strong> ${seo.location || 'Global/No decl.'}</div>
                                        </div>
                                    </div>
                                </div>
                            </section>

                            <!-- STACK TECNOLÓGICO -->
                            <section>
                                <h3 style="font-size: 0.875rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 1rem; letter-spacing: 0.05em; display:flex; align-items:center; gap:10px;">
                                    <span style="width:16px; height:2px; background:var(--text-muted);"></span> Engine & Stack Detectado
                                </h3>
                                <div style="display:flex; flex-wrap:wrap; gap:8px;">
                                   ${(() => {
                const rawStack = auditTech.tech_stack || lead.tecnologias_detectadas || {};
                const stackEntries = Object.entries(rawStack);
                return stackEntries.length > 0 ? stackEntries.map(([name, data]) => `
                                            <span class="tech-tag" style="background:rgba(99,102,241,0.05); color:var(--accent-indigo); border: 1px solid rgba(99,102,241,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.875rem; font-weight: 700;">
                                                ${name} ${data.version ? `<span style="opacity:0.5; font-weight:400; margin-left:4px;">${data.version}</span>` : ''}
                                            </span>
                                       `).join('') : '<span style="color:var(--text-muted); font-size:0.875rem;">Sin datos de stack detallados.</span>';
            })()}
                                </div>
                            </section>
                        </div>

                        <!-- COLUMNA 2: ESTRATEGIA DE CONTACTO & IA -->
                        <div class="strategy-column" style="background: rgba(15, 23, 42, 0.5); padding: 2rem; border-radius: 24px; border: 1px solid var(--glass-border); box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                            <h3 style="font-size: 0.875rem; text-transform: uppercase; color: var(--accent-emerald); margin-bottom: 1.5rem; letter-spacing: 0.05em; display:flex; align-items:center; gap:10px;">
                                <span style="width:16px; height:2px; background:var(--accent-emerald);"></span> Ficha de Contacto & IA
                            </h3>
                            
                            <!-- FICHA EDITABLE -->
                            <div class="ficha-empresa" style="margin-bottom: 2rem; display:grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; font-size: 0.875rem;">
                                <div>
                                    <span class="edit-label">Empresa</span>
                                    <div contenteditable="true" id="edit-empresa" class="editable-field">${lead.empresa || ''}</div>
                                </div>
                                <div>
                                    <span class="edit-label">WhatsApp</span>
                                    <div contenteditable="true" id="edit-tel" class="editable-field" style="color:var(--accent-emerald);">${lead.telefono || lead.telefono_dueno || ''}</div>
                                </div>
                                <div>
                                    <span class="edit-label">Email</span>
                                    <div contenteditable="true" id="edit-email" class="editable-field">${lead.email || ''}</div>
                                </div>
                                <div style="grid-column: span 2;">
                                    <span class="edit-label">Domicilio</span>
                                    <div contenteditable="true" id="edit-dir" class="editable-field" style="font-size: 0.8rem;">${lead.direccion || ''}</div>
                                </div>
                            </div>

                            <!-- MATRIZ DE CONTACTO (EVIDENCIA DE EXTRACCIÓN) -->
                            <div style="margin-bottom: 2rem; padding: 1.25rem; background: rgba(15, 23, 42, 0.4); border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); box-shadow: inset 0 0 20px rgba(16, 185, 129, 0.05);">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem;">
                                    <div style="font-size: 0.875rem; color: var(--accent-emerald); text-transform: uppercase; letter-spacing: 0.1em; font-weight:800; display:flex; align-items:center; gap:8px;">
                                        <span style="font-size:1.1rem;">🎯</span> Matriz de Contacto
                                    </div>
                                    <span style="font-size: 0.75rem; color: var(--text-muted);">${lead.paginas_auditadas || 0} pág. rastreadas</span>
                                </div>
                                
                                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                                    <!-- TELÉFONOS / WHATSAPP -->
                                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                        ${(() => {
                const teltodos = (lead.telefonos_hallados || '').split(',').map(t => t.trim()).filter(t => t);
                const contacted = (lead.telefonos_contactados || '').split(',').map(t => t.trim());

                if (teltodos.length === 0) return '<div style="font-size:0.8rem; color:var(--text-muted); font-style:italic;">No se detectaron teléfonos adicionales.</div>';

                return teltodos.map(t => {
                    const isWA = t.startsWith('549') || t.length > 10;
                    const isContacted = contacted.includes(t);
                    return `
                                                    <div data-contact-value="${t}" style="background: ${isContacted ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)'}; border: 1px solid ${isContacted ? 'var(--accent-emerald)' : 'rgba(255,255,255,0.1)'}; color: var(--text-primary); padding: 6px 12px; border-radius: 12px; font-size: 0.875rem; display: flex; align-items: center; gap: 8px; transition: all 0.2s;">
                                                        <span style="color: ${isWA ? 'var(--accent-emerald)' : 'var(--text-muted)'}; font-size:1rem;">${isWA ? '💬' : '📞'}</span>
                                                        <span style="font-family:monospace; font-weight:600;">${t}</span>
                                                        <span class="status-icon" style="display: ${isContacted ? 'inline' : 'none'}; color: var(--accent-emerald); font-size:0.75rem;">✅</span>
                                                        <div style="display:flex; gap:6px; margin-left:8px; padding-left:8px; border-left:1px solid rgba(255,255,255,0.1);">
                                                            <button onclick="abrirWhatsApp('${t}')" title="Enviar WhatsApp" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1rem; filter:grayscale(1) brightness(1.5);">🚀</button>
                                                            <button onclick="marcarContacto(${lead.id}, 'telefono', '${t}')" title="Marcar como enviado" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1.1rem; filter:grayscale(1);">✔️</button>
                                                            <button onclick="removerHallazgo(${lead.id}, 'telefono', '${t}')" title="Eliminar y no mostrar más" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1.1rem; filter:grayscale(1); opacity:0.5;">🗑️</button>
                                                        </div>
                                                    </div>
                                                `;
                }).join('');
            })()}
                                    </div>

                                    <!-- EMAILS -->
                                    <div style="display: flex; flex-wrap: wrap; gap: 8px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 0.75rem;">
                                        ${(() => {
                const mailtodos = (lead.emails_hallados || '').split(',').map(m => m.trim()).filter(m => m);
                const contacted = (lead.emails_contactados || '').split(',').map(m => m.trim());

                if (mailtodos.length === 0) return '<div style="font-size:0.8rem; color:var(--text-muted); font-style:italic;">No se detectaron correos adicionales.</div>';

                return mailtodos.map(m => {
                    const isContacted = contacted.includes(m);
                    return `
                                                    <div data-contact-value="${m}" style="background: ${isContacted ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)'}; border: 1px solid ${isContacted ? 'var(--accent-indigo)' : 'rgba(255,255,255,0.1)'}; color: var(--text-primary); padding: 6px 12px; border-radius: 12px; font-size: 0.875rem; display: flex; align-items: center; gap: 8px; transition: all 0.2s;">
                                                        <span style="color: var(--accent-indigo); font-size:1rem;">📧</span>
                                                        <span style="font-weight:500;">${m}</span>
                                                        <span class="status-icon" style="display: ${isContacted ? 'inline' : 'none'}; color: var(--accent-indigo); font-size:0.75rem;">✅</span>
                                                        <div style="display:flex; gap:6px; margin-left:8px; padding-left:8px; border-left:1px solid rgba(255,255,255,0.1);">
                                                            <button onclick="abrirEmail('${m}')" title="Enviar Email" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1rem; filter:grayscale(1) brightness(1.5);">🚀</button>
                                                            <button onclick="marcarContacto(${lead.id}, 'email', '${m}')" title="Marcar como enviado" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1.1rem; filter:grayscale(1);">✔️</button>
                                                            <button onclick="removerHallazgo(${lead.id}, 'email', '${m}')" title="Eliminar y no mostrar más" style="background:none; border:none; cursor:pointer; padding:2px; font-size:1.1rem; filter:grayscale(1); opacity:0.5;">🗑️</button>
                                                        </div>
                                                    </div>
                                                `;
                }).join('');
            })()}
                                    </div>
                                </div>
                            </div>

                            <!-- OBSERVACIONES HUMANAS -->
                            <div style="margin-bottom: 1.5rem;">
                                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                                    <span style="font-size:0.875rem; text-transform:uppercase; color:var(--accent-amber); font-weight:800;">👁️ Inyección de Observaciones</span>
                                </div>
                                <textarea id="observacionesHumanas" placeholder="Ej: Estética antigua, mobile roto, falta de Call to Action claro..." style="width:100%; min-height:80px; background:rgba(245,158,11,0.03); border:1px solid rgba(245,158,11,0.2); border-radius:12px; padding:12px; color:var(--text-primary); font-size:0.875rem; line-height:1.5; outline:none; font-family:inherit;">${lead.observaciones_humanas || ''}</textarea>
                            </div>

                            <!-- PITCH IA -->
                            <div style="margin-bottom: 1.5rem;">
                                 <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                                    <h4 style="font-size:0.875rem; text-transform:uppercase; color: var(--text-secondary); margin:0;">Propuesta de Valor</h4>
                                    <button onclick="copiarPromptMaestro(${lead.id})" class="premium-btn secondary" style="width:auto; padding: 4px 10px; font-size:0.875rem;">📋 COPIAR PROMPT</button>
                                 </div>
                                 <div id="salesPitchText" contenteditable="true" style="max-height:250px; overflow-y:auto; font-size:0.9rem; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: 12px; padding: 1.25rem; color: var(--text-primary); line-height: 1.6; outline:none;">${pitchContenido}</div>
                            </div>

                            <div style="display: grid; grid-template-columns: 1fr; gap: 1rem;">
                                <button onclick="saveAllChanges(${lead.id})" class="premium-btn" style="font-size: 0.875rem;">💾 GUARDAR CAMBIOS Y NOTAS</button>
                            </div>
                            </div>
                            
                            <textarea id="masterPromptContent" style="display:none;"></textarea>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Cargar Prompt Maestro asíncronamente
        (async () => {
            const promptBox = document.getElementById('masterPromptContent');
            if (promptBox && id) {
                try {
                    const resp = await fetch(`${API_BASE_URL}/${id}/prompt`);
                    const data = await resp.json();
                    promptBox.value = data.prompt || "Error cargando prompt.";
                } catch (err) { console.error(err); }
            }
        })();

        reportModal.classList.add('active');
    } catch (e) {
        console.error("Error al abrir informe:", e);
    }
};

window.saveAllChanges = async (id) => {
    const editor = document.getElementById('salesPitchText');
    const stateSelect = document.getElementById('crmStateSelect');
    const obsTextarea = document.getElementById('observacionesHumanas');

    const payload = {
        empresa: document.getElementById('edit-empresa')?.innerText || "",
        email: document.getElementById('edit-email')?.innerText || "",
        telefono: document.getElementById('edit-tel')?.innerText || "",
        direccion: document.getElementById('edit-dir')?.innerText || "",
        pitch_curado: editor ? editor.innerHTML : "",
        observaciones_humanas: obsTextarea ? obsTextarea.value : "",
        estado: stateSelect ? stateSelect.value : ""
    };

    try {
        const resp = await fetch(`${API_BASE_URL}/${id}/analysis`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (resp.ok) {
            alert('Cambios guardados correctamente.');
            fetchLeads();
        }
    } catch (e) { console.error("Error al guardar:", e); }
};

window.copiarPromptMaestro = async (id) => {
    const promptBox = document.getElementById('masterPromptContent');
    const obsTextarea = document.getElementById('observacionesHumanas');
    if (!promptBox) return;

    // 1. Guardar observaciones en BD antes de regenerar el prompt
    const obsValue = obsTextarea ? obsTextarea.value.trim() : '';
    if (obsValue) {
        try {
            await fetch(`${API_BASE_URL}/${id}/analysis`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ observaciones_humanas: obsValue })
            });
        } catch (err) { console.warn('No se pudieron guardar las observaciones:', err); }
    }

    // 2. Regenerar el prompt fresco (ya con las observaciones inyectadas en BD)
    try {
        const resp = await fetch(`${API_BASE_URL}/${id}/prompt?t=${Date.now()}`);
        const data = await resp.json();
        const freshPrompt = data.prompt || promptBox.value || '';
        promptBox.value = freshPrompt;

        // 3. Copiar al portapapeles
        await navigator.clipboard.writeText(freshPrompt);
        alert('Prompt copiado al portapapeles.' + (obsValue ? '\n✅ Observaciones incluidas.' : ''));
    } catch (err) {
        // Fallback si falla clipboard API o el fetch
        const textToCopy = promptBox.value;
        const textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        alert('Prompt copiado (fallback).');
    }
};

window.closeModal = () => reportModal.classList.remove('active');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// NIVEL 1: AUTOMATIZACIÓN DE ENVÍO
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Convierte HTML a texto plano limpio.
 * Maneja tags de Angular/Gemini Web que se pegan desde el editor.
 */
function htmlToPlainText(html) {
    if (!html) return '';
    // Si no contiene tags HTML, devolver directo
    if (!html.includes('<')) return html;
    // Convertir bloques estructurales a saltos de línea ANTES de strip
    const withBreaks = html
        .replace(/<br\s*\/?>/gi, '\n')
        .replace(/<\/p>/gi, '\n\n')
        .replace(/<\/div>/gi, '\n')
        .replace(/<\/li>/gi, '\n')
        .replace(/<li>/gi, '\u2022 ');
    // Usar el DOM del navegador para strip limpio (maneja entidades HTML)
    const tmp = document.createElement('div');
    tmp.innerHTML = withBreaks;
    const text = tmp.textContent || tmp.innerText || '';
    // Limpiar líneas vacías múltiples y espacios extra
    return text.replace(/\n{3,}/g, '\n\n').trim();
}

function extractEmailFromPitch(pitch, empresa) {
    if (!pitch) return { subject: `Consulta - ${empresa}`, body: '' };
    // Limpiar HTML primero (incluyendo tags de Angular/Gemini Web)
    const clean = htmlToPlainText(pitch);

    // 1. Extraer cuerpo del email (NUEVO FORMATO: [5. PITCH_EMAIL] o CUERPO DEL EMAIL)
    // Buscamos desde el tag hasta el siguiente tag [6. o el final
    const fullPitchMatch = clean.match(/(?:\[5\. PITCH_EMAIL\]|CUERPO DEL_EMAIL)[^\n]*\n+([\s\S]*?)(?=\n\[6\.|\[6\.|$)/i);
    let bodyRaw = fullPitchMatch ? fullPitchMatch[1].trim() : clean.substring(0, 1500);

    // 2. Limpieza de ASUNTOS (Si están dentro del cuerpo, los quitamos para que el body empiece en el saludo)
    // El saludo suele ser "Hola,", "Buen día,", etc. 
    // Buscamos la primera ocurrencia de "Hola" o "Buen día" para limpiar el cabezal de asuntos si se coló
    const greetingMatch = bodyRaw.match(/(?:Hola|Buen día|Estimado)[\s\S]*/i);
    const body = greetingMatch ? greetingMatch[0].trim() : bodyRaw;

    // 3. Extraer asunto (primer asunto disponible después de "ASUNTOS:")
    const subjectMatch = clean.match(/(?:Urgencia|Curiosidad|Beneficio)[^\n:]*:[^\n]*\n?([^\n]+)/i);
    const subject = subjectMatch ? subjectMatch[1].replace(/^[\u2014\-]\s*/, '').trim() : `Consulta - ${empresa}`;

    return { subject, body };
}

function extractWhatsAppFromPitch(pitch) {
    if (!pitch) return '';
    // Limpiar HTML primero
    const clean = htmlToPlainText(pitch);
    const match = clean.match(/\[6\. MENSAJE_WHATSAPP\]\n([\s\S]*?)(?=\(Caracteres|\[7\.|$)/i);
    return match ? match[1].trim() : clean.substring(0, 450);
}

async function autoContactar() {
    // Cambiar estado a contactado en el selector
    const stateSelect = document.getElementById('crmStateSelect');
    if (stateSelect) stateSelect.value = 'contactado';
    // Guardar automáticamente
    if (currentLeadId) {
        await saveAllChanges(currentLeadId);
        console.log('[Nivel 1] Pitch guardado y estado actualizado a contactado.');
    }
}

window.abrirEmail = async (customEmail = null) => {
    if (!currentLeadData) { alert('No hay lead activo.'); return; }
    const editor = document.getElementById('salesPitchText');
    const pitch = (editor && editor.innerHTML.trim())
        ? editor.innerHTML
        : (currentLeadData.pitch_curado || currentLeadData.pitch_ia || '');

    if (!pitch || pitch.trim() === '') { alert('Este lead todavía no tiene pitch generado.'); return; }

    const { subject, body } = extractEmailFromPitch(pitch, currentLeadData.empresa);
    const email = customEmail || currentLeadData.email || currentLeadData.email_dueno || '';

    const mailtoUrl = `mailto:${email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.open(mailtoUrl);

    // Marcar como contactado automáticamente
    if (customEmail) {
        await marcarContacto(currentLeadData.id, 'email', customEmail);
    }
    await autoContactar();
};

window.abrirWhatsApp = async (customPhone = null) => {
    if (!currentLeadData) { alert('No hay lead activo.'); return; }
    const editor = document.getElementById('salesPitchText');
    const pitch = (editor && editor.innerHTML.trim())
        ? editor.innerHTML
        : (currentLeadData.pitch_curado || currentLeadData.pitch_ia || '');

    if (!pitch || pitch.trim() === '') { alert('Este lead todavía no tiene pitch generado.'); return; }

    const msg = extractWhatsAppFromPitch(pitch);
    const rawPhone = customPhone || currentLeadData.telefono || currentLeadData.telefono_dueno || '';
    const phone = sanitizePhone(rawPhone);

    if (!phone) { alert('No hay número válido registrado.'); return; }

    const waUrl = `https://wa.me/${phone}?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank');

    // Marcar como contactado automáticamente
    if (customPhone) {
        await marcarContacto(currentLeadData.id, 'telefono', customPhone);
    }
    await autoContactar();
};

window.marcarContacto = async (id, tipo, valor) => {
    try {
        await fetch(`${API_BASE_URL}/${id}/marcar-contacto`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo, valor })
        });
        // Feedback visual inmediato si el modal está abierto
        const pill = document.querySelector(`[data-contact-value="${valor}"]`);
        if (pill) {
            pill.style.background = 'rgba(16, 185, 129, 0.25) !important';
            pill.style.borderColor = 'var(--accent-emerald) !important';
            const checkIcon = pill.querySelector('.status-icon');
            if (checkIcon) checkIcon.style.display = 'inline';
        }
    } catch (e) { console.error(e); }
};

window.removerHallazgo = async (id, tipo, valor) => {
    if (!confirm(`¿Estás seguro de eliminar "${valor}" e ignorarlo en el futuro?`)) return;
    try {
        const resp = await fetch(`${API_BASE_URL}/${id}/remover-hallazgo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo, valor })
        });
        if (resp.ok) {
            const pill = document.querySelector(`[data-contact-value="${valor}"]`);
            if (pill) pill.remove();
        }
    } catch (e) { console.error(e); }
};

window.switchTab = (tabId) => {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(`tab-${tabId}`).classList.add('active');
    const btns = document.querySelectorAll('.tab-btn');
    if (tabId === 'resumen') btns[0].classList.add('active');
    else if (tabId === 'crudo') btns[1].classList.add('active');
};

window.iniciarAuditoria = async (id) => {
    try {
        const response = await fetch(`${API_BASE_URL}/${id}/iniciar-auditoria`, { method: 'POST' });
        if (response.ok) fetchLeads();
    } catch (e) { }
};

window.deleteLead = async (id) => {
    if (!confirm('¿Eliminar prospecto?')) return;
    try {
        await fetch(`${API_BASE_URL}/${id}`, { method: 'DELETE' });
        fetchLeads();
    } catch (e) { }
};

// --- ✨ MAGIA: IMPORTACIÓN DESDE GOOGLE MAPS (v5.3.0) ---
const magicBtn = document.getElementById('magic-btn');
const mapsLinkInput = document.getElementById('maps-link');

if (magicBtn) {
    magicBtn.addEventListener('click', async () => {
        const url = mapsLinkInput.value.trim();
        if (!url) {
            alert('Por favor, pega un enlace de Google Maps primero.');
            return;
        }

        if (!url.includes('google.com/maps') && !url.includes('goo.gl/maps')) {
            alert('El enlace no parece ser de Google Maps válido.');
            return;
        }

        // Estado de carga
        magicBtn.disabled = true;
        magicBtn.innerHTML = '🕒';
        magicBtn.classList.add('loading');
        document.querySelector('.controls-panel')?.classList.add('loading-overlay');

        try {
            const response = await fetch(`${API_BASE_URL}/extract-maps`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (!response.ok) throw new Error('Error en la extracción');

            const data = await response.json();

            // Autocompletar campos
            if (data.empresa) document.getElementById('empresa').value = data.empresa;
            if (data.url) document.getElementById('url').value = data.url;
            if (data.telefono) document.getElementById('telefonoInput').value = data.telefono;
            if (data.direccion) document.getElementById('direccionInput').value = data.direccion;

            // Feedback visual de éxito
            magicBtn.innerHTML = '✅';
            setTimeout(() => { magicBtn.innerHTML = '✨'; }, 3000);
            
            console.log("Importación de Maps exitosa:", data);

        } catch (e) {
            console.error("Error Magic Import:", e);
            alert('No se pudo extraer la información. Google Maps suele ser complejo; intenta recargar el link o copiarlo de nuevo.');
            magicBtn.innerHTML = '❌';
            setTimeout(() => { magicBtn.innerHTML = '✨'; }, 3000);
        } finally {
            magicBtn.disabled = false;
            magicBtn.classList.remove('loading');
            document.querySelector('.controls-panel')?.classList.remove('loading-overlay');
        }
    });
}

if (prospectForm) {
    prospectForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nuevoLead = {
            empresa: document.getElementById('empresa')?.value || '',
            url: document.getElementById('url')?.value || null,
            telefono: document.getElementById('telefonoInput')?.value || null,
            direccion: document.getElementById('direccionInput')?.value || null,
            email: document.getElementById('emailInput')?.value || null,
            estado: "nuevo"
        };
        try {
            const response = await fetch(API_BASE_URL + '/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(nuevoLead)
            });
            if (response.ok) { prospectForm.reset(); fetchLeads(); }
        } catch (e) { }
    });
}

fetchLeads();
