"""
Diagnosis Agent
Combines symptom logs + wearable trends + patient history into clinical assessments.
Uses multithreading to fetch data from Supabase in parallel.
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from app.agents.llm_provider import get_llm
from app.database import supabase_client as supa


DIAGNOSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "assessment": {"type": "string", "description": "Overall clinical assessment summary"},
        "severity_level": {"type": "string", "enum": ["stable", "mild_concern", "moderate_concern", "urgent"]},
        "call_doctor": {"type": "boolean", "description": "Whether patient should contact their oncologist"},
        "triggers": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific clinical triggers that drove this assessment"
        },
        "recommendations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Actionable recommendations for the patient"
        },
        "recovery_score": {
            "type": "number",
            "description": "Recovery score 0-100 (100 = fully recovered)"
        }
    }
}

SYSTEM_PROMPT = """You are a clinical diagnosis agent for a cancer recovery monitoring system.
You MUST analyze the patient's recent data and produce a clinical assessment.

IMPORTANT RULES:
1. You are NOT a doctor. Frame everything as "suggestions" and "observations"
2. Include "Call Doctor" triggers ONLY for truly concerning patterns:
   - Fever >104F, Pain >8/10, inability to eat/drink for 24h+
   - HRV drop >50%, sustained tachycardia >130bpm
   - Multiple severe symptoms simultaneously
3. Recovery Score guidelines:
   - 80-100: Minimal symptoms, stable vitals, good sleep
   - 60-79: Mild symptoms, some wearable fluctuation
   - 40-59: Moderate symptoms, notable HRV decline
   - 20-39: Severe symptoms, significant physiological stress
   - 0-19: Critical, needs immediate attention
4. Be specific about which data points drive your assessment
5. Recommendations should be practical and actionable"""


class DiagnosisAgent:
    """Generates clinical assessments from multi-modal patient data."""

    def __init__(self):
        self.llm = get_llm()

    def assess(self, patient_id: str, additional_context: str = None) -> dict:
        """
        Generate a clinical assessment for a patient using all available data.
        Fetches data in parallel using ThreadPoolExecutor.
        """
        # Fetch all data sources in parallel
        data = self._fetch_all_data(patient_id)

        # Build context prompt
        context = self._build_context(**data)
        if additional_context:
            context += f"\n\nAdditional context: {additional_context}"

        # Get LLM assessment
        result = self.llm.generate_structured(
            prompt=context,
            schema=DIAGNOSIS_SCHEMA,
            system_prompt=SYSTEM_PROMPT,
        )

        # Save to database
        self._save_diagnosis(patient_id, result, data['symptoms'], data['wearable'])

        return result

    def _fetch_all_data(self, patient_id: str) -> dict:
        """Fetch all patient data concurrently via ThreadPoolExecutor."""
        results = {}

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(supa.get_patient, patient_id): 'patient',
                executor.submit(supa.get_symptoms, patient_id, 20): 'symptoms',
                executor.submit(supa.get_wearable_readings, patient_id, None, 20): 'wearable',
                executor.submit(supa.get_medications, patient_id): 'meds',
                executor.submit(supa.get_lab_results, patient_id, 10): 'labs',
                executor.submit(supa.get_diagnoses, patient_id, 3): 'prev_diagnoses',
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    print(f"  Warning: failed to fetch {key}: {e}")
                    results[key] = [] if key != 'patient' else None

        return results

    def _build_context(self, patient, symptoms, wearable, meds, labs, prev_diagnoses):
        """Build a comprehensive context string for the LLM."""
        parts = []

        if patient:
            parts.append(
                f"PATIENT: {patient.get('first_name', '')} {patient.get('last_name', '')}, "
                f"Age: {patient.get('birth_date', 'unknown')}, "
                f"Cancer: {patient.get('cancer_type', 'unknown')}, "
                f"Phase: {patient.get('treatment_phase', 'unknown')}"
            )

        if meds:
            chemo = [m for m in meds if m.get('is_chemo')]
            other = [m for m in meds if not m.get('is_chemo')]
            if chemo:
                parts.append(f"CHEMO MEDS: {', '.join(m['name'] for m in chemo)}")
            if other:
                parts.append(f"OTHER MEDS: {', '.join(m['name'] for m in other[:5])}")

        if symptoms:
            recent = symptoms[:10]
            parts.append("RECENT SYMPTOMS:")
            for sym in recent:
                score_str = f" (score: {sym['score']})" if sym.get('score') else ""
                date_str = str(sym.get('logged_at', ''))[:10]
                parts.append(f"  - {sym['symptom_name']}: {sym['severity']}{score_str} [{date_str}]")

        if wearable:
            hrv = [r for r in wearable if r['reading_type'] == 'hrv'][:5]
            sleep = [r for r in wearable if r['reading_type'] == 'sleep'][:3]
            if hrv:
                parts.append(f"RECENT HRV: RMSSD={[r.get('rmssd') for r in hrv]}, "
                             f"HR={[r.get('mean_hr') for r in hrv]}")
            if sleep:
                parts.append(f"RECENT SLEEP: Efficiency={[r.get('sleep_efficiency') for r in sleep]}, "
                             f"Awakenings={[r.get('awakenings') for r in sleep]}")

        if labs:
            parts.append("LATEST LABS:")
            for lab in labs[:5]:
                ref = lab.get('reference_range')
                ref_str = f" (ref: {ref})" if ref and ref != 'N/A' else ""
                parts.append(f"  - {lab['test_name']}: {lab['value']} {lab.get('unit', '')}{ref_str}")

        if prev_diagnoses:
            prev = prev_diagnoses[0]
            summary = prev.get('symptom_summary', {})
            if isinstance(summary, str):
                try:
                    summary = json.loads(summary)
                except (json.JSONDecodeError, TypeError):
                    summary = {}
            recovery = summary.get('recovery_score', 'N/A')
            parts.append(f"PREVIOUS ASSESSMENT: {prev.get('severity_level', 'unknown')} - "
                         f"Recovery Score: {recovery}")

        return '\n'.join(parts) if parts else "No patient data available."

    def _save_diagnosis(self, patient_id, result, symptoms, wearable):
        """Save diagnosis to Supabase."""
        try:
            record = {
                'patient_id': patient_id,
                'assessment': result.get('assessment', ''),
                'severity_level': result.get('severity_level', 'stable'),
                # Pass native Python objects — supabase-py serialises JSONB automatically.
                # json.dumps() here would double-encode the strings and cause insert errors.
                'triggers': result.get('triggers', []),
                'recommendations': result.get('recommendations', []),
                'symptom_summary': {
                    'count': len(symptoms) if symptoms else 0,
                    'recovery_score': result.get('recovery_score', 50),
                },
                'wearable_summary': {
                    'readings_analyzed': len(wearable) if wearable else 0,
                },
                'call_doctor': result.get('call_doctor', False),
                'generated_at': datetime.now(timezone.utc).isoformat(),
            }
            supa.insert_diagnosis(record)
        except Exception as e:
            print(f"[DiagnosisAgent] Warning: failed to persist diagnosis to DB: {e}")

    def get_recovery_trend(self, patient_id: str) -> dict:
        """Get recovery score trend over time."""
        diagnoses = supa.get_diagnoses(patient_id, limit=10)
        scores = []
        for d in diagnoses:
            summary = d.get('symptom_summary', {})
            if isinstance(summary, str):
                try:
                    summary = json.loads(summary)
                except (json.JSONDecodeError, TypeError):
                    summary = {}
            score = summary.get('recovery_score')
            if score is not None:
                scores.append({
                    'score': score,
                    'date': d.get('generated_at'),
                    'severity': d.get('severity_level'),
                })
        return {
            'trend': scores,
            'current': scores[0] if scores else None,
            'improving': len(scores) >= 2 and scores[0].get('score', 0) > scores[1].get('score', 0),
        }
