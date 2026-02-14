import pandas as pd
import json

# Load all data
print("Loading data...")
patients = pd.read_csv('master_patients.csv')
conditions = pd.read_csv('master_conditions.csv')
medications = pd.read_csv('master_medications.csv')
observations = pd.read_csv('master_observations.csv')
encounters = pd.read_csv('master_encounters.csv')
hrv = pd.read_csv('wearable_hrv.csv')
sleep = pd.read_csv('wearable_sleep.csv')

# Select 10 diverse patients: mix of cancer types, gender, race, age, living/deceased
# Pick ~3-4 from each cancer type, mix genders, include some deceased
selected_ids = []

# Strategy: for each cancer type, pick diverse patients
for ctype in ['LUNG', 'BREAST', 'COLORECTAL']:
    subset = patients[patients['cancer_type'] == ctype]
    
    if ctype == 'LUNG':
        # Pick 4: 2M, 1F living, 1F deceased, mix races
        living_m = subset[(subset['GENDER'] == 'M') & (subset['DEATHDATE'].isna())].head(1)
        deceased_m = subset[(subset['GENDER'] == 'M') & (subset['DEATHDATE'].notna())].head(1)
        living_f = subset[(subset['GENDER'] == 'F') & (subset['DEATHDATE'].isna())].head(1)
        deceased_f = subset[(subset['GENDER'] == 'F') & (subset['DEATHDATE'].notna())].head(1)
        selected_ids.extend(living_m['Id'].tolist() + deceased_m['Id'].tolist() + living_f['Id'].tolist())
    elif ctype == 'BREAST':
        # Pick 3: mostly F (breast cancer more common in women)
        living_f = subset[(subset['GENDER'] == 'F') & (subset['DEATHDATE'].isna())]
        # Try different races
        white_f = living_f[living_f['RACE'] == 'white'].head(1)
        black_f = living_f[living_f['RACE'] == 'black'].head(1)
        deceased_f = subset[(subset['GENDER'] == 'F') & (subset['DEATHDATE'].notna())].head(1)
        selected_ids.extend(white_f['Id'].tolist() + black_f['Id'].tolist() + deceased_f['Id'].tolist())
    else:  # COLORECTAL
        # Pick 4: 2M 2F mix
        living_m = subset[(subset['GENDER'] == 'M') & (subset['DEATHDATE'].isna())]
        hispanic_m = living_m[living_m['ETHNICITY'] == 'hispanic'].head(1)
        other_m = living_m[living_m['RACE'] == 'asian'].head(1)
        if other_m.empty:
            other_m = living_m[living_m['RACE'] == 'black'].head(1)
        living_f = subset[(subset['GENDER'] == 'F') & (subset['DEATHDATE'].isna())].head(1)
        deceased_m_cr = subset[(subset['GENDER'] == 'M') & (subset['DEATHDATE'].notna())].head(1)
        selected_ids.extend(hispanic_m['Id'].tolist() + other_m['Id'].tolist() + living_f['Id'].tolist() + deceased_m_cr['Id'].tolist())

# Trim to 10
selected_ids = selected_ids[:10]

print(f"Selected {len(selected_ids)} patients")

for pid in selected_ids:
    print("\n" + "="*100)
    pat = patients[patients['Id'] == pid].iloc[0]
    print(f"\n### PATIENT: {pat['FIRST']} {pat['LAST']}")
    print(f"ID: {pid}")
    print(f"DOB: {pat['BIRTHDATE']}, Gender: {pat['GENDER']}, Race: {pat['RACE']}, Ethnicity: {pat['ETHNICITY']}")
    print(f"Marital: {pat['MARITAL']}, Cancer Type: {pat['cancer_type']}")
    print(f"City: {pat['CITY']}, State: {pat['STATE']}")
    death = pat['DEATHDATE']
    if pd.notna(death):
        print(f"DECEASED: {death}")
    else:
        print("STATUS: Living")
    print(f"Income: ${pat['INCOME']:,.0f}, Healthcare Expenses: ${pat['HEALTHCARE_EXPENSES']:,.2f}, Coverage: ${pat['HEALTHCARE_COVERAGE']:,.2f}")
    
    # Conditions
    pat_conditions = conditions[conditions['PATIENT'] == pid].sort_values('START')
    print(f"\n--- CONDITIONS ({len(pat_conditions)}) ---")
    for _, c in pat_conditions.iterrows():
        stop = c['STOP'] if pd.notna(c['STOP']) else 'ongoing'
        print(f"  {c['START']} - {stop}: {c['DESCRIPTION']}")
    
    # Medications (unique)
    pat_meds = medications[medications['PATIENT'] == pid]
    unique_meds = pat_meds.groupby('DESCRIPTION').agg(
        first_date=('START', 'min'),
        last_date=('STOP', 'max'),
        count=('DESCRIPTION', 'count'),
        reason=('REASONDESCRIPTION', 'first')
    ).reset_index().sort_values('first_date')
    print(f"\n--- MEDICATIONS ({len(unique_meds)} unique) ---")
    for _, m in unique_meds.iterrows():
        print(f"  {m['DESCRIPTION']} (x{m['count']}) [{m['first_date'][:10]} to {str(m['last_date'])[:10]}] Reason: {m['reason']}")
    
    # Key observations (vital signs & labs)
    pat_obs = observations[observations['PATIENT'] == pid]
    # Get latest of key metrics
    key_codes = ['72514-3', '718-7', '20570-8', '6690-2', '789-8', '751-8', '32623-1',
                 '8302-2', '29463-7', '39156-5', '8480-6', '8462-4', '8867-4',
                 '2947-0', '33914-3', '4544-3', '2093-3', '2571-8']
    key_obs = pat_obs[pat_obs['CODE'].isin(key_codes)]
    latest_obs = key_obs.sort_values('DATE').groupby('DESCRIPTION').last().reset_index()
    print(f"\n--- LATEST KEY OBSERVATIONS ({len(latest_obs)}) ---")
    for _, o in latest_obs.iterrows():
        print(f"  {o['DESCRIPTION']}: {o['VALUE']} {o['UNITS'] if pd.notna(o.get('UNITS')) else ''} (date: {str(o['DATE'])[:10]})")
    
    # Encounters summary
    pat_enc = encounters[encounters['PATIENT'] == pid]
    enc_types = pat_enc.groupby('ENCOUNTERCLASS').size().reset_index(name='count')
    print(f"\n--- ENCOUNTERS ({len(pat_enc)} total) ---")
    for _, e in enc_types.iterrows():
        print(f"  {e['ENCOUNTERCLASS']}: {e['count']}")
    
    # Wearable HRV summary
    pat_hrv = hrv[hrv['PATIENT'] == pid]
    if not pat_hrv.empty:
        print(f"\n--- WEARABLE HRV ({len(pat_hrv)} days) ---")
        print(f"  RMSSD: mean={pat_hrv['RMSSD'].mean():.1f}, min={pat_hrv['RMSSD'].min():.1f}, max={pat_hrv['RMSSD'].max():.1f}")
        print(f"  SDNN: mean={pat_hrv['SDNN'].mean():.1f}, min={pat_hrv['SDNN'].min():.1f}, max={pat_hrv['SDNN'].max():.1f}")
        print(f"  MEAN_HR: mean={pat_hrv['MEAN_HR'].mean():.1f}, min={pat_hrv['MEAN_HR'].min():.1f}, max={pat_hrv['MEAN_HR'].max():.1f}")
        # Find dates of lowest RMSSD (worst HRV)
        worst_hrv = pat_hrv.nsmallest(3, 'RMSSD')
        print(f"  Worst HRV days: {', '.join(worst_hrv['DATE'].tolist())}")
    
    # Wearable Sleep summary
    pat_sleep = sleep[sleep['PATIENT'] == pid]
    if not pat_sleep.empty:
        print(f"\n--- WEARABLE SLEEP ({len(pat_sleep)} days) ---")
        print(f"  Total Sleep: mean={pat_sleep['TOTAL_SLEEP_MIN'].mean():.0f}min, min={pat_sleep['TOTAL_SLEEP_MIN'].min():.0f}min, max={pat_sleep['TOTAL_SLEEP_MIN'].max():.0f}min")
        print(f"  Deep Sleep: mean={pat_sleep['DEEP_SLEEP_MIN'].mean():.0f}min")
        print(f"  REM Sleep: mean={pat_sleep['REM_SLEEP_MIN'].mean():.0f}min")
        print(f"  Efficiency: mean={pat_sleep['SLEEP_EFFICIENCY'].mean():.3f}, min={pat_sleep['SLEEP_EFFICIENCY'].min():.3f}")
        print(f"  Awakenings: mean={pat_sleep['AWAKENINGS'].mean():.1f}, max={pat_sleep['AWAKENINGS'].max()}")
        worst_sleep = pat_sleep.nsmallest(3, 'TOTAL_SLEEP_MIN')
        print(f"  Worst sleep days: {', '.join(worst_sleep['DATE'].tolist())}")

print("\n\nDONE")
