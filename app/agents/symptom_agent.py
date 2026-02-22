"""
Symptom Extraction Agent
Parses natural language text/speech into structured symptom data and stores in Supabase.
"""
import json
from datetime import datetime, timezone
from app.agents.llm_provider import get_llm
from app.database import supabase_client as supa


SYMPTOM_SCHEMA = {
    "type": "object",
    "properties": {
        "symptoms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Standardized symptom name"},
                    "severity": {"type": "string", "enum": ["none", "mild", "moderate", "severe"]},
                    "score": {"type": "number", "description": "Numeric value if mentioned (e.g., temp, pain score)"},
                    "unit": {"type": "string", "description": "Unit for the score (F, scale, etc.)"},
                    "context": {"type": "string", "description": "Additional context (e.g., 'after eating', 'post-chemo')"}
                },
                "required": ["name", "severity"]
            }
        },
        "summary": {"type": "string", "description": "Brief summary of the patient's reported state"},
        "urgency": {"type": "string", "enum": ["routine", "monitor", "urgent"],
                    "description": "Overall urgency assessment"}
    }
}

SYSTEM_PROMPT = """You are a medical symptom extraction agent for a cancer recovery monitoring system.
Your job is to parse patient messages into structured symptom data.

KNOWN SYMPTOMS (use these exact names):
- Fever, Fatigue, Nausea & Vomiting, Sore Mouth, Diarrhea, Constipation
- Loss of Appetite, Swallowing Difficulty, Anxiety / Depression
- Edema (Hands/Feet), Itching / Rash, Shortness of Breath
- Muscle / Joint Pain, Numbness / Tingling, Pain (general)

SEVERITY GUIDELINES:
- none: Patient explicitly says no issue
- mild: Minor discomfort, does not affect daily activities
- moderate: Noticeable impact on daily activities, needs attention
- severe: Significantly affects daily life, potential emergency

URGENCY GUIDELINES:
- routine: Normal check-in, no concerning symptoms
- monitor: Some symptoms need monitoring over next 24-48 hours
- urgent: Severe symptoms that may need immediate medical attention (fever >104F, severe pain >8/10, inability to eat/drink)

Extract ALL symptoms mentioned, even casual ones. If a patient gives a number (e.g., "pain is a 7"), map it to severity accordingly.
Be conservative with urgency - only flag urgent if truly concerning."""


class SymptomAgent:
    """Extracts structured symptoms from natural language input."""

    def __init__(self):
        self.llm = get_llm()

    def extract(self, text: str, patient_id: str = None) -> dict:
        """
        Extract symptoms from text input.
        Returns structured symptom data and optionally saves to Supabase.
        """
        result = self.llm.generate_structured(
            prompt=text,
            schema=SYMPTOM_SCHEMA,
            system_prompt=SYSTEM_PROMPT,
        )

        # Save to database if patient_id provided
        if patient_id and result.get('symptoms'):
            self._save_symptoms(patient_id, result['symptoms'], text)

        return result

    def _save_symptoms(self, patient_id: str, symptoms: list, raw_input: str):
        """Save extracted symptoms to Supabase."""
        now = datetime.now(timezone.utc).isoformat()
        records = []
        for s in symptoms:
            records.append({
                'patient_id': patient_id,
                'symptom_name': s['name'],
                'severity': s['severity'],
                'score': s.get('score'),
                'unit': s.get('unit'),
                'context': s.get('context'),
                'source': 'chat',
                'raw_input': raw_input,
                'logged_at': now,
            })
        if records:
            supa.log_symptoms_batch(records)

    async def extract_and_respond(self, text: str, patient_id: str = None) -> dict:
        """Extract symptoms and generate a conversational response."""
        extraction = self.extract(text, patient_id)

        response_prompt = (
            f"Patient said: {text}\n\n"
            f"Extracted symptoms: {json.dumps(extraction['symptoms'], indent=2)}\n"
            f"Urgency: {extraction.get('urgency', 'routine')}\n\n"
            "Generate a brief, empathetic response acknowledging their symptoms. "
            "If urgency is 'urgent', advise contacting their care team immediately. "
            "If 'monitor', suggest watching closely and reporting changes. "
            "Keep response under 3 sentences. Be warm but professional."
        )

        response_text = self.llm.generate(
            prompt=response_prompt,
            system_prompt="You are a caring cancer recovery assistant. Be empathetic and supportive.",
            temperature=0.7,
        )

        return {
            'extraction': extraction,
            'response': response_text,
        }
