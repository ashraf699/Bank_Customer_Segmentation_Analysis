import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from pathlib import Path

input_file = Path(__file__).resolve().parent / "results" / "mapreduce_output.txt"
data = {}

with input_file.open(encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t", 1)
        if len(parts) != 2:
            continue
        key, value = parts
        try:
            value = float(value)
        except ValueError:
            continue
        if "|" in key:
            metric, name = key.split("|", 1)
            data.setdefault(metric, {})[name] = value

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def barh(metric, title, xlabel, ylabel, filename, top=10, size=(11, 7)):
    items = sorted(data[metric].items(), key=lambda x: x[1], reverse=True)[:top]
    items.reverse()
    plt.figure(figsize=size)
    plt.barh([x[0] for x in items], [x[1] for x in items])
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()


# Chart 1: Top 10 locations by transaction value
barh("LOCATION_AMOUNT", "Top 10 Locations by Transaction Value",
     "Transaction Value (INR)", "Location", str(RESULTS_DIR / "top_10_locations.png"))

# Chart 2: Top 10 locations by transaction count
barh("LOCATION_COUNT", "Top 10 Locations by Number of Transactions",
     "Number of Transactions", "Location", str(RESULTS_DIR / "top_10_locations_by_count.png"))

# Chart 3: Transaction value by age group
ages = sorted(data["AGE_GROUP_AMOUNT"].items())
plt.figure(figsize=(10, 6))
plt.bar([x[0] for x in ages], [x[1] for x in ages])
plt.xlabel("Age Group")
plt.ylabel("Transaction Value (INR)")
plt.title("Transaction Value by Customer Age Group")
plt.tight_layout()
plt.savefig(str(RESULTS_DIR / "age_group_value.png"), dpi=200)
plt.close()

# Chart 4: Transactions by hour of day
hours = sorted(data["HOUR_COUNT"].items())
plt.figure(figsize=(11, 6))
plt.bar([x[0] for x in hours], [x[1] for x in hours])
plt.xlabel("Hour of Day")
plt.ylabel("Number of Transactions")
plt.title("Transactions by Hour of Day")
plt.tight_layout()
plt.savefig(str(RESULTS_DIR / "transactions_by_hour.png"), dpi=200)
plt.close()

# Chart 5: Daily transaction value
days = sorted(data["DAILY_AMOUNT"].items())
plt.figure(figsize=(12, 6))
plt.plot([x[0] for x in days], [x[1] for x in days])
step = max(1, len(days) // 10)
plt.xticks([x[0] for x in days][::step], rotation=45)
plt.xlabel("Date")
plt.ylabel("Transaction Value (INR)")
plt.title("Daily Transaction Value (Aug - Oct 2016)")
plt.tight_layout()
plt.savefig(str(RESULTS_DIR / "daily_transaction_value.png"), dpi=200)
plt.close()

print("Visualizations created successfully!")
for f in ["top_10_locations", "top_10_locations_by_count", "age_group_value",
          "transactions_by_hour", "daily_transaction_value"]:
    print(f"  results/{f}.png")
