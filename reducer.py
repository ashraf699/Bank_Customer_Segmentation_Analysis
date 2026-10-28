#!/usr/bin/env python3
import sys

current_key = None
total = 0.0

for line in sys.stdin:
    line = line.rstrip("\n")

    if "\t" not in line:
        continue

    key, value = line.split("\t", 1)

    try:
        value = float(value)
    except ValueError:
        continue

    if key == current_key:
        total += value
    else:
        if current_key is not None:
            print(f"{current_key}\t{total:.2f}")

        current_key = key
        total = value

if current_key is not None:
    print(f"{current_key}\t{total:.2f}")
