from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

# The Kaggle download is already a CSV, but it has Windows line endings and
# awkward column names (e.g. "TransactionAmount (INR)"). This step standardises
# the file so that every later step can rely on stable column names.
input_file = BASE_DIR / "input" / "bank_transactions_original.csv"
output_file = BASE_DIR / "input" / "bank_transactions.csv"

print("Reading original dataset...")
df = pd.read_csv(input_file, encoding="utf-8-sig")

df = df.rename(columns={
    "CustGender": "Gender",
    "CustLocation": "Location",
    "CustAccountBalance": "AccountBalance",
    "TransactionAmount (INR)": "Amount",
})

print("Writing standardised CSV...")
df.to_csv(output_file, index=False, encoding="utf-8")

print("\nConversion successful!")
print("Dataset shape:", df.shape)
print("Columns:", df.columns.tolist())
print("\nFirst five records:")
print(df.head().to_string(index=False))
print("\nCSV saved to:", output_file)
