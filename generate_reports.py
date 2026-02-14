"""
Main Report Generator -- Orchestrates all 6 report types for cancer patients.

Usage:
    python generate_reports.py --test          # 10 test patients
    python generate_reports.py --all           # ALL patients in dataset
    python generate_reports.py --patients ID1 ID2  # Specific patient IDs
"""

import argparse
import os
import pandas as pd
from data_loader import DataLoader
from report_utils import patient_folder_name, clean_name
from report_renderers import (
    BasePDF, SideEffectModel,
    render_chemo_worksheet, render_medicine_list,
    render_test_results, render_pain_diary, render_appointments,
)
from report_explainability import render_explainability_report


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patient_reports')

TEST_PATIENT_IDS = [
    '497c0923-b34e-0004-095a-54b61544403e',  # Hilton Prosacco  - LUNG
    '65343425-3160-297c-d371-32119d34cfcc',  # Ignacio Dach     - LUNG
    'c3495c1a-3a6e-edaf-9b91-8aa7ebd0f2c4',  # Beatrice Zieme   - LUNG
    '03611e2a-fa1a-740f-0d37-3477b58b6974',  # Song Bednar      - BREAST
    '0fc698de-9c91-5eac-0eba-d74cb7540c47',  # Catrice Schoen   - BREAST
    '44466ba7-b0ca-c6bb-ac02-58cfc05398ac',  # See Wuckert      - BREAST
    '19b781ac-82c4-6a42-495b-b59d4c4811d3',  # Brandon Sanford  - COLORECTAL
    'dfeb81a1-9050-2bd6-07d1-5c294c7dec16',  # Merlin Graham    - COLORECTAL
    'a0d74db0-05f1-489b-356a-05ee8752ae89',  # Katharina King   - COLORECTAL
    'eecdf189-f43e-b108-5991-6ff9731bd93f',  # Freddy Little    - COLORECTAL
]


def generate_all_reports(loader, model, patient_id, output_dir):
    """Generate all applicable reports for a single patient into their own folder."""
    info = loader.get_patient(patient_id)
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    name = f"{first} {last}"

    # Create patient folder
    folder = os.path.join(output_dir, patient_folder_name(info))
    os.makedirs(folder, exist_ok=True)

    print(f"\n  [{name}] -> {os.path.basename(folder)}/")
    reports_generated = []

    # 1. Medicine List (all patients)
    meds = loader.get_patient_medications_detail(patient_id)
    path = os.path.join(folder, 'medicine_list.pdf')
    render_medicine_list(BasePDF, info, meds, path)
    reports_generated.append('medicine_list')
    print(f"    [+] medicine_list.pdf ({len(meds)} medications)")

    # 2. Test Results (all patients)
    lab_hist = loader.get_patient_lab_history(patient_id)
    path = os.path.join(folder, 'test_results.pdf')
    render_test_results(BasePDF, info, lab_hist, path)
    reports_generated.append('test_results')
    print(f"    [+] test_results.pdf ({len(lab_hist)} tests)")

    # 3. Pain Diary (all patients)
    pain_obs = loader.get_patient_pain_observations(patient_id)
    wearable = loader.get_patient_wearable_summary(patient_id)
    path = os.path.join(folder, 'pain_diary.pdf')
    render_pain_diary(BasePDF, model, info, pain_obs, wearable, path)
    reports_generated.append('pain_diary')
    print(f"    [+] pain_diary.pdf ({len(pain_obs)} entries)")

    # 4. Appointments (all patients)
    encounters = loader.get_patient_encounters_detail(patient_id)
    path = os.path.join(folder, 'appointments.pdf')
    render_appointments(BasePDF, info, encounters, path)
    reports_generated.append('appointments')
    print(f"    [+] appointments.pdf ({len(encounters)} encounters)")

    # 5. Chemo Worksheet (only patients with chemo drugs)
    drugs = loader.get_patient_drugs(patient_id)
    labs = loader.get_patient_labs(patient_id)
    cycle_data = None

    if drugs:
        first_med, last_med = loader.get_patient_med_dates(patient_id)
        if first_med is not None:
            mid = first_med + (last_med - first_med) / 2
            cycle_start = mid.strftime('%Y-%m-%d')
            total_days = (last_med - first_med).days
            est_cycles = max(1, total_days // 21)
            cycle_num = max(1, est_cycles // 2)
        else:
            cycle_start = '2024-01-01'
            cycle_num = 1

        path = os.path.join(folder, 'chemo_side_effects.pdf')
        cycle_data = render_chemo_worksheet(
            BasePDF, model, info, drugs, labs, wearable, path, cycle_num, cycle_start
        )
        reports_generated.append('chemo_side_effects')
        print(f"    [+] chemo_side_effects.pdf (drugs: {', '.join(d.title() for d in drugs)}, cycle #{cycle_num})")

        # 6. Explainability Report (only for chemo patients)
        path = os.path.join(folder, 'clinical_reasoning.pdf')
        render_explainability_report(info, drugs, labs, wearable, cycle_data, cycle_num, path)
        reports_generated.append('clinical_reasoning')
        print(f"    [+] clinical_reasoning.pdf (explainability document)")
    else:
        print(f"    [SKIP] chemo_side_effects.pdf (no chemo drugs)")
        print(f"    [SKIP] clinical_reasoning.pdf (no chemo drugs)")

    return reports_generated


def main():
    parser = argparse.ArgumentParser(description='Generate patient reports from clinical data')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--test', action='store_true', help='Generate for 10 test patients')
    group.add_argument('--all', action='store_true', help='Generate for ALL patients')
    group.add_argument('--patients', nargs='+', help='Specific patient ID(s)')
    parser.add_argument('--output', default=OUTPUT_DIR, help='Output directory')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    loader = DataLoader()
    model = SideEffectModel(seed=args.seed)
    loader.load()

    if args.test:
        patient_ids = TEST_PATIENT_IDS
    elif args.all:
        patient_ids = loader.patients['Id'].tolist()
    else:
        patient_ids = args.patients

    print(f"\nGenerating reports for {len(patient_ids)} patients...")
    print(f"Output: {args.output}\n")

    total_reports = 0
    for pid in patient_ids:
        try:
            reports = generate_all_reports(loader, model, pid, args.output)
            total_reports += len(reports)
        except Exception as e:
            print(f"  ERROR for {pid}: {e}")

    print(f"\n{'='*60}")
    print(f"COMPLETE: {total_reports} reports generated for {len(patient_ids)} patients")
    print(f"Output: {args.output}")


if __name__ == '__main__':
    main()
