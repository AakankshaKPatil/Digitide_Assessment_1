
# Interactive Loan Calculator (Streamlit)

An interactive loan calculator where users can input details (name, age, deposit, interest, duration, fees, etc.) and see results with multiple graphs and dataframes.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push this folder to a **public GitHub repo**.
2. On https://share.streamlit.io, select "New app", pick your repo and `app.py` path, then deploy.

## Features
- Multiple input types: text, numbers, sliders, selects, toggles.
- EMI calculation with amortization table.
- Charts: balance over time, stacked principal vs interest, cumulative curves.
- Download CSV for amortization schedule.
