import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

input_file = BASE_DIR / "input" / "bank_transactions.csv"
output_file = BASE_DIR / "input" / "bank_transactions_clean.csv"
hadoop_file = BASE_DIR / "input" / "bank_transactions_hadoop.csv"
summary_file = BASE_DIR / "results" / "cleaning_summary.json"

print("Loading dataset...")
df = pd.read_csv(input_file)
original_rows = len(df)
steps = {}

def record(name, before):
    steps[name] = int(before - len(df))

# Keep only valid gender codes (M / F)
n = len(df)
df = df[df["Gender"].isin(["M", "F"])].copy()
record("invalid_or_missing_gender", n)

# Remove missing locations
n = len(df)
df = df[df["Location"].notna() & (df["Location"].astype(str).str.strip() != "")].copy()
record("missing_location", n)

# Remove missing account balances
n = len(df)
df = df[df["AccountBalance"].notna()].copy()
record("missing_account_balance", n)

# Remove non-positive transaction amounts
n = len(df)
df = df[df["Amount"] > 0].copy()
record("non_positive_amount", n)

# Parse the transaction date (d/m/yy)
df["TransactionDate"] = pd.to_datetime(df["TransactionDate"], format="%d/%m/%y")

# Parse the date of birth. Two-digit years 17-99 are 1917-1999, 00-16 are 2000-2016.
# The placeholder 1/1/1800 and missing values become invalid.
n = len(df)
dob = df["CustomerDOB"].astype("string")
parts = dob.str.split("/", expand=True)
year = pd.to_numeric(parts[2], errors="coerce")
year = year.where(year >= 100, (year + 1900).where(year > 16, year + 2000))
year = year.where(year != 1800)
df["BirthYear"] = year
df["Age"] = df["TransactionDate"].dt.year - df["BirthYear"]
df = df[df["Age"].between(18, 100)].copy()
record("invalid_or_placeholder_birth_date", n)

df["Age"] = df["Age"].astype(int)

# Derived columns
df["AgeGroup"] = pd.cut(
    df["Age"], bins=[17, 25, 35, 45, 55, 65, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
).astype(str)
df["TransactionHour"] = df["TransactionTime"] // 10000
df["TransactionDate"] = df["TransactionDate"].dt.strftime("%Y-%m-%d")
df["Weekday"] = pd.to_datetime(df["TransactionDate"]).dt.day_name()
df["AmountBand"] = pd.cut(
    df["Amount"], bins=[0, 100, 500, 1000, 5000, 10000, float("inf")],
    labels=["1_<=100", "2_101-500", "3_501-1000", "4_1001-5000", "5_5001-10000", "6_>10000"]
).astype(str)
df["Location"] = (
    df["Location"].astype(str)
    .str.replace("\t", " ", regex=False)
    .str.replace("|", " ", regex=False)
    .str.strip()
)

columns = [
    "TransactionID", "CustomerID", "Gender", "Location", "AccountBalance",
    "TransactionDate", "TransactionHour", "Amount", "Age", "AgeGroup",
    "Weekday", "AmountBand",
]
df = df[columns]

df.to_csv(output_file, index=False, encoding="utf-8")
df.to_csv(hadoop_file, index=False, header=False, encoding="utf-8")

summary = {
    "original_rows": original_rows,
    "cleaned_rows": int(len(df)),
    "rows_removed": int(original_rows - len(df)),
    "removed_by_step": steps,
    "unique_customers": int(df["CustomerID"].nunique()),
    "unique_locations": int(df["Location"].nunique()),
    "total_amount_inr": round(float(df["Amount"].sum()), 2),
}
summary_file.parent.mkdir(exist_ok=True)
Path(summary_file).write_text(json.dumps(summary, indent=2))

print("\n===== CLEANING RESULTS =====")
print("Original rows:", original_rows)
print("Cleaned rows:", len(df))
print("Rows removed:", original_rows - len(df))
for k, v in steps.items():
    print(f"  removed ({k}): {v}")
print("Unique customers:", summary["unique_customers"])
print("Unique locations:", summary["unique_locations"])
print("Total transaction amount: INR {:,.2f}".format(df["Amount"].sum()))
print("\nCleaned columns:")
print(df.columns.tolist())
print("\nFirst 5 cleaned records:")
print(df.head().to_string(index=False))
print("\nFiles saved:", output_file, "and", hadoop_file)
