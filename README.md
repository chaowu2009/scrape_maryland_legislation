
# Maryland House Bill 2025 Project

This project was developed as part of the 2025 MIT Breakthrough Tech AI program.

## Project Overview

The objective is to create a machine learning model to predict whether a legislative bill will pass or fail. Students will work with various classification methods, including:

- Logistic Regression
- XGBoost
- Deep Learning Neural Networks
- Large Language Models (LLMs)

## Data Scraping

### `scrapper.py`
Scrapes all legislative bills for a given year. The output includes:

- `bill_xxxx.pdf`: Legislative bill document
- `bill_xxxx_fiscal_note.pdf`: Fiscal note of the bill (may not exist for all bills)
- `bill_xxxx_summary.csv`: Contains bill title, synopsis, sponsors, and status (if signed by governor, meaning Passed. Otherwise, Failed to pass)
- `bill_xxxx_witness_list.csv`: List of witnesses for the bill