"""
HealthGen Wearable Data Generator
==================================
Generates synthetic wearable device data (HRV + Sleep) for Synthea cancer patients.
Implements the "Seed and Decay" model from the PRD:
  - Clinical states (cancer staging conditions) drive physiological decay
  - HRV (RMSSD, SDNN) drops during inferred treatment windows
  - Sleep quality degrades during chemo windows
  - Recovery rebound occurs after treatment ends

Reads:  master_patients.csv, master_conditions.csv
Writes: wearable_hrv.csv, wearable_sleep.csv

NOTE: We derive chemo treatment windows from master_conditions.csv
(cancer staging events) rather than the 66MB master_medications.csv,
which is too large for practical loading. Staging diagnoses (TNM stage)
reliably indicate when chemotherapy begins.

See HEALTHGEN_PARAMETERS.md for detailed parameter justifications.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta
import sys
import time

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent
RNG_SEED = 42

# HRV baseline ranges by age band (RMSSD in ms)
HRV_BASELINES = {
    (40, 50): {"rmssd": 38, "sdnn": 45, "hr": 68},
    (50, 60): {"rmssd": 32, "sdnn": 40, "hr": 72},
    (60, 70): {"rmssd": 26, "sdnn": 34, "hr": 74},
    (70, 80): {"rmssd": 21, "sdnn": 28, "hr": 76},
    (80, 91): {"rmssd": 17, "sdnn": 23, "hr": 78},
}

FEMALE_HRV_BOOST = 1.05

# Treatment decay parameters
CHEMO_RMSSD_DECAY_RANGE = (0.20, 0.50)
CHEMO_CYCLE_DAYS = (14, 28)        # Typical chemo cycle length
NUM_CHEMO_CYCLES = (4, 8)          # Number of cycles per treatment
RECOVERY_DAYS = (14, 28)

# Sleep baseline ranges
SLEEP_BASELINES = {
    "total_min":  (420, 480),
    "deep_pct":   (0.15, 0.25),
    "rem_pct":    (0.20, 0.25),
    "awakenings": (1, 3),
    "efficiency": (0.85, 0.95),
}

DAILY_NOISE_CV = 0.10

# Conditions that indicate cancer staging / start of treatment
TREATMENT_INDICATORS = [
    "tnm stage",
    "primary malignant neoplasm",
    "primary small cell malignant",
    "carcinoma of lung",
    "malignant neoplasm of breast",
    "overlapping malignant neoplasm",
    "malignant neoplasm of colon",
    "metastatic malignant neoplasm",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_age_at_date(birthdate, date):
    return int((date - birthdate).days / 365.25)


def get_hrv_baseline(age, gender, rng):
    for (lo, hi), vals in HRV_BASELINES.items():
        if lo <= age < hi:
            base = vals.copy()
            break
    else:
        base = {"rmssd": 17, "sdnn": 23, "hr": 78}

    individual_factor = rng.uniform(0.85, 1.15)
    base["rmssd"] *= individual_factor
    base["sdnn"]  *= individual_factor
    base["hr"]    *= rng.uniform(0.92, 1.08)

    if gender == "F":
        base["rmssd"] *= FEMALE_HRV_BOOST
        base["sdnn"]  *= FEMALE_HRV_BOOST

    return base


def get_sleep_baseline(age, rng):
    age_factor = max(0.0, 1.0 - (age - 40) * 0.005)

    total = rng.uniform(*SLEEP_BASELINES["total_min"]) * age_factor
    deep_pct = rng.uniform(*SLEEP_BASELINES["deep_pct"]) * age_factor
    rem_pct  = rng.uniform(*SLEEP_BASELINES["rem_pct"])
    eff      = rng.uniform(*SLEEP_BASELINES["efficiency"]) * (0.95 + 0.05 * age_factor)
    awake    = int(rng.uniform(*SLEEP_BASELINES["awakenings"]) / max(age_factor, 0.1))

    return {
        "total_min":  total,
        "deep_pct":   deep_pct,
        "rem_pct":    rem_pct,
        "efficiency": min(eff, 0.99),
        "awakenings": max(awake, 0),
    }


def build_chemo_windows_from_conditions(pt_conds, rng):
    """
    Infer chemo treatment windows from cancer staging conditions.
    When a patient receives a staging diagnosis (e.g. TNM stage 1),
    we generate a series of chemo cycles starting from that date.
    """
    # Find staging/treatment indicator conditions
    treatment_starts = []
    for _, row in pt_conds.iterrows():
        desc = str(row.get("DESCRIPTION", "")).lower()
        if any(kw in desc for kw in TREATMENT_INDICATORS):
            treatment_starts.append(row["START"])

    if not treatment_starts:
        return []

    windows = []
    for tx_start in treatment_starts:
        # Generate chemo cycles from this staging date
        num_cycles = rng.integers(*NUM_CHEMO_CYCLES)
        cycle_length = rng.integers(*CHEMO_CYCLE_DAYS)
        decay = rng.uniform(*CHEMO_RMSSD_DECAY_RANGE)

        for cycle in range(num_cycles):
            cycle_start = tx_start + timedelta(days=int(cycle * cycle_length))
            # Active infusion/toxicity period is ~7 days per cycle
            cycle_end = cycle_start + timedelta(days=7)
            windows.append((cycle_start, cycle_end, decay))

    return windows


def compute_treatment_factor(date, chemo_windows, rng):
    factor = 1.0

    for start, stop, decay_strength in chemo_windows:
        if start <= date <= stop:
            days_in = (date - start).days
            ramp = min(1.0, days_in / 5.0)
            factor = min(factor, 1.0 - decay_strength * ramp)
        elif stop < date:
            days_post = (date - stop).days
            recovery_len = rng.integers(*RECOVERY_DAYS)
            if days_post < recovery_len:
                recovery_progress = days_post / recovery_len
                residual_decay = decay_strength * (1.0 - recovery_progress)
                factor = min(factor, 1.0 - residual_decay)

    return max(factor, 0.3)


# ---------------------------------------------------------------------------
# Main Generation Logic
# ---------------------------------------------------------------------------

def load_synthea_data():
    """Load Synthea CSVs (patients + conditions only)."""
    print("[*] Loading Synthea data...")

    patients = pd.read_csv(
        DATA_DIR / "master_patients.csv",
        usecols=["Id", "BIRTHDATE", "DEATHDATE", "GENDER"],
        parse_dates=["BIRTHDATE", "DEATHDATE"],
    )
    print(f"   [OK] {len(patients)} patients loaded")

    conditions = pd.read_csv(
        DATA_DIR / "master_conditions.csv",
        usecols=["START", "PATIENT", "DESCRIPTION"],
        parse_dates=["START"],
    )
    print(f"   [OK] {len(conditions)} condition records loaded")

    return patients, conditions


def generate_for_patient(pt_row, pt_conds, rng):
    """Generate HRV and sleep data for a single patient."""
    patient_id = pt_row["Id"]

    # Date range
    if len(pt_conds) > 0:
        start_date = pt_conds["START"].min() - timedelta(days=30)
        end_candidates = [pt_conds["START"].max() + timedelta(days=180)]
    else:
        start_date = pd.Timestamp("2000-01-01")
        end_candidates = [start_date + timedelta(days=365)]

    if pd.notna(pt_row.get("DEATHDATE")):
        end_candidates.append(pt_row["DEATHDATE"])

    end_date = max(end_candidates)

    # Cap at 3 years to keep data size reasonable
    max_days = 3 * 365
    if (end_date - start_date).days > max_days:
        end_date = start_date + timedelta(days=max_days)

    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    if len(date_range) == 0:
        return [], []

    age = get_age_at_date(pt_row["BIRTHDATE"], start_date)
    gender = pt_row.get("GENDER", "M")
    hrv_base = get_hrv_baseline(age, gender, rng)
    sleep_base = get_sleep_baseline(age, rng)

    chemo_windows = build_chemo_windows_from_conditions(pt_conds, rng)

    hrv_rows = []
    sleep_rows = []

    for date in date_range:
        tf = compute_treatment_factor(date, chemo_windows, rng)

        # --- HRV ---
        noise_rmssd = rng.normal(1.0, DAILY_NOISE_CV)
        noise_sdnn  = rng.normal(1.0, DAILY_NOISE_CV)
        noise_hr    = rng.normal(1.0, DAILY_NOISE_CV * 0.5)

        rmssd = max(5.0, hrv_base["rmssd"] * tf * noise_rmssd)
        sdnn  = max(5.0, hrv_base["sdnn"]  * tf * noise_sdnn)
        hr_factor = 1.0 + (1.0 - tf) * 0.15
        mean_hr = max(50, min(120, hrv_base["hr"] * hr_factor * noise_hr))

        hrv_rows.append({
            "PATIENT":  patient_id,
            "DATE":     date.strftime("%Y-%m-%d"),
            "RMSSD":    round(rmssd, 2),
            "SDNN":     round(sdnn, 2),
            "MEAN_HR":  round(mean_hr, 1),
        })

        # --- Sleep ---
        sleep_noise = rng.normal(1.0, DAILY_NOISE_CV * 0.7)
        total_sleep = max(180, sleep_base["total_min"] * tf * sleep_noise)
        deep_pct    = max(0.05, sleep_base["deep_pct"] * tf)
        rem_pct     = max(0.10, sleep_base["rem_pct"] * (0.7 + 0.3 * tf))
        light_pct   = 1.0 - deep_pct - rem_pct

        deep_min  = round(total_sleep * deep_pct, 1)
        rem_min   = round(total_sleep * rem_pct, 1)
        light_min = round(total_sleep * light_pct, 1)

        eff = max(0.50, min(0.99, sleep_base["efficiency"] * tf * rng.normal(1.0, 0.03)))
        extra_awake = int((1.0 - tf) * rng.integers(1, 5))
        awakenings = max(0, sleep_base["awakenings"] + extra_awake)

        sleep_rows.append({
            "PATIENT":          patient_id,
            "DATE":             date.strftime("%Y-%m-%d"),
            "TOTAL_SLEEP_MIN":  round(total_sleep, 1),
            "DEEP_SLEEP_MIN":   deep_min,
            "REM_SLEEP_MIN":    rem_min,
            "LIGHT_SLEEP_MIN":  light_min,
            "AWAKENINGS":       awakenings,
            "SLEEP_EFFICIENCY": round(eff, 3),
        })

    return hrv_rows, sleep_rows


def main():
    t0 = time.time()
    rng = np.random.default_rng(RNG_SEED)

    patients, conditions = load_synthea_data()

    # Pre-index conditions by patient
    print("[*] Pre-indexing conditions by patient...")
    conds_by_patient = dict(list(conditions.groupby("PATIENT")))
    empty_df = pd.DataFrame(columns=conditions.columns)
    print(f"   [OK] {len(conds_by_patient)} patients have conditions")

    total = len(patients)
    all_hrv = []
    all_sleep = []

    print(f"\n[+] Generating wearable data for {total} patients...\n")

    for i, (_, pt_row) in enumerate(patients.iterrows(), 1):
        pid = pt_row["Id"]
        pt_conds = conds_by_patient.get(pid, empty_df)

        hrv_rows, sleep_rows = generate_for_patient(pt_row, pt_conds, rng)
        all_hrv.extend(hrv_rows)
        all_sleep.extend(sleep_rows)

        if i % 100 == 0 or i == total:
            elapsed = time.time() - t0
            print(f"   [{i}/{total}] {elapsed:.0f}s elapsed "
                  f"({len(all_hrv):,} HRV rows, {len(all_sleep):,} sleep rows)")

    # Save outputs
    hrv_path   = DATA_DIR / "wearable_hrv.csv"
    sleep_path = DATA_DIR / "wearable_sleep.csv"

    print("\n[*] Saving CSV files...")
    hrv_df = pd.DataFrame(all_hrv)
    sleep_df = pd.DataFrame(all_sleep)

    hrv_df.to_csv(hrv_path, index=False)
    sleep_df.to_csv(sleep_path, index=False)

    elapsed = time.time() - t0
    print(f"\n[DONE] in {elapsed:.1f} seconds")
    print(f"   {hrv_path.name}   -> {len(hrv_df):,} rows, {hrv_df['PATIENT'].nunique()} patients")
    print(f"   {sleep_path.name} -> {len(sleep_df):,} rows, {sleep_df['PATIENT'].nunique()} patients")
    print(f"\nHRV Summary:")
    print(hrv_df[["RMSSD", "SDNN", "MEAN_HR"]].describe().round(2).to_string())
    print(f"\nSleep Summary:")
    print(sleep_df[["TOTAL_SLEEP_MIN", "DEEP_SLEEP_MIN", "SLEEP_EFFICIENCY"]].describe().round(2).to_string())


if __name__ == "__main__":
    main()
