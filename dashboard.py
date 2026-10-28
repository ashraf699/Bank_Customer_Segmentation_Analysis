import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(
    page_title="Bank Customer Segmentation Analysis",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Customer Segmentation Analysis Dashboard")
st.caption("Big Data Analytics | Hadoop MapReduce | Python | Streamlit")

# ---------------- LOAD MAPREDUCE RESULTS ----------------
file_path = Path(__file__).resolve().parent / "results" / "mapreduce_output.txt"
summary_path = Path(__file__).resolve().parent / "results" / "cleaning_summary.json"


@st.cache_data
def load_results(path):
    totals = {}
    metrics = {}

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) != 2:
                continue
            key, raw_value = parts
            try:
                value = float(raw_value)
            except ValueError:
                continue

            if "|" in key:
                metric, name = key.split("|", 1)
                metrics.setdefault(metric, {})[name] = value
            else:
                totals[key] = value

    def frame(metric, column):
        data = metrics.get(metric, {})
        return pd.DataFrame(
            {"Name": list(data.keys()), column: list(data.values())}
        )

    location = frame("LOCATION_AMOUNT", "Value").merge(
        frame("LOCATION_COUNT", "Transactions"), on="Name"
    ).merge(frame("LOCATION_BALANCE_SUM", "BalanceSum"), on="Name")
    location["Avg Transaction"] = location["Value"] / location["Transactions"]
    location["Avg Account Balance"] = location["BalanceSum"] / location["Transactions"]
    location = location.drop(columns="BalanceSum").rename(columns={"Name": "Location"})

    gender = frame("GENDER_AMOUNT", "Value").merge(
        frame("GENDER_COUNT", "Transactions"), on="Name"
    ).rename(columns={"Name": "Gender"})

    age = frame("AGE_GROUP_AMOUNT", "Value").merge(
        frame("AGE_GROUP_COUNT", "Transactions"), on="Name"
    ).rename(columns={"Name": "Age Group"}).sort_values("Age Group")

    month = frame("MONTH_AMOUNT", "Value").merge(
        frame("MONTH_COUNT", "Transactions"), on="Name"
    ).rename(columns={"Name": "Month"}).sort_values("Month")

    daily = frame("DAILY_AMOUNT", "Value").rename(
        columns={"Name": "Date"}
    ).sort_values("Date")

    weekday = frame("WEEKDAY_COUNT", "Transactions").rename(columns={"Name": "Weekday"})
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday["Weekday"] = pd.Categorical(weekday["Weekday"], categories=order, ordered=True)
    weekday = weekday.sort_values("Weekday")

    hour = frame("HOUR_COUNT", "Transactions").rename(
        columns={"Name": "Hour"}
    ).sort_values("Hour")

    band = frame("AMOUNT_BAND_COUNT", "Transactions").rename(
        columns={"Name": "Amount Band"}
    ).sort_values("Amount Band")
    band["Amount Band"] = band["Amount Band"].str.split("_", n=1).str[1]

    return totals, location, gender, age, month, daily, weekday, hour, band


if not file_path.exists():
    st.error(f"Results file not found: {file_path}")
    st.info("Run the MapReduce job and copy the output into the results folder.")
    st.stop()

(totals, location_df, gender_df, age_df, month_df,
 daily_df, weekday_df, hour_df, band_df) = load_results(str(file_path))

if location_df.empty:
    st.error("Location results are missing from the MapReduce output.")
    st.stop()

summary = {}
if summary_path.exists():
    summary = json.loads(summary_path.read_text())

total_value = totals.get("TOTAL_AMOUNT", 0.0)
total_txn = totals.get("TOTAL_TRANSACTIONS", 0.0)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Dashboard Filters")

search_text = st.sidebar.text_input("Search Location", placeholder="Enter city name")

min_txn = st.sidebar.number_input(
    "Minimum transactions per location", min_value=1, max_value=1000, value=1
)

top_n = st.sidebar.slider(
    "Number of items to display",
    min_value=5,
    max_value=20,
    value=10
)

# ---------------- KEY PERFORMANCE INDICATORS ----------------
st.subheader("Transaction Overview")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Transaction Value", f"₹{total_value:,.2f}")
col2.metric("Total Transactions", f"{total_txn:,.0f}")
col3.metric("Average Transaction", f"₹{total_value / max(total_txn, 1):,.2f}")
col4.metric("Locations", f"{location_df['Location'].nunique():,}")

st.divider()

# ---------------- LOCATION ANALYSIS ----------------
st.subheader("🌍 Location Analysis")

filtered_locations = location_df[location_df["Transactions"] >= min_txn].copy()
if search_text.strip():
    filtered_locations = filtered_locations[
        filtered_locations["Location"].str.contains(
            search_text.strip(), case=False, na=False, regex=False
        )
    ]

location_chart_df = filtered_locations.nlargest(top_n, "Value").sort_values("Value")

if location_chart_df.empty:
    st.warning("No locations match your filters.")
else:
    fig_loc = px.bar(
        location_chart_df, x="Value", y="Location", orientation="h",
        title=f"Transaction Value by Location (Top {top_n})",
        labels={"Value": "Transaction Value (₹)"},
        color="Value", color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_loc, width="stretch")

    count_chart_df = filtered_locations.nlargest(top_n, "Transactions").sort_values("Transactions")
    fig_cnt = px.bar(
        count_chart_df, x="Transactions", y="Location", orientation="h",
        title=f"Number of Transactions by Location (Top {top_n})",
        color="Transactions", color_continuous_scale="Teal"
    )
    st.plotly_chart(fig_cnt, width="stretch")

st.dataframe(
    filtered_locations.sort_values("Value", ascending=False),
    width="stretch", hide_index=True
)

st.divider()

# ---------------- CUSTOMER DEMOGRAPHICS ----------------
st.subheader("👥 Customer Demographics")

left, right = st.columns(2)
with left:
    fig_gender = px.pie(
        gender_df, names="Gender", values="Value",
        title="Transaction Value by Gender", hole=0.4
    )
    st.plotly_chart(fig_gender, width="stretch")
with right:
    fig_age = px.bar(
        age_df, x="Age Group", y="Value",
        title="Transaction Value by Age Group",
        labels={"Value": "Transaction Value (₹)"},
        color="Value", color_continuous_scale="Oranges"
    )
    st.plotly_chart(fig_age, width="stretch")

st.dataframe(age_df, width="stretch", hide_index=True)

st.divider()

# ---------------- TIME ANALYSIS ----------------
st.subheader("🕒 Time Analysis")

fig_daily = px.line(
    daily_df, x="Date", y="Value", title="Daily Transaction Value",
    labels={"Value": "Transaction Value (₹)"}
)
st.plotly_chart(fig_daily, width="stretch")

left, right = st.columns(2)
with left:
    st.plotly_chart(
        px.bar(hour_df, x="Hour", y="Transactions", title="Transactions by Hour of Day"),
        width="stretch"
    )
with right:
    st.plotly_chart(
        px.bar(weekday_df, x="Weekday", y="Transactions", title="Transactions by Weekday"),
        width="stretch"
    )

st.divider()

# ---------------- AMOUNT DISTRIBUTION ----------------
st.subheader("💰 Transaction Size Distribution")
st.plotly_chart(
    px.bar(band_df, x="Amount Band", y="Transactions",
           title="Transactions by Amount Band (₹)"),
    width="stretch"
)

# ---------------- PROJECT DETAILS ----------------
with st.expander("About this project"):
    st.write(
        "This dashboard visualizes aggregated results produced by a "
        "Hadoop Streaming MapReduce job on the cleaned Bank Customer Segmentation dataset."
    )
    st.write(f"**MapReduce output records:** {sum(1 for _ in open(file_path, encoding='utf-8')):,}")
    st.write(f"**Cleaned transaction records processed:** {total_txn:,.0f}")
    if summary:
        st.write(f"**Original records:** {summary['original_rows']:,}")
        st.write(f"**Records removed during cleaning:** {summary['rows_removed']:,}")
        st.write(f"**Unique customers:** {summary['unique_customers']:,}")
    st.write(
        "**Cleaning:** Invalid or missing gender, missing location, missing account "
        "balance, non-positive amounts and invalid or placeholder birth dates were excluded."
    )
    st.write(
        "**Important:** Values are transaction amounts in Indian Rupees (INR) from "
        "retained records; they are not profit or bank revenue."
    )

st.caption("Data source: Bank Customer Segmentation dataset (Kaggle) | Analysis: Hadoop MapReduce")
