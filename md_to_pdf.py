from fpdf import FPDF
import re

def s(text):
    """Sanitize text to ASCII-compatible for fpdf core fonts."""
    return (text
        .replace('\u2014', '--')   # em-dash
        .replace('\u2013', '-')    # en-dash
        .replace('\u2018', "'")    # left single quote
        .replace('\u2019', "'")    # right single quote
        .replace('\u201c', '"')    # left double quote
        .replace('\u201d', '"')    # right double quote
        .replace('\u2026', '...')  # ellipsis
        .replace('\u00b3', '3')    # superscript 3
        .replace('\u00b6', '6')    # pilcrow
        .replace('\u2192', '->')   # right arrow
    )

class PatientProfilePDF(FPDF):
    def normalize_text(self, text):
        return super().normalize_text(s(text))

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 5, 'Cancer Recovery Monitoring Program — Patient Profiles', align='R')
            self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(26, 26, 46)
        self.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.8)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(15, 52, 96)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font('Helvetica', '', 9.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def italic_text(self, text):
        self.set_font('Helvetica', 'I', 9.5)
        self.set_text_color(80, 80, 80)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def add_table(self, headers, data, col_widths=None):
        if col_widths is None:
            col_widths = [(self.w - self.l_margin - self.r_margin) / len(headers)] * len(headers)
        
        # Header
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(26, 26, 46)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
        self.ln()
        
        # Data
        self.set_font('Helvetica', '', 8)
        self.set_text_color(40, 40, 40)
        for row_idx, row in enumerate(data):
            fill = row_idx % 2 == 1
            if fill:
                self.set_fill_color(245, 245, 245)
            h = 6
            for i, cell in enumerate(row):
                self.cell(col_widths[i], h, str(cell), border=1, fill=fill, align='L')
            self.ln()
        self.ln(3)

    def add_separator(self):
        self.set_draw_color(233, 69, 96)
        self.set_line_width(0.5)
        y = self.get_y() + 3
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(8)


pdf = PatientProfilePDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# ===== COVER PAGE =====
pdf.ln(40)
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(26, 26, 46)
pdf.cell(0, 15, 'Patient Profiles', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('Helvetica', '', 16)
pdf.set_text_color(233, 69, 96)
pdf.cell(0, 10, 'Cancer Recovery Monitoring Program', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(10)
pdf.set_font('Helvetica', 'I', 11)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 6, '10 comprehensive patient dossiers drawn from synthetic clinical data (Synthea)\nenriched with wearable biometric monitoring (HRV + Sleep).\n\nEach profile includes background, diagnosis, treatment history,\nwearable trends, and clinical narrative assessment.', align='C')
pdf.ln(30)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(120, 120, 120)
pdf.cell(0, 6, 'Data Sources: Synthea Clinical Records + Generated Wearable Biometrics', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, 'Cancer Types: LUNG | BREAST | COLORECTAL', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 6, 'Total Patient Pool: 1,500 patients (500 per cancer type)', align='C', new_x="LMARGIN", new_y="NEXT")

# ===== PATIENT 1 =====
pdf.add_page()
pdf.chapter_title('Patient 1 — Hilton Prosacco')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '497c0923-b34e-0004-095a-54b61544403e'],
        ['Age', '64 (born Nov 12, 1961)'],
        ['Sex', 'Male'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Southbridge, Massachusetts'],
        ['Income', '$35,968/yr'],
        ['Status', 'LIVING — Active treatment'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Hilton is a retired machine-tool operator from central Massachusetts who spent 30 years breathing metal dust and solvent fumes on the factory floor. A lifelong non-complainer, he ignored a nagging cough for months until his wife insisted he see his GP in the spring of 2023. An emergency chest X-ray followed by a CT scan confirmed what nobody wanted to hear. He has two grown sons and four grandchildren; his youngest grandson was born the same week he started chemotherapy. Despite the diagnosis, Hilton tells his oncologist he\'s "not done yet" — he wants to see that grandson start school.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['May 14, 2023', 'Suspected lung cancer flagged after imaging'],
        ['May 26, 2023', 'Confirmed Non-small cell lung cancer (NSCLC) + Anemia'],
        ['May 28, 2023', 'Staged as NSCLC TNM Stage I — curative-intent chemo initiated'],
    ],
    [40, 150]
)

pdf.section_title('Treatment Protocol')
pdf.add_table(
    ['Medication', 'Route', 'Cycles', 'Period'],
    [
        ['Cisplatin 50 mg', 'IV Injection', '179', 'May 2023 – Jan 2026'],
        ['Paclitaxel 100 mg', 'IV Injection', '179', 'May 2023 – Jan 2026'],
        ['Vitamin B12 5 mg/mL', 'IM Injectable', '1', 'May 2023'],
    ],
    [55, 35, 20, 80]
)

pdf.section_title('Latest Lab Panel (Jan 2, 2026)')
pdf.add_table(
    ['Test', 'Value', 'Reference', 'Status'],
    [
        ['Hemoglobin', '15.5 g/dL', '13.5-17.5', 'Normal'],
        ['Hematocrit', '49.3%', '38.3-48.6', 'Slightly high'],
        ['WBC', '2.9 x10^3/uL', '4.5-11.0', 'LOW (leukopenia)'],
        ['RBC', '4.8 x10^6/uL', '4.7-6.1', 'Normal'],
        ['GFR (eGFR)', '23.2 mL/min', '>60', 'SEVERE renal impairment'],
        ['Pain Score', '9 / 10', '—', 'SEVERE'],
    ],
    [45, 40, 35, 70]
)

pdf.section_title('Wearable Biometrics (225-day window)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '22.0', '15.5', '30.0'],
        ['SDNN (ms)', '28.4', '20.0', '40.5'],
        ['Resting HR (bpm)', '71.3', '61.9', '82.1'],
        ['Total Sleep (min)', '369', '271', '450'],
        ['Deep Sleep (min)', '64', '—', '—'],
        ['Sleep Efficiency', '0.797', '0.632', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Hilton is a Stage I NSCLC patient entering his 3rd year of platinum-doublet chemotherapy. While his hemoglobin has stabilized, his severe leukopenia (WBC 2.9) places him at elevated infection risk, and his eGFR of 23.2 indicates cisplatin-induced nephrotoxicity in CKD Stage 4 territory. His pain score of 9/10 is the most acute concern — likely neuropathic pain from cumulative paclitaxel toxicity. Wearable data corroborates his clinical picture: depressed HRV and poor sleep architecture align with chronic treatment burden.')

# ===== PATIENT 2 =====
pdf.add_page()
pdf.chapter_title('Patient 2 — Ignacio Dach')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '65343425-3160-297c-d371-32119d34cfcc'],
        ['Age at Death', '65 (born Nov 20, 1937 — died Nov 26, 2003)'],
        ['Sex', 'Male'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Lynn, Massachusetts'],
        ['Income', '$28,030/yr'],
        ['Status', 'DECEASED'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Ignacio was a quiet Portuguese-American fisherman\'s son who grew up on the North Shore. After serving in the Army during Vietnam, he worked decades in a tannery — a job that gave him a modest living but chronic exposure to industrial chemicals. By his early sixties, the persistent "smoker\'s cough" he attributed to decades of Camels turned out to be something far worse. His wife of 40 years, Dolores, cared for him through three and a half years of treatment before he passed six days after his 66th birthday.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Mar 31, 2000', 'Suspected lung cancer'],
        ['Apr 13, 2000', 'Confirmed NSCLC + Anemia'],
        ['Apr 14, 2000', 'Staged NSCLC TNM Stage I — chemo initiated'],
        ['Nov 26, 2003', 'DEATH (3.5 years post-diagnosis)'],
    ],
    [40, 150]
)

pdf.section_title('Treatment Protocol')
pdf.add_table(
    ['Medication', 'Cycles', 'Period'],
    [
        ['Cisplatin 50 mg IV', '195', 'Apr 2000 – Oct 2003'],
        ['Paclitaxel 100 mg IV', '195', 'Apr 2000 – Oct 2003'],
    ],
    [70, 30, 90]
)

pdf.section_title('Final Lab Panel (Oct 28, 2003)')
pdf.add_table(
    ['Test', 'Value', 'Status'],
    [
        ['Hemoglobin', '16.5 g/dL', 'Normal'],
        ['Hematocrit', '40.6%', 'Normal'],
        ['WBC', '2.6 x10^3/uL', 'Leukopenia'],
        ['GFR', '13.9 mL/min', 'Kidney failure (Stage 5)'],
        ['Pain Score', '9 / 10', 'Severe'],
    ],
    [50, 50, 90]
)

pdf.section_title('Wearable Biometrics (1,096 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '27.6', '17.5', '36.8'],
        ['Resting HR (bpm)', '73.5', '62.1', '85.1'],
        ['Total Sleep (min)', '412', '262', '521'],
        ['Deep Sleep (min)', '79', '—', '—'],
        ['Sleep Efficiency', '0.925', '0.655', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Ignacio\'s case illustrates the long-term toll of platinum-based chemotherapy. Despite maintaining adequate hemoglobin through 195 treatment cycles, his kidneys ultimately failed (eGFR 13.9 at final labs). His 35 inpatient stays paint a picture of escalating medical fragility. Wearable data shows HRV dips correlated with chemo cycles, but sleep architecture remained surprisingly resilient until the final months.')

# ===== PATIENT 3 =====
pdf.add_page()
pdf.chapter_title('Patient 3 — Beatrice Zieme')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', 'c3495c1a-3a6e-edaf-9b91-8aa7ebd0f2c4'],
        ['Age', '48 (born Aug 22, 1977)'],
        ['Sex', 'Female'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Marlborough, Massachusetts'],
        ['Income', '$4,206/yr (very low income)'],
        ['Status', 'LIVING — Active treatment'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Beatrice is the youngest patient in this cohort and the one with the least financial resources. A single working mom who later married her high school boyfriend when their youngest started kindergarten, she held part-time jobs at a daycare center to keep the family afloat. Her diagnosis at 47 was devastating — she was the one in the family everyone depended on. Her husband took FMLA leave to drive her to chemo sessions at UMass Memorial. She worries less about the cancer and more about the medical bills she can see piling up while her coverage barely covers the infusions.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Sep 13, 2024', 'Suspected lung cancer after routine imaging'],
        ['Oct 5, 2024', 'Confirmed NSCLC + Anemia'],
        ['Oct 6, 2024', 'Staged NSCLC TNM Stage I — chemo initiated'],
    ],
    [40, 150]
)

pdf.section_title('Latest Lab Panel (Jan 18, 2026)')
pdf.add_table(
    ['Test', 'Value', 'Status'],
    [
        ['Hemoglobin', '14.4 g/dL', 'Normal'],
        ['WBC', '3.1 x10^3/uL', 'Leukopenia'],
        ['GFR', '8.2 mL/min', 'CRITICAL renal failure'],
        ['Pain Score', '7 / 10', 'High'],
    ],
    [50, 50, 90]
)

pdf.section_title('Wearable Biometrics (234 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '35.2', '18.8', '52.0'],
        ['Total Sleep (min)', '397', '251', '539'],
        ['Sleep Efficiency', '0.743', '0.500', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Despite being the youngest patient and showing the best baseline HRV (mean 35.2 ms), Beatrice\'s GFR of 8.2 mL/min is the most alarming value in the entire cohort — she is in Stage 5 CKD (kidney failure) after only 80 chemo cycles. This suggests heightened cisplatin sensitivity. Her sleep efficiency of 74.3% (dropping to 50% at worst) is the poorest of all female patients. Immediate nephrology consult is warranted.')

# ===== PATIENT 4 =====
pdf.add_page()
pdf.chapter_title('Patient 4 — Song Bednar')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '03611e2a-fa1a-740f-0d37-3477b58b6974'],
        ['Age', '76 (born Aug 4, 1949)'],
        ['Sex', 'Female'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Boston, Massachusetts'],
        ['Income', '$137,757/yr'],
        ['Status', 'LIVING — Post-treatment surveillance'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Song is a retired public librarian from Boston\'s Allston neighborhood who spent 35 years helping immigrant families navigate the American school system. Widowed at 68 when her husband Victor died of heart disease, she poured herself into volunteer work at the Asian Community Development Corporation. When a routine mammogram in 2020 revealed a suspicious mass, she approached it the same way she approached everything — by learning everything she could. Now in post-treatment surveillance, she organizes a support group for cancer survivors at her local church.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Dec 10, 2020', 'Diagnosed with Malignant neoplasm of breast'],
        ['Dec 31, 2020', 'Chemotherapy initiated'],
        ['May 27, 2021', 'Carboplatin course completed (8 cycles)'],
        ['Jun 1, 2021', 'Switched to Fulvestrant (hormonal therapy)'],
    ],
    [40, 150]
)

pdf.section_title('Wearable Biometrics (211 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '18.7', '10.4', '26.5'],
        ['Resting HR (bpm)', '82.4', '72.9', '92.6'],
        ['Total Sleep (min)', '319', '186', '448'],
        ['Deep Sleep (min)', '49', '—', '—'],
        ['Awakenings/night', '2.1', '—', '3'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Song is the oldest breast cancer patient in the cohort with the lowest baseline HRV (RMSSD 18.7 ms) — consistent with her age and reduced cardiovascular reserve. Her resting heart rate of 82.4 bpm is the highest in the cohort. Despite completing treatment, her sleep quality remains poor (only 5.3 hrs avg, 49 min deep sleep) with frequent awakenings (2.1/night). This is a modifiable risk factor for recurrence-related fatigue.')

# ===== PATIENT 5 =====
pdf.add_page()
pdf.chapter_title('Patient 5 — Catrice Schoen')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '0fc698de-9c91-5eac-0eba-d74cb7540c47'],
        ['Age', '53 (born Mar 6, 1972)'],
        ['Sex', 'Female'],
        ['Race / Ethnicity', 'Black, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Worthington, Massachusetts'],
        ['Income', '$68,151/yr'],
        ['Status', 'LIVING — Long-term survivor'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Catrice was just 16 years old when she found a lump in her breast — an almost unheard-of diagnosis for a teenager. Growing up in a close-knit Black family in rural western Massachusetts, she was the star point guard on her high school basketball team. Instead of playing D-II ball, she spent her junior year in treatment. The experience forged an unshakeable resilience: she earned a nursing degree, married her college sweetheart Darnell, and spent her career at Baystate Medical Center. Now 53, she has been cancer-free for over three decades.')

pdf.section_title('Diagnosis')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Mar 31, 1988', 'Diagnosed with Malignant neoplasm of breast at age 16'],
        ['1988 – present', 'Long-term survivor (37 years)'],
    ],
    [40, 150]
)

pdf.section_title('Wearable Biometrics (211 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '16.8', '12.1', '22.0'],
        ['Total Sleep (min)', '438', '330', '552'],
        ['Deep Sleep (min)', '98', '—', '—'],
        ['Sleep Efficiency', '0.797', '0.653', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Catrice presents a unique profile as a 37-year breast cancer survivor diagnosed in adolescence. Her sleep metrics are the best in the entire cohort — 7.3 hrs average with 98 min deep sleep, reflecting excellent recovery and overall health. She represents the gold standard of what a cancer survivor monitoring program hopes to see.')

# ===== PATIENT 6 =====
pdf.add_page()
pdf.chapter_title('Patient 6 — See Wuckert')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '44466ba7-b0ca-c6bb-ac02-58cfc05398ac'],
        ['Age at Death', '54 (born Jan 29, 1970 — died Feb 4, 2024)'],
        ['Sex', 'Female'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Divorced'],
        ['Residence', 'West Falmouth, MA (Cape Cod)'],
        ['Income', '$113,505/yr'],
        ['Status', 'DECEASED'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('See was a marine biologist at the Woods Hole Oceanographic Institution who specialized in coastal ecosystem health. Divorced with one daughter, she threw herself into research after the split. When she found the lump, she delayed telling anyone for weeks. She fought through paclitaxel, doxorubicin, tamoxifen, and Verzenio — the full arsenal — but the disease progressed. She died on a cold February morning in 2024, five years after diagnosis. Her colleagues named a newly discovered species of sea sponge after her.')

pdf.section_title('Treatment Protocol')
pdf.add_table(
    ['Medication', 'Cycles', 'Period'],
    [
        ['Paclitaxel 100 mg IV', '8', 'Mar – Aug 2019'],
        ['Doxorubicin 20 mg IV', '8', 'Sep 2019 – Feb 2020'],
        ['Tamoxifen 10 mg Oral', '1', 'Mar 2020'],
        ['Abemaciclib (Verzenio) 100 mg', '1', 'Mar 2020'],
    ],
    [70, 30, 90]
)

pdf.section_title('Wearable Biometrics (1,096 days — full disease course)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '34.1', '17.3', '49.6'],
        ['Resting HR (bpm)', '72.0', '61.7', '85.9'],
        ['Total Sleep (min)', '412', '239', '538'],
        ['Sleep Efficiency', '0.915', '0.557', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('See\'s wearable data spans her entire disease trajectory — a rare 1,096-day window from diagnosis to death. Her HRV shows a classic "treatment valley" pattern: RMSSD dropping to 17.3 ms during active chemo, partially recovering during hormonal therapy, then gradually declining in her final year. Her case is a textbook example of how wearable data can track disease progression longitudinally.')

# ===== PATIENT 7 =====
pdf.add_page()
pdf.chapter_title('Patient 7 — Brandon Sanford')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', '19b781ac-82c4-6a42-495b-b59d4c4811d3'],
        ['Age', '82 (born May 19, 1943)'],
        ['Sex', 'Male'],
        ['Race / Ethnicity', 'White, Hispanic'],
        ['Marital Status', 'Single (never married)'],
        ['Residence', 'Northborough, Massachusetts'],
        ['Income', '$906,274/yr'],
        ['Status', 'LIVING — In remission'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Brandon is a Cuban-American entrepreneur who built a small chain of auto body shops into a multi-million dollar operation. A lifelong bachelor "married to the business," he hired his nieces and nephews to run the shops. When a routine colonoscopy found a polyp, he brushed it off. When the polyp came back malignant, he couldn\'t. He achieved remission by 2017 without chemotherapy, and at 82 still drives a 1967 Mustang to his flagship shop every Saturday.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['May 25, 2013', 'Polyp of colon discovered'],
        ['Oct 29, 2014', 'Recurrent rectal polyp'],
        ['Nov 3, 2014', 'Malignant neoplasm of colon diagnosed'],
        ['Feb 12, 2017', 'Cancer resolved — in remission'],
    ],
    [40, 150]
)

pdf.section_title('Wearable Biometrics (738 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '27.3', '12.4', '37.0'],
        ['Resting HR (bpm)', '76.2', '64.8', '89.2'],
        ['Total Sleep (min)', '379', '190', '476'],
        ['Sleep Efficiency', '0.860', '0.500', '—'],
        ['Awakenings/night', '2.0', '—', '3'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Brandon\'s profile is a success story. Diagnosed with colorectal cancer that progressed from benign polyps to malignancy over 18 months, he achieved remission through surgery alone. His wearable data shows RMSSD dropping to 12.4 ms around active cancer (late 2014 – early 2015), with sleep hitting a nadir of 3.2 hrs. Post-remission, metrics gradually improved. At 82, he is the oldest living patient in the cohort.')

# ===== PATIENT 8 =====
pdf.add_page()
pdf.chapter_title('Patient 8 — Merlin Graham')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', 'dfeb81a1-9050-2bd6-07d1-5c294c7dec16'],
        ['Age', '69 (born Apr 25, 1956)'],
        ['Sex', 'Male'],
        ['Race / Ethnicity', 'Asian, Non-Hispanic'],
        ['Marital Status', 'Single'],
        ['Residence', 'Groton, Massachusetts'],
        ['Income', '$80,413/yr'],
        ['Status', 'LIVING — In remission'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Merlin is a second-generation Chinese-American who grew up in Lowell\'s Cambodian quarter. A quiet quality-assurance engineer at a semiconductor plant, he lived alone in Groton with a garden of heritage tomatoes and a cat named Diode. His cancer was caught during a workplace screening initiative in 2016. The anemia explained the fatigue he\'d blamed on twelve-hour shifts. He achieved remission by 2018 and now advocates for colorectal cancer screening in Asian-American communities.')

pdf.section_title('Lab Panel at Diagnosis (May 11, 2016)')
pdf.add_table(
    ['Test', 'Value', 'Status'],
    [
        ['Hemoglobin', '11.9 g/dL', 'Low (anemia)'],
        ['Hematocrit', '34.9%', 'Low'],
        ['WBC', '3.5 x10^3/uL', 'Low'],
        ['RBC', '4.5 x10^6/uL', 'Normal'],
    ],
    [50, 50, 90]
)

pdf.section_title('Wearable Biometrics (221 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '33.7', '19.7', '47.4'],
        ['Resting HR (bpm)', '67.6', '55.6', '76.4'],
        ['Total Sleep (min)', '356', '225', '441'],
        ['Sleep Efficiency', '0.809', '0.570', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Merlin\'s case highlights the importance of workplace screening programs. His cancer was caught early enough for curative surgical management without systemic chemotherapy. His wearable profile shows the lowest resting heart rate in the cohort (mean 67.6 bpm), suggesting good cardiovascular fitness. His anemia (Hgb 11.9) was mild and likely resolved post-treatment.')

# ===== PATIENT 9 =====
pdf.add_page()
pdf.chapter_title('Patient 9 — Katharina King')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', 'a0d74db0-05f1-489b-356a-05ee8752ae89'],
        ['Age', '71 (born Oct 31, 1954)'],
        ['Sex', 'Female'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Divorced'],
        ['Residence', 'Peabody, Massachusetts'],
        ['Income', '$193,904/yr'],
        ['Status', 'LIVING — Post-treatment monitoring'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Katharina is a retired pharmaceutical sales director who spent decades on the road, living on hotel room service and airport food. After the divorce, she settled in Peabody near her sister\'s family. The polyp found in 2019 came back recurrent and malignant by 2021. "I spent 25 years selling drugs to hospitals," she said. "I suppose it\'s my turn to be on the receiving end." Her overlapping malignant neoplasm resolved by September 2022, but the anemia persists, managed with B12 injections.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Nov 7, 2019', 'Polyp of colon found'],
        ['Mar 2, 2021', 'Recurrent rectal polyp'],
        ['Mar 6, 2021', 'Overlapping malignant neoplasm + Anemia'],
        ['Sep 24, 2022', 'Cancer resolved'],
    ],
    [40, 150]
)

pdf.section_title('Lab Panel (Mar 6, 2021)')
pdf.add_table(
    ['Test', 'Value', 'Status'],
    [
        ['Hemoglobin', '11.5 g/dL', 'Low (anemia)'],
        ['WBC', '8.3 x10^3/uL', 'Normal'],
        ['Pain Score', '8 / 10', 'Severe'],
    ],
    [50, 50, 90]
)

pdf.section_title('Wearable Biometrics (696 days)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '26.2', '13.8', '34.7'],
        ['Resting HR (bpm)', '69.3', '58.1', '82.2'],
        ['Total Sleep (min)', '393', '228', '511'],
        ['Deep Sleep (min)', '73', '—', '—'],
        ['Sleep Efficiency', '0.889', '0.554', '—'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Katharina\'s profile demonstrates the classic colorectal cancer trajectory: polyp -> recurrence -> malignancy -> resolution. Her RMSSD bottomed at 13.8 ms during active cancer (Mar-Apr 2021) and gradually improved. Her persistent anemia (ongoing B12 therapy) is the primary residual concern. Sleep architecture shows good recovery with 73 min deep sleep and 88.9% efficiency average.')

# ===== PATIENT 10 =====
pdf.add_page()
pdf.chapter_title('Patient 10 — Freddy Little')

pdf.add_table(
    ['Field', 'Detail'],
    [
        ['Patient ID', 'eecdf189-f43e-b108-5991-6ff9731bd93f'],
        ['Age at Death', '79 (born May 28, 1938 — died Oct 15, 2017)'],
        ['Sex', 'Male'],
        ['Race / Ethnicity', 'White, Non-Hispanic'],
        ['Marital Status', 'Married'],
        ['Residence', 'Middleborough, Massachusetts'],
        ['Income', '$104,254/yr'],
        ['Status', 'DECEASED'],
    ],
    [50, 140]
)

pdf.section_title('Backstory')
pdf.italic_text('Freddy was a cranberry farmer from Middleborough — the heart of Massachusetts\' cranberry country. He and his wife Eleanor raised three kids on their 40-acre bog, wading through knee-deep water every fall to harvest berries. A man who didn\'t trust doctors and hadn\'t seen one since his Army physical in 1958, it was Eleanor who dragged him to the clinic when his bowel habits changed. The overlapping malignant neoplasm was aggressive, and while oxaliplatin and leucovorin bought him years, the disease never fully resolved. He died on a Sunday morning in October 2017, with the bog still red from the harvest his sons finished without him.')

pdf.section_title('Diagnosis & Clinical Timeline')
pdf.add_table(
    ['Date', 'Event'],
    [
        ['Jun 4, 2013', 'Polyp of colon discovered'],
        ['Jun 13, 2013', 'Overlapping malignant neoplasm + Anemia'],
        ['Jul – Dec 2013', 'FOLFOX chemotherapy'],
        ['Oct 15, 2017', 'DEATH (4.3 years post-diagnosis)'],
    ],
    [40, 150]
)

pdf.section_title('Treatment Protocol')
pdf.add_table(
    ['Medication', 'Cycles', 'Period'],
    [
        ['Oxaliplatin 50 mg IV', '6', 'Jul – Dec 2013'],
        ['Leucovorin 100 mg IV', '6', 'Jul – Dec 2013'],
    ],
    [70, 30, 90]
)

pdf.section_title('Final Lab Panel (Dec 25, 2013)')
pdf.add_table(
    ['Test', 'Value', 'Status'],
    [
        ['Hemoglobin', '12.6 g/dL', 'Borderline low'],
        ['Hematocrit', '28.8%', 'SEVERELY low'],
        ['WBC', '2.7 x10^3/uL', 'Leukopenia'],
        ['GFR', '11.8 mL/min', 'Kidney failure'],
        ['Pain Score', '3 / 10', 'Managed'],
    ],
    [50, 50, 90]
)

pdf.section_title('Wearable Biometrics (1,096 days — full disease course)')
pdf.add_table(
    ['Metric', 'Mean', 'Min', 'Max'],
    [
        ['RMSSD (ms)', '22.8', '10.8', '31.4'],
        ['Resting HR (bpm)', '76.5', '64.4', '91.1'],
        ['Total Sleep (min)', '343', '196', '427'],
        ['Deep Sleep (min)', '50', '—', '—'],
        ['Sleep Efficiency', '0.918', '0.583', '—'],
        ['Awakenings/night', '3.0', '—', '4'],
    ],
    [50, 40, 40, 60]
)

pdf.section_title('Clinical Assessment')
pdf.body_text('Freddy\'s case is the most concerning in the colorectal cohort. His overlapping malignant neoplasm never resolved, and his final labs show severe hematocrit depletion (28.8%), leukopenia (WBC 2.7), and kidney failure (GFR 11.8). Wearable data reveals the lowest RMSSD minimum in the cohort (10.8 ms) and the highest frequency of awakenings (mean 3.0/night, max 4), indicating profound autonomic dysregulation and sleep fragmentation. Despite all this, his pain was well-managed at 3/10 — a small mercy.')

# ===== COHORT SUMMARY =====
pdf.add_page()
pdf.chapter_title('Cohort Summary')

pdf.add_table(
    ['#', 'Name', 'Cancer', 'Age', 'Sex', 'Race', 'Status', 'Key Finding'],
    [
        ['1', 'Hilton Prosacco', 'LUNG', '64', 'M', 'White', 'Living', 'CKD Stage 4, pain 9/10'],
        ['2', 'Ignacio Dach', 'LUNG', '65+', 'M', 'White', 'Deceased', '195 chemo cycles, renal fail'],
        ['3', 'Beatrice Zieme', 'LUNG', '48', 'F', 'White', 'Living', 'Critical GFR 8.2'],
        ['4', 'Song Bednar', 'BREAST', '76', 'F', 'White', 'Living', 'Lowest HRV, post-treatment'],
        ['5', 'Catrice Schoen', 'BREAST', '53', 'F', 'Black', 'Living', '37-year survivor, best sleep'],
        ['6', 'See Wuckert', 'BREAST', '54+', 'F', 'White', 'Deceased', 'Full trajectory, 1096 days'],
        ['7', 'Brandon Sanford', 'COLORECTAL', '82', 'M', 'Hispanic', 'Living', 'Oldest, remission, no chemo'],
        ['8', 'Merlin Graham', 'COLORECTAL', '69', 'M', 'Asian', 'Living', 'Early screening catch'],
        ['9', 'Katharina King', 'COLORECTAL', '71', 'F', 'White', 'Living', 'Classic polyp-to-resolution'],
        ['10', 'Freddy Little', 'COLORECTAL', '79+', 'M', 'White', 'Deceased', 'Worst HRV, never remitted'],
    ],
    [8, 30, 24, 10, 10, 18, 18, 72]
)

pdf.ln(5)
pdf.set_font('Helvetica', 'I', 9)
pdf.set_text_color(100, 100, 100)
pdf.multi_cell(0, 5, 'Data Sources: Synthea clinical records (master_patients.csv, master_conditions.csv, master_medications.csv, master_observations.csv, master_encounters.csv) + Generated wearable biometrics (wearable_hrv.csv, wearable_sleep.csv)')

# Output
pdf.output('patient_profiles.pdf')
print('PDF created successfully: patient_profiles.pdf')
