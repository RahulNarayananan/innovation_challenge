"""
Real-time Wearable Data Simulator
Generates synthetic HRV/sleep data that streams like a real wearable device.
Uses the Seed & Decay model from the existing healthgen_wearable.py.
"""
import asyncio
import json
import math
import random
import time
from datetime import datetime, timezone, timedelta


class WearableSimulator:
    """
    Generates real-time synthetic wearable data for a patient.
    Simulates chemo cycle effects on HRV and sleep patterns.
    """

    def __init__(self, patient_config: dict = None, speed_factor: float = 1.0):
        """
        Args:
            patient_config: Dict with patient-specific parameters
                - base_rmssd: Baseline HRV RMSSD (default 35)
                - base_hr: Baseline heart rate (default 72)
                - chemo_day: Current day in chemo cycle (0-20, default 0)
                - cancer_type: LUNG/BREAST/COLORECTAL
                - age: Patient age (affects baselines)
            speed_factor: How fast to simulate. 1.0 = real-time, 60 = 1 reading/sec = 1 min of data/sec
        """
        cfg = patient_config or {}
        self.base_rmssd = cfg.get('base_rmssd', 35.0)
        self.base_hr = cfg.get('base_hr', 72.0)
        self.base_sleep_eff = cfg.get('base_sleep_eff', 0.85)
        self.chemo_day = cfg.get('chemo_day', 0)
        self.cancer_type = cfg.get('cancer_type', 'LUNG')
        self.age = cfg.get('age', 55)
        self.speed_factor = speed_factor

        # Age adjustments
        if self.age >= 70:
            self.base_rmssd *= 0.7
            self.base_hr += 5
        elif self.age >= 60:
            self.base_rmssd *= 0.85

        self._running = False
        self._tick = 0

    def _chemo_decay_factor(self, day):
        """
        Seed & Decay model: HRV decays during chemo nadir (days 3-10),
        then recovers gradually.
        """
        if day <= 1:
            return 1.0  # Infusion day, minimal effect yet
        elif day <= 3:
            return 0.85  # Onset
        elif day <= 7:
            return 0.55 + 0.05 * random.random()  # Nadir - deep decay
        elif day <= 10:
            return 0.65 + 0.05 * (day - 7)  # Early recovery
        elif day <= 14:
            return 0.80 + 0.03 * (day - 10)  # Recovery
        else:
            return 0.95 + 0.05 * random.random()  # Near baseline

    def generate_hrv_reading(self) -> dict:
        """Generate a single HRV reading with realistic variation."""
        self._tick += 1
        day = self.chemo_day + (self._tick / (3600 * self.speed_factor))  # Advance day slowly

        decay = self._chemo_decay_factor(int(day) % 21)  # 21-day cycle

        # Circadian rhythm (HRV higher at night)
        hour = (self._tick * self.speed_factor / 60) % 24
        circadian = 1.0 + 0.15 * math.sin(2 * math.pi * (hour - 3) / 24)

        # Random physiological noise
        noise = random.gauss(0, 2.5)

        rmssd = self.base_rmssd * decay * circadian + noise
        rmssd = max(5.0, rmssd)  # Floor

        # SDNN correlates with RMSSD
        sdnn = rmssd * (1.2 + random.gauss(0, 0.1))

        # Heart rate inversely correlated with HRV
        hr_noise = random.gauss(0, 3)
        mean_hr = self.base_hr * (2.0 - decay) + hr_noise
        mean_hr = max(50, min(140, mean_hr))

        return {
            'reading_type': 'hrv',
            'rmssd': round(rmssd, 2),
            'sdnn': round(sdnn, 2),
            'mean_hr': round(mean_hr, 1),
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                'chemo_day': int(day) % 21,
                'decay_factor': round(decay, 3),
                'circadian_hour': round(hour, 1),
            }
        }

    def generate_sleep_reading(self) -> dict:
        """Generate a sleep reading (1 per simulated night)."""
        day = self.chemo_day + (self._tick / (3600 * self.speed_factor))
        decay = self._chemo_decay_factor(int(day) % 21)

        sleep_eff = self.base_sleep_eff * (0.7 + 0.3 * decay) + random.gauss(0, 0.03)
        sleep_eff = max(0.4, min(1.0, sleep_eff))

        total_sleep = random.gauss(420, 30) * decay  # ~7h baseline
        total_sleep = max(180, total_sleep)

        deep_pct = 0.20 * decay + random.gauss(0, 0.03)
        deep_pct = max(0.05, min(0.35, deep_pct))

        awakenings = int(max(0, random.gauss(3 / decay, 1)))

        return {
            'reading_type': 'sleep',
            'total_sleep_min': round(total_sleep, 1),
            'sleep_efficiency': round(sleep_eff, 3),
            'deep_sleep_pct': round(deep_pct, 3),
            'awakenings': awakenings,
            'recorded_at': datetime.now(timezone.utc).isoformat(),
            'metadata': {
                'chemo_day': int(day) % 21,
                'decay_factor': round(decay, 3),
            }
        }

    async def stream(self, interval_seconds: float = 2.0, on_reading=None):
        """
        Stream HRV readings at a fixed interval.
        Generates sleep reading every ~30 HRV readings.

        Args:
            interval_seconds: Time between readings
            on_reading: async callback function(reading_dict)
        """
        self._running = True
        reading_count = 0

        while self._running:
            reading = self.generate_hrv_reading()
            reading_count += 1

            if on_reading:
                await on_reading(reading)
            else:
                yield reading

            # Generate sleep reading every ~30 HRV readings
            if reading_count % 30 == 0:
                sleep = self.generate_sleep_reading()
                if on_reading:
                    await on_reading(sleep)
                else:
                    yield sleep

            await asyncio.sleep(interval_seconds)

    def stop(self):
        """Stop the streaming."""
        self._running = False

    def detect_hrv_decay(self, readings: list, threshold: float = 0.30) -> dict:
        """
        Detect HRV decay (RMSSD drop > threshold) from a list of readings.
        Returns alert info if decay detected.
        """
        if len(readings) < 5:
            return None

        rmssd_values = [r['rmssd'] for r in readings if r.get('rmssd')]
        if len(rmssd_values) < 5:
            return None

        recent = sum(rmssd_values[-3:]) / 3
        baseline = sum(rmssd_values[:3]) / 3

        if baseline > 0:
            drop_pct = (baseline - recent) / baseline
            if drop_pct >= threshold:
                return {
                    'alert': 'HRV_DECAY',
                    'drop_pct': round(drop_pct * 100, 1),
                    'baseline_rmssd': round(baseline, 1),
                    'current_rmssd': round(recent, 1),
                    'severity': 'urgent' if drop_pct >= 0.50 else 'moderate',
                    'message': f"HRV dropped {drop_pct:.0%} from baseline ({baseline:.0f} -> {recent:.0f} ms). "
                              f"This may indicate treatment toxicity or autonomic stress.",
                }
        return None
