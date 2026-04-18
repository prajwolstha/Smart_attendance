import streamlit as st
import pandas as pd
import sqlite3
import os
import glob
import base64
import plotly.express as px

# --- CONFIGURATION ---
st.set_page_config(page_title="Orchid Student Portal", layout="wide", page_icon="🎓")

# --- CSS FOR NON-SCROLLABLE SIDEBAR & PURPLE THEME ---
st.markdown("""
    <style>
    /* Remove default Streamlit gaps and disable main scrolling if needed */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Sidebar container: Fixed height, no scrolling */
    section[data-testid="stSidebar"] > div {
        height: 100vh;
        overflow: hidden; 
        display: flex;
        flex-direction: column;
        padding: 0px !important; /* Removes white block above image */
    }

    /* White Background for Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        min-width: 300px !important;
        border-right: 1px solid #eee;
    }
    
    /* Profile Section - Starts at the very top */
    .profile-container {
        padding: 30px 20px;
        text-align: center;
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
    }
    .profile-pic {
        width: 120px; height: 120px;
        object-fit: cover;
        border: 4px solid #6f42c1;
        border-radius: 50%;
        margin-bottom: 10px;
    }
    .profile-info h3 { 
        margin: 0; 
        font-size: 1.2rem; 
        color: #333; 
        text-transform: capitalize;
    }

    /* Menu Container - Adjusts to fit screen */
    .menu-container {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }

    /* Fixed Size Menu Items - Uniform Purple Selection */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important; /* Slightly shorter to ensure no scroll on small screens */
        border: none !important;
        border-radius: 0px !important;
        background-color: transparent !important;
        color: #555 !important;
        text-align: left !important;
        padding: 0px 30px !important;
        font-size: 15px !important;
        margin: 0px !important;
        display: flex !important;
        align-items: center !important;
        border-left: 5px solid transparent !important;
    }
    
    /* Hover and Selection Effect */
    div.stButton > button:hover {
        background-color: #f3f0ff !important;
        color: #6f42c1 !important;
        border-left: 5px solid #6f42c1 !important;
    }

    /* Content Styling */
    .info-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #6f42c1;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "attendance.db")
CSV_PATH = os.path.join(BASE_DIR, "database", "student_details.csv")
FACES_DIR = os.path.join(BASE_DIR, "dataset", "all_faces")

def get_img_64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def find_photo(name):
    pattern = os.path.join(FACES_DIR, f"{name.replace(' ', '_')}_*.jpg")
    files = glob.glob(pattern)
    return files[0] if files else None

@st.dialog("Confirm Logout")
def logout_confirm():
    st.write("Are you sure you want to log out?")
    c1, c2 = st.columns(2)
    if c1.button("Yes", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    if c2.button("No", use_container_width=True):
        st.rerun()

# --- LOGIN ---
if 'student_name' not in st.session_state:
    st.title("🎓 Orchid Portal")
    u_in = st.text_input("Name:")
    if st.button("Enter"):
        df = pd.read_csv(CSV_PATH)
        if u_in.lower() in df['Name'].str.lower().values:
            st.session_state.student_name = df[df['Name'].str.lower() == u_in.lower()]['Name'].values[0]
            st.session_state.page = "Dashboard"
            st.rerun()
    st.stop()

# --- LOAD DATA ---
user = st.session_state.student_name
df_students = pd.read_csv(CSV_PATH)
s_info = df_students[df_students['Name'] == user].iloc[0]

# --- SIDEBAR ---
with st.sidebar:
    # Profile Section - Starts at top
    pic = find_photo(user)
    st.markdown('<div class="profile-container">', unsafe_allow_html=True)
    if pic:
        st.markdown(f'<img src="data:image/jpeg;base64,{get_img_64(pic)}" class="profile-pic">', unsafe_allow_html=True)
    st.markdown(f'<div class="profile-info"><h3>{user}</h3></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Menu items
    if st.button("🏠 Dashboard"): st.session_state.page = "Dashboard"
    if st.button("👤 Profile"): st.session_state.page = "Profile"
    if st.button("📅 Attendance"): st.session_state.page = "Attendance"
    if st.button("📖 Syllabus"): st.session_state.page = "Syllabus"
    if st.button("🏫 Weekly Classes"): st.session_state.page = "Classes"
    
    # Push logout to the absolute bottom of sidebar
    st.markdown('<div style="margin-top: auto; border-top: 1px solid #eee;">', unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        logout_confirm()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE ROUTING ---
pg = st.session_state.page
# --- PAGE ROUTING ---
pg = st.session_state.get('page', 'Dashboard') # cite: image_f1427f.png

# Ensure current_user is defined for all pages using the session state
if 'student_name' in st.session_state:
    current_user = st.session_state.student_name # cite: image_f0cad7.png
else:
    st.error("Session expired. Please log in again.")
    st.stop()
if pg == "Dashboard":
    st.title("🏠 Student Dashboard")
    
    # --- DATA FETCHING ---
    conn = sqlite3.connect(DB_PATH)
    db_name = current_user.replace(" ", "_") # cite: image_f0cad7.png
    query = f"SELECT date FROM attendance WHERE name IN ('{current_user}', '{db_name}')"
    df_att = pd.read_sql(query, conn)
    conn.close()

    # --- TOP METRIC CARDS ---
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="info-card"><h2>{len(df_att)}</h2><p>Days Attended</p></div>', unsafe_allow_html=True) # cite: image_f0cad7.png
    with c2:
        st.markdown(f'<div class="info-card"><h2>{s_info["Semester"]}</h2><p>Current Semester</p></div>', unsafe_allow_html=True) # cite: image_eff066.png

    st.markdown("### Simple Attendance Summary")
    
    if not df_att.empty:
        col_left, col_right = st.columns(2)
        
        with col_left:
            # 1. SIMPLE DONUT CHART (Presence vs Absence)
            # Assuming a standard 60-day semester goal
            total_goal = 60
            attended = len(df_att)
            missed = max(0, total_goal - attended)
            
            fig_donut = px.pie(
                values=[attended, missed], 
                names=['Present', 'Remaining'],
                hole=0.6,
                color_discrete_sequence=['#6f42c1', '#f3f0ff'], # Purple theme cite: image_f0cad7.png
                title="Semester Progress"
            )
            fig_donut.update_layout(height=300, showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)

        with col_right:
            # 2. SIMPLE WEEKLY BAR CHART (Last 7 Entries)
            df_att['date'] = pd.to_datetime(df_att['date'])
            # Get count of attendance per day for the last few entries
            df_recent = df_att.groupby('date').size().reset_index(name='count').tail(7)
            
            fig_bar = px.bar(
                df_recent, 
                x='date', 
                y='count',
                title="Recent Activity",
                color_discrete_sequence=['#6f42c1'] # cite: image_f0cad7.png
            )
            # Clean up axes for easier reading
            fig_bar.update_layout(height=300, margin=dict(t=30, b=0, l=0, r=0))
            fig_bar.update_yaxes(visible=False) # Hide count since it's usually 1 per day
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No attendance records found yet.")
elif pg == "Profile":
    st.title("👤 My Info")
    st.markdown(f"""<div class="info-card">
        <p><b>Name:</b> {s_info['Name']}</p>
        <p><b>Roll:</b> {s_info['Roll']}</p>
        <p><b>Program:</b> {s_info['Program']}</p>
        <p><b>Semester:</b> {s_info['Semester']}</p>
    </div>""", unsafe_allow_html=True)

elif pg == "Classes":
    st.title("🏫 Schedule")
    st.markdown("""<div class="info-card">
        <h4 style="color:#6f42c1;">Sunday - Tuesday</h4><p>Mobile Programming</p><p>Distributed Systems</p>
        <hr><h4 style="color:#6f42c1;">Wednesday - Friday</h4><p>Applied Economics</p><p>Advanced Java</p>
    </div>""", unsafe_allow_html=True)

elif pg == "Attendance":
    st.title("📅 Attendance Tracking")
    
    # --- DATA RETRIEVAL ---
    conn = sqlite3.connect(DB_PATH)
    db_name = current_user.replace(" ", "_") # Matches 'Prajwol_shrestha'
    
    # Query checking both formats to ensure data displays
    query = f"SELECT date, time FROM attendance WHERE name IN ('{current_user}', '{db_name}')"
    df_att = pd.read_sql(query, conn)
    conn.close()

    if not df_att.empty:
        # Metrics Card
        st.markdown(f"""
        <div class="info-card">
            <h3>Total Presence: {len(df_att)} Days</h3>
            <p>Your attendance is being tracked via the Smart Attendance System.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Detailed Log Table
        st.markdown("### Detailed Entry Log")
        st.dataframe(df_att.sort_values(by='date', ascending=False), use_container_width=True)
    else:
        st.warning(f"No attendance records found for {current_user}. Please ensure the name matches your face-registration ID.")
elif pg == "Syllabus":
    st.title("📖 Course Syllabus")
    
    # 1. Get the student's program and semester from the CSV data
    student_program = s_info['Program']  # Matches 'BCA' or 'CSIT'
    student_semester = s_info['Semester'] # Matches '6th', '1st', etc.
    
    # 2. Extract only the number (e.g., '1' from '1st') for flexible matching
    sem_digit = ''.join(filter(str.isdigit, student_semester)) 
    
    # 3. Connect to DB and filter strictly by PROGRAM and SEMESTER
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT subject, link 
        FROM syllabus 
        WHERE program = '{student_program}' 
        AND semester LIKE '%{sem_digit}%'
    """
    df_syl = pd.read_sql(query, conn)
    conn.close()

    if not df_syl.empty:
        st.info(f"Showing {student_program} Syllabus - Semester {student_semester}")
        for _, row in df_syl.iterrows():
            with st.expander(f"📚 {row['subject']}"):
                st.write(f"Official curriculum for {row['subject']}.")
                if row['link']:
                    st.link_button("View Details", row['link'])
    else:
        st.warning(f"No syllabus found for {student_program} Semester {sem_digit}.")