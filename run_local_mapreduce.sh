#!/usr/bin/env bash
# Runs the exact same mapper.py / reducer.py that Hadoop Streaming uses, with the
# Unix pipeline that mimics Hadoop's map -> shuffle & sort -> reduce phases.
# Useful for testing without a Hadoop cluster.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
export LC_ALL=C
time (cat input/bank_transactions_hadoop.csv | python3 mapper.py | sort -t$'\t' -k1,1 | python3 reducer.py > results/mapreduce_output.txt)
echo "Output records: $(wc -l < results/mapreduce_output.txt)"
