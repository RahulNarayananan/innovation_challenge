"""
Seed Supabase with existing CSV data.
Migrates the 10 test patients + their medications, labs, and wearable data.
"""
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from datetime import datetime

# Add parent dirs to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.supabase_client import db


DATA_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_PATIENT_IDS = [
    '497c0923-b34e-0004-095a-54b61544403e',
    '65343425-3160-297c-d371-32119d34cfcc',
    'c3495c1a-3a6e-edaf-9b91-8aa7ebd0f2c4',
    '03611e2a-fa1a-740f-0d37-3477b58b6974',
    '0fc698de-9c91-5eac-0eba-d74cb7540c47',
    '44466ba7-b0ca-c6bb-ac02-58cfc05398ac',
    '19b781ac-82c4-6a42-495b-b59d4c4811d3',
    'dfeb81a1-9050-2bd6-07d1-5c294c7dec16',
    'a0d74db0-05f1-489b-356a-05ee8752ae89',
    'eecdf189-f43e-b108-5991-6ff9731bd93f',
]

CHEMO_DRUGS = ['cisplatin', 'paclitaxel', 'doxorubicin', 'carboplatin',
               'oxaliplatin', 'leucovorin', 'fulvestrant', 'tamoxifen']


def clean_name(name):
    return re.sub(r'\d+$', '', str(name))


def detect_cancer_type(patient_id, conditions_df):
    conds = conditions_df[conditions_df['PATIENT'] == patient_id]
    desc_concat = ' '.join(conds['DESCRIPTION'].str.lower().values)
    if 'lung' in desc_concat or 'pulmonary' in desc_concat:
        return 'LUNG'
    elif 'breast' in desc_concat:
        return 'BREAST'
    elif 'colon' in desc_concat or 'rectum' in desc_concat or 'colorectal' in desc_concat:
        return 'COLORECTAL'
    return 'UNKNOWN'


# Global mapping: synthea patient ID -> supabase UUID
patient_map = {}


def seed_patients(patients_df, conditions_df, patient_ids):
    """Seed patients table. Returns a mapping of synthea_id -> supabase UUID."""
    global patient_map
    print("Seeding patients...")
    records = []
    ordered_ids = []
    for pid in patient_ids:
        row = patients_df[patients_df['Id'] == pid]
        if row.empty:
            print(f"  SKIP - patient {pid} not found")
            continue
        row = row.iloc[0]
        cancer_type = detect_cancer_type(pid, conditions_df)
        records.append({
            'first_name': clean_name(row['FIRST']),
            'last_name': clean_name(row['LAST']),
            'birth_date': str(row['BIRTHDATE']),
            'gender': row['GENDER'],
            'race': row.get('RACE', 'unknown'),
            'city': row.get('CITY', ''),
            'state': row.get('STATE', ''),
            'cancer_type': cancer_type,
            'treatment_phase': 'active',
        })
        ordered_ids.append(pid)

    if records:
        result = db().table('patients').insert(records).execute()
        # Build synthea_id -> supabase UUID mapping from returned data
        for i, row in enumerate(result.data):
            patient_map[ordered_ids[i]] = row['id']
        print(f"  Seeded {len(records)} patients")
    return patient_map


def seed_medications(meds_df, patient_ids):
    """Seed medications table."""
    print("Seeding medications...")
    global patient_map

    total = 0
    for synthea_id, supabase_id in patient_map.items():
        rows = meds_df[meds_df['PATIENT'] == synthea_id]
        if rows.empty:
            continue
        grouped = rows.groupby('DESCRIPTION').agg(
            start=('START', 'min'), stop=('STOP', 'max'), count=('DESCRIPTION', 'count'),
            reason=('REASONDESCRIPTION', 'first')
        ).reset_index()

        batch = []
        for _, m in grouped.iterrows():
            name_lower = m['DESCRIPTION'].lower()
            is_chemo = any(d in name_lower for d in CHEMO_DRUGS)
            batch.append({
                'patient_id': supabase_id,
                'name': m['DESCRIPTION'],
                'reason': str(m['reason']) if pd.notna(m['reason']) else 'Supportive care',
                'start_date': str(m['start'])[:10],
                'end_date': str(m['stop'])[:10] if pd.notna(m['stop']) else None,
                'is_chemo': is_chemo,
            })
        if batch:
            db().table('medications').insert(batch).execute()
            total += len(batch)

    print(f"  Seeded {total} medications")


def seed_lab_results(obs_df, patient_ids):
    """Seed lab_results table."""
    print("Seeding lab results...")
    global patient_map

    code_map = {
        '6690-2': ('WBC', 'x1000/mm3', '4.5-11.0'),
        '718-7': ('Hemoglobin', 'g/dL', '12-18'),
        '789-8': ('RBC', 'x10^6/uL', '4.2-5.9'),
        '4544-3': ('Hematocrit', '%', '36-54'),
        '751-8': ('Neutrophils', 'x1000/mm3', '2.5-7.0'),
        '32623-1': ('GFR', 'mL/min', '>60'),
        '20570-8': ('Creatinine', 'mg/dL', '0.6-1.2'),
        '72514-3': ('Pain Score', 'scale', '0-10'),
    }

    total = 0
    for synthea_id, supabase_id in patient_map.items():
        rows = obs_df[(obs_df['PATIENT'] == synthea_id) & (obs_df['CODE'].isin(code_map.keys()))]
        if rows.empty:
            continue
        # Sample up to 20 per patient to avoid huge inserts
        if len(rows) > 20:
            rows = rows.sample(20, random_state=42)

        batch = []
        for _, r in rows.iterrows():
            code = str(r['CODE'])
            if code not in code_map:
                continue
            name, unit, ref = code_map[code]
            try:
                val = float(r['VALUE'])
            except (ValueError, TypeError):
                continue
            batch.append({
                'patient_id': supabase_id,
                'test_code': code,
                'test_name': name,
                'value': val,
                'unit': unit,
                'reference_range': ref,
                'observed_at': str(r['DATE']),
            })
        if batch:
            db().table('lab_results').insert(batch).execute()
            total += len(batch)

    print(f"  Seeded {total} lab results")


def seed_wearable(hrv_df, sleep_df, patient_ids):
    """Seed wearable_readings table with a sample of HRV and sleep data."""
    print("Seeding wearable data...")
    global patient_map

    total = 0
    for synthea_id, supabase_id in patient_map.items():
        # HRV - sample 30 readings
        h = hrv_df[hrv_df['PATIENT'] == synthea_id]
        if not h.empty:
            sample = h.sample(min(30, len(h)), random_state=42)
            batch = []
            for _, r in sample.iterrows():
                batch.append({
                    'patient_id': supabase_id,
                    'reading_type': 'hrv',
                    'rmssd': float(r['RMSSD']) if pd.notna(r.get('RMSSD')) else None,
                    'sdnn': float(r['SDNN']) if pd.notna(r.get('SDNN')) else None,
                    'mean_hr': float(r['MEAN_HR']) if pd.notna(r.get('MEAN_HR')) else None,
                    'recorded_at': str(r['DATE']),
                })
            if batch:
                db().table('wearable_readings').insert(batch).execute()
                total += len(batch)

        # Sleep - sample 30 readings
        s = sleep_df[sleep_df['PATIENT'] == synthea_id]
        if not s.empty:
            sample = s.sample(min(30, len(s)), random_state=42)
            batch = []
            for _, r in sample.iterrows():
                batch.append({
                    'patient_id': supabase_id,
                    'reading_type': 'sleep',
                    'total_sleep_min': float(r['TOTAL_SLEEP_MIN']) if pd.notna(r.get('TOTAL_SLEEP_MIN')) else None,
                    'sleep_efficiency': float(r['SLEEP_EFFICIENCY']) if pd.notna(r.get('SLEEP_EFFICIENCY')) else None,
                    'deep_sleep_pct': float(r['DEEP_PCT']) if pd.notna(r.get('DEEP_PCT')) else None,
                    'awakenings': int(r['AWAKENINGS']) if pd.notna(r.get('AWAKENINGS')) else None,
                    'recorded_at': str(r['DATE']),
                })
            if batch:
                db().table('wearable_readings').insert(batch).execute()
                total += len(batch)

    print(f"  Seeded {total} wearable readings")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Seed Supabase with CSV data')
    parser.add_argument('--all', action='store_true', help='Seed ALL patients (not just test 10)')
    args = parser.parse_args()

    print("Loading CSVs...")
    patients_df = pd.read_csv(os.path.join(DATA_DIR, 'master_patients.csv'))
    conditions_df = pd.read_csv(os.path.join(DATA_DIR, 'master_conditions.csv'))
    meds_df = pd.read_csv(os.path.join(DATA_DIR, 'master_medications.csv'))
    obs_df = pd.read_csv(os.path.join(DATA_DIR, 'master_observations.csv'))
    hrv_df = pd.read_csv(os.path.join(DATA_DIR, 'wearable_hrv.csv'))
    sleep_df = pd.read_csv(os.path.join(DATA_DIR, 'wearable_sleep.csv'))
    print("CSVs loaded.\n")

    if args.all:
        patient_ids = patients_df['Id'].tolist()
    else:
        patient_ids = TEST_PATIENT_IDS

    print(f"Seeding {len(patient_ids)} patients...\n")

    # Patients must be seeded first (others reference patient UUIDs)
    seed_patients(patients_df, conditions_df, patient_ids)

    # Seed remaining data sequentially (Supabase client doesn't support
    # concurrent connections well on Windows)
    seed_medications(meds_df, patient_ids)
    seed_lab_results(obs_df, patient_ids)
    seed_wearable(hrv_df, sleep_df, patient_ids)

    print(f"\nDone! Seeded {len(patient_ids)} patients into Supabase.")


if __name__ == '__main__':
    main()
