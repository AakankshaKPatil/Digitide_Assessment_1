
import math
from datetime import date
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Interactive Loan Calculator", page_icon="💸", layout="wide")

# --- Sidebar: user profile / app options ---
with st.sidebar:
    st.header("🧑 Profile")
    name = st.text_input("Name", value="Aakanksha")
    age = st.number_input("Age", min_value=0, max_value=120, value=22, step=1)
    st.header("⚙️ Options")
    currency = st.selectbox("Currency", ["₹ INR", "$ USD", "€ EUR", "£ GBP"], index=0)
    show_amort = st.toggle("Show amortization table", value=True)
    allow_prepay = st.toggle("Enable extra monthly prepayment?", value=False)
    theme = st.radio("Chart theme", ["light", "dark"], horizontal=True)
    st.markdown("---")
    st.caption("Tip: Use the main area to change loan inputs and compare scenarios.")

st.title("💸 Interactive Loan Calculator")
st.write("Enter loan details below. The app computes EMI, total interest, and shows multiple charts and dataframes.")

# --- Main inputs ---
col1, col2, col3 = st.columns(3)
with col1:
    purchase_price = st.number_input("Purchase Price", min_value=0.0, value=1_000_000.0, step=50_000.0, format="%.2f")
    down_payment = st.number_input("Down Payment / Deposit", min_value=0.0, value=200_000.0, step=50_000.0, format="%.2f")
    interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.1, max_value=25.0, value=9.5, step=0.1)
with col2:
    tenure_years = st.slider("Loan Tenure (years)", min_value=1, max_value=40, value=20)
    frequency = st.selectbox("Repayment Frequency", ["Monthly", "Bi-weekly", "Weekly"])
    processing_fee = st.number_input("Processing Fee (one-time)", min_value=0.0, value=5_000.0, step=500.0, format="%.2f")
with col3:
    insurance = st.number_input("Insurance / Add-on (annual)", min_value=0.0, value=3_000.0, step=500.0, format="%.2f")
    taxes = st.number_input("Other Yearly Charges (taxes, etc.)", min_value=0.0, value=0.0, step=500.0, format="%.2f")
    start_date = st.date_input("Loan Start Date", value=date.today())

# Effective principal
principal = max(purchase_price - down_payment, 0.0)

# Frequency mapping
if frequency == "Monthly":
    periods_per_year = 12
elif frequency == "Bi-weekly":
    periods_per_year = 26
else:
    periods_per_year = 52

periods = tenure_years * periods_per_year
periodic_rate = (interest_rate / 100) / periods_per_year

extra_prepay = 0.0
if allow_prepay:
    extra_prepay = st.number_input("Extra payment each period", min_value=0.0, value=0.0, step=100.0, format="%.2f")

# EMI formula: A = P * r * (1+r)^n / ((1+r)^n - 1)
def payment(principal, r, n):
    if r == 0:
        return principal / n
    return principal * r * (1 + r)**n / ((1 + r)**n - 1)

scheduled_payment = payment(principal, periodic_rate, periods) if principal > 0 and periods > 0 else 0.0
gross_payment = scheduled_payment + extra_prepay

# Build amortization schedule
balance = principal
rows = []
total_interest = 0.0
total_principal = 0.0
i = 0
while balance > 0 and i < periods + 5_000:  # safety cap
    i += 1
    interest = balance * periodic_rate
    principal_component = min(gross_payment - interest, balance) if periodic_rate >= 0 else gross_payment
    if principal_component < 0:
        principal_component = 0
    closing_balance = balance - principal_component
    rows.append({
        "Period": i,
        "Opening Balance": balance,
        "Payment": gross_payment,
        "Interest": interest,
        "Principal": principal_component,
        "Closing Balance": closing_balance
    })
    total_interest += interest
    total_principal += principal_component
    balance = closing_balance
    if balance <= 0.01:
        balance = 0.0
        break

schedule = pd.DataFrame(rows)
if not schedule.empty:
    schedule[["Opening Balance","Payment","Interest","Principal","Closing Balance"]] = schedule[["Opening Balance","Payment","Interest","Principal","Closing Balance"]].round(2)

# Totals & KPIs
total_paid = total_interest + total_principal + processing_fee + (insurance + taxes) * tenure_years
months_to_payoff = len(schedule)
years_to_payoff = months_to_payoff / periods_per_year if periods_per_year else 0

k1,k2,k3,k4 = st.columns(4)
k1.metric("EMI / Periodic Payment", f"{currency.split()[0]} {gross_payment:,.2f}")
k2.metric("Total Interest", f"{currency.split()[0]} {total_interest:,.2f}")
k3.metric("Total Paid (incl. fees)", f"{currency.split()[0]} {total_paid:,.2f}")
k4.metric("Time to Payoff", f"{years_to_payoff:.2f} years ({months_to_payoff} periods)")

# Charts
if not schedule.empty:
    # Balance over time
    fig_balance = px.line(schedule, x="Period", y="Closing Balance", title="Loan Balance Over Time", template="plotly_dark" if theme=="dark" else "plotly_white")
    st.plotly_chart(fig_balance, use_container_width=True)

    # Principal vs Interest stacked by period
    fig_stack = px.area(schedule.melt(id_vars=["Period","Payment","Opening Balance","Closing Balance"], value_vars=["Principal","Interest"], var_name="Type", value_name="Amount"),
                        x="Period", y="Amount", color="Type", title="Principal vs Interest by Period",
                        template="plotly_dark" if theme=="dark" else "plotly_white")
    st.plotly_chart(fig_stack, use_container_width=True)

    # Cumulative interest vs principal
    schedule["Cum Principal"] = schedule["Principal"].cumsum()
    schedule["Cum Interest"] = schedule["Interest"].cumsum()
    fig_cum = px.line(schedule, x="Period", y=["Cum Principal","Cum Interest"], title="Cumulative Principal vs Interest",
                      template="plotly_dark" if theme=="dark" else "plotly_white")
    st.plotly_chart(fig_cum, use_container_width=True)

# Dataframes
st.subheader("🔢 Summary")
summary_df = pd.DataFrame({
    "Name":[name],
    "Age":[age],
    "Currency":[currency],
    "Principal":[round(principal,2)],
    "EMI / Periodic Payment":[round(gross_payment,2)],
    "Total Interest":[round(total_interest,2)],
    "Total Paid (incl. fees)":[round(total_paid,2)],
    "Tenure Years":[tenure_years],
    "Repayment Frequency":[frequency],
    "Payoff Periods":[months_to_payoff]
})
st.dataframe(summary_df, use_container_width=True)

if show_amort and not schedule.empty:
    st.subheader("📄 Amortization Schedule")
    st.dataframe(schedule, use_container_width=True, height=400)

# Download buttons
if not schedule.empty:
    st.download_button("Download schedule (CSV)", data=schedule.to_csv(index=False).encode("utf-8"),
                       file_name="amortization_schedule.csv", mime="text/csv")

st.caption("Built with Streamlit • Educational estimates only – verify with your lender.")
