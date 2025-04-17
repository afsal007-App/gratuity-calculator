# 📁 gratuity_manual_entry.py

import streamlit as st
from datetime import date, datetime
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Manual Gratuity Calculator", layout="wide")
st.title("📝 UAE Gratuity Calculator – Manual Multi-Employee Entry")

# --------- Session State Setup ---------
if "employee_data" not in st.session_state:
    st.session_state.employee_data = []

# --------- Date Selection ---------
as_of_date = st.date_input("Gratuity Provision As of", date.today())

# --------- Employee Entry Form ---------
with st.form("employee_form"):
    st.subheader("Enter Employee Details")

    col1, col2, col3 = st.columns(3)
    with col1:
        emp_name = st.text_input("Employee Name")
    with col2:
        doj = st.date_input("Date of Joining", date(2020, 1, 1))
    with col3:
        basic_salary = st.number_input("Basic Salary (AED)", min_value=0.0, value=10000.0)

    submitted = st.form_submit_button("➕ Add Employee")
    if submitted:
        if doj >= as_of_date:
            st.error("❌ Date of joining must be before the 'As of' date.")
        elif not emp_name.strip():
            st.error("❌ Employee Name is required.")
        else:
            st.session_state.employee_data.append({
                "Employee Name": emp_name.strip(),
                "Date of Joining": doj,
                "Basic Salary (AED)": basic_salary
            })
            st.success(f"✅ Added {emp_name.strip()}")

# --------- Helper Function ---------
def calculate_gratuity(doj, basic_salary, as_of):
    months = (as_of.year - doj.year) * 12 + (as_of.month - doj.month)
    if as_of.day < doj.day:
        months -= 1

    years = months // 12
    rem_months = months % 12

    first_5 = min(5, years)
    after_5 = max(0, years - 5)

    yearly_21 = (21 / 30) * basic_salary
    yearly_30 = basic_salary
    monthly_rate = yearly_30 / 12 if years >= 5 else yearly_21 / 12

    provision = first_5 * yearly_21 + after_5 * yearly_30 + rem_months * monthly_rate
    return round(provision, 2), years, rem_months

# --------- Display Table ---------
if st.session_state.employee_data:
    st.subheader("📋 Employee Gratuity Table")

    records = []
    for emp in st.session_state.employee_data:
        provision, years, months = calculate_gratuity(emp["Date of Joining"], emp["Basic Salary (AED)"], as_of_date)
        records.append({
            "Employee Name": emp["Employee Name"],
            "Date of Joining": emp["Date of Joining"],
            "Basic Salary (AED)": emp["Basic Salary (AED)"],
            "Years": years,
            "Months": months,
            "Total Provision (AED)": provision
        })

    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True)

    st.subheader(f"📊 Total Provision: AED {df['Total Provision (AED)'].sum():,.2f}")

    # --------- Download Button ---------
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Gratuity Summary")
        writer.save()
    st.download_button("📥 Download as Excel", data=output.getvalue(), file_name="manual_gratuity_summary.xlsx")

# --------- Reset Button ---------
if st.button("🗑️ Reset All Entries"):
    st.session_state.employee_data = []
    st.experimental_rerun()
