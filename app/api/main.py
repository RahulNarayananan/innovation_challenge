"""
FastAPI Backend Server
REST + WebSocket endpoints for the Cancer Recovery Assistant.
"""
import asyncio
import json
import os
import sys

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import supabase_client as supa
from app.agents.orchestrator import process_chat
from app.agents.wearable_simulator import WearableSimulator
from app.agents.wearable_agent import WearableAgent
from app.agents.diagnosis_agent import DiagnosisAgent
from app.reporting.report_generator import generate_patient_report


# ============================================================================
# APP SETUP
# ============================================================================

# ============================================================================
# IN-MEMORY WEARABLE STATE
# ============================================================================
# Stores the latest reading per patient_id for instant WebSocket broadcast.
_latest_readings: dict = {}          # {patient_id: reading_dict}
_wearable_subscribers: dict = {}     # {patient_id: set of WebSocket}
_PROTOTYPE_PATIENT_LIMIT = 10        # Only simulate for first N patients
_PERSIST_INTERVAL_TICKS = 30        # Persist every 30 ticks × 5s = 150s


async def wearable_background_loop():
    """
    Single coordinated tick loop:
    - Generates HRV readings for all prototype patients every 5 seconds (in-memory).
    - Broadcasts to any connected WebSocket subscribers.
    - Batch-inserts to Supabase only every 60 seconds (downsampled).
    """
    # Wait for app to be ready
    await asyncio.sleep(2)

    # Load up to PROTOTYPE_PATIENT_LIMIT patients
    try:
        patients = supa.get_patients(limit=_PROTOTYPE_PATIENT_LIMIT)
    except Exception as exc:
        print(f"[Wearable] Could not load patients: {exc}")
        return

    if not patients:
        print("[Wearable] No patients found — background loop exiting.")
        return

    print(f"[Wearable] Starting simulator for {len(patients)} patients.")

    # Build one simulator per patient
    simulators: dict = {}
    for p in patients:
        cfg = {'cancer_type': p.get('cancer_type', 'LUNG')}
        try:
            birth = p.get('birth_date', '')
            if birth:
                age = (datetime.now() - datetime.fromisoformat(birth)).days // 365
                cfg['age'] = age
        except Exception:
            pass
        simulators[p['id']] = WearableSimulator(patient_config=cfg, speed_factor=60.0)

    wearable_agent = WearableAgent()
    tick = 0
    pending_batch: list = []

    while True:
        tick += 1
        try:
            for patient_id, sim in simulators.items():
                reading = sim.generate_hrv_reading()
                reading['patient_id'] = patient_id

                # Update in-memory latest state
                _latest_readings[patient_id] = reading

                # Collect for batch insert
                pending_batch.append({
                    'patient_id': patient_id,
                    'reading_type': reading['reading_type'],
                    'rmssd': reading.get('rmssd'),
                    'sdnn': reading.get('sdnn'),
                    'mean_hr': reading.get('mean_hr'),
                    'recorded_at': reading.get('recorded_at'),
                })

                # Broadcast to any subscribers
                subs = _wearable_subscribers.get(patient_id, set())
                dead = set()
                for ws in subs:
                    try:
                        # Run anomaly checks
                        alerts = wearable_agent._check_anomalies(reading)
                        payload = {'type': 'reading', 'data': reading}
                        if alerts:
                            payload['alerts'] = alerts
                        await ws.send_json(payload)
                    except Exception:
                        dead.add(ws)
                subs -= dead

            # Also generate sleep readings every 30 ticks
            if tick % 30 == 0:
                for patient_id, sim in simulators.items():
                    sleep_r = sim.generate_sleep_reading()
                    pending_batch.append({
                        'patient_id': patient_id,
                        'reading_type': 'sleep',
                        'total_sleep_min': sleep_r.get('total_sleep_min'),
                        'sleep_efficiency': sleep_r.get('sleep_efficiency'),
                        'deep_sleep_pct': sleep_r.get('deep_sleep_pct'),
                        'awakenings': sleep_r.get('awakenings'),
                        'recorded_at': sleep_r.get('recorded_at'),
                    })

            # Batch-insert to Supabase every _PERSIST_INTERVAL_TICKS ticks
            if tick % _PERSIST_INTERVAL_TICKS == 0 and pending_batch:
                try:
                    supa.insert_wearables_batch(pending_batch)
                    print(f"[Wearable] Persisted {len(pending_batch)} readings (tick {tick})")
                except Exception as exc:
                    print(f"[Wearable] DB write error: {exc}")
                pending_batch.clear()

        except Exception as exc:
            print(f"[Wearable] Tick error: {exc}")

        await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Cancer Recovery Assistant API starting...")
    task = asyncio.create_task(wearable_background_loop())
    yield
    task.cancel()
    print("Shutting down.")

app = FastAPI(
    title="Cancer Recovery Assistant API",
    version="1.0.0",
    description="AI-powered cancer recovery monitoring with real-time wearable data",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app.mount('/static', StaticFiles(directory=FRONTEND_DIR), name='static')


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    patient_id: str

class SymptomLogRequest(BaseModel):
    patient_id: str
    symptom_name: str
    severity: str
    score: Optional[float] = None
    context: Optional[str] = None

class DiagnoseRequest(BaseModel):
    patient_id: str
    context: Optional[str] = None


# ============================================================================
# REST ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))


# --- Patients ---
@app.get("/api/patients")
async def list_patients():
    patients = supa.get_patients(limit=100)
    return {"patients": patients}

@app.get("/api/patients/{patient_id}")
async def get_patient(patient_id: str):
    patient = supa.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"patient": patient}


# --- Chat (sync endpoint for simple requests) ---
@app.post("/api/chat")
async def chat(req: ChatRequest):
    result = await process_chat(req.patient_id, req.message)
    return result


# --- Symptoms ---
@app.get("/api/symptoms/{patient_id}")
async def get_symptoms(patient_id: str, limit: int = 50):
    symptoms = supa.get_symptoms(patient_id, limit=limit)
    return {"symptoms": symptoms}

@app.post("/api/symptoms")
async def log_symptom(req: SymptomLogRequest):
    from datetime import datetime, timezone
    record = {
        'patient_id': req.patient_id,
        'symptom_name': req.symptom_name,
        'severity': req.severity,
        'score': req.score,
        'context': req.context,
        'source': 'manual',
        'logged_at': datetime.now(timezone.utc).isoformat(),
    }
    supa.log_symptom(record)
    return {"status": "logged", "symptom": record}


# --- Wearable ---
@app.get("/api/wearable/{patient_id}")
async def get_wearable(patient_id: str, reading_type: str = None, limit: int = 100):
    readings = supa.get_wearable_readings(patient_id, reading_type=reading_type, limit=limit)
    return {"readings": readings}


# --- Lab Results ---
@app.get("/api/labs/{patient_id}")
async def get_labs(patient_id: str, limit: int = 50):
    labs = supa.get_lab_results(patient_id, limit=limit)
    return {"labs": labs}


# --- Medications ---
@app.get("/api/medications/{patient_id}")
async def get_medications(patient_id: str):
    meds = supa.get_medications(patient_id)
    return {"medications": meds}


# --- Diagnoses ---
@app.get("/api/diagnoses/{patient_id}")
async def get_diagnoses(patient_id: str, limit: int = 20):
    diagnoses = supa.get_diagnoses(patient_id, limit=limit)
    return {"diagnoses": diagnoses}

@app.post("/api/diagnose")
async def run_diagnosis(req: DiagnoseRequest):
    """Run diagnosis agent in a thread pool to avoid blocking the event loop."""
    import traceback as tb
    from functools import partial
    from app.agents.llm_provider import RateLimitError

    def _run():
        """Runs entirely in a thread — LLM init + inference are both blocking."""
        agent = DiagnosisAgent()
        return agent.assess(req.patient_id, req.context)

    loop = asyncio.get_event_loop()
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(None, _run),
            timeout=180.0   # llama3.1 (8B) can take 2-3 min on first call
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Assessment timed out after 3 minutes. The model may be loading — try again.")
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail=str(exc))
    except Exception as exc:
        tb.print_exc()
        raise HTTPException(status_code=500, detail=f"Assessment failed: {type(exc).__name__}: {exc}")


# --- Reports ---
@app.get("/api/reports/{patient_id}")
async def get_reports(patient_id: str):
    reports = supa.get_reports(patient_id)
    return {"reports": reports}


# ============================================================================
# REPORT GENERATION
# ============================================================================

class ReportRequest(BaseModel):
    patient_id: str

@app.post("/api/report/generate")
async def generate_report(request: ReportRequest):
    """Generate a PDF clinical report for a patient and return a download URL."""
    patient_id = request.patient_id

    try:
        import tempfile, pathlib, json as _json

        # Gather data
        patient = supa.get_patient(patient_id) or {}
        wearable = supa.get_wearable_readings(patient_id, None, 20) or []
        diagnoses = supa.get_diagnoses(patient_id, 5) or []
        symptoms = supa.get_symptoms(patient_id, 10) or []

        # Build vitals dict
        hrv_readings = [r for r in wearable if r.get('reading_type') == 'hrv']
        sleep_readings = [r for r in wearable if r.get('reading_type') == 'sleep']
        vitals = {}
        if hrv_readings:
            vitals['HRV RMSSD (latest)'] = f"{hrv_readings[0].get('rmssd', '—'):.1f} ms"
            vitals['Heart Rate (latest)'] = f"{hrv_readings[0].get('mean_hr', '—'):.0f} bpm"
        if sleep_readings:
            eff = sleep_readings[0].get('sleep_efficiency')
            if eff:
                vitals['Sleep Efficiency'] = f"{eff*100:.0f}%"

        # Build clinical summary from latest diagnosis
        clinical_summary = "No assessment available. Run a diagnostic assessment first."
        recovery_score = '—'
        if diagnoses:
            d = diagnoses[0]
            clinical_summary = d.get('assessment', clinical_summary)
            try:
                sym_sum = d.get('symptom_summary', {})
                if isinstance(sym_sum, str):
                    sym_sum = _json.loads(sym_sum)
                score = sym_sum.get('recovery_score')
                if score is not None:
                    recovery_score = score
                    vitals['Recovery Score'] = f"{score}/100"
            except Exception:
                pass
            recs = d.get('recommendations', '[]')
            if isinstance(recs, str):
                try:
                    recs = _json.loads(recs)
                except Exception:
                    recs = []
            if recs:
                clinical_summary += '\n\nRecommendations:\n' + '\n'.join(f'- {r}' for r in recs)

        # Symptom summary
        if symptoms:
            vitals['Active Symptoms'] = len(symptoms)
            clinical_summary += '\n\nRecent Symptoms:\n' + '\n'.join(
                f"- {s['symptom_name']}: {s['severity']}" for s in symptoms[:5]
            )

        # Patient name
        patient_name = patient.get('name') or (
            f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()
        ) or patient_id

        patient_data = {
            'name': patient_name,
            'id': patient_id,
            'cancer_type': patient.get('cancer_type', 'N/A'),
            'age': patient.get('birth_date', 'N/A'),
        }

        # Generate PDF to temp file
        tmp_dir = pathlib.Path(tempfile.gettempdir())
        filename = tmp_dir / f"report_{patient_id}.pdf"
        generate_patient_report(patient_data, vitals, clinical_summary, str(filename))

        # Serve from /static mount by copying to FRONTEND_DIR
        report_name = f"report_{patient_id}.pdf"
        dest = pathlib.Path(FRONTEND_DIR) / report_name
        import shutil
        shutil.copy2(str(filename), str(dest))

        return {
            'message': f'Report generated for {patient_name}. Click Download to save.',
            'download_url': f'/static/{report_name}',
            'recovery_score': recovery_score,
        }

    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/chat/{patient_id}")
async def ws_chat(websocket: WebSocket, patient_id: str):
    """WebSocket for real-time chat with the agent."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_input = msg.get('message', '')

            # Process through agent pipeline
            result = await process_chat(patient_id, user_input)

            await websocket.send_json({
                'type': 'response',
                'response': result.get('response', ''),
                'symptoms': result.get('symptoms', []),
                'diagnosis': result.get('diagnosis', {}),
            })
    except WebSocketDisconnect:
        pass


@app.websocket("/ws/wearable/{patient_id}")
async def ws_wearable(websocket: WebSocket, patient_id: str):
    """
    WebSocket for real-time wearable broadcast.
    Serves data from the in-memory store kept by wearable_background_loop.
    Only available for the prototype patient set.
    """
    await websocket.accept()

    # Register subscriber
    if patient_id not in _wearable_subscribers:
        _wearable_subscribers[patient_id] = set()
    _wearable_subscribers[patient_id].add(websocket)

    # Immediately send the latest reading if available
    latest = _latest_readings.get(patient_id)
    if latest:
        try:
            await websocket.send_json({'type': 'reading', 'data': latest})
        except Exception:
            pass

    try:
        # Keep alive — the background loop pushes data to this socket
        while True:
            await asyncio.sleep(30)  # Heartbeat
            await websocket.send_json({'type': 'ping'})
    except (WebSocketDisconnect, Exception):
        subs = _wearable_subscribers.get(patient_id, set())
        subs.discard(websocket)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)
