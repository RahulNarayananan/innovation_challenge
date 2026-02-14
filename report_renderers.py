"""
PDF renderers for all 6 report templates.
Each renderer takes patient data and produces a filled PDF worksheet.
"""
import os
import numpy as np
import pandas as pd
from fpdf import FPDF
from report_utils import clean_name, sanitize_text

# ============================================================================
# BASE PDF CLASS
# ============================================================================

class BasePDF(FPDF):
    """Base PDF with sanitization and standard header/footer."""
    def __init__(self, patient_name, title, orientation='L'):
        super().__init__(orientation=orientation, format='A4')
        self.patient_name = patient_name
        self.report_title = title

    def normalize_text(self, text):
        return super().normalize_text(sanitize_text(text))

    def header(self):
        if self.page_no() > 0:
            self.set_font('Helvetica', 'B', 9)
            self.set_text_color(26, 26, 46)
            self.cell(0, 5, f'{self.report_title}  |  {self.patient_name}', align='L')
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
        self.cell(0, 5, 'Generated from clinical data. Modeled on ACS reporting templates.', align='C')

    def add_patient_box(self, info, extra_fields=None):
        """Add a standard patient info box."""
        first = clean_name(info['FIRST'])
        last = clean_name(info['LAST'])
        age = None
        try:
            birth = pd.to_datetime(info['BIRTHDATE'])
            age = int((pd.Timestamp.now() - birth).days / 365.25)
        except Exception:
            pass

        self.set_fill_color(245, 245, 250)
        self.set_draw_color(200, 200, 210)
        box_y = self.get_y()
        self.rect(self.l_margin, box_y, self.w - self.l_margin - self.r_margin, 22, 'DF')

        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(15, 52, 96)
        col1 = self.l_margin + 5
        col2 = self.l_margin + 140

        self.set_xy(col1, box_y + 3)
        self.cell(130, 5, f"Patient: {first} {last}")
        self.set_xy(col2, box_y + 3)
        self.cell(100, 5, f"DOB: {info['BIRTHDATE']}   Age: {age or 'N/A'}")

        self.set_font('Helvetica', '', 8)
        self.set_text_color(40, 40, 40)
        self.set_xy(col1, box_y + 9)
        self.cell(130, 5, f"Cancer Type: {info.get('cancer_type', 'N/A')}   Gender: {info.get('GENDER', 'N/A')}")
        self.set_xy(col2, box_y + 9)
        if extra_fields:
            self.cell(100, 5, extra_fields)

        self.set_xy(col1, box_y + 15)
        self.cell(130, 5, f"Location: {info.get('CITY', 'N/A')}, {info.get('STATE', 'N/A')}")

        self.set_y(box_y + 26)


# ============================================================================
# GRADE CONSTANTS
# ============================================================================

GRADE_LABELS = ['None', 'Mild', 'Moderate', 'Severe']
GRADE_COLORS = [(220,237,220), (255,248,220), (255,230,200), (255,210,210)]
GRADE_TEXT_COLORS = [(60,120,60), (160,140,0), (200,100,0), (180,30,30)]

CHEMO_SIDE_EFFECTS = [
    {'name': 'Fever', 'levels': ['None -- Temp 98.6 F', 'Mild -- 98.7-100.4 F', 'Moderate -- 100.5-104 F', 'Severe -- >104 F'],
     'has_measurement': True, 'measurement_label': 'Max Temp', 'measurement_unit': 'F'},
    {'name': 'Fatigue', 'levels': ['None', 'Mild -- Relieved by rest', 'Moderate -- Not relieved by rest', 'Severe -- Unable to care for self']},
    {'name': 'Nausea & Vomiting', 'levels': ['None', 'Mild -- Can eat', 'Moderate -- Eating less', 'Severe -- Cannot eat or drink']},
    {'name': 'Sore Mouth', 'levels': ['None', 'Mild -- Soreness', 'Moderate -- Painful, can eat', 'Severe -- Trouble eating']},
    {'name': 'Diarrhea', 'levels': ['None', 'Mild -- 1-3 extra stools', 'Moderate -- 4-6 extra', 'Severe -- 7+ extra'],
     'has_measurement': True, 'measurement_label': '# BMs', 'measurement_unit': ''},
    {'name': 'Constipation', 'levels': ['None', 'Mild -- Occasional softeners', 'Moderate -- Daily laxatives', 'Severe -- Unable to move bowels']},
    {'name': 'Loss of Appetite', 'levels': ['None', 'Mild -- Eating well', 'Moderate -- Eating less', 'Severe -- Significant weight loss']},
    {'name': 'Swallowing Difficulty', 'levels': ['None', 'Mild -- Can eat solids', 'Moderate -- Trouble with solids', 'Severe -- Cannot eat solids']},
    {'name': 'Anxiety / Depression', 'levels': ['None', 'Mild -- Normal activities', 'Moderate -- Interferes with activities', 'Severe -- Interferes with self-care']},
    {'name': 'Edema (Hands/Feet)', 'levels': ['None', 'Mild -- Visible swelling', 'Moderate -- Interferes with activities', 'Severe -- Interferes with self-care']},
    {'name': 'Itching / Rash', 'levels': ['None', 'Mild -- Small area', 'Moderate -- Up to 1/3 body', 'Severe -- Over 1/3 body']},
    {'name': 'Shortness of Breath', 'levels': ['None', 'Mild -- Moderate activity', 'Moderate -- Minimal activity', 'Severe -- At rest']},
    {'name': 'Muscle / Joint Pain', 'levels': ['None', 'Mild -- Sore', 'Moderate -- Limits activities', 'Severe -- Interferes with self-care']},
    {'name': 'Numbness / Tingling', 'levels': ['None', 'Mild -- Slight tingling', 'Moderate -- Interferes with activities', 'Severe -- Pain, trouble walking']},
]


# ============================================================================
# SIDE EFFECT MODEL
# ============================================================================

class SideEffectModel:
    TEMPORAL_CURVE = [0.4, 0.7, 1.0, 1.0, 0.9, 0.6, 0.4]

    def __init__(self, seed=42):
        self.rng = np.random.default_rng(seed)

    def compute_base_severity(self, drugs):
        from data_loader import DRUG_SIDE_EFFECT_PROFILES
        base = {}
        for se in CHEMO_SIDE_EFFECTS:
            name = se['name']
            mx = 0.0
            for drug in drugs:
                profile = DRUG_SIDE_EFFECT_PROFILES.get(drug, {})
                mx = max(mx, profile.get(name, 0.05))
            base[name] = mx
        return base

    def compute_clinical_modifier(self, labs, wearable, age):
        mods = {se['name']: 1.0 for se in CHEMO_SIDE_EFFECTS}
        wbc = labs.get('wbc')
        if wbc is not None:
            if wbc < 3.0: mods['Fever'] *= 1.5; mods['Fatigue'] *= 1.3
            elif wbc < 4.5: mods['Fever'] *= 1.2; mods['Fatigue'] *= 1.1
        hgb = labs.get('hemoglobin')
        if hgb is not None:
            if hgb < 10: mods['Fatigue'] *= 1.5; mods['Shortness of Breath'] *= 1.4; mods['Loss of Appetite'] *= 1.2
            elif hgb < 12: mods['Fatigue'] *= 1.2; mods['Shortness of Breath'] *= 1.1
        pain = labs.get('pain_score')
        if pain is not None:
            if pain >= 7: mods['Anxiety / Depression'] *= 1.4; mods['Muscle / Joint Pain'] *= 1.3
            elif pain >= 4: mods['Anxiety / Depression'] *= 1.2
        gfr = labs.get('gfr')
        if gfr is not None:
            if gfr < 15: mods['Nausea & Vomiting'] *= 1.5; mods['Fatigue'] *= 1.4
            elif gfr < 30: mods['Nausea & Vomiting'] *= 1.3; mods['Fatigue'] *= 1.2
        rmssd = wearable.get('rmssd_mean')
        if rmssd is not None:
            if rmssd < 20: mods['Fatigue'] *= 1.3; mods['Anxiety / Depression'] *= 1.3
            elif rmssd < 30: mods['Fatigue'] *= 1.1; mods['Anxiety / Depression'] *= 1.1
        sleep_eff = wearable.get('sleep_eff_mean')
        if sleep_eff is not None:
            if sleep_eff < 0.75: mods['Fatigue'] *= 1.3; mods['Anxiety / Depression'] *= 1.3
            elif sleep_eff < 0.85: mods['Fatigue'] *= 1.1
        if age is not None:
            if age >= 75:
                for k in mods: mods[k] *= 1.2
            elif age >= 65:
                for k in mods: mods[k] *= 1.1
        return mods

    def severity_to_grade(self, s):
        if s < 0.20: return 0
        elif s < 0.45: return 1
        elif s < 0.70: return 2
        else: return 3

    def generate_cycle(self, drugs, labs, wearable, age, cycle_number=1):
        base = self.compute_base_severity(drugs)
        mods = self.compute_clinical_modifier(labs, wearable, age)
        cycle_factor = min(1.0 + (cycle_number - 1) * 0.02, 1.4)
        result = {}
        for se in CHEMO_SIDE_EFFECTS:
            name = se['name']
            daily = []
            for day in range(7):
                raw = base[name] * mods[name] * self.TEMPORAL_CURVE[day] * cycle_factor
                raw = max(0.0, min(1.0, raw + self.rng.normal(0, 0.08)))
                daily.append(self.severity_to_grade(raw))
            result[name] = daily
        return result

    def generate_measurement(self, name, grade):
        if name == 'Fever':
            ranges = [(97.5,98.6),(98.7,100.4),(100.5,103.0),(104.0,105.5)]
            lo, hi = ranges[grade]
            return f"{self.rng.uniform(lo, hi):.1f}"
        elif name == 'Diarrhea':
            ranges = [(1,4),(3,6),(6,9),(9,14)]
            lo, hi = ranges[grade]
            return str(int(self.rng.integers(lo, hi)))
        return ''


# ============================================================================
# 1. CHEMO WORKSHEET RENDERER
# ============================================================================

def render_chemo_worksheet(pdf_class, model, info, drugs, labs, wearable, output_path, cycle_num, cycle_start):
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    name = f"{first} {last}"
    age = None
    try:
        birth = pd.to_datetime(info['BIRTHDATE'])
        age = int((pd.Timestamp.now() - birth).days / 365.25)
    except: pass

    cycle_data = model.generate_cycle(drugs, labs, wearable, age, cycle_num)
    start = pd.to_datetime(cycle_start) if cycle_start else pd.Timestamp.now()
    dates = [(start + pd.Timedelta(days=i)).strftime('%m/%d/%y') for i in range(7)]

    pdf = pdf_class(name, 'Chemotherapy Side Effects Worksheet')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Cover + heatmap
    pdf.add_page()
    pdf.add_patient_box(info, f"Cycle #{cycle_num}  |  Meds: {', '.join(d.title() for d in drugs)}")

    # Instructions
    pdf.set_font('Helvetica', 'I', 7)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 3.5, 'Severity grades derived from drug profiles, lab results, and wearable biometrics. '
                   'Green=None, Yellow=Mild, Orange=Moderate, Red=Severe.')
    pdf.ln(3)

    # Heatmap
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 6, f'Cycle Overview -- {dates[0]} to {dates[6]}', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    nw, dw, rh = 42, 24, 5
    pdf.set_font('Helvetica', 'B', 6.5)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(nw, rh, 'Side Effect', border=1, fill=True, align='C')
    for d in dates:
        pdf.cell(dw, rh, d, border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font('Helvetica', '', 6.5)
    for se in CHEMO_SIDE_EFFECTS:
        n = se['name']
        grades = cycle_data[n]
        pdf.set_fill_color(245, 245, 250)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(nw, rh, n, border=1, fill=True, align='L')
        for g in grades:
            r, gc, b = GRADE_COLORS[g]
            pdf.set_fill_color(r, gc, b)
            tr, tg, tb = GRADE_TEXT_COLORS[g]
            pdf.set_text_color(tr, tg, tb)
            pdf.cell(dw, rh, GRADE_LABELS[g], border=1, fill=True, align='C')
        pdf.ln()

    # Pages 2-5: Detailed grids
    groups = [CHEMO_SIDE_EFFECTS[0:4], CHEMO_SIDE_EFFECTS[4:8], CHEMO_SIDE_EFFECTS[8:12], CHEMO_SIDE_EFFECTS[12:14]]
    for group in groups:
        pdf.add_page()
        for se in group:
            n = se['name']
            grades = cycle_data[n]
            if pdf.get_y() > 155:
                pdf.add_page()
            pdf.set_font('Helvetica', 'B', 9)
            pdf.set_text_color(15, 52, 96)
            pdf.cell(0, 6, n, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('Helvetica', '', 7)
            pdf.set_text_color(100, 100, 100)
            for lv in se['levels']:
                pdf.cell(0, 3.5, f"  {lv}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

            lw, dw2, rh2 = 42, 31, 7
            pdf.set_font('Helvetica', 'B', 7)
            pdf.set_fill_color(26, 26, 46)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(lw, rh2, '', border=1, fill=True)
            for i, d in enumerate(dates):
                pdf.cell(dw2, rh2, f"Day {i+1} ({d})", border=1, fill=True, align='C')
            pdf.ln()

            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_fill_color(245, 245, 250)
            pdf.set_text_color(40, 40, 40)
            pdf.cell(lw, rh2, 'Severity', border=1, fill=True, align='C')
            for g in grades:
                r, gc, b = GRADE_COLORS[g]
                pdf.set_fill_color(r, gc, b)
                tr, tg, tb = GRADE_TEXT_COLORS[g]
                pdf.set_text_color(tr, tg, tb)
                pdf.cell(dw2, rh2, f"[X] {GRADE_LABELS[g]}", border=1, fill=True, align='C')
            pdf.ln()

            if se.get('has_measurement'):
                pdf.set_font('Helvetica', '', 7)
                pdf.set_fill_color(250, 250, 255)
                pdf.set_text_color(40, 40, 40)
                pdf.cell(lw, rh2, se['measurement_label'], border=1, fill=True, align='C')
                for g in grades:
                    val = model.generate_measurement(n, g)
                    u = se.get('measurement_unit', '')
                    pdf.cell(dw2, rh2, f"{val} {u}".strip(), border=1, fill=True, align='C')
                pdf.ln()
            pdf.ln(3)

    # Last page: Summary
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 7, 'Cycle Summary & Notes', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 5, 'Side Effects Reaching Moderate or Severe:', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 8)
    pdf.set_text_color(40, 40, 40)
    flagged = []
    for se in CHEMO_SIDE_EFFECTS:
        n = se['name']
        grades = cycle_data[n]
        mx = max(grades)
        if mx >= 2:
            days = [i+1 for i, g in enumerate(grades) if g == mx]
            flagged.append((n, GRADE_LABELS[mx], days))
    if flagged:
        for n, sev, days in flagged:
            ds = ', '.join(f"Day {d}" for d in days)
            mk = '!!' if sev == 'Severe' else '!'
            pdf.cell(0, 4.5, f"  {mk} {n}: {sev} on {ds}", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 4.5, '  No side effects reached Moderate or Severe.', new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 5, 'Questions for Cancer Care Team:', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 7.5)
    pdf.set_text_color(80, 80, 80)
    for q in ['Which side effects should I notify you about right away?',
              'What can I do for the side effects I have?',
              'Who should I contact after hours or on weekends/holidays?']:
        pdf.cell(0, 4.5, f'- {q}', new_x="LMARGIN", new_y="NEXT")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    return cycle_data


# ============================================================================
# 2. MEDICINE LIST RENDERER
# ============================================================================

def render_medicine_list(pdf_class, info, meds_detail, output_path):
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    pdf = pdf_class(f"{first} {last}", 'My Medicines')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_patient_box(info)

    if not meds_detail:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 8, 'No medications recorded.', new_x="LMARGIN", new_y="NEXT")
        pdf.output(output_path)
        return

    cols = [('Medicine', 70), ('Reason', 65), ('Period', 40), ('Cycles', 18), ('Notes', 70)]
    rh = 6

    pdf.set_font('Helvetica', 'B', 7.5)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    for name, w in cols:
        pdf.cell(w, rh, name, border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font('Helvetica', '', 7)
    for i, m in enumerate(meds_detail):
        bg = (245,245,250) if i % 2 == 0 else (255,255,255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(cols[0][1], rh, m['name'][:45], border=1, fill=True)
        pdf.cell(cols[1][1], rh, m['reason'][:40], border=1, fill=True)
        pdf.cell(cols[2][1], rh, f"{m['start']} - {m['end']}", border=1, fill=True, align='C')
        pdf.cell(cols[3][1], rh, str(m['count']), border=1, fill=True, align='C')
        pdf.cell(cols[4][1], rh, '', border=1, fill=True)
        pdf.ln()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)


# ============================================================================
# 3. TEST RESULTS RENDERER
# ============================================================================

def render_test_results(pdf_class, info, lab_history, output_path):
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    pdf = pdf_class(f"{first} {last}", 'My Lab Results')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_patient_box(info)

    if not lab_history:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 8, 'No lab results recorded.', new_x="LMARGIN", new_y="NEXT")
        pdf.output(output_path)
        return

    max_dates = max(len(t['date_vals']) for t in lab_history)
    cw_test, cw_ref, cw_date, cw_note = 50, 38, 30, 55
    rh = 7

    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(cw_test, rh, 'Test', border=1, fill=True, align='C')
    pdf.cell(cw_ref, rh, 'Reference Range', border=1, fill=True, align='C')
    # Use dates from first test that has max dates
    ref_test = [t for t in lab_history if len(t['date_vals']) == max_dates][0]
    for dv in ref_test['date_vals']:
        pdf.cell(cw_date, rh, dv[0], border=1, fill=True, align='C')
    pdf.cell(cw_note, rh, 'Notes', border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font('Helvetica', '', 7)
    for i, t in enumerate(lab_history):
        bg = (245,245,250) if i % 2 == 0 else (255,255,255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(cw_test, rh, t['name'], border=1, fill=True)
        pdf.cell(cw_ref, rh, t['ref_range'], border=1, fill=True, align='C')
        for j in range(max_dates):
            if j < len(t['date_vals']):
                pdf.cell(cw_date, rh, t['date_vals'][j][1], border=1, fill=True, align='C')
            else:
                pdf.cell(cw_date, rh, '--', border=1, fill=True, align='C')
        pdf.cell(cw_note, rh, t['note'], border=1, fill=True)
        pdf.ln()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)


# ============================================================================
# 4. PAIN DIARY RENDERER
# ============================================================================

def render_pain_diary(pdf_class, model, info, pain_obs, wearable, output_path):
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    pdf = pdf_class(f"{first} {last}", 'Daily Pain Diary')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_patient_box(info)

    # Pain scale reference
    pdf.set_font('Helvetica', 'B', 8)
    pdf.set_text_color(15, 52, 96)
    pdf.cell(0, 5, 'Pain Rating Scale (0-10)', new_x="LMARGIN", new_y="NEXT")
    scale = [('0-1','No pain',(220,237,220)), ('2-3','Mild',(255,248,220)),
             ('4-5','Moderate',(255,230,200)), ('6-7','Distressing',(255,210,210)),
             ('8-9','Severe',(255,190,190)), ('10','Worst',(255,170,170))]
    pdf.set_font('Helvetica', '', 7)
    for val, label, color in scale:
        pdf.set_fill_color(*color)
        pdf.cell(18, 4.5, val, border=1, fill=True, align='C')
        pdf.set_fill_color(255,255,255)
        pdf.cell(25, 4.5, label, border=1, fill=True)
    pdf.ln(6)

    if not pain_obs:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 8, 'No pain observations recorded.', new_x="LMARGIN", new_y="NEXT")
        pdf.output(output_path)
        return

    # Diary table
    cols = [('Date', 25), ('Pain Score', 20), ('Location & Type', 55), ('Activity', 40),
            ('Medicine Taken', 50), ('Score After', 20), ('Duration', 20), ('Notes', 30)]
    rh = 7

    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    for name, w in cols:
        pdf.cell(w, rh, name, border=1, fill=True, align='C')
    pdf.ln()

    rng = model.rng
    locations = ['Lower back', 'Chest area', 'Abdomen', 'Joint pain', 'Head/neck', 'Surgical site']
    types = ['Dull ache', 'Sharp', 'Throbbing', 'Burning', 'Steady']
    activities = ['Resting', 'Walking', 'Sitting', 'After treatment', 'Morning routine']

    pdf.set_font('Helvetica', '', 7)
    for i, obs in enumerate(pain_obs):
        bg = (245,245,250) if i % 2 == 0 else (255,255,255)
        pdf.set_fill_color(*bg)
        score = obs['score']
        if score <= 1: sc = GRADE_COLORS[0]
        elif score <= 3: sc = GRADE_COLORS[1]
        elif score <= 5: sc = GRADE_COLORS[2]
        else: sc = GRADE_COLORS[3]

        pdf.set_text_color(40, 40, 40)
        pdf.cell(cols[0][1], rh, obs['date'], border=1, fill=True, align='C')
        pdf.set_fill_color(*sc)
        pdf.cell(cols[1][1], rh, f"{score:.0f}", border=1, fill=True, align='C')
        pdf.set_fill_color(*bg)
        loc = rng.choice(locations)
        typ = rng.choice(types)
        pdf.cell(cols[2][1], rh, f"{loc} - {typ}", border=1, fill=True)
        pdf.cell(cols[3][1], rh, rng.choice(activities), border=1, fill=True)
        pdf.cell(cols[4][1], rh, 'As prescribed' if score > 3 else '--', border=1, fill=True)
        post = max(0, score - rng.integers(1, 4)) if score > 3 else score
        pdf.cell(cols[5][1], rh, f"{post:.0f}", border=1, fill=True, align='C')
        dur = f"{rng.integers(1, 5)}h" if score > 3 else '<1h'
        pdf.cell(cols[6][1], rh, dur, border=1, fill=True, align='C')
        pdf.cell(cols[7][1], rh, '', border=1, fill=True)
        pdf.ln()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)


# ============================================================================
# 5. APPOINTMENTS RENDERER
# ============================================================================

def render_appointments(pdf_class, info, encounters, output_path):
    first = clean_name(info['FIRST'])
    last = clean_name(info['LAST'])
    pdf = pdf_class(f"{first} {last}", 'My Appointments and Questions')
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_patient_box(info)

    if not encounters:
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 8, 'No encounters recorded.', new_x="LMARGIN", new_y="NEXT")
        pdf.output(output_path)
        return

    cols = [('Date', 25), ('Time', 15), ('Type', 25), ('Description', 80), ('Reason/Notes', 80)]
    rh = 6

    pdf.set_font('Helvetica', 'B', 7)
    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    for name, w in cols:
        pdf.cell(w, rh, name, border=1, fill=True, align='C')
    pdf.ln()

    pdf.set_font('Helvetica', '', 6.5)
    # Show last 30 encounters
    recent = encounters[-30:] if len(encounters) > 30 else encounters
    for i, e in enumerate(recent):
        bg = (245,245,250) if i % 2 == 0 else (255,255,255)
        pdf.set_fill_color(*bg)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(cols[0][1], rh, e['date'], border=1, fill=True, align='C')
        pdf.cell(cols[1][1], rh, e['time'], border=1, fill=True, align='C')
        pdf.cell(cols[2][1], rh, e['class'][:15], border=1, fill=True)
        pdf.cell(cols[3][1], rh, e['description'][:55], border=1, fill=True)
        pdf.cell(cols[4][1], rh, e['reason'][:55], border=1, fill=True)
        pdf.ln()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
