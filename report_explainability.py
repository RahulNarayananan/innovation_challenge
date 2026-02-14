"""
Explainability Report Generator
Produces a reasoning document explaining WHY each side-effect severity was assigned.
"""
import os
import pandas as pd
from fpdf import FPDF
from report_utils import clean_name, sanitize_text
from report_renderers import CHEMO_SIDE_EFFECTS, GRADE_LABELS, GRADE_COLORS, GRADE_TEXT_COLORS


class ExplainPDF(FPDF):
    def __init__(self, patient_name):
        super().__init__(orientation='P', format='A4')
        self.patient_name = patient_name

    def normalize_text(self, text):
        return super().normalize_text(sanitize_text(text))

    def header(self):
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(26, 26, 46)
        self.cell(0, 5, f'Clinical Reasoning Report  |  {self.patient_name}', align='L')
        self.set_font('Helvetica', '', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f'Page {self.page_no()}/{{nb}}', align='R')
        self.ln(7)
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-10)
        self.set_font('Helvetica', 'I', 6)
        self.set_text_color(180, 180, 180)
        self.cell(0, 5, 'Explainability document -- generated from clinical data analysis', align='C')


def render_explainability_report(info, drugs, labs, wearable, cycle_data, cycle_num, output_path):
    """Generate a PDF explaining the reasoning behind all report data."""
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    name = f"{first} {last}"

    age = None
    try:
        birth = pd.to_datetime(info['BIRTHDATE'])
        age = int((pd.Timestamp.now() - birth).days / 365.25)
    except:
        pass

    pdf = ExplainPDF(name)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 10, 'Clinical Reasoning & Explainability Report', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, f'Patient: {name}  |  Cycle #{cycle_num}', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Section 1: Patient Context
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '1. Patient Context', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(40, 40, 40)

    pdf.cell(0, 5, f"Cancer Type: {info.get('cancer_type', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Age: {age or 'N/A'}  |  Gender: {info.get('GENDER', 'N/A')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Chemotherapy Drugs: {', '.join(d.title() for d in drugs)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 2: Clinical Data Inputs
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '2. Clinical Data Inputs & Their Impact', new_x="LMARGIN", new_y="NEXT")

    # Labs subsection
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 6, '2a. Laboratory Values', new_x="LMARGIN", new_y="NEXT")

    lab_explanations = []
    wbc = labs.get('wbc')
    if wbc is not None:
        status = 'LOW' if wbc < 4.5 else 'NORMAL'
        impact = 'Increased fever/infection risk and fatigue severity' if wbc < 4.5 else 'No modifier applied'
        lab_explanations.append(('WBC', f'{wbc:.1f} x1000/mm3', '4.5-11.0', status, impact))

    hgb = labs.get('hemoglobin')
    if hgb is not None:
        status = 'LOW' if hgb < 12 else 'NORMAL'
        impact = 'Increased fatigue, shortness of breath, appetite loss' if hgb < 12 else 'No modifier applied'
        lab_explanations.append(('Hemoglobin', f'{hgb:.1f} g/dL', '12-18', status, impact))

    gfr = labs.get('gfr')
    if gfr is not None:
        status = 'LOW' if gfr < 60 else 'NORMAL'
        impact = 'Increased nausea/fatigue (drug toxicity accumulation)' if gfr < 60 else 'No modifier applied'
        lab_explanations.append(('GFR', f'{gfr:.1f} mL/min', '>60', status, impact))

    pain = labs.get('pain_score')
    if pain is not None:
        status = 'HIGH' if pain >= 4 else 'LOW'
        impact = 'Increased anxiety/depression and muscle/joint pain' if pain >= 4 else 'No modifier applied'
        lab_explanations.append(('Pain Score', f'{pain:.0f}/10', '0-3', status, impact))

    if lab_explanations:
        cw = [35, 30, 25, 18, 75]
        rh = 6
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_fill_color(26, 26, 46)
        pdf.set_text_color(255, 255, 255)
        for hdr, w in zip(['Lab Test', 'Value', 'Normal', 'Status', 'Impact on Side Effects'], cw):
            pdf.cell(w, rh, hdr, border=1, fill=True, align='C')
        pdf.ln()

        pdf.set_font('Helvetica', '', 7)
        for lab_name, val, normal, status, impact in lab_explanations:
            sc = (255,210,210) if status in ('LOW','HIGH') else (220,237,220)
            pdf.set_fill_color(*sc)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(cw[0], rh, lab_name, border=1, fill=True)
            pdf.cell(cw[1], rh, val, border=1, fill=True, align='C')
            pdf.cell(cw[2], rh, normal, border=1, fill=True, align='C')
            tc = (180,30,30) if status in ('LOW','HIGH') else (60,120,60)
            pdf.set_text_color(*tc)
            pdf.cell(cw[3], rh, status, border=1, fill=True, align='C')
            pdf.set_text_color(40, 40, 40)
            pdf.cell(cw[4], rh, impact, border=1, fill=True)
            pdf.ln()
    else:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.cell(0, 5, 'No lab values available.', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Wearable subsection
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 6, '2b. Wearable Biometric Data', new_x="LMARGIN", new_y="NEXT")

    wear_explanations = []
    rmssd = wearable.get('rmssd_mean')
    if rmssd is not None:
        status = 'LOW' if rmssd < 30 else 'NORMAL'
        impact = 'Autonomic stress -> increased fatigue, anxiety, SOB' if rmssd < 30 else 'Healthy autonomic function'
        wear_explanations.append(('HRV (RMSSD)', f'{rmssd:.1f} ms', '>30 ms', status, impact))

    sleep_eff = wearable.get('sleep_eff_mean')
    if sleep_eff is not None:
        status = 'LOW' if sleep_eff < 0.85 else 'NORMAL'
        impact = 'Poor sleep -> amplified fatigue and anxiety' if sleep_eff < 0.85 else 'Adequate sleep quality'
        wear_explanations.append(('Sleep Efficiency', f'{sleep_eff:.0%}', '>85%', status, impact))

    hr = wearable.get('hr_mean')
    if hr is not None:
        wear_explanations.append(('Mean Heart Rate', f'{hr:.0f} bpm', '60-100', 'INFO', 'Contextual cardiovascular data'))

    if wear_explanations:
        cw = [35, 25, 25, 18, 80]
        rh = 6
        pdf.set_font('Helvetica', 'B', 7)
        pdf.set_fill_color(26, 26, 46)
        pdf.set_text_color(255, 255, 255)
        for hdr, w in zip(['Metric', 'Value', 'Normal', 'Status', 'Impact'], cw):
            pdf.cell(w, rh, hdr, border=1, fill=True, align='C')
        pdf.ln()

        pdf.set_font('Helvetica', '', 7)
        for met, val, normal, status, impact in wear_explanations:
            sc = (255,210,210) if status == 'LOW' else (220,237,220) if status == 'NORMAL' else (245,245,250)
            pdf.set_fill_color(*sc)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(cw[0], rh, met, border=1, fill=True)
            pdf.cell(cw[1], rh, val, border=1, fill=True, align='C')
            pdf.cell(cw[2], rh, normal, border=1, fill=True, align='C')
            tc = (180,30,30) if status == 'LOW' else (60,120,60) if status == 'NORMAL' else (100,100,100)
            pdf.set_text_color(*tc)
            pdf.cell(cw[3], rh, status, border=1, fill=True, align='C')
            pdf.set_text_color(40, 40, 40)
            pdf.cell(cw[4], rh, impact, border=1, fill=True)
            pdf.ln()
    else:
        pdf.set_font('Helvetica', 'I', 8)
        pdf.cell(0, 5, 'No wearable data available.', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Age modifier
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 6, '2c. Age Modifier', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(40, 40, 40)
    if age and age >= 75:
        pdf.cell(0, 5, f'Age {age}: 20% severity increase applied (elderly patients have reduced drug clearance)', new_x="LMARGIN", new_y="NEXT")
    elif age and age >= 65:
        pdf.cell(0, 5, f'Age {age}: 10% severity increase applied (older adults show increased sensitivity)', new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 5, f'Age {age or "N/A"}: No age modifier applied', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Section 3: Drug profiles
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '3. Drug Side-Effect Profiles', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', 'I', 7.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, 'Base severity weights for each drug (0-1 scale, higher = more likely/severe)', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    from data_loader import DRUG_SIDE_EFFECT_PROFILES
    for drug in drugs:
        profile = DRUG_SIDE_EFFECT_PROFILES.get(drug, {})
        if not profile:
            continue

        pdf.set_font('Helvetica', 'B', 9)
        pdf.set_text_color(15, 52, 96)
        pdf.cell(0, 6, f'{drug.title()} -- Known Side Effect Affinities', new_x="LMARGIN", new_y="NEXT")

        sorted_effects = sorted(profile.items(), key=lambda x: -x[1])
        cw_name, cw_bar, cw_val = 45, 90, 15
        rh = 5.5

        pdf.set_font('Helvetica', '', 7)
        for se_name, weight in sorted_effects:
            pdf.set_text_color(40, 40, 40)
            pdf.cell(cw_name, rh, se_name, border=0)
            # Draw bar
            x = pdf.get_x()
            y = pdf.get_y()
            bar_w = cw_bar * weight
            if weight >= 0.7: bc = (180, 30, 30)
            elif weight >= 0.4: bc = (200, 100, 0)
            elif weight >= 0.2: bc = (160, 140, 0)
            else: bc = (60, 120, 60)
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(x, y + 1, cw_bar, rh - 2, 'F')
            pdf.set_fill_color(*bc)
            pdf.rect(x, y + 1, bar_w, rh - 2, 'F')
            pdf.set_xy(x + cw_bar + 2, y)
            pdf.cell(cw_val, rh, f'{weight:.0%}')
            pdf.ln()
        pdf.ln(3)

    # Section 4: Temporal Model
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '4. Temporal Severity Model', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 4.5, 'Side-effect severity follows a temporal curve across the 7-day chemo cycle. '
                   'Day 1 (infusion) starts mild, severity peaks at Days 3-5 (nadir period when blood counts are lowest), '
                   'then eases on Days 6-7 (recovery). This pattern is well-established in oncology literature.')
    pdf.ln(2)

    temporal = [0.4, 0.7, 1.0, 1.0, 0.9, 0.6, 0.4]
    cw_day, cw_mult, cw_phase = 20, 25, 40
    rh = 6
    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(cw_day, rh, 'Day', border=1, fill=True, align='C')
    pdf.cell(cw_mult, rh, 'Multiplier', border=1, fill=True, align='C')
    pdf.cell(cw_phase, rh, 'Phase', border=1, fill=True, align='C')
    pdf.ln()

    phases = ['Infusion', 'Onset', 'Nadir (Peak)', 'Nadir (Peak)', 'Late Nadir', 'Recovery', 'Recovery']
    pdf.set_font('Helvetica', '', 7)
    for i, (mult, phase) in enumerate(zip(temporal, phases)):
        intensity = int(255 * (1 - mult * 0.7))
        pdf.set_fill_color(255, intensity, intensity)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(cw_day, rh, f'Day {i+1}', border=1, fill=True, align='C')
        pdf.cell(cw_mult, rh, f'{mult:.1f}x', border=1, fill=True, align='C')
        pdf.cell(cw_phase, rh, phase, border=1, fill=True)
        pdf.ln()
    pdf.ln(3)

    # Section 5: Per-Side-Effect Reasoning
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '5. Per-Side-Effect Severity Reasoning', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, 'Final Grade = Drug Base x Clinical Modifier x Temporal Curve x Cycle Factor + Random Noise', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    for se in CHEMO_SIDE_EFFECTS:
        n = se['name']
        if cycle_data and n in cycle_data:
            grades = cycle_data[n]
            max_g = max(grades)

            if pdf.get_y() > 260:
                pdf.add_page()

            pdf.set_font('Helvetica', 'B', 8.5)
            pdf.set_text_color(15, 52, 96)
            pdf.cell(50, 5, n)

            # Mini grade display
            pdf.set_font('Helvetica', '', 7)
            for g in grades:
                r, gc, b = GRADE_COLORS[g]
                pdf.set_fill_color(r, gc, b)
                tr, tg, tb = GRADE_TEXT_COLORS[g]
                pdf.set_text_color(tr, tg, tb)
                pdf.cell(12, 5, GRADE_LABELS[g][:4], border=1, fill=True, align='C')
            pdf.ln()

            # Reasoning text
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(60, 60, 60)
            reasons = []
            from data_loader import DRUG_SIDE_EFFECT_PROFILES
            for d in drugs:
                w = DRUG_SIDE_EFFECT_PROFILES.get(d, {}).get(n, 0)
                if w > 0:
                    reasons.append(f"{d.title()} base affinity: {w:.0%}")
            if wbc and wbc < 4.5 and n in ('Fever', 'Fatigue'):
                reasons.append(f"Low WBC ({wbc:.1f}) amplifies this effect")
            if hgb and hgb < 12 and n in ('Fatigue', 'Shortness of Breath', 'Loss of Appetite'):
                reasons.append(f"Low hemoglobin ({hgb:.1f}) amplifies this effect")
            if rmssd and rmssd < 30 and n in ('Fatigue', 'Anxiety / Depression', 'Shortness of Breath'):
                reasons.append(f"Low HRV ({rmssd:.1f}ms) indicates autonomic stress")
            if sleep_eff and sleep_eff < 0.85 and n in ('Fatigue', 'Anxiety / Depression'):
                reasons.append(f"Poor sleep efficiency ({sleep_eff:.0%}) worsens this")

            pdf.cell(50, 4, '')  # indent
            pdf.cell(0, 4, '  |  '.join(reasons) if reasons else 'Low base affinity, no clinical amplifiers', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

    # Section 6: Methodology note
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 8, '6. Methodology & Data Sources', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(40, 40, 40)
    methodology = [
        'SEVERITY CALCULATION: Final severity = Drug_Base_Weight x Clinical_Modifier x Temporal_Curve x Cycle_Factor + Gaussian_Noise(0, 0.08)',
        'DRUG PROFILES: Based on published chemotherapy side-effect incidence rates from oncology literature.',
        'CLINICAL MODIFIERS: Lab values (WBC, Hemoglobin, GFR, Pain) adjust severity multipliers based on clinical thresholds.',
        'WEARABLE DATA: HRV (RMSSD) and sleep efficiency provide real-time physiological stress indicators.',
        'TEMPORAL MODEL: 7-day cycle follows established nadir pattern (peak toxicity Days 3-5 post-infusion).',
        'CYCLE FACTOR: Later cycles accumulate toxicity at +2% per cycle (capped at 40% increase).',
        'GRADING: Continuous 0-1 score mapped to 4 grades: None (<0.20), Mild (0.20-0.44), Moderate (0.45-0.69), Severe (>=0.70).',
        'DATA SOURCES: Synthea synthetic patient data (demographics, conditions, medications, observations, encounters) + generated wearable biometrics.',
    ]
    for m in methodology:
        pdf.multi_cell(0, 4.5, f'-- {m}')
        pdf.ln(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
