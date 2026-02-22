"""
Wearable Analysis Agent
Interprets real-time wearable data, detects anomalies, and generates clinical alerts.
"""
from datetime import datetime, timezone
from app.agents.llm_provider import get_llm
from app.agents.wearable_simulator import WearableSimulator
from app.database import supabase_client as supa


class WearableAgent:
    """Analyzes wearable data streams and detects clinically significant patterns."""

    def __init__(self):
        self._llm = None  # Lazy-init so missing Ollama/Gemini doesn't crash the loop
        self.reading_buffer = []  # Rolling buffer for trend detection
        self.buffer_size = 30

    def process_reading(self, reading: dict, patient_id: str) -> dict:
        """
        Process a single wearable reading.
        Returns alert dict if anomaly detected, else None.
        """
        # Add to buffer
        self.reading_buffer.append(reading)
        if len(self.reading_buffer) > self.buffer_size:
            self.reading_buffer.pop(0)

        # Save to Supabase
        record = {
            'patient_id': patient_id,
            'reading_type': reading['reading_type'],
            'rmssd': reading.get('rmssd'),
            'sdnn': reading.get('sdnn'),
            'mean_hr': reading.get('mean_hr'),
            'total_sleep_min': reading.get('total_sleep_min'),
            'sleep_efficiency': reading.get('sleep_efficiency'),
            'deep_sleep_pct': reading.get('deep_sleep_pct'),
            'awakenings': reading.get('awakenings'),
            'recorded_at': reading.get('recorded_at', datetime.now(timezone.utc).isoformat()),
        }
        supa.insert_wearable(record)

        # Check for anomalies
        alerts = self._check_anomalies(reading)
        return alerts

    def _check_anomalies(self, reading: dict) -> dict:
        """Run anomaly detection on the current reading + buffer."""
        alerts = []

        if reading['reading_type'] == 'hrv':
            # 1. HRV Decay detection (PRD requirement)
            sim = WearableSimulator()
            hrv_readings = [r for r in self.reading_buffer if r['reading_type'] == 'hrv']
            decay = sim.detect_hrv_decay(hrv_readings)
            if decay:
                alerts.append(decay)

            # 2. Tachycardia check
            hr = reading.get('mean_hr', 0)
            if hr > 110:
                alerts.append({
                    'alert': 'TACHYCARDIA',
                    'value': hr,
                    'severity': 'urgent' if hr > 130 else 'moderate',
                    'message': f"Elevated heart rate: {hr:.0f} bpm",
                })

            # 3. Very low HRV
            rmssd = reading.get('rmssd', 100)
            if rmssd < 10:
                alerts.append({
                    'alert': 'CRITICALLY_LOW_HRV',
                    'value': rmssd,
                    'severity': 'urgent',
                    'message': f"Critically low HRV: RMSSD={rmssd:.1f}ms (severe autonomic stress)",
                })

        elif reading['reading_type'] == 'sleep':
            # Sleep quality check
            eff = reading.get('sleep_efficiency', 1.0)
            if eff < 0.60:
                alerts.append({
                    'alert': 'POOR_SLEEP',
                    'value': eff,
                    'severity': 'moderate',
                    'message': f"Very poor sleep efficiency: {eff:.0%}",
                })

            awakenings = reading.get('awakenings', 0)
            if awakenings >= 8:
                alerts.append({
                    'alert': 'SLEEP_FRAGMENTATION',
                    'value': awakenings,
                    'severity': 'moderate',
                    'message': f"High sleep fragmentation: {awakenings} awakenings",
                })

        return alerts if alerts else None

    def get_trend_summary(self, patient_id: str) -> dict:
        """Generate an LLM-powered summary of recent wearable trends."""
        if self._llm is None:
            try:
                self._llm = get_llm()
            except Exception as exc:
                return {'summary': f'LLM unavailable: {exc}', 'trend': 'unknown'}
        readings = supa.get_wearable_readings(patient_id, limit=50)
        if not readings:
            return {'summary': 'No wearable data available.', 'trend': 'unknown'}

        hrv_data = [r for r in readings if r['reading_type'] == 'hrv']
        sleep_data = [r for r in readings if r['reading_type'] == 'sleep']

        data_summary = f"Recent HRV readings (RMSSD): {[r.get('rmssd') for r in hrv_data[:10]]}\n"
        data_summary += f"Recent HR: {[r.get('mean_hr') for r in hrv_data[:10]]}\n"
        if sleep_data:
            data_summary += f"Recent sleep efficiency: {[r.get('sleep_efficiency') for r in sleep_data[:5]]}\n"

        prompt = (
            f"Analyze this cancer patient's wearable data and provide a brief clinical summary:\n\n"
            f"{data_summary}\n"
            f"Assess: 1) Overall autonomic health trend 2) Sleep quality trend "
            f"3) Any concerning patterns. Keep it under 4 sentences."
        )

        summary = self._llm.generate(
            prompt=prompt,
            system_prompt="You are a clinical data analyst reviewing wearable biometrics for a cancer patient.",
            temperature=0.5,
        )

        return {
            'summary': summary,
            'hrv_latest': hrv_data[0] if hrv_data else None,
            'sleep_latest': sleep_data[0] if sleep_data else None,
            'alert_count': len([r for r in readings if r.get('rmssd') and r['rmssd'] < 15]),
        }
