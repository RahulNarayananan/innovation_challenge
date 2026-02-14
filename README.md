# Cancer Recovery Monitoring -- Patient Report Generator

A data-driven system that generates comprehensive clinical reports for cancer patients from Synthea synthetic health records and wearable biometric data.

## Overview

This project creates filled-in clinical worksheets (PDFs) modeled on [American Cancer Society](https://www.cancer.org) reporting templates. Reports are generated from patient demographics, conditions, medications, lab observations, encounters, and wearable data (HRV + sleep).

## Reports Generated

| Report | Description | Patients |
|:---|:---|:---|
| **Medicine List** | Complete medication inventory with dosage periods | All |
| **Test Results** | Lab values across multiple dates with reference ranges | All |
| **Pain Diary** | Pain scores with location, type, and interventions | All |
| **Appointments** | Encounter history (visits, type, reason) | All |
| **Chemo Side Effects** | 7-day cycle worksheet with 14 side effects graded None/Mild/Moderate/Severe | Chemo patients |
| **Clinical Reasoning** | Explainability document detailing *why* each severity was assigned | Chemo patients |

## Architecture

```
generate_reports.py      # Main orchestrator (CLI entry point)
data_loader.py           # Loads all CSVs, provides patient-level lookups
report_renderers.py      # PDF renderers for 5 report types + side-effect model
report_explainability.py # Clinical reasoning / explainability PDF generator
report_utils.py          # Shared utilities (name cleaning, text sanitization)
```

### Side-Effect Severity Model

Chemo side-effect grades are computed from:
1. **Drug profiles** -- known side-effect affinities per drug (cisplatin, paclitaxel, doxorubicin, etc.)
2. **Lab values** -- WBC, hemoglobin, GFR, pain score modulate severity
3. **Wearable biometrics** -- HRV (RMSSD) and sleep efficiency as stress indicators
4. **Temporal curve** -- 7-day nadir pattern (peak toxicity Days 3-5 post-infusion)
5. **Age modifier** -- elderly patients receive increased severity multipliers

## Data Files

The master data files are stored as compressed archives in this repository:
- `master_patients.csv` -- 1,500 patients (500 each: Lung, Breast, Colorectal)
- `master_conditions.csv` -- Diagnoses and conditions
- `master_medications.csv` -- Medication history
- `master_observations.csv` -- Lab results and clinical observations
- `master_encounters.csv` -- Visit/encounter records
- `wearable_hrv.csv` -- Heart rate variability data
- `wearable_sleep.csv` -- Sleep tracking data

### Supporting Files
- `healthgen_wearable.py` -- Wearable data generator (Seed & Decay model)
- `extract_profiles.py` -- Patient profile data extractor
- `md_to_pdf.py` -- Markdown-to-PDF converter for patient profile documents
- `prd.md` -- Product Requirements Document
- `HEALTHGEN_PARAMETERS.md` -- Wearable data generation parameters
- `reporting_worksheets/` -- Original ACS PDF templates (reference)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Extract data files (if not already extracted)
# unzip the master CSV archives

# Generate reports for 10 test patients
python generate_reports.py --test

# Generate for ALL 1,500 patients
python generate_reports.py --all

# Generate for specific patient(s)
python generate_reports.py --patients <PATIENT_ID_1> <PATIENT_ID_2>
```

### Output Structure
```
patient_reports/
  Hilton_Prosacco/
    medicine_list.pdf
    test_results.pdf
    pain_diary.pdf
    appointments.pdf
    chemo_side_effects.pdf
    clinical_reasoning.pdf
  Beatrice_Zieme/
    ...
```

## Requirements

- Python 3.10+
- See `requirements.txt` for dependencies
