# Dataset Information

## Dataset
Bank Customer Segmentation (bank transactions), Kaggle

## Official Source
https://www.kaggle.com/datasets/shivamb/bank-customer-segmentation

## Original Dataset
- Original file: bank_transactions.csv (approximately 65 MB)
- Original records: 1,048,567
- Original columns: 9 (TransactionID, CustomerID, CustomerDOB, CustGender, CustLocation, CustAccountBalance, TransactionDate, TransactionTime, TransactionAmount (INR))

## Project Data Files
The original dataset is included here as `bank_transactions_original.csv`. Running the scripts (or `../run_all.sh`) creates:
- bank_transactions.csv: standardized column names (approximately 65 MB)
- bank_transactions_clean.csv: cleaned dataset with derived columns (approximately 79 MB)
- bank_transactions_hadoop.csv: headerless CSV prepared for Hadoop MapReduce (approximately 79 MB)

## Cleaning
The cleaning process excludes invalid or missing gender, missing location, missing account balance, non-positive amounts and invalid or placeholder birth dates.

- Cleaned records: 983,040
- Cleaned columns: 12

Download the original dataset from the Kaggle link above and follow the project scripts to reproduce the processing steps.
