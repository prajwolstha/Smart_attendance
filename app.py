import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
from datetime import datetime

st.set_page_config(page_title="Smart AI Attendance", layout="wide")
python_exe = sys.executable 

st.sidebar.title("System Menu")
choice = st.sidebar.selectbox("Select Action", ["Dashboard", "Enrollment", "Live Attendance"])

def get_data():
    conn = sqlite3.connect('database/attendance.db')
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    conn.close()
    # Date column lai proper format ma rakheko filter garna sajilo huncha
    df['date'] = pd.to_datetime(df['date'])
    return df

if choice == "Dashboard":
    st.title("📊 Attendance Analytics & Export")
     
    if os.path.exists('database/attendance.db'):
        df = get_data()
        
        # --- FILTERS SECTION ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Individual Filter
            names = ["All"] + list(df['name'].unique())
            selected_user = st.selectbox("Select Person", names)
            
        with col2:
            # Monthly Filter
            df['month_year'] = df['date'].dt.strftime('%B %Y')
            months = ["All"] + list(df['month_year'].unique())
            selected_month = st.selectbox("Select Month", months)

        # Apply Filters
        filtered_df = df.copy()
        if selected_user != "All":
            filtered_df = filtered_df[filtered_df['name'] == selected_user]
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df['month_year'] == selected_month]

        # Display Data
        st.dataframe(filtered_df[['name', 'date', 'time']], width="stretch")
        
        # --- EXPORT SECTION ---
        st.subheader("📥 Export Attendance")
        export_col = st.columns(3)
        
        file_name = f"Attendance_{selected_user}_{selected_month}.csv"
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label=f"Download {selected_user} {selected_month} Report",
            data=csv,
            file_name=file_name,
            mime='text/csv',
        )

elif choice == "Enrollment":
    st.title("👤 Register New Student")
    # Browser mai name type garne
    student_name = st.text_input("Enter Student Full Name")
    
    if st.button("Start Capture"):
        if student_name:
            clean_name = student_name.strip().replace(" ", "_")
            st.info(f"Capturing photos for {clean_name}... Please look at the camera window.")
            # Pass the name directly to the script so terminal doesn't ask
            subprocess.run([python_exe, "enroll.py", clean_name])
            st.success("Enrollment Finished Successfully!")
        else:
            st.error("Please enter a name in the box above!")

elif choice == "Live Attendance":
    st.title("📹 Live Recognition")
    if st.button("Start Marking Attendance"):
        subprocess.run([python_exe, "attendance.py"])