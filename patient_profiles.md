# Patient Profiles — Cancer Recovery Monitoring Program

> 10 comprehensive patient dossiers drawn from synthetic clinical data (Synthea) enriched with wearable biometric monitoring. Each profile includes background, diagnosis, treatment history, wearable trends, and a narrative backstory written in clinical-narrative style.

---

## Patient 1 — Hilton Prosacco

| Field | Detail |
|:---|:---|
| **Patient ID** | `497c0923-b34e-0004-095a-54b61544403e` |
| **Age** | 64 (born Nov 12, 1961) |
| **Sex** | Male |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Southbridge, Massachusetts |
| **Occupation / Income** | Blue-collar worker · $35,968/yr |
| **Status** | **Living — Active treatment** |

### Backstory
Hilton is a retired machine-tool operator from central Massachusetts who spent 30 years breathing metal dust and solvent fumes on the factory floor. A lifelong non-complainer, he ignored a nagging cough for months until his wife insisted he see his GP in the spring of 2023. An emergency chest X-ray followed by a CT scan confirmed what nobody wanted to hear. He has two grown sons and four grandchildren; his youngest grandson was born the same week he started chemotherapy. Despite the diagnosis, Hilton tells his oncologist he's "not done yet" — he wants to see that grandson start school.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| May 14, 2023 | Suspected lung cancer flagged after imaging |
| May 26, 2023 | Confirmed **Non-small cell lung cancer (NSCLC)** + treatment-related **Anemia** |
| May 28, 2023 | Staged as **NSCLC TNM Stage I** — curative-intent chemo initiated |

### Treatment Protocol
| Medication | Route | Cycles | Period | Indication |
|:---|:---|:---|:---|:---|
| Cisplatin 50 mg | IV Injection | 179 | May 2023 – Jan 2026 | NSCLC Stage I |
| Paclitaxel 100 mg | IV Injection | 179 | May 2023 – Jan 2026 | NSCLC Stage I |
| Vitamin B12 5 mg/mL | IM Injectable | 1 | May 2023 | Anemia support |

### Latest Lab Panel (Jan 2, 2026)
| Test | Value | Reference | Status |
|:---|:---|:---|:---|
| Hemoglobin | 15.5 g/dL | 13.5–17.5 | ✅ Normal |
| Hematocrit | 49.3% | 38.3–48.6 | ⚠️ Slightly high |
| WBC | 2.9 × 10³/µL | 4.5–11.0 | 🔴 Low (leukopenia) |
| RBC | 4.8 × 10⁶/µL | 4.7–6.1 | ✅ Normal |
| Platelet MPV | 9.9 fL | 7.5–12.0 | ✅ Normal |
| GFR (eGFR) | 23.2 mL/min | >60 | 🔴 Severe renal impairment |
| Sodium | 142.4 mmol/L | 136–145 | ✅ Normal |
| Pain Score | **9 / 10** | — | 🔴 Severe |

### Encounter Summary
41 total encounters: 25 inpatient stays, 4 outpatient, 1 emergency visit, 1 ambulatory, 10 routine wellness

### Wearable Biometrics (225-day monitoring window)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 22.0 | 15.5 | 30.0 |
| SDNN (ms) | 28.4 | 20.0 | 40.5 |
| Resting HR (bpm) | 71.3 | 61.9 | 82.1 |
| Total Sleep (min) | 369 | 271 | 450 |
| Deep Sleep (min) | 64 | — | — |
| Sleep Efficiency | 0.797 | 0.632 | — |
| Awakenings/night | 1.0 | — | 1 |

**HRV Trend**: Consistently low RMSSD (mean 22.0 ms), indicating chronic autonomic stress from ongoing chemotherapy. Worst dips in Aug–Sep 2023 (mid-treatment nadir).

**Sleep Trend**: Average 6.2 hrs/night with efficiency of ~80% — below healthy thresholds. Deep sleep is suppressed at 64 min, suggesting fatigue-related sleep architecture disruption.

### Clinical Assessment
Hilton is a Stage I NSCLC patient entering his 3rd year of platinum-doublet chemotherapy. While his hemoglobin has stabilized, his **severe leukopenia (WBC 2.9)** places him at elevated infection risk, and his **eGFR of 23.2** indicates cisplatin-induced nephrotoxicity in CKD Stage 4 territory. His pain score of 9/10 is the most acute concern — likely neuropathic pain from cumulative paclitaxel toxicity. Wearable data corroborates his clinical picture: depressed HRV and poor sleep architecture align with chronic treatment burden.

---

## Patient 2 — Ignacio Dach

| Field | Detail |
|:---|:---|
| **Patient ID** | `65343425-3160-297c-d371-32119d34cfcc` |
| **Age at Death** | 65 (born Nov 20, 1937 — died Nov 26, 2003) |
| **Sex** | Male |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Lynn, Massachusetts |
| **Occupation / Income** | Low-income earner · $28,030/yr |
| **Status** | **Deceased** |

### Backstory
Ignacio was a quiet Portuguese-American fisherman's son who grew up on the North Shore. After serving in the Army during Vietnam, he worked decades in a tannery — a job that gave him a modest living but chronic exposure to industrial chemicals. By his early sixties, the persistent "smoker's cough" he attributed to decades of Camels turned out to be something far worse. His wife of 40 years, Dolores, cared for him through three and a half years of treatment before he passed six days after his 66th birthday.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Mar 31, 2000 | Suspected lung cancer |
| Apr 13, 2000 | Confirmed **Non-small cell lung cancer** + **Anemia** |
| Apr 14, 2000 | Staged as **NSCLC TNM Stage I** — chemo initiated |
| Nov 26, 2003 | **Death** (3.5 years post-diagnosis) |

### Treatment Protocol
| Medication | Cycles | Period |
|:---|:---|:---|
| Cisplatin 50 mg IV | 195 | Apr 2000 – Oct 2003 |
| Paclitaxel 100 mg IV | 195 | Apr 2000 – Oct 2003 |

### Final Lab Panel (Oct 28, 2003)
| Test | Value | Status |
|:---|:---|:---|
| Hemoglobin | 16.5 g/dL | ✅ Normal |
| Hematocrit | 40.6% | ✅ Normal |
| WBC | 2.6 × 10³/µL | 🔴 Leukopenia |
| GFR | 13.9 mL/min | 🔴 Kidney failure (Stage 5) |
| Pain Score | **9 / 10** | 🔴 Severe |

### Encounter Summary
51 total encounters: 35 inpatient admissions, 1 emergency visit, 11 wellness visits — heavily hospitalized in final years.

### Wearable Biometrics (1,096-day monitoring window)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 27.6 | 17.5 | 36.8 |
| Resting HR (bpm) | 73.5 | 62.1 | 85.1 |
| Total Sleep (min) | 412 | 262 | 521 |
| Deep Sleep (min) | 79 | — | — |
| Sleep Efficiency | 0.925 | 0.655 | — |

**Clinical Summary**: Ignacio's case illustrates the long-term toll of platinum-based chemotherapy. Despite maintaining adequate hemoglobin through 195 treatment cycles, his kidneys ultimately failed (eGFR 13.9 at final labs). His 35 inpatient stays paint a picture of escalating medical fragility. Wearable data shows HRV dips that correlated with chemo cycles, but his sleep architecture remained surprisingly resilient until the final months.

---

## Patient 3 — Beatrice Zieme

| Field | Detail |
|:---|:---|
| **Patient ID** | `c3495c1a-3a6e-edaf-9b91-8aa7ebd0f2c4` |
| **Age** | 48 (born Aug 22, 1977) |
| **Sex** | Female |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Marlborough, Massachusetts |
| **Occupation / Income** | Service worker · $4,206/yr (very low income) |
| **Status** | **Living — Active treatment** |

### Backstory
Beatrice is the youngest patient in this cohort and the one with the least financial resources. A single working mom who later married her high school boyfriend when their youngest started kindergarten, she held part-time jobs at a daycare center to keep the family afloat. Her diagnosis at 47 was devastating — she was the one in the family everyone depended on. Her husband took FMLA leave to drive her to chemo sessions at UMass Memorial. She worries less about the cancer and more about the medical bills she can see piling up while her coverage barely covers the infusions.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Sep 13, 2024 | Suspected lung cancer after routine imaging |
| Oct 5, 2024 | Confirmed **NSCLC** + **Anemia** |
| Oct 6, 2024 | Staged as **NSCLC TNM Stage I** — chemo initiated |

### Treatment Protocol
| Medication | Cycles | Period |
|:---|:---|:---|
| Cisplatin 50 mg IV | 80 | Oct 2024 – Jan 2026 |
| Paclitaxel 100 mg IV | 80 | Oct 2024 – Jan 2026 |
| Vitamin B12 IM | 1 | Oct 2024 |

### Latest Lab Panel (Jan 18, 2026)
| Test | Value | Status |
|:---|:---|:---|
| Hemoglobin | 14.4 g/dL | ✅ Normal |
| WBC | 3.1 × 10³/µL | 🔴 Leukopenia |
| GFR | 8.2 mL/min | 🔴 **Critical renal failure** |
| Pain Score | **7 / 10** | 🟡 High |

### Encounter Summary
26 encounters: 13 inpatient, 6 outpatient, 1 emergency, 5 wellness

### Wearable Biometrics (234 days)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 35.2 | 18.8 | 52.0 |
| Total Sleep (min) | 397 | 251 | 539 |
| Sleep Efficiency | 0.743 | 0.500 | — |

**Clinical Assessment**: Despite being the youngest patient and showing the best baseline HRV (mean 35.2 ms), Beatrice's GFR of 8.2 mL/min is the most alarming value in the entire cohort — she is in **Stage 5 CKD (kidney failure)** after only 80 chemo cycles. This suggests heightened cisplatin sensitivity. Her sleep efficiency of 74.3% (dropping to 50% at worst) is the poorest of all female patients, reflecting acute treatment distress. Immediate nephrology consult is warranted.

---

## Patient 4 — Song Bednar

| Field | Detail |
|:---|:---|
| **Patient ID** | `03611e2a-fa1a-740f-0d37-3477b58b6974` |
| **Age** | 76 (born Aug 4, 1949) |
| **Sex** | Female |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Boston, Massachusetts |
| **Occupation / Income** | Middle income · $137,757/yr |
| **Status** | **Living — Post-treatment surveillance** |

### Backstory
Song is a retired public librarian from Boston's Allston neighborhood who spent 35 years helping immigrant families navigate the American school system. Widowed at 68 when her husband Victor died of heart disease, she poured herself into volunteer work at the Asian Community Development Corporation. When a routine mammogram in 2020 revealed a suspicious mass, she approached it the same way she approached everything — by learning everything she could. She checked out every oncology textbook her former library carried and arrived at her first appointment with a typed list of questions. Now in post-treatment surveillance, she organizes a support group for cancer survivors at her local church.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Dec 10, 2020 | Diagnosed with **Malignant neoplasm of breast** |
| Dec 31, 2020 | Chemotherapy initiated |
| May 27, 2021 | Carboplatin course completed (8 cycles) |
| Jun 1, 2021 | Transitioned to Fulvestrant (hormonal therapy) |
| 2021 – present | Post-treatment monitoring |

### Treatment Protocol
| Medication | Cycles | Period |
|:---|:---|:---|
| Carboplatin 10 mg/mL IV | 8 | Dec 2020 – May 2021 |
| Fulvestrant 50 mg/mL Prefilled Syringe | 1 | Jun 2021 |

### Encounter Summary
44 encounters: 30 ambulatory follow-ups, 1 inpatient, 2 outpatient, 1 virtual, 10 wellness — consistent with long-term surveillance

### Wearable Biometrics (211 days around treatment)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 18.7 | 10.4 | 26.5 |
| Resting HR (bpm) | 82.4 | 72.9 | 92.6 |
| Total Sleep (min) | 319 | 186 | 448 |
| Deep Sleep (min) | 49 | — | — |
| Sleep Efficiency | 0.784 | 0.506 | — |
| Awakenings/night | 2.1 | — | 3 |

**Clinical Assessment**: Song is the oldest breast cancer patient in our cohort and shows the **lowest baseline HRV** (RMSSD 18.7 ms) — consistent with her age and reduced cardiovascular reserve. Her resting heart rate of 82.4 bpm is the highest in the cohort, suggesting chronotropic stress. Despite completing treatment, her sleep quality remains poor (only 5.3 hrs avg, 49 min deep sleep) with frequent awakenings (2.1/night). This pattern is common in elderly breast cancer survivors and is a modifiable risk factor for recurrence-related fatigue.

---

## Patient 5 — Catrice Schoen

| Field | Detail |
|:---|:---|
| **Patient ID** | `0fc698de-9c91-5eac-0eba-d74cb7540c47` |
| **Age** | 53 (born Mar 6, 1972) |
| **Sex** | Female |
| **Race / Ethnicity** | **Black**, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Worthington, Massachusetts |
| **Occupation / Income** | Moderate income · $68,151/yr |
| **Status** | **Living — Long-term survivor** |

### Backstory
Catrice was just 16 years old when she found a lump in her breast — an almost unheard-of diagnosis for a teenager. Growing up in a close-knit Black family in rural western Massachusetts, she was the star point guard on her high school basketball team with dreams of playing D-II ball. Instead, she spent her junior year in treatment. The experience forged an unshakeable resilience: she went on to earn a nursing degree, married her college sweetheart Darnell, and has spent her career at Baystate Medical Center — sometimes caring for patients diagnosed with the same disease that tried to take her out at sixteen. Now 53, she has been cancer-free for over three decades, though she never misses an annual screening.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Mar 31, 1988 | Diagnosed with **Malignant neoplasm of breast** at age **16** |
| 1988 – present | Long-term survivor (37 years) |

### Treatment Protocol
No chemotherapy medications recorded in the dataset — suggests surgical intervention (likely lumpectomy or mastectomy at diagnosis) without documented systemic chemotherapy, consistent with treatment approaches for adolescent breast cancer in the late 1980s.

### Encounter Summary
30 encounters: 20 ambulatory, 2 outpatient, 1 virtual, 7 wellness — consistent with long-term survivorship monitoring

### Wearable Biometrics (211 days)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 16.8 | 12.1 | 22.0 |
| Resting HR (bpm) | 80.7 | 70.2 | 91.2 |
| Total Sleep (min) | 438 | 330 | 552 |
| Deep Sleep (min) | 98 | — | — |
| Sleep Efficiency | 0.797 | 0.653 | — |

**Clinical Assessment**: Catrice presents a unique profile as a **37-year breast cancer survivor** diagnosed in adolescence. Remarkably, her sleep metrics are the **best in the entire cohort** — 7.3 hrs average with 98 min deep sleep, reflecting excellent recovery and overall health. Her low RMSSD (16.8 ms) may be a long-term echo of early-life cancer treatment or simply her physiology, rather than acute disease burden. She represents the gold standard of what a cancer survivor monitoring program hopes to see.

---

## Patient 6 — See Wuckert

| Field | Detail |
|:---|:---|
| **Patient ID** | `44466ba7-b0ca-c6bb-ac02-58cfc05398ac` |
| **Age at Death** | 54 (born Jan 29, 1970 — died Feb 4, 2024) |
| **Sex** | Female |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Divorced |
| **Residence** | West Falmouth, Massachusetts (Cape Cod) |
| **Occupation / Income** | Upper-middle income · $113,505/yr |
| **Status** | **Deceased** |

### Backstory
See was a marine biologist at the Woods Hole Oceanographic Institution who specialized in coastal ecosystem health — an irony not lost on her when her own health began to fail. Divorced with one daughter, she threw herself into her research after the split, spending long seasons on research vessels in the North Atlantic. When she found the lump, she delayed telling anyone for weeks, assuming it was a cyst. The biopsy said otherwise. She fought through paclitaxel, doxorubicin, tamoxifen, and Verzenio — the full arsenal — but the disease progressed. She died on a cold February morning in 2024, five years after diagnosis, with her daughter and her lab partner at her bedside. Her colleagues named a newly discovered species of sea sponge after her.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Mar 15, 2019 | Diagnosed with **Malignant neoplasm of breast** |
| Mar – Aug 2019 | Paclitaxel chemotherapy (8 cycles) |
| Sep 2019 – Feb 2020 | Doxorubicin (8 cycles) |
| Mar 2020 | Switched to Tamoxifen + Verzenio (hormonal/targeted) |
| Feb 4, 2024 | **Death** (4.9 years post-diagnosis) |

### Treatment Protocol
| Medication | Cycles | Period |
|:---|:---|:---|
| Paclitaxel 100 mg IV | 8 | Mar – Aug 2019 |
| Doxorubicin 20 mg IV | 8 | Sep 2019 – Feb 2020 |
| Tamoxifen 10 mg Oral | 1 | Mar 2020 |
| Abemaciclib (Verzenio) 100 mg Oral | 1 | Mar 2020 |

### Encounter Summary
51 encounters: 38 ambulatory, 1 inpatient, 2 outpatient, 2 virtual, 8 wellness

### Wearable Biometrics (1,096 days — full disease course)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 34.1 | 17.3 | 49.6 |
| Resting HR (bpm) | 72.0 | 61.7 | 85.9 |
| Total Sleep (min) | 412 | 239 | 538 |
| Deep Sleep (min) | 68 | — | — |
| Sleep Efficiency | 0.915 | 0.557 | — |

**Clinical Assessment**: See's wearable data spans her entire disease trajectory — a rare 1,096-day window from diagnosis to death. Her HRV shows a classic "treatment valley" pattern: RMSSD dropping to 17.3 ms during active chemo (Apr–Jun 2019), partially recovering during hormonal therapy, then gradually declining again in her final year. Her sleep efficiency of 91.5% average is deceptively good, masking the dramatic drops to 55.7% during active treatment. Her case is a textbook example of how wearable data can track disease progression and treatment response longitudinally.

---

## Patient 7 — Brandon Sanford

| Field | Detail |
|:---|:---|
| **Patient ID** | `19b781ac-82c4-6a42-495b-b59d4c4811d3` |
| **Age** | 82 (born May 19, 1943) |
| **Sex** | Male |
| **Race / Ethnicity** | White, **Hispanic** |
| **Marital Status** | Single (never married) |
| **Residence** | Northborough, Massachusetts |
| **Occupation / Income** | High income · $906,274/yr |
| **Status** | **Living — In remission** |

### Backstory
Brandon is a Cuban-American entrepreneur who built a small chain of auto body shops across central Massachusetts into a multi-million dollar operation. A lifelong bachelor who insists he was "married to the business," he hired his nieces and nephews to run the shops while he focused on expansion. When a routine colonoscopy in 2013 found a polyp, he brushed it off. When the polyp came back — recurrent and malignant by late 2014 — he couldn't brush that off. His wealth afforded him the best care money could buy, but it couldn't buy him time back. He achieved remission by 2017 without requiring chemotherapy (managed surgically), and now at 82, he's the oldest living patient in this cohort and still drives a 1967 Mustang to his flagship shop every Saturday morning.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| May 25, 2013 | **Polyp of colon** discovered during colonoscopy |
| Oct 29, 2014 | **Recurrent rectal polyp** detected |
| Nov 3, 2014 | Diagnosed with **Malignant neoplasm of colon** |
| Feb 12, 2017 | Cancer resolved — **in remission** |

### Treatment Protocol
No systemic chemotherapy recorded — managed through surgical intervention (polypectomy/resection). Consistent with early-stage colorectal cancer treated surgically.

### Encounter Summary
16 encounters: 4 ambulatory, 2 outpatient, 10 wellness — remarkably low healthcare utilization

### Wearable Biometrics (738 days)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 27.3 | 12.4 | 37.0 |
| Resting HR (bpm) | 76.2 | 64.8 | 89.2 |
| Total Sleep (min) | 379 | 190 | 476 |
| Deep Sleep (min) | 59 | — | — |
| Sleep Efficiency | 0.860 | 0.500 | — |
| Awakenings/night | 2.0 | — | 3 |

**Clinical Assessment**: Brandon's profile is a success story. Diagnosed with colorectal cancer that progressed from benign polyps to malignancy over 18 months, he achieved remission through surgery alone within ~2.3 years. His wearable data shows the physiological stress of diagnosis and treatment: RMSSD dropped to 12.4 ms around the active cancer period (late 2014 – early 2015), with sleep hitting a nadir of just 3.2 hrs during that period. Post-remission, his metrics gradually improved, though at 82, his baseline HRV remains age-appropriately low.

---

## Patient 8 — Merlin Graham

| Field | Detail |
|:---|:---|
| **Patient ID** | `dfeb81a1-9050-2bd6-07d1-5c294c7dec16` |
| **Age** | 69 (born Apr 25, 1956) |
| **Sex** | Male |
| **Race / Ethnicity** | **Asian**, Non-Hispanic |
| **Marital Status** | Single |
| **Residence** | Groton, Massachusetts |
| **Occupation / Income** | Moderate income · $80,413/yr |
| **Status** | **Living — In remission** |

### Backstory
Merlin is a second-generation Chinese-American who grew up in Lowell's Cambodian quarter. A quiet, methodical man, he worked as a quality-assurance engineer at a semiconductor plant in the Route 128 corridor. He lived alone in a modest colonial in Groton — no wife, no kids, just a garden full of heritage tomatoes and a cat named Diode. His primary malignant neoplasm of the colon was caught during a screenings initiative at work in 2016. The anemia that accompanied it explained the fatigue he'd blamed on twelve-hour shifts. He achieved remission by 2018 without chemotherapy and now serves as an advocate for colorectal cancer screening in Asian-American communities, where screening rates historically lag behind.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| May 2, 2016 | **Polyp of colon** discovered |
| May 12, 2016 | **Primary malignant neoplasm of colon** confirmed + **Anemia** |
| Apr 6, 2018 | Cancer resolved — **in remission** |

### Lab Panel at Diagnosis (May 11, 2016)
| Test | Value | Status |
|:---|:---|:---|
| Hemoglobin | 11.9 g/dL | 🟡 Low (anemia) |
| Hematocrit | 34.9% | 🟡 Low |
| WBC | 3.5 × 10³/µL | 🔴 Low |
| RBC | 4.5 × 10⁶/µL | ✅ Normal |

### Encounter Summary
15 encounters: 5 ambulatory, 10 wellness

### Wearable Biometrics (221 days)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 33.7 | 19.7 | 47.4 |
| Resting HR (bpm) | 67.6 | 55.6 | 76.4 |
| Total Sleep (min) | 356 | 225 | 441 |
| Deep Sleep (min) | 52 | — | — |
| Sleep Efficiency | 0.809 | 0.570 | — |

**Clinical Assessment**: Merlin's case highlights the importance of workplace screening programs. His cancer was caught early enough for curative surgical management without systemic chemotherapy. His wearable profile shows the **lowest resting heart rate** in the cohort (mean 67.6 bpm), suggesting good cardiovascular fitness. HRV dips during the active cancer period (Jun–Aug 2016) are well-documented in the data. His anemia (Hgb 11.9) was mild and likely resolved post-treatment.

---

## Patient 9 — Katharina King

| Field | Detail |
|:---|:---|
| **Patient ID** | `a0d74db0-05f1-489b-356a-05ee8752ae89` |
| **Age** | 71 (born Oct 31, 1954) |
| **Sex** | Female |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Divorced |
| **Residence** | Peabody, Massachusetts |
| **Occupation / Income** | Upper-middle income · $193,904/yr |
| **Status** | **Living — Post-treatment monitoring** |

### Backstory
Katharina is a retired pharmaceutical sales director who spent decades on the road, living on hotel room service and airport food. Her ex-husband once joked that her colon had processed more airline peanuts than any organ in medical history. After the divorce, she settled in Peabody near her sister's family and finally got the colonoscopy she'd been putting off for years. The polyp found in November 2019 came back recurrent and malignant by March 2021. She was philosophical about it: "I spent 25 years selling drugs to hospitals. I suppose it's my turn to be on the receiving end." Her overlapping malignant neoplasm resolved by September 2022, but the anemia persists, managed with B12 injections.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Nov 7, 2019 | **Polyp of colon** found |
| Mar 2, 2021 | **Recurrent rectal polyp** |
| Mar 6, 2021 | **Overlapping malignant neoplasm of colon** + **Anemia** |
| Sep 24, 2022 | Cancer resolved |

### Lab Panel (Mar 6, 2021)
| Test | Value | Status |
|:---|:---|:---|
| Hemoglobin | 11.5 g/dL | 🔴 Low (anemia) |
| Hematocrit | 33.4% | 🔴 Low |
| WBC | 8.3 × 10³/µL | ✅ Normal |
| RBC | 5.4 × 10⁶/µL | ✅ Normal |
| Pain Score | **8 / 10** | 🔴 Severe |

### Encounter Summary
17 encounters: 5 ambulatory, 1 inpatient, 2 outpatient, 9 wellness

### Wearable Biometrics (696 days)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 26.2 | 13.8 | 34.7 |
| Resting HR (bpm) | 69.3 | 58.1 | 82.2 |
| Total Sleep (min) | 393 | 228 | 511 |
| Deep Sleep (min) | 73 | — | — |
| Sleep Efficiency | 0.889 | 0.554 | — |
| Awakenings/night | 1.0 | — | 2 |

**Clinical Assessment**: Katharina's profile demonstrates the **classic colorectal cancer trajectory**: polyp → recurrence → malignancy → resolution. Her pain score of 8/10 at diagnosis was significant and likely related to the overlapping neoplasm. Her wearable data tells a compelling recovery story — RMSSD bottomed at 13.8 ms during active cancer (Mar–Apr 2021) and gradually improved as the malignancy resolved. Her persistent anemia (ongoing B12 therapy) is the primary residual concern. Sleep architecture shows good recovery with 73 min deep sleep and 88.9% efficiency average.

---

## Patient 10 — Freddy Little

| Field | Detail |
|:---|:---|
| **Patient ID** | `eecdf189-f43e-b108-5991-6ff9731bd93f` |
| **Age at Death** | 79 (born May 28, 1938 — died Oct 15, 2017) |
| **Sex** | Male |
| **Race / Ethnicity** | White, Non-Hispanic |
| **Marital Status** | Married |
| **Residence** | Middleborough, Massachusetts |
| **Occupation / Income** | Moderate income · $104,254/yr |
| **Status** | **Deceased** |

### Backstory
Freddy was a cranberry farmer from Middleborough — the heart of Massachusetts' cranberry country. He and his wife Eleanor raised three kids on their 40-acre bog, wading through knee-deep water every fall to harvest the berries that paid the mortgage. A man who didn't trust doctors and hadn't seen one voluntarily since his Army physical in 1958, it was Eleanor who dragged him to the clinic when his bowel habits changed and he started losing weight he couldn't afford to lose. The overlapping malignant neoplasm they found was aggressive, and while oxaliplatin and leucovorin bought him years, the disease never fully resolved. He died on a Sunday morning in October 2017, four years after diagnosis, with the bog still red from the harvest his sons finished without him.

### Diagnosis & Clinical Timeline
| Date | Event |
|:---|:---|
| Jun 4, 2013 | **Polyp of colon** discovered |
| Jun 13, 2013 | **Overlapping malignant neoplasm of colon** + **Anemia** |
| Jul – Dec 2013 | Chemotherapy (FOLFOX protocol) |
| Oct 15, 2017 | **Death** (4.3 years post-diagnosis) |

### Treatment Protocol
| Medication | Cycles | Period |
|:---|:---|:---|
| Oxaliplatin 50 mg IV | 6 | Jul – Dec 2013 |
| Leucovorin 100 mg IV | 6 | Jul – Dec 2013 |

### Final Lab Panel (Dec 25, 2013)
| Test | Value | Status |
|:---|:---|:---|
| Hemoglobin | 12.6 g/dL | 🟡 Borderline low |
| Hematocrit (automated) | 28.8% | 🔴 Severely low |
| WBC | 2.7 × 10³/µL | 🔴 Leukopenia |
| GFR | 11.8 mL/min | 🔴 Kidney failure |
| Pain Score | 3 / 10 | ✅ Managed |
| Sodium | 138.2 mmol/L | ✅ Normal |

### Encounter Summary
22 encounters: 11 ambulatory, 1 inpatient, 10 wellness

### Wearable Biometrics (1,096 days — full disease course)
| Metric | Mean | Min | Max |
|:---|:---|:---|:---|
| RMSSD (ms) | 22.8 | 10.8 | 31.4 |
| Resting HR (bpm) | 76.5 | 64.4 | 91.1 |
| Total Sleep (min) | 343 | 196 | 427 |
| Deep Sleep (min) | 50 | — | — |
| Sleep Efficiency | 0.918 | 0.583 | — |
| Awakenings/night | 3.0 | — | 4 |

**Clinical Assessment**: Freddy's case is the most concerning in the colorectal cohort. His **overlapping malignant neoplasm never resolved** (recorded as "ongoing" at time of death), and his final labs show the classic toxicity triad: severe hematocrit depletion (28.8%), leukopenia (WBC 2.7), and kidney failure (GFR 11.8). Wearable data reveals the **lowest RMSSD minimum** in the entire cohort (10.8 ms) and the **highest frequency of awakenings** (mean 3.0/night, max 4), indicating profound autonomic dysregulation and sleep fragmentation. Despite all this, his pain was well-managed at 3/10 — a small mercy in an otherwise difficult trajectory. His 1,096-day wearable dataset provides one of the most complete longitudinal records of cancer-related physiological decline in our data.

---

## Cohort Summary

| # | Name | Cancer | Age | Sex | Race | Status | Key Finding |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 1 | Hilton Prosacco | LUNG | 64 | M | White | Living | Active chemo, CKD Stage 4, pain 9/10 |
| 2 | Ignacio Dach | LUNG | 65† | M | White | Deceased | 195 chemo cycles, kidney failure at death |
| 3 | Beatrice Zieme | LUNG | 48 | F | White | Living | Youngest, critical GFR 8.2, worst sleep |
| 4 | Song Bednar | BREAST | 76 | F | White | Living | Oldest breast, lowest HRV, post-treatment |
| 5 | Catrice Schoen | BREAST | 53 | F | Black | Living | 37-year survivor, best sleep quality |
| 6 | See Wuckert | BREAST | 54† | F | White | Deceased | Full trajectory captured, 1096 days data |
| 7 | Brandon Sanford | COLORECTAL | 82 | M | Hispanic | Living | Oldest, remission, no chemo needed |
| 8 | Merlin Graham | COLORECTAL | 69 | M | Asian | Living | Workplace screening catch, best HR |
| 9 | Katharina King | COLORECTAL | 71 | F | White | Living | Classic polyp→cancer→resolution arc |
| 10 | Freddy Little | COLORECTAL | 79† | M | White | Deceased | Worst HRV, most awakenings, never remitted |

> **Data Sources**: Synthea clinical records (`master_patients.csv`, `master_conditions.csv`, `master_medications.csv`, `master_observations.csv`, `master_encounters.csv`) + Generated wearable biometrics (`wearable_hrv.csv`, `wearable_sleep.csv`)
