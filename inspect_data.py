from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

file_path = BASE_DIR / "input" / "bank_transactions.csv"

df = pd.read_csv(file_path)

print("===== DATASET INFORMATION =====")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nColumn names:")
print(df.columns.tolist())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== GENDER VALUES =====")
print(df["Gender"].value_counts(dropna=False))

print("\n===== PLACEHOLDER BIRTH DATES (1/1/1800) =====")
print("Rows with placeholder DOB:", (df["CustomerDOB"] == "1/1/1800").sum())

print("\n===== NON-POSITIVE TRANSACTION AMOUNTS =====")
print("Rows with amount <= 0:", (df["Amount"] <= 0).sum())

print("\n===== DUPLICATE TRANSACTION IDS =====")
print("Duplicates:", df["TransactionID"].duplicated().sum())

print("\n===== SAMPLE RECORDS =====")
print(df.head(5).to_string(index=False))
