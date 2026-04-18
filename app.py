import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import subprocess
from datetime import datetime, timedelta
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="Orchid Admin Portal", layout="wide", page_icon="🏫")

# --- MODERN UI STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    [data-testid="stSidebar"] { background-color: #111827; }
    .main-header { font-size: 2.5rem; color: #111827; font-weight: 700; margin-bottom: 1rem; }
    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #e5e7eb;
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

python_exe = sys.executable 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATTENDANCE_DB = os.path.join(BASE_DIR, "database", "attendance.db")
CSV_RECORDS = os.path.join(BASE_DIR, "database", "student_details.csv")

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# --- SIDEBAR NAV (Modern Selectbox) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3449/3449692.png", width=70)
    st.title("Orchid Portal")
    
    if st.session_state.admin_logged_in:
        # Replaced Radio with Selectbox for modern feel
        page = st.selectbox("MENU", ["📊 Analytics Dashboard", "📹 Attendance Camera", "👥 Student Management"])
        if st.button("Logout", use_container_width=True):
            st.session_state.admin_logged_in = False
            st.rerun()
    else:
        page = st.selectbox("GUEST MENU", ["📹 Attendance Camera", "🔐 Admin Login"])

# --- CORE FUNCTIONS ---
def get_conn():
    return sqlite3.connect(ATTENDANCE_DB) if os.path.exists(ATTENDANCE_DB) else None

# --- PAGES ---

if "Camera" in page:
    st.markdown('<h1 class="main-header">📹 Attendance Scanner</h1>', unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    with c1:
        st.info("The camera will close automatically once your attendance is recorded.")
        if st.button("LAUNCH SCANNER", type="primary", use_container_width=True):
            subprocess.run([python_exe, "attendance.py"])
            st.success("Attendance Captured! You can check the dashboard now.")

elif "Login" in page:
    st.title("Admin Access")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "admin" and p == "admin123":
                st.session_state.admin_logged_in = True
                st.rerun()
            else: st.error("Invalid credentials")

elif "Analytics Dashboard" in page:
    st.markdown('<h1 class="main-header">System Analytics</h1>', unsafe_allow_html=True)
    df_details = pd.read_csv(CSV_RECORDS)
    conn = get_conn()
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    today = datetime.now().strftime('%Y-%m-%d')
    present = 0
    if conn:
        try: present = pd.read_sql(f"SELECT COUNT(DISTINCT name) FROM attendance WHERE date='{today}'", conn).iloc[0,0]
        except: pass
    
    m1.metric("Enrolled", len(df_details))
    m2.metric("Present Today", present)
    m3.metric("System Status", "Active", delta="Ready")

    st.markdown("---")
    
    # Graphs
    g1, g2 = st.columns(2)
    with g1:
        if conn:
            trend = pd.read_sql("SELECT date, COUNT(name) as count FROM attendance GROUP BY date ORDER BY date DESC LIMIT 7", conn)
            fig = px.line(trend, x='date', y='count', title="Weekly Volume", markers=True)
            st.plotly_chart(fig, use_container_width=True)
    with g2:
        if not df_details.empty:
            fig2 = px.pie(df_details, names='Program', title="Student Base by Program", hole=0.5)
            st.plotly_chart(fig2, use_container_width=True)

elif "Student Management" in page:
    st.markdown('<h1 class="main-header">Management Portal</h1>', unsafe_allow_html=True)
    df_details = pd.read_csv(CSV_RECORDS)
    
    tab1, tab2, tab3 = st.tabs(["📋 Reports", "➕ Enrollment", "⚙️ AI Sync"])
    
    with tab1:
        # Replacing Radio with Selectbox for report type
        view_mode = st.selectbox("View Records For:", ["Class-wise", "Individual Student"])
        conn = get_conn()
        
        if conn:
            if view_mode == "Class-wise":
                c1, c2 = st.columns(2)
                d = c1.date_input("Date", datetime.now())
                prog = c2.selectbox("Program", df_details['Program'].unique())
                
                query = f"SELECT name, time FROM attendance WHERE date='{d}'"
                att_df = pd.read_sql(query, conn)
                
                # Normalization
                att_df['m_name'] = att_df['name'].str.replace("_", " ").str.lower()
                df_details['m_name'] = df_details['Name'].str.replace("_", " ").str.lower()
                
                report = pd.merge(df_details[df_details['Program']==prog], att_df, on='m_name')
                st.table(report[['Name', 'Roll', 'time']])
                
            else:
                selected = st.selectbox("Search Student Name", sorted(df_details['Name'].unique()))
                # PROBLEM 1 FIX: Match both spaced and underscored versions
                search_name = selected.replace(" ", "_")
                query = f"SELECT date, time FROM attendance WHERE name = '{selected}' OR name = '{search_name}'"
                hist = pd.read_sql(query, conn)
                
                if not hist.empty:
                    st.dataframe(hist, use_container_width=True)
                else:
                    st.warning("No attendance records found for this student.")

    with tab2:
        with st.form("enroll"):
            n = st.text_input("Full Name")
            r = st.text_input("Roll")
            p = st.selectbox("Program", ["BCA", "CSIT", "BBM"])
            if st.form_submit_button("Enroll"):
                new_data = pd.DataFrame([[n, r, "1st", p, today]], columns=df_details.columns)
                pd.concat([df_details, new_data]).to_csv(CSV_RECORDS, index=False)
                subprocess.run([python_exe, "enroll.py", n.replace(" ", "_")])
                st.success("Done!")

    with tab3:
        if st.button("Retrain AI Model"):
            subprocess.run([python_exe, "train.py"])
            st.success("Encodings Updated")