/**
 * Chemo Companion — Frontend Application Logic
 * Preserves all existing API integration while adding new UI features.
 */
const API = window.location.origin;

const app = {
    currentPatientId: null,
    patients: [],
    charts: {},
    wearableWs: null,
    wearableReconnectTimer: null,
    latestSleep: null,
    micActive: false,
    streamingEnabled: true,   // Persisted in localStorage

    // ========================================================================
    // INIT
    // ========================================================================
    async init() {
        // Restore streaming preference
        const stored = localStorage.getItem('wearableStreamingEnabled');
        this.streamingEnabled = stored === null ? true : stored === 'true';
        this.updateGreeting();
        await this.loadPatients();
        this.setupNavigation();
        this.setupChatInput();
        this.initCharts();
    },

    updateGreeting() {
        const hour = new Date().getHours();
        const greetings = {
            morning: 'Good morning 🌸',
            afternoon: 'Good afternoon ☀️',
            evening: 'Good evening 🌙',
        };
        const label = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
        const titleEl = document.querySelector('.page-title');
        if (titleEl) titleEl.textContent = greetings[label];
    },

    async loadPatients() {
        try {
            const res = await fetch(`${API}/api/patients`);
            const data = await res.json();
            this.patients = data.patients || [];
            const select = document.getElementById('patient-select');
            select.innerHTML = this.patients.map(p =>
                `<option value="${p.id}">${p.first_name} ${p.last_name}</option>`
            ).join('');
            select.addEventListener('change', () => {
                this.currentPatientId = select.value;
                this.refreshDashboard();
                this.updateSidebarPatient();
                this.connectWearable();
            });
            if (this.patients.length > 0) {
                this.currentPatientId = this.patients[0].id;
                this.updateSidebarPatient();
                this.refreshDashboard();
                this.connectWearable();
            }
        } catch (e) {
            console.error('Failed to load patients:', e);
            // Show demo state gracefully
            document.getElementById('patient-greeting').textContent = 'Connect your backend to load patient data.';
            document.getElementById('sidebar-patient-name').textContent = 'Demo Patient';
        }
    },

    updateSidebarPatient() {
        const patient = this.patients.find(p => p.id === this.currentPatientId);
        if (!patient) return;
        const nameEl = document.getElementById('sidebar-patient-name');
        const avatarEl = document.getElementById('patient-avatar');
        if (nameEl) nameEl.textContent = `${patient.first_name} ${patient.last_name}`;
        if (avatarEl) avatarEl.textContent = patient.first_name ? patient.first_name[0].toUpperCase() : 'P';
    },

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
                document.getElementById(`page-${page}`).classList.add('active');
                if (page === 'reports') this.loadReportsPage();
                if (page === 'settings') this.loadSettingsPage();
            });
        });
    },

    setupChatInput() {
        const textarea = document.getElementById('chat-input');
        if (!textarea) return;
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendChat(); }
        });
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        });
    },

    // ========================================================================
    // DASHBOARD
    // ========================================================================
    async refreshDashboard() {
        if (!this.currentPatientId) return;
        const pid = this.currentPatientId;
        const patient = this.patients.find(p => p.id === pid);
        document.getElementById('patient-greeting').textContent =
            patient ? `${patient.first_name} ${patient.last_name}'s health overview` : '';

        const [wearableRes, symptomsRes, diagnosesRes] = await Promise.all([
            fetch(`${API}/api/wearable/${pid}?limit=50`).then(r => r.json()).catch(() => ({ readings: [] })),
            fetch(`${API}/api/symptoms/${pid}?limit=20`).then(r => r.json()).catch(() => ({ symptoms: [] })),
            fetch(`${API}/api/diagnoses/${pid}?limit=5`).then(r => r.json()).catch(() => ({ diagnoses: [] })),
        ]);

        this.updateStatCards(wearableRes.readings, symptomsRes.symptoms, diagnosesRes.diagnoses);
        this.updateCharts(wearableRes.readings);
        this.updateSymptomList(symptomsRes.symptoms);
        this.updateDiagnosisCard(diagnosesRes.diagnoses);
    },

    updateStatCards(readings, symptoms, diagnoses) {
        const hrv = readings.filter(r => r.reading_type === 'hrv');
        const sleep = readings.filter(r => r.reading_type === 'sleep');

        // Recovery score
        let recovery = '—';
        if (diagnoses.length > 0) {
            const summary = typeof diagnoses[0].symptom_summary === 'string'
                ? JSON.parse(diagnoses[0].symptom_summary) : diagnoses[0].symptom_summary;
            recovery = summary?.recovery_score || '—';
        }
        document.getElementById('recovery-score').textContent = recovery !== '—' ? `${recovery}` : '—';
        const bar = document.getElementById('recovery-bar');
        bar.style.width = recovery !== '—' ? `${recovery}%` : '0%';

        // HRV
        if (hrv.length > 0) {
            document.getElementById('hrv-value').textContent = `${hrv[0].rmssd?.toFixed(1)}`;
            const trend = hrv.length >= 3 ? (hrv[0].rmssd > hrv[2].rmssd ? '↑ Improving' : '↓ Declining') : '';
            const trendEl = document.getElementById('hrv-trend');
            trendEl.textContent = trend;
            trendEl.style.color = trend.includes('↑') ? 'var(--teal)' : 'var(--coral)';
        }

        // Sleep
        if (sleep.length > 0) {
            document.getElementById('sleep-value').textContent = `${(sleep[0].sleep_efficiency * 100).toFixed(0)}%`;
        }

        // Symptoms
        document.getElementById('symptom-count').textContent = symptoms.length;
    },

    updateCharts(readings) {
        const hrv = readings.filter(r => r.reading_type === 'hrv').reverse().slice(-20);
        const labels = hrv.map(r => new Date(r.recorded_at).toLocaleDateString('en-SG', { month: 'short', day: 'numeric' }));

        if (this.charts.hrv) this.charts.hrv.destroy();
        const hrvCtx = document.getElementById('hrv-chart').getContext('2d');
        this.charts.hrv = new Chart(hrvCtx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'RMSSD (ms)',
                    data: hrv.map(r => r.rmssd),
                    borderColor: '#0d9ca0',
                    backgroundColor: this._gradient(hrvCtx, 'rgba(13,156,160,0.18)', 'rgba(13,156,160,0)'),
                    fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#0d9ca0',
                    borderWidth: 2,
                }]
            },
            options: this.chartOptions('#0d9ca0')
        });

        if (this.charts.hr) this.charts.hr.destroy();
        const hrCtx = document.getElementById('hr-chart').getContext('2d');
        this.charts.hr = new Chart(hrCtx, {
            type: 'line',
            data: {
                labels,
                datasets: [{
                    label: 'Heart Rate (bpm)',
                    data: hrv.map(r => r.mean_hr),
                    borderColor: '#f4645f',
                    backgroundColor: this._gradient(hrCtx, 'rgba(244,100,95,0.18)', 'rgba(244,100,95,0)'),
                    fill: true, tension: 0.4, pointRadius: 3, pointBackgroundColor: '#f4645f',
                    borderWidth: 2,
                }]
            },
            options: this.chartOptions('#f4645f')
        });
    },

    _gradient(ctx, from, to) {
        const g = ctx.createLinearGradient(0, 0, 0, 200);
        g.addColorStop(0, from);
        g.addColorStop(1, to);
        return g;
    },

    chartOptions(color = '#818cf8') {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(255,255,255,0.92)',
                    borderColor: 'rgba(200,180,200,0.4)',
                    borderWidth: 1,
                    titleColor: '#1a1623',
                    bodyColor: '#5b5572',
                    padding: 10,
                    cornerRadius: 10,
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(200,180,200,0.15)', lineWidth: 1 },
                    ticks: { color: '#9b92b4', font: { size: 10, family: 'DM Sans, sans-serif' } },
                    border: { display: false },
                },
                y: {
                    grid: { color: 'rgba(200,180,200,0.15)', lineWidth: 1 },
                    ticks: { color: '#9b92b4', font: { size: 10, family: 'DM Sans, sans-serif' } },
                    border: { display: false },
                },
            }
        };
    },

    updateSymptomList(symptoms) {
        const container = document.getElementById('symptom-list');
        if (!symptoms.length) {
            container.innerHTML = '<p class="empty-state">No symptoms logged yet. Use <strong>Check-in</strong> to log symptoms.</p>';
            return;
        }
        container.innerHTML = symptoms.slice(0, 10).map(s => `
      <div class="symptom-item">
        <span class="severity-dot ${s.severity}"></span>
        <span style="flex:1">${s.symptom_name}</span>
        <span style="color:var(--text-muted);font-size:11px">${s.severity}</span>
        <span style="color:var(--text-muted);font-size:11px">${new Date(s.logged_at).toLocaleDateString()}</span>
      </div>
    `).join('');
    },

    updateDiagnosisCard(diagnoses) {
        const container = document.getElementById('latest-diagnosis');
        if (!diagnoses.length) {
            container.innerHTML = '<p class="empty-state">No assessment yet. Click <strong>Run Assessment</strong> above.</p>';
            return;
        }
        const d = diagnoses[0];
        const triggers = typeof d.triggers === 'string' ? JSON.parse(d.triggers) : (d.triggers || []);
        const recs = typeof d.recommendations === 'string' ? JSON.parse(d.recommendations) : (d.recommendations || []);
        container.innerHTML = `
      <span class="diagnosis-badge ${d.severity_level}">${d.severity_level?.replace('_', ' ')}</span>
      ${d.call_doctor ? '<span class="diagnosis-badge urgent">⚠️ Contact Doctor</span>' : ''}
      <p style="margin-top:8px;line-height:1.6">${d.assessment}</p>
      ${triggers.length ? `<p style="margin-top:8px;color:var(--text-secondary);font-size:0.83rem"><strong>Triggers:</strong> ${triggers.join(', ')}</p>` : ''}
      ${recs.length ? `<div style="margin-top:8px"><p style="font-size:0.83rem;font-weight:600;margin-bottom:4px">Recommendations:</p><ul style="padding-left:18px;display:flex;flex-direction:column;gap:3px">${recs.map(r => `<li style="font-size:0.83rem;color:var(--text-secondary)">${r}</li>`).join('')}</ul></div>` : ''}
    `;
    },

    // ========================================================================
    // CHAT
    // ========================================================================
    quickPrompt(text) {
        const input = document.getElementById('chat-input');
        const prompts = document.getElementById('quick-prompts');
        input.value = text;
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        if (prompts) prompts.style.display = 'none';
        this.sendChat();
    },

    async sendChat() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        if (!message || !this.currentPatientId) return;

        this.addChatMessage(message, 'user');
        input.value = '';
        input.style.height = 'auto';

        const typingId = this.addChatMessage('<div class="loading-spinner"></div> Thinking...', 'assistant');

        try {
            const res = await fetch(`${API}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, patient_id: this.currentPatientId })
            });
            const data = await res.json();
            document.getElementById(typingId).remove();
            this.addChatMessage(data.response || 'I have logged your check-in.', 'assistant');

            if (data.symptoms?.length) {
                const symText = data.symptoms.map(s =>
                    `<span class="symptom-item" style="display:inline-flex;margin:2px 4px;padding:4px 10px;border-radius:20px">
            <span class="severity-dot ${s.severity}"></span>&nbsp;${s.name}: ${s.severity}
          </span>`
                ).join('');
                this.addChatMessage(`<strong>Symptoms logged:</strong><br>${symText}`, 'assistant');
            }
            this.refreshDashboard();
        } catch (e) {
            document.getElementById(typingId).remove();
            this.addChatMessage('Sorry, I couldn\'t connect to the server. Please try again.', 'assistant');
            console.error(e);
        }
    },

    addChatMessage(content, role) {
        const container = document.getElementById('chat-messages');
        const id = 'msg-' + Date.now() + Math.random().toString(36).substr(2, 5);
        const div = document.createElement('div');
        div.className = `message ${role}`;
        div.id = id;

        const avatarHTML = role === 'user'
            ? '<div class="message-avatar">👤</div>'
            : `<div class="message-avatar ai-avatar"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg></div>`;

        div.innerHTML = `${avatarHTML}<div class="message-bubble"><p>${content}</p></div>`;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
        return id;
    },

    toggleMic() {
        this.micActive = !this.micActive;
        const btn = document.getElementById('btn-mic');
        if (this.micActive) {
            btn.classList.add('active');
            btn.title = 'Stop recording';
        } else {
            btn.classList.remove('active');
            btn.title = 'Voice input';
        }
        // Voice recognition placeholder (MERaLiON integration point)
        console.log('Voice input toggled:', this.micActive);
    },

    // ========================================================================
    // WEARABLE — Auto-connect smartwatch stream
    // ========================================================================
    connectWearable() {
        if (this.wearableWs) {
            this.wearableWs.onclose = null;
            this.wearableWs.close();
            this.wearableWs = null;
        }
        if (this.wearableReconnectTimer) {
            clearTimeout(this.wearableReconnectTimer);
            this.wearableReconnectTimer = null;
        }
        if (!this.currentPatientId) return;

        // Respect Settings toggle
        if (!this.streamingEnabled) {
            this.syncSettingsStatus(false);
            return;
        }

        const wsUrl = `ws://${window.location.host}/ws/wearable/${this.currentPatientId}`;
        this.wearableWs = new WebSocket(wsUrl);

        const statusEl = document.getElementById('stream-status');

        this.wearableWs.onopen = () => {
            if (statusEl) {
                statusEl.innerHTML = '<span class="status-dot"></span> Live';
                statusEl.className = 'stream-status connected';
            }
            this.syncSettingsStatus(true);
        };

        this.wearableWs.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            if (msg.type === 'ping') return;

            if (msg.type === 'reading') {
                const d = msg.data;
                if (d.reading_type === 'hrv') {
                    this.updateWatchFace(d);
                } else if (d.reading_type === 'sleep') {
                    this.latestSleep = d;
                    this.updateSleepDetail(d);
                }
            }

            if (msg.alerts) {
                const container = document.getElementById('wearable-alerts');
                msg.alerts.forEach(alert => {
                    const div = document.createElement('div');
                    div.className = `alert-item ${alert.severity}`;
                    div.innerHTML = `⚠️ <strong>${alert.alert}</strong>: ${alert.message}`;
                    container.prepend(div);
                    if (container.children.length > 10) container.lastChild.remove();
                });
            }
        };

        this.wearableWs.onclose = () => {
            if (statusEl) {
                statusEl.innerHTML = '<span class="status-dot"></span> Reconnecting…';
                statusEl.className = 'stream-status';
            }
            this.syncSettingsStatus(false);
            if (this.streamingEnabled) {
                this.wearableReconnectTimer = setTimeout(() => this.connectWearable(), 5000);
            }
        };

        this.wearableWs.onerror = () => this.wearableWs.close();
    },

    updateWatchFace(d) {
        const hr = d.mean_hr ?? null;
        const rmssd = d.rmssd ?? null;
        const sdnn = d.sdnn ?? null;
        const chemoDay = d.metadata?.chemo_day ?? null;

        // Primary HR value
        const hrEl = document.getElementById('live-hr');
        if (hrEl) hrEl.textContent = hr !== null ? Math.round(hr) : '—';

        // HRV ring SVG (maps 40–160bpm to 0–100% of ring)
        const ringFill = document.getElementById('ring-hr-fill');
        if (ringFill && hr !== null) {
            const pct = Math.min(1, Math.max(0, (hr - 40) / 120));
            const circumference = 314;
            ringFill.style.strokeDashoffset = circumference - pct * circumference;
            ringFill.style.stroke = hr > 110 ? '#f4645f' : hr > 90 ? '#f59e0b' : '#e05c7a';
        }

        // Pulse icon animation
        const pulseIcon = document.getElementById('watch-pulse-icon');
        if (pulseIcon) {
            pulseIcon.classList.remove('beating');
            void pulseIcon.offsetWidth; // reflow to restart animation
            pulseIcon.classList.add('beating');
        }

        if (document.getElementById('live-rmssd')) document.getElementById('live-rmssd').textContent = rmssd !== null ? rmssd.toFixed(1) : '—';
        if (document.getElementById('live-sdnn')) document.getElementById('live-sdnn').textContent = sdnn !== null ? sdnn.toFixed(1) : '—';
        if (document.getElementById('live-chemo-day')) document.getElementById('live-chemo-day').textContent = chemoDay !== null ? chemoDay : '—';

        // Autonomic status
        const { label, cls } = this.getAutonomicStatus(rmssd);
        const pill = document.getElementById('autonomic-status');
        if (pill) {
            pill.textContent = label;
            pill.className = `autonomic-pill ${cls}`;
        }

        // Last updated
        const updEl = document.getElementById('watch-updated');
        if (updEl) updEl.textContent = 'Updated ' + new Date().toLocaleTimeString();

        // Also push to dashboard stat cards if they exist
        const dashHrv = document.getElementById('hrv-value');
        if (dashHrv && rmssd !== null) dashHrv.textContent = rmssd.toFixed(1);
    },

    updateSleepDetail(d) {
        const totalHrs = d.total_sleep_min ? (d.total_sleep_min / 60).toFixed(1) : '—';
        const eff = d.sleep_efficiency ? `${(d.sleep_efficiency * 100).toFixed(0)}%` : '—';
        const deep = d.deep_sleep_pct ? `${(d.deep_sleep_pct * 100).toFixed(0)}%` : '—';
        const awake = d.awakenings !== undefined ? d.awakenings : '—';

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
        set('live-sleep', totalHrs);
        set('sleep-efficiency', eff);
        set('sleep-deep', deep);
        set('sleep-awakenings', awake);
        set('sleep-total', totalHrs + ' hrs');

        // Also push to dashboard sleep card
        const dashSleep = document.getElementById('sleep-value');
        if (dashSleep && d.sleep_efficiency) dashSleep.textContent = `${(d.sleep_efficiency * 100).toFixed(0)}%`;
    },

    getAutonomicStatus(rmssd) {
        if (rmssd === null || rmssd === undefined) return { label: 'Awaiting data…', cls: '' };
        if (rmssd < 10) return { label: '🔴 Severely Stressed', cls: 'critical' };
        if (rmssd < 20) return { label: '🟠 Stressed', cls: 'stressed' };
        if (rmssd < 30) return { label: '🟡 Recovering', cls: 'recovering' };
        if (rmssd < 50) return { label: '🟢 Stable', cls: 'stable' };
        return { label: '✅ Strong', cls: 'strong' };
    },

    // ========================================================================
    // SETTINGS
    // ========================================================================
    loadSettingsPage() {
        // Sync toggle to current state
        const toggle = document.getElementById('toggle-wearable-stream');
        if (toggle) toggle.checked = this.streamingEnabled;
        this.syncSettingsStatus(this.streamingEnabled && !!this.wearableWs);
    },

    onWearableToggle(enabled) {
        this.streamingEnabled = enabled;
        localStorage.setItem('wearableStreamingEnabled', enabled);
        if (enabled) {
            this.connectWearable();
        } else {
            // Disconnect and cancel any pending reconnect
            if (this.wearableReconnectTimer) {
                clearTimeout(this.wearableReconnectTimer);
                this.wearableReconnectTimer = null;
            }
            if (this.wearableWs) {
                this.wearableWs.onclose = null; // prevent auto-reconnect
                this.wearableWs.close();
                this.wearableWs = null;
            }
            // Update wearable page status pill
            const statusEl = document.getElementById('stream-status');
            if (statusEl) {
                statusEl.innerHTML = '<span class="status-dot"></span> Paused';
                statusEl.className = 'stream-status';
            }
            this.syncSettingsStatus(false, true);
        }
    },

    syncSettingsStatus(connected, paused = false) {
        const dot = document.getElementById('settings-stream-dot');
        const text = document.getElementById('settings-stream-text');
        if (!dot || !text) return;
        if (paused) {
            dot.className = 'settings-status-dot paused';
            text.textContent = 'Streaming paused — toggle on to resume';
        } else if (connected) {
            dot.className = 'settings-status-dot live';
            text.textContent = 'Stream is live — receiving data every 2 seconds';
        } else {
            dot.className = 'settings-status-dot';
            text.textContent = 'Connecting to stream…';
        }
    },

    // ========================================================================
    // REPORTS PAGE
    // ========================================================================
    async loadReportsPage() {
        if (!this.currentPatientId) return;
        const pid = this.currentPatientId;

        const [medsRes, labsRes, diagRes] = await Promise.all([
            fetch(`${API}/api/medications/${pid}`).then(r => r.json()).catch(() => ({ medications: [] })),
            fetch(`${API}/api/labs/${pid}`).then(r => r.json()).catch(() => ({ labs: [] })),
            fetch(`${API}/api/diagnoses/${pid}?limit=10`).then(r => r.json()).catch(() => ({ diagnoses: [] })),
        ]);

        const medsContainer = document.getElementById('meds-list');
        medsContainer.innerHTML = (medsRes.medications || []).map(m => `
      <div class="data-item">
        <div>
          <div class="data-item-name">${m.name}</div>
          <div class="data-item-meta">${m.reason || ''}</div>
        </div>
        <div style="text-align:right">
          <span class="badge" style="background:${m.is_chemo ? 'rgba(244,100,95,0.12);color:#f4645f' : 'rgba(13,156,160,0.12);color:#0d9ca0'}">${m.is_chemo ? 'Chemo' : 'Supportive'}</span>
          <div class="data-item-meta">${m.start_date || ''}</div>
        </div>
      </div>
    `).join('') || '<p class="empty-state">No medications recorded.</p>';

        const labsContainer = document.getElementById('labs-list');
        labsContainer.innerHTML = (labsRes.labs || []).map(l => `
      <div class="data-item">
        <div class="data-item-name">${l.test_name}</div>
        <div>
          <span class="data-item-value">${l.value} ${l.unit || ''}</span>
          <span class="data-item-meta" style="margin-left:8px">ref: ${l.reference_range || 'N/A'}</span>
        </div>
      </div>
    `).join('') || '<p class="empty-state">No lab results.</p>';

        const diagContainer = document.getElementById('diagnosis-history');
        diagContainer.innerHTML = (diagRes.diagnoses || []).map(d => `
      <div class="data-item" style="flex-direction:column;align-items:flex-start;gap:6px">
        <div style="display:flex;gap:8px;align-items:center">
          <span class="diagnosis-badge ${d.severity_level}">${d.severity_level?.replace('_', ' ')}</span>
          <span class="data-item-meta">${new Date(d.generated_at).toLocaleString()}</span>
        </div>
        <p style="font-size:0.83rem;color:var(--text-secondary);line-height:1.5">${d.assessment}</p>
      </div>
    `).join('') || '<p class="empty-state">No assessments yet.</p>';
    },

    // ========================================================================
    // REPORT GENERATION — Reporting Agent Hook
    // ========================================================================
    async generateReport() {
        if (!this.currentPatientId) {
            alert('Please select a patient first.');
            return;
        }
        const btn = document.getElementById('btn-generate-report');
        const resultEl = document.getElementById('report-result');
        const resultText = document.getElementById('report-result-text');
        const downloadLink = document.getElementById('report-download-link');

        btn.innerHTML = '<div class="loading-spinner"></div> Generating...';
        btn.disabled = true;
        resultEl.style.display = 'none';

        try {
            const res = await fetch(`${API}/api/report/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: this.currentPatientId })
            });

            if (!res.ok) throw new Error(`Server returned ${res.status}`);
            const data = await res.json();

            resultText.textContent = data.message || `Report generated for patient ${this.currentPatientId}.`;
            if (data.download_url) {
                downloadLink.href = data.download_url;
                downloadLink.style.display = 'inline-flex';
            } else {
                downloadLink.style.display = 'none';
            }
            resultEl.style.display = 'block';
        } catch (e) {
            resultText.textContent = `Could not generate report: ${e.message}. Ensure the backend is running.`;
            downloadLink.style.display = 'none';
            resultEl.style.display = 'block';
            console.error('Report generation error:', e);
        }

        btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg> Generate Report`;
        btn.disabled = false;
    },

    // ========================================================================
    // DIAGNOSIS
    // ========================================================================
    async runDiagnosis() {
        if (!this.currentPatientId) {
            alert('Please select a patient first.');
            return;
        }
        const btn = document.getElementById('btn-diagnose');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<div class="loading-spinner"></div> Assessing…';
        btn.disabled = true;

        try {
            const res = await fetch(`${API}/api/diagnose`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ patient_id: this.currentPatientId })
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error(err.detail || `Server error ${res.status}`);
            }
            await res.json();
            await this.refreshDashboard();
            // Brief success flash on the button
            btn.innerHTML = '✓ Assessment complete';
            btn.disabled = false;
            setTimeout(() => { btn.innerHTML = originalHTML; }, 2500);
            return;
        } catch (e) {
            console.error('Diagnosis error:', e);
            // Show visible error inline below the button
            let errEl = document.getElementById('assess-error');
            if (!errEl) {
                errEl = document.createElement('p');
                errEl.id = 'assess-error';
                errEl.style.cssText = 'color:var(--coral);font-size:0.83rem;margin-top:8px';
                btn.parentNode.appendChild(errEl);
            }
            errEl.textContent = `Assessment failed: ${e.message}`;
            setTimeout(() => { if (errEl) errEl.remove(); }, 6000);
        } finally {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }
    },

    // ========================================================================
    // EMERGENCY
    // ========================================================================
    callEmergency() {
        if (confirm('⚠️ This will call emergency services (995). Are you sure?')) {
            window.location.href = 'tel:995';
        }
    },

    // ========================================================================
    // CHARTS INIT
    // ========================================================================
    initCharts() {
        // Charts initialized after data loads
    }
};

// Boot
document.addEventListener('DOMContentLoaded', () => app.init());
