# 📁 gratuity_calculator.py

import streamlit as st
from datetime import datetime, date
import pandas as pd

# -------------------- App Title --------------------
st.title("🧮 UAE Gratuity Provision Calculator")

# -------------------- Inputs --------------------
st.header("Enter Employee Details")

col1, col2 = st.columns(2)

with col1:
    emp_name = st.text_input("Employee Name", "Sicily George")
    doj = st.date_input("Date of Joining", date(2018, 8, 1))

with col2:
    basic_salary = st.number_input("Basic Salary (AED)", value=10000)
    as_of_date = st.date_input("Gratuity as of", date.today())

# -------------------- Calculate Provision --------------------
if doj >= as_of_date:
    st.error("Gratuity as of date must be after the date of joining.")
else:
    # Calculate number of years and months
    delta_years = as_of_date.year - doj.year
    delta_months = (as_of_date.year - doj.year) * 12 + as_of_date.month - doj.month

    # Adjust if day is earlier in the month
    if as_of_date.day < doj.day:
        delta_months -= 1

    total_years = delta_months // 12
    remaining_months = delta_months % 12

    # Gratuity provision
    first_5_years = min(5, total_years)
    after_5_years = max(0, total_years - 5)

    yearly_21_day_prov = (21 / 30) * basic_salary  # For first 5 years
    yearly_30_day_prov = basic_salary              # After 5 years

    provision_5_years = first_5_years * yearly_21_day_prov
    provision_after_5 = after_5_years * yearly_30_day_prov

    # Monthly provision based on current year of service
    if total_years < 5:
        monthly_rate = yearly_21_day_prov / 12
    else:
        monthly_rate = yearly_30_day_prov / 12

    provision_extra_months = remaining_months * monthly_rate
    total_provision = provision_5_years + provision_after_5 + provision_extra_months

    # -------------------- Output Summary --------------------
    st.subheader("📊 Gratuity Summary")
    st.markdown(f"**Employee:** {emp_name}")
    st.markdown(f"**Years of Service:** {total_years} years and {remaining_months} months")
    st.markdown(f"**Total Provision (AED):** `AED {total_provision:,.2f}`")

    st.write("---")

    # -------------------- Yearly Breakdown --------------------
    st.subheader("📆 Yearly Provision Breakdown")

    yearly_data = []
    for i in range(1, total_years + 1):
        if i <= 5:
            yearly_amt = yearly_21_day_prov
            rate = "70% (21 days)"
        else:
            yearly_amt = yearly_30_day_prov
            rate = "100% (30 days)"
        year_date = doj.replace(year=doj.year + i)
        if year_date > as_of_date:
            break
        yearly_data.append({
            "Year": f"Year {i}",
            "End Date": year_date,
            "Rate": rate,
            "Provision (AED)": round(yearly_amt, 2)
        })

    if remaining_months > 0:
        yearly_data.append({
            "Year": f"Extra {remaining_months} month(s)",
            "End Date": as_of_date,
            "Rate": f"{'100%' if total_years >= 5 else '70%'}",
            "Provision (AED)": round(provision_extra_months, 2)
        })

    df_yearly = pd.DataFrame(yearly_data)
    st.dataframe(df_yearly)

    # -------------------- Month-wise Breakdown --------------------
    st.subheader("🗓️ Monthly Provision Breakdown")
    monthly_data = []
    current = doj
    for i in range(delta_months):
        year = current.year
        month = current.month
        rate = yearly_21_day_prov/12 if (i < 60) else yearly_30_day_prov/12
        monthly_data.append({
            "Month": f"{current.strftime('%b %Y')}",
            "Provision (AED)": round(rate, 2)
        })
        # Move to next month
        if month == 12:
            current = current.replace(year=year + 1, month=1)
        else:
            current = current.replace(month=month + 1)

    df_monthly = pd.DataFrame(monthly_data)
    st.dataframe(df_monthly)
