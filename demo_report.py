import sys
import os

# Ensure we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.reporting.report_generator import generate_patient_report

# Mock Data (simulating Writer Agent output)
patient_data = {
    "name": "Lean McDermott",
    "id": "123-456-789",
    "age": "45",
    "cancer_type": "Breast Cancer (Stage II)"
}

vitals = {
    "Average HRV": "28 ms (Low)",
    "Sleep Efficiency": "82%",
    "Resting HR": "78 bpm",
    "Steps (Avg)": "4,500/day",
    "Symptom Burden": "Moderate (Nausea, Fatigue)"
}

clinical_summary = """
Patient reports increasing fatigue and nausea following the latest chemotherapy cycle (Doxorubicin/Cyclophosphamide). 

Sleep efficiency has dropped to 82% with frequent awakenings reported. HRV is suppressed at 28ms, indicating physiological stress. 

Adherence to anti-emetics is 100%, but symptom control is suboptimal. Recommended review of hydration status and potential adjustment of supportive care medications.
"""

print("Generating demo report...")
filename = generate_patient_report(patient_data, vitals, clinical_summary.strip(), "demo_patient_report.pdf")
print(f"Report generated: {filename}")
