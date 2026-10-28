#!/usr/bin/env bash
# Runs the whole pipeline offline. Prerequisite:
#   input/bank_transactions_original.csv (the Kaggle file) must exist.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -f input/bank_transactions_original.csv ]; then
  echo "Missing input/bank_transactions_original.csv"; exit 1
fi
python3 convert_to_csv.py
python3 inspect_data.py
python3 clean_data.py
./run_local_mapreduce.sh
python3 visualize_results.py
echo "Done. Start the dashboard with: streamlit run dashboard.py"
