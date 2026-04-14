import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="smart attendance system", layout="wide", initial_sidebar_state="collapsed")
python_exe = sys.executable 
CSV_RECORDS = "database/student_details.csv"
ATTENDANCE_DB = "database/attendance.db"

# Ensure directories exist
os.makedirs("database", exist_ok=True)

# Initialize CSV for student details if it doesn't exist
if not os.path.exists(CSV_RECORDS):
    df_init = pd.DataFrame(columns=["Name", "Roll", "Semester", "Program", "Enroll_Date"])
    df_init.to_csv(CSV_RECORDS, index=False)

# --- SESSION STATE FOR LOGIN ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- MODERN NAVIGATION (Top Bar Style) ---
if st.session_state.admin_logged_in:
    # Top header for Admin
    nav_col1, nav_col2, nav_col3 = st.columns([6, 2, 1])
    with nav_col1:
        st.subheader("🚀 Smart Attendance Admin")
    with nav_col2:
        page = st.selectbox("Navigation", ["Dashboard", "Live Attendance"], label_visibility="collapsed")
    with nav_col3:
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()
else:
    # Top header for Guest
    nav_col1, nav_col2 = st.columns([8, 2])
    with nav_col1:
        st.subheader("🚀 Smart Attendance System")
    with nav_col2:
        page = st.selectbox("Menu", ["Live Attendance", "Admin Login"], label_visibility="collapsed")

st.divider()

# --- PAGE LOGIC ---

# 1. LIVE ATTENDANCE
if page == "Live Attendance":
    st.title("📹 Facial Recognition Attendance")
    st.info("System matches your face and verifies for 4 seconds.")
    if st.button("Start Camera", type="primary", use_container_width=True):
        subprocess.run([python_exe, "attendance.py"])

# 2. ADMIN LOGIN
elif page == "Admin Login":
    st.title("🔐 Admin Portal")
    col_l, col_r = st.columns([1, 1])
    with col_l:
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Verify Identity", use_container_width=True, type="primary"):
            if user == "admin" and password == "admin123": 
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid credentials.")

# 3. ADMIN DASHBOARD
elif page == "Dashboard":
    # --- METRICS SECTION ---
    df_details = pd.read_csv(CSV_RECORDS)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Students", len(df_details))
    
    # Calculate Today's Attendance
    if os.path.exists(ATTENDANCE_DB):
        conn = sqlite3.connect(ATTENDANCE_DB)
        today = datetime.now().strftime('%Y-%m-%d')
        present_today = pd.read_sql_query(f"SELECT COUNT(DISTINCT name) as c FROM attendance WHERE date='{today}'", conn)['c'][0]
        conn.close()
    else:
        present_today = 0
        
    m2.metric("Present Today", present_today)
    m3.metric("Programs", len(df_details['Program'].unique()) if len(df_details)>0 else 0)
    m4.metric("Status", "System Online")

    # --- MAIN TABS ---
    tab1, tab2, tab3 = st.tabs(["📋 Student Directory", "➕ New Enrollment", "⚙️ Model Training"])

    # TAB 1: REGISTERED STUDENTS LIST WITH FILTERS
    with tab1:
        st.subheader("Student Database")
        if not df_details.empty:
            # Filter Row
            f1, f2, f3 = st.columns(3)
            search = f1.text_input("Search Name")
            filter_sem = f2.multiselect("Filter Semester", options=df_details['Semester'].unique())
            filter_prog = f3.multiselect("Filter Program", options=df_details['Program'].unique())

            # Applying logic
            filtered_df = df_details.copy()
            if search:
                filtered_df = filtered_df[filtered_df['Name'].str.contains(search, case=False)]
            if filter_sem:
                filtered_df = filtered_df[filtered_df['Semester'].isin(filter_sem)]
            if filter_prog:
                filtered_df = filtered_df[filtered_df['Program'].isin(filter_prog)]

            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.info("No students registered yet.")

    # TAB 2: ENROLLMENT FORM
    with tab2:
        st.subheader("Add New Student")
        with st.form("enroll_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            new_name = col_a.text_input("Full Name")
            new_roll = col_b.text_input("Roll Number")
            new_sem = col_a.selectbox("Semester", ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th"])
            new_prog = col_b.selectbox("Program", ["BCA", "CSIT", "BBM", "BBA", "B.Tech"])
            
            if st.form_submit_button("Capture Biometrics", use_container_width=True):
                if new_name and new_roll:
                    # Save to CSV
                    entry = pd.DataFrame([[new_name, new_roll, new_sem, new_prog, datetime.now().strftime("%Y-%m-%d")]], 
                                         columns=["Name", "Roll", "Semester", "Program", "Enroll_Date"])
                    df_details = pd.concat([df_details, entry], ignore_index=True)
                    df_details.to_csv(CSV_RECORDS, index=False)
                    
                    # Call enrollment script
                    subprocess.run([python_exe, "enroll.py", new_name.strip().replace(" ", "_")])
                    st.success(f"Successfully enrolled {new_name}")
                    st.rerun()

    # TAB 3: TRAINING
    with tab3:
        st.subheader("Update Recognition Brain")
        st.write("Clicking this button will process all enrolled photos into the AI model.")
        if st.button("🔥 Sync & Train Model", type="primary", use_container_width=True):
            with st.spinner("Training..."):
                subprocess.run([python_exe, "train.py"])
            st.success("System updated successfully!")