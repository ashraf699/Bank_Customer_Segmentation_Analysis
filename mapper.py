#!/usr/bin/env python3
import sys
import csv

for line in sys.stdin:
    try:
        row = next(csv.reader([line]))

        if len(row) != 12:
            continue

        (txn_id, customer, gender, location, balance, date, hour,
         amount, age, age_group, weekday, band) = row

        amount = float(amount)
        balance = float(balance)

        location = location.replace("\t", " ").replace("|", " ").strip()
        month = date[:7]

        print(f"TOTAL_AMOUNT\t{amount}")
        print(f"TOTAL_TRANSACTIONS\t1")
        print(f"GENDER_AMOUNT|{gender}\t{amount}")
        print(f"GENDER_COUNT|{gender}\t1")
        print(f"LOCATION_AMOUNT|{location}\t{amount}")
        print(f"LOCATION_COUNT|{location}\t1")
        print(f"LOCATION_BALANCE_SUM|{location}\t{balance}")
        print(f"AGE_GROUP_AMOUNT|{age_group}\t{amount}")
        print(f"AGE_GROUP_COUNT|{age_group}\t1")
        print(f"MONTH_AMOUNT|{month}\t{amount}")
        print(f"MONTH_COUNT|{month}\t1")
        print(f"DAILY_AMOUNT|{date}\t{amount}")
        print(f"WEEKDAY_COUNT|{weekday}\t1")
        print(f"HOUR_COUNT|{int(hour):02d}\t1")
        print(f"AMOUNT_BAND_COUNT|{band}\t1")

    except (ValueError, StopIteration, csv.Error):
        continue
