-- Cancer Recovery Assistant - Supabase Schema
-- Run this in the Supabase SQL Editor to create all tables

-- 1. Patients
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date DATE,
    gender TEXT,
    race TEXT,
    city TEXT,
    state TEXT,
    cancer_type TEXT,
    treatment_phase TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Medications
CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    reason TEXT,
    start_date DATE,
    end_date DATE,
    dosage TEXT,
    is_chemo BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Lab Results
CREATE TABLE IF NOT EXISTS lab_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    test_code TEXT,
    test_name TEXT NOT NULL,
    value NUMERIC,
    unit TEXT,
    reference_range TEXT,
    observed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Symptom Logs (from agent extraction)
CREATE TABLE IF NOT EXISTS symptom_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    symptom_name TEXT NOT NULL,
    severity TEXT CHECK (severity IN ('none', 'mild', 'moderate', 'severe')),
    score NUMERIC,
    unit TEXT,
    context TEXT,
    source TEXT DEFAULT 'chat' CHECK (source IN ('chat', 'voice', 'manual', 'agent')),
    raw_input TEXT,
    logged_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Wearable Readings (real-time stream)
CREATE TABLE IF NOT EXISTS wearable_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    reading_type TEXT NOT NULL CHECK (reading_type IN ('hrv', 'sleep', 'heart_rate')),
    rmssd NUMERIC,
    sdnn NUMERIC,
    mean_hr NUMERIC,
    total_sleep_min NUMERIC,
    sleep_efficiency NUMERIC,
    deep_sleep_pct NUMERIC,
    awakenings INTEGER,
    recorded_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Diagnoses (agent-generated)
CREATE TABLE IF NOT EXISTS diagnoses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    assessment TEXT NOT NULL,
    severity_level TEXT CHECK (severity_level IN ('stable', 'mild_concern', 'moderate_concern', 'urgent')),
    triggers JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    symptom_summary JSONB DEFAULT '{}',
    wearable_summary JSONB DEFAULT '{}',
    call_doctor BOOLEAN DEFAULT false,
    generated_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL,
    file_path TEXT,
    metadata JSONB DEFAULT '{}',
    generated_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_symptom_logs_patient ON symptom_logs(patient_id, logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_wearable_patient ON wearable_readings(patient_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_lab_results_patient ON lab_results(patient_id, observed_at DESC);
CREATE INDEX IF NOT EXISTS idx_diagnoses_patient ON diagnoses(patient_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_medications_patient ON medications(patient_id);

-- Enable RLS (Row Level Security) - initially open for development
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE wearable_readings ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnoses ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE medications ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_results ENABLE ROW LEVEL SECURITY;

-- Allow all access for anon key during development
CREATE POLICY "Allow all for dev" ON patients FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON symptom_logs FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON wearable_readings FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON diagnoses FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON reports FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON medications FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all for dev" ON lab_results FOR ALL USING (true) WITH CHECK (true);
