## **. Product Overview**

* **Mission:** To eliminate the "clinical blind spot" between hospital visits by providing a holistic, AI-powered recovery assistant for cancer patients.  
* **Target Audience:** Cancer patients (Breast, Lung, Colorectal) aged 40–90 and their oncology teams.  
* **Core Problem:** Traditional EHRs are episodic and lack "real-world" physiological context, leading to late detection of treatment toxicities and patient isolation.  
  ---

  ## **2\. Functional Requirements**

  ### **A. Monitoring: Predictive "Multimodal Agent"**

The agent acts as the brain of the platform, correlating two distinct data streams.

* **Clinical State Ingestion:** Automatically parse Synthea-generated master\_conditions.csv and master\_medications.csv to identify active treatment phases.  
* **Wearable Sync:** Ingest continuous HRV (RMSSD/SDNN) and sleep data from HealthGen.  
* **Toxicity Signaling:** Detect "HRV Decay"—a reduction in RMSSD \>30%—as a marker for Cancer-Related Fatigue (CRF) or medication toxicity.  
* **Daily Check-ins:** Trigger specific prompts (Mental, Meds, Physical) based on physiological dips to capture qualitative patient data.

  ### **B. Reporting: Unified Holistic Patient Chart**

The objective is to create a "Hospital-Plus" chart that merges episodic and continuous data.

* **Hospital Standard Layer:** Include demographics, active problem lists, and medication administration records (MAR) sourced from Synthea.  
* **Wearable Overlay:** Visualize HRV trends and sleep efficiency directly alongside chemotherapy cycles to show the "Inter-Encounter Narrative".  
* **Clinician Summary:** An AI-generated note summarizing patient progress between visits (e.g., *"Patient shows improving recovery velocity post-Cycle 4"*).

  ### **C. Enabling Community: Peer Matching & Progress Tracking**

Use cohort data to foster support networks.

* **Matching Algorithm:** Connect patients based on diagnosis, age (40–90), and "Physiological Trajectory" (similarity in how their HRV responds to treatment).  
* **Progress Benchmarking:** Allow patients to see their recovery progress relative to a synthetic "peer average" of 1,000 similar patients.  
  ---

  ## **3\. Data & Technical Specifications**

  ### **Data Fusion Model**

The platform relies on a "Seed and Decay" model where Synthea clinical states influence wearable noise.

| Data Source | Type | Key Metrics | Role in PRD |
| :---- | :---- | :---- | :---- |
| **Synthea** | Episodic | SNOMED Codes, Med Start/Stop | Clinical Ground Truth |
| **HealthGen** | Continuous | HRV RMSSD, Sleep Stages | Physiological Response |
| **User Input** | Qualitative | Pain Scale, Mental State | Subjective Context |

---

## **4\. User Experience (UX) & Design**

* **Patient Dashboard:** Simplified view focusing on "Recovery Score" and community connections.  
* **Clinician View:** High-density "Holistic Chart" designed to be reviewed in under 2 minutes during a consultation.  
* **Tone & Voice:** Grounded, empathetic, and supportive (avoiding clinical jargon for the patient-facing side).  
  ---

  ## **5\. Security & Safety Boundaries**

* **Medical Disclaimer:** The AI provides "Healthcare Suggestions" only; it is not a diagnostic tool and must include "Call Doctor" triggers for critical alerts.  
* **Data Privacy:** All initial cohort processing must use anonymized UUIDs.  
* **Hallucination Guardrails:** AI summaries must be grounded strictly in the joined CSV data.