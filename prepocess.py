import pandas as pd

# -------------------------------
# STEP 1: LOAD CSV
# -------------------------------
df = pd.read_csv("crime_data.csv")

print("Original Data:")
print(df.head())

# -------------------------------
# STEP 2: HANDLE MISSING VALUES
# -------------------------------
# Fill missing numeric values with mean
df['Victim Age'] = df['Victim Age'].fillna(df['Victim Age'].mean())

# Fill missing categorical values
df['City'] = df['City'].fillna("Unknown")
df['Crime Des'] = df['Crime Des'].fillna("Unknown")

# -------------------------------
# STEP 3: REMOVE DUPLICATES
# -------------------------------
df = df.drop_duplicates()

# -------------------------------
# STEP 4: CLEAN TEXT DATA
# -------------------------------
df['City'] = df['City'].str.strip().str.title()
df['Crime Des'] = df['Crime Des'].str.strip().str.upper()

# -------------------------------
# STEP 5: CONVERT DATE FORMAT
# -------------------------------
df['Date of Occ'] = pd.to_datetime(df['Date of Occ'], errors='coerce')

# -------------------------------
# STEP 6: REMOVE INVALID COORDINATES
# -------------------------------
df = df[(df['latitude'].notnull()) & (df['longitude'].notnull())]

# -------------------------------
# STEP 7: NORMALIZE DATA (OPTIONAL)
# -------------------------------
df['Victim Age'] = df['Victim Age'] / df['Victim Age'].max()

# -------------------------------
# STEP 8: SAVE CLEAN DATA
# -------------------------------
df.to_csv("crime_data_cleaned.csv", index=False)

print("✅ Preprocessing Done! Clean file saved.")