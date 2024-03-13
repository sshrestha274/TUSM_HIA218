import pandas as pd
import random
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker
import numpy as np

# Initialize Faker to generate fake text data
fake = Faker()

# List of pre-defined ICD-10 diagnostic codes
columns = ["ICD10CM", "Description"]
colspecs = [(0, 7), (8, None)]
icd10_codes = pd.read_fwf("Week8\Datasets\icd10cm-codes-2024.txt",colspecs=colspecs, header=None,  names=columns, index_col=False)

icd10cm_dict =icd10_codes.set_index("ICD10CM").to_dict(orient="index")

# # List of pre-defined HCPC procedure codes
# CPT_codes = pd.read_csv("2022_DHS_Code_List_Addendum_10_28_21/CPT_codes.csv")
# # CPT_codes.head()
# CPTcode_dict = CPT_codes.set_index('CPT_code').to_dict(orient='index')

drug_codes = pd.read_csv(r"Week8\Datasets\usp_drug_classification_edited.csv", index_col=False)
# drug_codes.head()
drug_codes = drug_codes.drop_duplicates(subset=['kegg_id'])
drug_codes = drug_codes.dropna()

drug_id = drug_codes["kegg_id"]
drug_codes_dict = drug_codes.set_index('kegg_id').to_dict(orient='index')


complaint_data = pd.read_csv(r"Week8\Datasets\PatientDataOutput.csv",  index_col=False)
complaint_data = complaint_data.drop_duplicates(subset=['unique_code'])
complaint_data = complaint_data.dropna()
complaint_id = complaint_data["unique_code"]
complaint_codes_dict = complaint_data.set_index('unique_code').to_dict(orient='index')

age_mean = 35
age_std = 15
num_samples = 10000  # Number of random samples you want
random_age = np.random.normal(age_mean, age_std, num_samples)
random_age = [None if x>90 or x<0 else round(x) for x in random_age]

pain_mean = 5
pain_std = 1.5
random_pain = np.random.normal(pain_mean, pain_std, num_samples)
random_pain= [None if x>10 or x<0 else round(x) for x in random_pain]

los_mean = 12
los_std = 4
random_los = np.random.normal(los_mean, los_std, num_samples)
random_los = [None if x < 0 else round(x) for x in random_los]


race_ethnicity = ["Non Hispanic White", "Hispanic White", "Non Hispanic Black", "Asian American and Pacific Islanders", "Others", "NA"]
gender = ["Male", "Female"]
#sampling probabilities
gender_probability = [0.49, 0.51]
race_probability = [0.55,0.15,0.18, 0.06,0.05,0.01]

# Initialize the dataset
dataset = []

# Generate 10,000 records
for i in range(200000):
    record = {
        "id": str(random.randint(10000000, 99999999)),  # 8-digit ID number
        "age": random.choice(random_age),
        "gender": random.choices(gender, gender_probability)[0],
        "race": random.choices(race_ethnicity, race_probability)[0],
        "patient_id": str(random.randint(100000, 999999)),  # 6-digit patient ID
        "datetime": (datetime(2016, 1, 1) + timedelta(days=random.randint(0, 2191), seconds=random.randint(0, 86399))).strftime("%Y-%m-%d %H:%M:%S"),
        "doctor_id": random.randint(1000, 9999),  # 4-digit doctor ID
        "pain": random.choice(random_pain),
        "dxg1": random.choice(icd10_codes['ICD10CM']), # randomly selected ICD10 code
        "dxg2": random.choice(icd10_codes['ICD10CM']), # randomly selected ICD10 code
        "dxg3": random.choice(icd10_codes['ICD10CM']), # randomly selected ICD10 code
        "dxg4": random.choice(icd10_codes['ICD10CM']), # randomly selected ICD10 code
        "dxg5": random.choice(icd10_codes['ICD10CM']), # randomly selected ICD10 code
        "complaint_id": random.choice(list(complaint_data['unique_code'])), 
        "length_of_stay": random.choice(random_los),  # Length of stay between 1 and 30 hours
        "drug1": random.choice(list(drug_codes["kegg_id"])),
        "drug2": random.choice(list(drug_codes["kegg_id"])),
        "drug3": random.choice(list(drug_codes["kegg_id"])),
        "cost": round(random.uniform(100.0, 5000.0), 2),  # Random cost between $100 and $5000
        "patient_rating": round(random.uniform(1.0, 5.0), 1) 
    }
    dataset.append(record)


df_frame = pd.DataFrame(dataset)

df_frame.to_csv(r"Week8\Datasets\patient_dataset_HIA.csv")

database = pd.read_csv(r"Week8\Datasets\patient_dataset_HIA.csv")

def description(x):
    return icd10cm_dict[x]['Description']

database['dxg1_desc'] = database['dxg1'].apply(description)
database['dxg2_desc'] = database['dxg2'].apply(description)
database['dxg3_desc'] = database['dxg3'].apply(description)
database['dxg4_desc'] = database['dxg4'].apply(description)
database['dxg5_desc'] = database['dxg5'].apply(description)

def description_drug_class(y):
    return drug_codes_dict[y]['usp_class']

database['drug1_class'] = database['drug1'].apply(description_drug_class)
database['drug2_class'] = database['drug2'].apply(description_drug_class)
database['drug3_class'] = database['drug3'].apply(description_drug_class)

def complaints(z):
    return complaint_codes_dict[z]['Complaints']

database['complaint'] = database['complaint_id'].apply(complaints)

discharge_options = ["Discharged to home", 'Admitted to hospital', 'Referral', 'Death']
discharge_probability = [0.7, 0.2, 0.08,0.02]

database['discharged_status'] = random.choices(discharge_options, discharge_probability)[0]

def replace_none_drugs(data, var, percentage):
    if (data[var] in ['Opioid Analgesics, Short-acting', 'Opioid Analgesics, Long-acting']) and data['race'] == "Non Hispanic Black":
        prob = random.uniform(0,1)
        if prob <= percentage:
            return None
        
    return data[var] 

database['drug1'] = database.apply(replace_none_drugs, args=('drug1_class', 0.2), axis=1)
database['drug2'] = database.apply(replace_none_drugs, args=( 'drug2_class', 0.4), axis=1)
database['drug3'] = database.apply(replace_none_drugs, args=( 'drug3_class', 0.6), axis=1)

def replace_random(x, percentage):
    prob = random.uniform(0,1)
    if prob <= percentage:
        return None
    else:
        return x
  
database['drug1'] = database['drug1'].apply(replace_random, percentage=0.1)
database['drug2'] = database['drug2'].apply(replace_random, percentage=0.2)
database['drug3'] = database['drug3'].apply(replace_random, percentage=0.3)

def replace_a_with_none(row, var1, var2):
    if row[var1] is None:
        return None
    else:
        return row[var2]
    
database['drug1_class'] = database.apply(replace_a_with_none, args=('drug1', 'drug1_class'), axis=1)
database['drug2_class'] = database.apply(replace_a_with_none, args=('drug2', 'drug2_class'), axis=1)
database['drug3_class'] = database.apply(replace_a_with_none, args=('drug3', 'drug3_class'), axis=1)

pain_meds_classes = ['Opioid Analgesics, Short-acting', 'Opioid Analgesics, Long-acting']

# Define a function to check for pain medications
def has_pain_meds(row):
    if (row['drug1_class'] in pain_meds_classes) or (row['drug2_class'] in pain_meds_classes) or (row['drug3_class'] in pain_meds_classes):
        return 1
    else:
        return 0

# Apply the function to create a new column 'pain_meds'
database['pain_meds'] = database.apply(has_pain_meds, axis=1)

database.to_csv(r"Week8\Datasets\UpdatedData_03_13_2024.csv")