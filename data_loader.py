"""
DataLoader - loads all CSV data once and provides fast patient-level lookups.
"""
import os
import pandas as pd

# Drug -> side-effect affinity weights (0-1 scale)
DRUG_SIDE_EFFECT_PROFILES = {
    'cisplatin': {
        'Nausea & Vomiting': 0.85, 'Fatigue': 0.70, 'Loss of Appetite': 0.65,
        'Numbness / Tingling': 0.30, 'Fever': 0.25, 'Diarrhea': 0.30,
        'Sore Mouth': 0.20, 'Edema (Hands/Feet)': 0.15, 'Shortness of Breath': 0.20,
        'Anxiety / Depression': 0.40, 'Muscle / Joint Pain': 0.30,
        'Itching / Rash': 0.10, 'Constipation': 0.20, 'Swallowing Difficulty': 0.10,
    },
    'paclitaxel': {
        'Numbness / Tingling': 0.80, 'Muscle / Joint Pain': 0.75, 'Fatigue': 0.70,
        'Nausea & Vomiting': 0.50, 'Loss of Appetite': 0.45, 'Diarrhea': 0.35,
        'Sore Mouth': 0.30, 'Edema (Hands/Feet)': 0.30, 'Fever': 0.25,
        'Shortness of Breath': 0.20, 'Itching / Rash': 0.20,
        'Anxiety / Depression': 0.35, 'Constipation': 0.25, 'Swallowing Difficulty': 0.10,
    },
    'doxorubicin': {
        'Nausea & Vomiting': 0.90, 'Fatigue': 0.80, 'Loss of Appetite': 0.60,
        'Sore Mouth': 0.55, 'Fever': 0.35, 'Diarrhea': 0.30,
        'Anxiety / Depression': 0.45, 'Shortness of Breath': 0.25,
        'Itching / Rash': 0.20, 'Edema (Hands/Feet)': 0.20,
        'Numbness / Tingling': 0.15, 'Muscle / Joint Pain': 0.30,
        'Constipation': 0.25, 'Swallowing Difficulty': 0.15,
    },
    'carboplatin': {
        'Nausea & Vomiting': 0.65, 'Fatigue': 0.65, 'Loss of Appetite': 0.50,
        'Diarrhea': 0.30, 'Constipation': 0.25, 'Numbness / Tingling': 0.35,
        'Fever': 0.20, 'Sore Mouth': 0.15, 'Muscle / Joint Pain': 0.25,
        'Anxiety / Depression': 0.35, 'Shortness of Breath': 0.15,
        'Itching / Rash': 0.15, 'Edema (Hands/Feet)': 0.10, 'Swallowing Difficulty': 0.05,
    },
    'oxaliplatin': {
        'Numbness / Tingling': 0.90, 'Nausea & Vomiting': 0.70, 'Fatigue': 0.65,
        'Diarrhea': 0.55, 'Loss of Appetite': 0.45, 'Fever': 0.20,
        'Muscle / Joint Pain': 0.40, 'Sore Mouth': 0.20, 'Anxiety / Depression': 0.30,
        'Shortness of Breath': 0.10, 'Constipation': 0.20, 'Itching / Rash': 0.10,
        'Edema (Hands/Feet)': 0.15, 'Swallowing Difficulty': 0.15,
    },
    'leucovorin': {
        'Nausea & Vomiting': 0.30, 'Diarrhea': 0.25, 'Sore Mouth': 0.20,
        'Fatigue': 0.15, 'Itching / Rash': 0.10, 'Loss of Appetite': 0.15,
        'Fever': 0.05, 'Numbness / Tingling': 0.05, 'Muscle / Joint Pain': 0.10,
        'Anxiety / Depression': 0.10, 'Shortness of Breath': 0.05,
        'Constipation': 0.10, 'Edema (Hands/Feet)': 0.05, 'Swallowing Difficulty': 0.05,
    },
    'fulvestrant': {
        'Nausea & Vomiting': 0.40, 'Fatigue': 0.50, 'Loss of Appetite': 0.30,
        'Muscle / Joint Pain': 0.55, 'Fever': 0.15, 'Diarrhea': 0.20,
        'Constipation': 0.20, 'Anxiety / Depression': 0.30, 'Shortness of Breath': 0.15,
        'Sore Mouth': 0.10, 'Edema (Hands/Feet)': 0.20, 'Itching / Rash': 0.15,
        'Numbness / Tingling': 0.10, 'Swallowing Difficulty': 0.05,
    },
    'tamoxifen': {
        'Fatigue': 0.45, 'Nausea & Vomiting': 0.30, 'Anxiety / Depression': 0.35,
        'Muscle / Joint Pain': 0.40, 'Edema (Hands/Feet)': 0.25,
        'Loss of Appetite': 0.20, 'Diarrhea': 0.15, 'Itching / Rash': 0.15,
        'Fever': 0.10, 'Shortness of Breath': 0.10, 'Sore Mouth': 0.10,
        'Constipation': 0.15, 'Numbness / Tingling': 0.10, 'Swallowing Difficulty': 0.05,
    },
}


class DataLoader:
    """Loads all CSV data once and provides fast patient-level lookups."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self._loaded = False

    def load(self):
        if self._loaded:
            return
        print("Loading datasets...")
        d = self.data_dir
        self.patients = pd.read_csv(os.path.join(d, 'master_patients.csv'))
        self.conditions = pd.read_csv(os.path.join(d, 'master_conditions.csv'))
        self.medications = pd.read_csv(os.path.join(d, 'master_medications.csv'))
        self.observations = pd.read_csv(os.path.join(d, 'master_observations.csv'))
        self.encounters = pd.read_csv(os.path.join(d, 'master_encounters.csv'))
        self.hrv = pd.read_csv(os.path.join(d, 'wearable_hrv.csv'))
        self.sleep = pd.read_csv(os.path.join(d, 'wearable_sleep.csv'))
        self._loaded = True
        print(f"Loaded {len(self.patients)} patients.")

    def get_patient(self, patient_id):
        self.load()
        row = self.patients[self.patients['Id'] == patient_id]
        if row.empty:
            raise ValueError(f"Patient {patient_id} not found.")
        return row.iloc[0].to_dict()

    def get_chemo_patients(self):
        self.load()
        chemo_ids = self.medications['PATIENT'].unique()
        valid = set(self.patients['Id'].values)
        return [pid for pid in chemo_ids if pid in valid]

    def get_patient_drugs(self, patient_id):
        self.load()
        meds = self.medications[self.medications['PATIENT'] == patient_id]
        drugs = set()
        for desc in meds['DESCRIPTION'].unique():
            desc_lower = desc.lower()
            for drug_key in DRUG_SIDE_EFFECT_PROFILES:
                if drug_key in desc_lower:
                    drugs.add(drug_key)
        return list(drugs)

    def get_patient_labs(self, patient_id):
        self.load()
        obs = self.observations[self.observations['PATIENT'] == patient_id]
        labs = {}
        code_map = {
            '718-7': 'hemoglobin', '6690-2': 'wbc', '72514-3': 'pain_score',
            '32623-1': 'gfr', '789-8': 'rbc', '751-8': 'neutrophils',
            '2093-3': 'cholesterol', '2571-8': 'triglycerides',
            '4544-3': 'hematocrit', '20570-8': 'creatinine',
            '2947-0': 'sodium', '33914-3': 'egfr',
        }
        for code, name in code_map.items():
            matches = obs[obs['CODE'] == code].sort_values('DATE')
            if not matches.empty:
                val = matches.iloc[-1]['VALUE']
                try:
                    labs[name] = float(val)
                except (ValueError, TypeError):
                    pass
        return labs

    def get_patient_lab_history(self, patient_id, num_dates=4):
        """Return lab results across multiple dates for the test results form."""
        self.load()
        obs = self.observations[self.observations['PATIENT'] == patient_id]
        key_codes = {
            '6690-2': ('WBC', '5-10 x1000/mm3', 'Infection-fighting cells'),
            '718-7': ('Hemoglobin (HGB)', '12-18 g/dL', 'Oxygen in red blood cells'),
            '789-8': ('RBC', '4.2-5.9 x10^6/uL', 'Red blood cell count'),
            '4544-3': ('Hematocrit (HCT)', '36-54 %', 'Proportion of red blood cells'),
            '751-8': ('Neutrophils', '2.5-7.0 x1000/mm3', 'Primary immune defense'),
            '32623-1': ('GFR', '>60 mL/min', 'Kidney function'),
            '20570-8': ('Creatinine', '0.6-1.2 mg/dL', 'Kidney waste product'),
            '72514-3': ('Pain Score', '0-10 scale', 'Subjective pain rating'),
        }
        results = []
        for code, (name, ref_range, note) in key_codes.items():
            matches = obs[obs['CODE'] == code].sort_values('DATE')
            if matches.empty:
                continue
            # Get up to num_dates evenly spaced results
            if len(matches) > num_dates:
                indices = [int(i * (len(matches)-1) / (num_dates-1)) for i in range(num_dates)]
                matches = matches.iloc[indices]
            date_vals = []
            for _, row in matches.iterrows():
                try:
                    val = float(row['VALUE'])
                    date_vals.append((str(row['DATE'])[:10], f"{val:.1f}"))
                except (ValueError, TypeError):
                    date_vals.append((str(row['DATE'])[:10], str(row['VALUE'])))
            results.append({
                'name': name, 'ref_range': ref_range, 'note': note,
                'date_vals': date_vals,
            })
        return results

    def get_patient_medications_detail(self, patient_id):
        """Return detailed medication list for the medicine list form."""
        self.load()
        meds = self.medications[self.medications['PATIENT'] == patient_id]
        if meds.empty:
            return []
        grouped = meds.groupby('DESCRIPTION').agg(
            first_date=('START', 'min'), last_date=('STOP', 'max'),
            count=('DESCRIPTION', 'count'),
            reason=('REASONDESCRIPTION', 'first')
        ).reset_index().sort_values('first_date')
        result = []
        for _, m in grouped.iterrows():
            result.append({
                'name': m['DESCRIPTION'],
                'reason': str(m['reason']) if pd.notna(m['reason']) else 'Supportive care',
                'start': str(m['first_date'])[:10],
                'end': str(m['last_date'])[:10],
                'count': int(m['count']),
            })
        return result

    def get_patient_encounters_detail(self, patient_id):
        """Return encounter list for the appointments form."""
        self.load()
        enc = self.encounters[self.encounters['PATIENT'] == patient_id].sort_values('START')
        results = []
        for _, e in enc.iterrows():
            results.append({
                'date': str(e['START'])[:10],
                'time': str(e['START'])[11:16] if len(str(e['START'])) > 11 else '09:00',
                'class': str(e['ENCOUNTERCLASS']),
                'description': str(e['DESCRIPTION']),
                'reason': str(e.get('REASONDESCRIPTION', '')) if pd.notna(e.get('REASONDESCRIPTION')) else '',
            })
        return results

    def get_patient_wearable_summary(self, patient_id):
        self.load()
        summary = {}
        h = self.hrv[self.hrv['PATIENT'] == patient_id]
        if not h.empty:
            summary['rmssd_mean'] = h['RMSSD'].mean()
            summary['rmssd_min'] = h['RMSSD'].min()
            summary['hr_mean'] = h['MEAN_HR'].mean()
        s = self.sleep[self.sleep['PATIENT'] == patient_id]
        if not s.empty:
            summary['sleep_mean'] = s['TOTAL_SLEEP_MIN'].mean()
            summary['sleep_eff_mean'] = s['SLEEP_EFFICIENCY'].mean()
            summary['awakenings_mean'] = s['AWAKENINGS'].mean()
        return summary

    def get_patient_med_dates(self, patient_id):
        self.load()
        meds = self.medications[self.medications['PATIENT'] == patient_id]
        if meds.empty:
            return None, None
        return pd.to_datetime(meds['START']).min(), pd.to_datetime(meds['STOP']).max()

    def get_patient_pain_observations(self, patient_id, num_entries=10):
        """Return pain score observations for the pain diary."""
        self.load()
        obs = self.observations[self.observations['PATIENT'] == patient_id]
        pain = obs[obs['CODE'] == '72514-3'].sort_values('DATE')
        if pain.empty:
            return []
        if len(pain) > num_entries:
            indices = [int(i * (len(pain)-1) / (num_entries-1)) for i in range(num_entries)]
            pain = pain.iloc[indices]
        results = []
        for _, row in pain.iterrows():
            try:
                score = float(row['VALUE'])
            except (ValueError, TypeError):
                score = 0
            results.append({
                'date': str(row['DATE'])[:10],
                'score': score,
            })
        return results
