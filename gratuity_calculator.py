import streamlit as st
from datetime import date, timedelta
import pandas as pd
from io import BytesIO
import calendar

st.set_page_config(page_title="Manual Gratuity Calculator", layout="wide")

# ---------- Custom Styling ----------
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stDownloadButton button {
        background-color: #4CAF50;
        color: white;
        padding: 0.6em 1.2em;
        border-radius: 8px;
        border: none;
    }
    .stButton button {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #2c3e50;'>UAE Gratuity Calculator</h1>
    <p style='text-align: center; color: grey;'>Multi-Employee Entry with Yearly and Monthly Breakdown</p>
""", unsafe_allow_html=True)

# --------- Session State ---------
if "employee_data" not in st.session_state:
    st.session_state.employee_data = []
if "processed" not in st.session_state:
    st.session_state.processed = False
if "remove_index" not in st.session_state:
    st.session_state.remove_index = None

# --------- Date Selection ---------
st.markdown("### 🗓️ Provision Date")
as_of_date = st.date_input("Gratuity Provision As of", date.today())

# --------- Employee Entry Form ---------
st.markdown("### 👥 Add Employee Details")
with st.form("employee_form"):
    col1, col2, col3 = st.columns(3)
    emp_name = col1.text_input("Employee Name")
    doj = col2.date_input("Date of Joining", date(2020, 1, 1))
    basic_salary = col3.number_input("Basic Salary (AED)", min_value=0.0, value=10000.0)

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
            st.session_state.processed = False

# --------- Helper Functions ---------
def calculate_gratuity(doj, basic_salary, as_of):
    # Check eligibility (minimum 1 year of service)
    if doj + timedelta(days=365) > as_of:
        return 0.0, 0, 0, 0.0, 0.0, [], False

    current = doj.replace(day=1)  # Start from month of joining
    total_prov = 0
    count_months = 0
    monthly_rows = []

    while current <= as_of:
        count_months += 1
        rate_applied = "21 days" if count_months <= 60 else "30 days"
        rate = (21 / 30) * basic_salary / 12 if count_months <= 60 else basic_salary / 12
        total_prov += rate
        monthly_rows.append((current.strftime("%b %Y"), round(rate, 2), rate_applied))

        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1, day=1)
        else:
            current = current.replace(month=current.month + 1, day=1)

    years = count_months // 12
    rem_months = count_months % 12
    yearly_21 = (21 / 30) * basic_salary
    yearly_30 = basic_salary
    return round(total_prov, 2), years, rem_months, yearly_21, yearly_30, monthly_rows, True

def generate_yearly_breakup(emp_name, doj, years, rem_months, yearly_21, yearly_30, as_of, eligible):
    if not eligible:
        return []
    rows = []
    provision_start = doj
    for i in range(1, years + 1):
        provision = yearly_21 if i <= 5 else yearly_30
        end_date = provision_start.replace(year=provision_start.year + i)
        rows.append({
            "Employee": emp_name,
            "Year": f"Year {i}",
            "End Date": end_date,
            "Provision (AED)": round(provision, 2),
            "Rate Applied": "21 days" if i <= 5 else "30 days"
        })
    if rem_months > 0:
        monthly_rate = yearly_30 / 12 if years >= 5 else yearly_21 / 12
        rows.append({
            "Employee": emp_name,
            "Year": f"Extra {rem_months} Month(s)",
            "End Date": as_of,
            "Provision (AED)": round(monthly_rate * rem_months, 2),
            "Rate Applied": "Monthly"
        })
    return rows

def generate_monthly_breakup(emp_name, monthly_rows):
    return [
        {
            "Employee": emp_name,
            "Month": month,
            "Provision (AED)": provision,
            "Rate Applied": rate
        } for month, provision, rate in monthly_rows
    ]

# --------- Display Entries with Remove Option ---------
if st.session_state.employee_data:
    st.markdown("### 🧾 Entries Added")
    for i, emp in enumerate(st.session_state.employee_data):
        with st.container():
            cols = st.columns([2, 2, 2, 2, 1])
            cols[0].markdown(f"👤 **{emp['Employee Name']}**")
            cols[1].markdown(f"📅 **{emp['Date of Joining'].strftime('%d-%b-%Y')}**")
            cols[2].markdown(f"💰 **AED {emp['Basic Salary (AED)']:,.2f}**")
            if cols[4].button("❌ Remove", key=f"remove_{i}"):
                st.session_state.remove_index = i

    if st.session_state.remove_index is not None:
        st.session_state.employee_data.pop(st.session_state.remove_index)
        st.session_state.remove_index = None
        st.session_state.processed = False
        st.rerun()

    colA, colB = st.columns([1, 1.2])
    with colA:
        if st.button("✅ Process Gratuity Calculations"):
            st.session_state.processed = True
    with colB:
        if st.button("🗑️ Reset All Entries"):
            st.session_state.employee_data = []
            st.session_state.processed = False
            st.success("✅ All entries cleared.")
            st.rerun()

# --------- Show Processed Results ---------
if st.session_state.processed:
    st.markdown("### 📋 Gratuity Summary")

    summary_data, yearly_data, monthly_data = [], [], []

    for emp in st.session_state.employee_data:
        name = emp["Employee Name"]
        doj = emp["Date of Joining"]
        salary = emp["Basic Salary (AED)"]

        total, yrs, mos, y21, y30, monthly_rows, eligible = calculate_gratuity(doj, salary, as_of_date)

        summary_data.append({
            "Employee Name": name,
            "Date of Joining": doj,
            "Basic Salary (AED)": salary,
            "Years": yrs,
            "Months": mos,
            "Eligible": "Yes" if eligible else "No",
            "Total Provision (AED)": total
        })

        yearly_data += generate_yearly_breakup(name, doj, yrs, mos, y21, y30, as_of_date, eligible)
        monthly_data += generate_monthly_breakup(name, monthly_rows)

    df_summary = pd.DataFrame(summary_data)
    df_yearly = pd.DataFrame(yearly_data)
    df_monthly = pd.DataFrame(monthly_data)

    st.dataframe(df_summary, use_container_width=True)
    st.subheader(f"📊 Total Provision (Eligible Only): AED {df_summary['Total Provision (AED)'].sum():,.2f}")

    with st.expander("📆 Yearly Provision Breakdown"):
        st.dataframe(df_yearly, use_container_width=True)

    with st.expander("🗓️ Monthly Provision Breakdown"):
        st.dataframe(df_monthly, use_container_width=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, index=False, sheet_name="Summary")
        df_yearly.to_excel(writer, index=False, sheet_name="Yearly Breakdown")
        df_monthly.to_excel(writer, index=False, sheet_name="Monthly Breakdown")

    st.download_button("📥 Download Excel Report", data=output.getvalue(), file_name="gratuity_report.xlsx")
