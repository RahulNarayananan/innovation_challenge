# HealthGen Wearable Data: Parameter Explainability

This document explains **why** and **how** every parameter in `healthgen_wearable.py` was chosen, grounded in clinical literature and the PRD's requirements.

---

## 1. HRV Baselines by Age

```python
HRV_BASELINES = {
    (40, 50): {"rmssd": 38, "sdnn": 45, "hr": 68},
    (50, 60): {"rmssd": 32, "sdnn": 40, "hr": 72},
    (60, 70): {"rmssd": 26, "sdnn": 34, "hr": 74},
    (70, 80): {"rmssd": 21, "sdnn": 28, "hr": 76},
    (80, 91): {"rmssd": 17, "sdnn": 23, "hr": 78},
}
```

### Why these values?

HRV decreases with age — this is one of the most consistent findings in autonomic physiology. Clinical reference ranges for **RMSSD** (the primary metric in our PRD for toxicity detection):

| Age Band | Published RMSSD Range | Our Baseline | Source |
|:---|:---|:---|:---|
| 40–50 | 35–48 ms | 38 ms | Neurofeedback Luxembourg meta-analysis; Welltory population data |
| 50–60 | 28–44 ms | 32 ms | Same sources; age-adjusted exponential decline model |
| 60–70 | 25–45 ms | 26 ms | Kubios normative data; NIH aging studies |
| 70–80 | 18–30 ms | 21 ms | NIH cardiovascular autonomic studies |
| 80–90 | 15–25 ms | 17 ms | Extrapolated from decline curve; limited data for this age group |

**SDNN** values are set ~20% higher than RMSSD at each band, consistent with the known relationship where SDNN captures both sympathetic and parasympathetic contributions while RMSSD is parasympathetic-dominant.

**Mean HR** baselines (68–78 bpm) reflect published resting heart rates for adults aged 40–90, with a gradual increase in resting HR associated with aging and reduced parasympathetic tone.

> [!NOTE]
> The PRD targets cancer patients aged 40–90. Our baselines begin at age 40 — younger patients would have higher HRV, but they are outside the PRD's target population.

---

## 2. Gender Modifier

```python
FEMALE_HRV_BOOST = 1.05  # 5% higher RMSSD for females
```

### Why 5%?

Women tend to exhibit slightly higher RMSSD values than men, particularly in younger age groups. The Kubios normative database reports women having ~3–8% higher RMSSD across most age bands. We use 5% as a conservative middle estimate. This difference diminishes with age, which our model simplifies into a flat boost (a known limitation for accuracy in older cohorts).

---

## 3. Individual Variation

```python
individual_factor = rng.uniform(0.85, 1.15)  # ±15% per-patient variation
```

### Why ±15%?

Even within the same age and gender group, individual HRV varies significantly due to genetics, fitness, BMI, comorbidities, and medication use. A ±15% uniform variation produces a realistic spread:

- For a 50-year-old with baseline RMSSD of 32 ms, this produces a range of **27.2 – 36.8 ms**
- This matches the interquartile ranges reported in large-population HRV studies (Welltory, ~300K users)

---

## 4. Treatment Decay Parameters

```python
CHEMO_RMSSD_DECAY_RANGE = (0.20, 0.50)  # 20–50% drop during active chemo
RECOVERY_DAYS = (14, 28)                  # 2–4 weeks to recover
```

### Why 20–50% decay?

This is the most critical parameter — it models the **"HRV Decay"** signal described in the PRD as the primary toxicity marker (>30% RMSSD reduction = Cancer-Related Fatigue signal).

| Evidence | Measured Decay | Source |
|:---|:---|:---|
| Anthracycline chemotherapy → SDNN/RMSSD reduction | 20–40% decrease | Viamedica cardio-oncology journal |
| Autonomic dysfunction in cancer patients | Significant RMSSD and pNN50% reduction | ResearchGate meta-analysis |
| Combined taxane + carboplatin | Variable (some increase, mostly decrease) | Frontiers in Oncology |
| Cancer stage III–IV vs healthy controls | 30–50% lower HRV | NIH systematic review |

We use a **random decay per chemo window** (uniform 0.20–0.50) because:
1. Different chemo drugs have different cardiotoxicity profiles
2. The same drug affects patients differently
3. The PRD specifically flags >30% as clinically significant, so our range straddles this threshold

### Why 2–4 week recovery?

Post-chemo HRV recovery is documented at 2–6 weeks in most studies. We use 14–28 days (2–4 weeks) as a conservative range that aligns with typical inter-cycle recovery windows in breast, lung, and colorectal cancer protocols.

### Ramp-up model

```python
ramp = min(1.0, days_in / 5.0)  # 5-day ramp to full decay
```

HRV doesn't crash immediately — autonomic dysfunction develops over 3–7 days post-infusion as the cytotoxic effects accumulate. We model this as a 5-day linear ramp to full decay strength.

### Floor at 30%

```python
return max(factor, 0.3)  # Never decay below 30% of baseline
```

Even severely ill patients maintain some HRV. An RMSSD of 5 ms (our absolute floor via `max(5.0, ...)`) represents extreme cardiac autonomic failure. The 30% multiplicative floor ensures we don't generate physiologically impossible values.

---

## 5. Sleep Baselines

```python
SLEEP_BASELINES = {
    "total_min":  (420, 480),    # 7–8 hours
    "deep_pct":   (0.15, 0.25),  # 15–25% deep sleep
    "rem_pct":    (0.20, 0.25),  # 20–25% REM
    "awakenings": (1, 3),
    "efficiency": (0.85, 0.95),
}
```

### Why these ranges?

| Parameter | Value | Clinical Reference |
|:---|:---|:---|
| **Total sleep: 420–480 min** | 7–8 hours | CDC recommendation for adults; National Sleep Foundation |
| **Deep sleep: 15–25%** | N3 stage percentage | American Academy of Sleep Medicine normative data. Deep sleep decreases with age, so 15% represents older adults, 25% younger within our range |
| **REM: 20–25%** | REM percentage | Consistent across adult populations; relatively stable with age |
| **Awakenings: 1–3** | Nighttime awakenings | Healthy adults average 1–2; mildly increases with age |
| **Sleep efficiency: 85–95%** | Time asleep / time in bed | Clinical threshold: <85% is poor. Healthy adults typically 85–95% |

### Age adjustment

```python
age_factor = max(0.0, 1.0 - (age - 40) * 0.005)
```

Sleep quality declines ~0.5% per year after age 40. This produces:
- Age 40: factor = 1.0 (no reduction)
- Age 60: factor = 0.90 (10% reduction)
- Age 80: factor = 0.80 (20% reduction)

This matches published findings that older adults get less deep sleep, lower efficiency, and more awakenings.

---

## 6. Treatment Effects on Sleep

During active chemo, sleep is disrupted via the treatment factor:

```python
total_sleep = sleep_base["total_min"] * tf       # Duration drops
deep_pct    = sleep_base["deep_pct"] * tf        # Deep sleep suppressed
rem_pct     = sleep_base["rem_pct"] * (0.7 + 0.3 * tf)  # REM partially preserved
extra_awake = int((1.0 - tf) * rng.integers(1, 5))       # More awakenings
efficiency  = sleep_base["efficiency"] * tf               # Efficiency drops
```

### Why this pattern?

Clinical studies on chemotherapy-induced sleep disturbances (30–75% of patients affected) show:

1. **Total sleep duration drops** — patients report difficulty maintaining sleep
2. **Deep sleep is most affected** — NREM fragmentation is the hallmark of chemo-induced sleep disruption (Oxford University Press, 2023)
3. **REM is partially preserved** — REM sleep is more resistant to disruption, hence the `0.7 + 0.3 * tf` formula that preserves 70% of REM even at maximum decay
4. **Awakenings increase** — frequent nocturnal awakenings are the most commonly reported symptom
5. **Sleep efficiency drops** — PSQI studies show efficiency declining from healthy (>85%) to poor (<75%) during active treatment

---

## 7. Daily Noise

```python
DAILY_NOISE_CV = 0.10  # Coefficient of variation
```

### Why 10%?

Day-to-day HRV variation in healthy individuals is typically ±8–15% (Kubios, Welltory research). We use 10% (coefficient of variation) applied as multiplicative Gaussian noise:

```python
noise_rmssd = rng.normal(1.0, 0.10)  # ~95% of values within ±20%
```

This ensures realistic daily fluctuations. For sleep, we use a slightly tighter `0.07` (7%) since sleep metrics are more stable night-to-night than HRV.

---

## 8. HR–HRV Inverse Relationship

```python
hr_factor = 1.0 + (1.0 - tf) * 0.15
```

### Why?

Heart rate and HRV are inversely correlated — when autonomic stress increases (lowering HRV), sympathetic activation raises resting HR. During peak chemo decay (tf = 0.3):

- HR increases by ~10.5% (`1.0 + 0.7 * 0.15 = 1.105`)
- A patient with baseline 72 bpm → ~79.6 bpm during treatment

This matches clinical observations of resting tachycardia in chemo patients (ResearchGate cardiovascular autonomic dysfunction studies).

---

## 9. Chemo Drug Keywords

```python
CHEMO_KEYWORDS = [
    "cisplatin", "carboplatin", "paclitaxel", "docetaxel",
    "doxorubicin", "cyclophosphamide", "fluorouracil", "5-fu",
    "gemcitabine", "oxaliplatin", "irinotecan", "etoposide",
    "vincristine", "pemetrexed", "bevacizumab", "capecitabine",
    "leucovorin", "methotrexate", "bleomycin", "topotecan",
]
```

### Why these drugs?

These cover the standard-of-care chemotherapy regimens for the PRD's three cancer types:

| Cancer Type | Common Regimens | Key Drugs Matched |
|:---|:---|:---|
| **Breast** | AC-T, CMF, TC | doxorubicin, cyclophosphamide, paclitaxel, docetaxel, methotrexate, fluorouracil |
| **Lung (NSCLC)** | Cisplatin/Carboplatin + Pemetrexed/Paclitaxel | cisplatin, carboplatin, paclitaxel, pemetrexed, bevacizumab, etoposide |
| **Colorectal** | FOLFOX, FOLFIRI, CAPOX | fluorouracil, oxaliplatin, irinotecan, leucovorin, capecitabine |

Synthea generates medication records using RxNorm descriptions that contain these drug names as substrings, enabling reliable keyword matching.

---

## 10. Date Range Logic

```python
start = first_condition_date - 30 days   # Pre-diagnosis baseline
end = max(death_date, last_condition + 60 days)
max_duration = 5 years
```

### Why?

- **30-day pre-diagnosis buffer**: Captures baseline HRV before cancer detection, enabling before/after comparison
- **60-day post-condition buffer**: Captures recovery phase after last documented treatment
- **5-year cap**: Prevents excessive data for patients with long survival, keeping file sizes manageable

---

## Summary of Key Assumptions

| Assumption | Justification | Limitation |
|:---|:---|:---|
| Age-banded HRV baselines | Published normative data | Within-band variation simplified to ±15% |
| 20–50% chemo decay | Clinical cardiotoxicity literature | All chemo drugs treated equally (no drug-specific profiles) |
| 2–4 week recovery | Inter-cycle recovery studies | Linear recovery model vs. real exponential |
| Sleep disruption tracking HRV decay | Co-occurrence of autonomic and sleep dysfunction | Single decay factor drives both (real correlation is complex) |
| Gender: +5% RMSSD for females | Population studies | Flat boost across all ages (real effect diminishes with age) |
| Daily noise: 10% CV | Wearable device measurement studies | Same noise level regardless of health state |
