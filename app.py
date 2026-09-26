import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import date, timedelta

# ==========================================
# DATABASE INITIALIZATION & BENCHMARK SEEDING
# ==========================================
def get_db():
    conn = sqlite3.connect("autism_inclusion_poc.db", check_same_thread=False)
    return conn

def init_and_seed_db():
    conn = get_db()
    c = conn.cursor()
    
    # 1. User Management Table (RBAC)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        full_name TEXT,
        role TEXT,
        assigned_scope TEXT
    )''')
    
    # 2. Student Registry Table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        alias_name TEXT,
        grade TEXT,
        strengths TEXT,
        challenges TEXT,
        accommodations TEXT
    )''')
    
    # 3. Risk Intake & Screening Table (Step 1)
    c.execute('''CREATE TABLE IF NOT EXISTS screenings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reporter_username TEXT,
        reporter_role TEXT,
        context TEXT,
        indicators_count INTEGER,
        concern_note TEXT,
        risk_level TEXT,
        created_at DATE
    )''')
    
    # 4. Digital Individualized Education Plan (IEP) Table (Steps 2 & 3)
    c.execute('''CREATE TABLE IF NOT EXISTS iep_plans (
        plan_id TEXT PRIMARY KEY,
        student_id TEXT,
        target_skill TEXT,
        strategy TEXT,
        lead_role TEXT,
        approved_by TEXT,
        status TEXT
    )''')
    
    # --- AUTOMATIC SCHEMA MIGRATION ---
    try:
        c.execute("ALTER TABLE iep_plans ADD COLUMN approved_by TEXT DEFAULT 'Pending Review'")
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute("ALTER TABLE progress_logs ADD COLUMN target_skill TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE progress_logs ADD COLUMN logged_by TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    try:
        c.execute("ALTER TABLE screenings ADD COLUMN reporter_username TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
        
    try:
        c.execute("ALTER TABLE transition_reviews ADD COLUMN reviewer_username TEXT DEFAULT 'tv_nam'")
    except sqlite3.OperationalError:
        pass
    # ----------------------------------

    # 5. Longitudinal Progress Log Table (Steps 4 & 5)
    c.execute('''CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id TEXT,
        student_id TEXT,
        logged_by TEXT,
        record_date DATE,
        target_skill TEXT,
        score INTEGER,
        notes TEXT
    )''')
    
    # 6. School Transition Review Table (Step 6)
    c.execute('''CREATE TABLE IF NOT EXISTS transition_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        reviewer_username TEXT,
        review_date DATE,
        summary TEXT,
        transition_plan TEXT
    )''')
    
    # Seed Default User Accounts
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        mock_users = [
            ("gv_lan", "Ms. Lan Hoang", "Homeroom / Subject Teacher", "Grades 1, 2, 3, 4, 5"),
            ("tv_nam", "Mr. Nam Tran", "School Counselor (Case Coordinator)", "School-wide (Case Triage)"),
            ("ht_minh", "Mr. Minh Le", "Special Education Support Personnel", "Technical Accommodations"),
            ("ph_huong", "Mrs. Huong (Parent of M.K)", "Parent / Guardian", "Observing HS-01")
        ]
        c.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", mock_users)
    
    # Seed 6 Standard Pediatric Benchmark Personas
    c.execute("SELECT COUNT(*) FROM students")
    if c.fetchone()[0] == 0:
        mock_students = [
            ("HS-01", "Student M.K", "Grade 1", "Rapid alphanumeric recall, visual puzzle proficiency", "Auditory hypersensitivity (school bell), meltdown on class transitions", "Noise-canceling headphones, 5-minute visual countdown timer"),
            ("HS-02", "Student T.A", "Grade 2", "High affinity for animals, strong rule compliance", "Social reciprocity deficit, isolated withdrawal during recess", "Structured peer buddy assignment during unstructured recess"),
            ("HS-03", "Student H.N", "Grade 3", "High attention to detail, rapid mental arithmetic", "Sensory overload in noise, anxiety-induced self-scratching", "3-minute sensory break card, quiet corner retreat access"),
            ("HS-04", "Student D.P", "Grade 1", "Dexterous fine motor skills, advanced Lego building", "Nonverbal/expressive speech limits, frustration tantrums", "PECS symbol communication board mounted at desk"),
            ("HS-05", "Student Q.L", "Grade 4", "Proficient text decoding, high adherence to order", "Pragmatic semantic rigidity, disorientation in unstructured group work", "Step-by-step written task checklists with explicit roles"),
            ("HS-06", "Student V.H", "Grade 5", "Spatial memory strength, Scratch coding proficiency", "Acute transition anxiety regarding secondary school shift", "Middle school campus walkthrough, personal strengths portfolio")
        ]
        c.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", mock_students)
        
        # Seed IEP Objective Records
        mock_ieps = [
            ("IEP-01", "HS-01", "Transition between lessons without distress crying", "Deploy visual timer cue 5 minutes prior to bell", "Special Education Support Personnel", "tv_nam", "Approved"),
            ("IEP-02", "HS-02", "Initiate joint play with peers at least 1x/day", "Roleplay structured play requests with designated buddy", "Homeroom / Subject Teacher", "tv_nam", "Approved"),
            ("IEP-03", "HS-03", "Independently present 'Sensory Break' card", "Nonverbal cueing when desk-tapping behavior emerges", "School Counselor (Case Coordinator)", "tv_nam", "In Progress"),
            ("IEP-04", "HS-04", "Exchange PECS icon to request learning materials", "Immediate positive reinforcement upon icon selection", "Special Education Support Personnel", "tv_nam", "Approved"),
            ("IEP-05", "HS-05", "Execute assigned group role via written checklist", "Designate explicit scribe/data recording function", "Homeroom / Subject Teacher", "tv_nam", "In Progress"),
            ("IEP-06", "HS-06", "Reduce secondary school anxiety questionnaire score", "Schedule familiarization tour before summer break", "School Counselor (Case Coordinator)", "tv_nam", "Pending Meeting")
        ]
        c.executemany("INSERT INTO iep_plans VALUES (?, ?, ?, ?, ?, ?, ?)", mock_ieps)

        today = date.today()
        mock_logs = []
        for week in range(4):
            d = today - timedelta(days=(3 - week) * 7)
            mock_logs.append(("IEP-01", "HS-01", "ht_minh", d, "Transition between lessons without distress crying", 1 + week, f"Week {week+1}: Noticeable reduction in transitional crying duration"))
            mock_logs.append(("IEP-02", "HS-02", "gv_lan", d, "Initiate joint play with peers at least 1x/day", 2 + (1 if week >= 2 else 0), f"Week {week+1}: Stood in proximity to peer playgroup"))
            mock_logs.append(("IEP-03", "HS-03", "tv_nam", d, "Independently present 'Sensory Break' card", min(5, 2 + week), f"Week {week+1}: Independently accessed quiet corner"))
        c.executemany("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, target_skill, score, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", mock_logs)

        mock_screenings = [
            ("HS-01", "gv_lan", "Homeroom / Subject Teacher", "Lesson Transitions", 3, "Covers ears and screams loudly during school bell rings", "Requires Multidisciplinary Evaluation", today - timedelta(days=35)),
            ("HS-02", "ph_huong", "Parent / Guardian", "Recess & Play", 2, "Does not initiate play with relatives; lines up toys repetitively", "Requires Routine Monitoring", today - timedelta(days=40))
        ]
        c.executemany("INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", mock_screenings)

        c.execute("""INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) 
                     VALUES ('HS-06', 'tv_nam', ?, 'Elementary goals achieved; exceptional computational aptitude', 'Transfer IEP summary and accommodations dossier to incoming middle school administration')""", (str(today),))
        
    conn.commit()
    conn.close()

init_and_seed_db()

# ==========================================
# PAGE CONFIGURATION & ROLE-BASED ACCESS CONTROL
# ==========================================
st.set_page_config(page_title="Digital Inclusion Platform for ASD", layout="wide", page_icon="🏫")
conn = get_db()

ROLE_PERMISSIONS = {
    "Homeroom / Subject Teacher": {
        "can_edit_student": True,
        "can_create_iep": False,
        "can_approve": False,
        "can_trans": False,
        "desc": "Daily observation, structured risk intake, classroom accommodation implementation, and session progress scoring."
    },
    "School Counselor (Case Coordinator)": {
        "can_edit_student": True,
        "can_create_iep": True,
        "can_approve": True,
        "can_trans": True,
        "desc": "Case triage lead, profile management, multidisciplinary meeting convener, IEP approver, and transition director."
    },
    "Special Education Support Personnel": {
        "can_edit_student": True,
        "can_create_iep": True,
        "can_approve": False,
        "can_trans": False,
        "desc": "Technical intervention specialist, SMART objective author, visual support designer, and joint progress logger."
    },
    "Parent / Guardian": {
        "can_edit_student": False,
        "can_create_iep": False,
        "can_approve": False,
        "can_trans": False,
        "desc": "Home observational screening provider, collaborative partner, and progress trajectory viewer."
    }
}

st.sidebar.title("INCLUSION PLATFORM")
st.sidebar.caption("Digital Governance Aligned with MOET Circulars 11/2024 & 21/2023")

users_df = pd.read_sql("SELECT * FROM users", conn)
user_dict = {f"{r['full_name']} ({r['role']})": r['username'] for _, r in users_df.iterrows()}

selected_user_display = st.sidebar.selectbox("👤 Select Authenticated User:", list(user_dict.keys()))
current_username = user_dict[selected_user_display]
current_user_row = users_df[users_df['username'] == current_username].iloc[0]
current_role = current_user_row['role']

st.sidebar.markdown(f"**Current Role:** `{current_role}`")
st.sidebar.info(f"📌 **Responsibilities:** {ROLE_PERMISSIONS[current_role]['desc']}")

all_steps = [
    "Architecture & System Overview",
    "Step 0: Student Profile Management",
    "Step 1: Intake & Structured Screening",
    "Step 2: Collaborative Assessment",
    "Step 3: Digital IEP Formulation",
    "Step 4 & 5: Classroom Intervention & Progress Tracking",
    "Step 6: Review & Transition Passport",
    "📊 System Analytics & Data Explorer"
]

step = st.sidebar.radio("Operational Workflow:", all_steps)

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size:12px; color:gray;'>
<b>Technical Engineering:</b><br>
MSc. Vo Thi Kim Anh (Ton Duc Thang Univ. & VSB-TU Ostrava)<br>
<b>Theoretical Foundation:</b><br>
Assoc. Prof. Dr. Nguyen Van Tuong & Dr. Le Thi Thanh Huyen (2026)
</div>
""", unsafe_allow_html=True)

# ==========================================
# SYSTEM ARCHITECTURE & WORKFLOW OVERVIEW
# ==========================================
if step == "Architecture & System Overview":
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); padding: 22px 28px; border-radius: 12px; color: white; margin-bottom: 25px;">
            <h2 style="margin:0; color:white; font-size: 26px;">Digital Platform for Autism Spectrum Disorder Inclusion in Mainstream Schools</h2>
            <p style="margin: 8px 0 0 0; opacity: 0.9; font-size: 14px;">
                Operationalizing the Multi-level Integration Model: <b>Data • Personnel • Governance</b> — Aligned with MOET Circulars 11/2024 & 21/2023
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 1. High-level KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    total_stu = len(pd.read_sql("SELECT student_id FROM students", conn))
    total_scr = len(pd.read_sql("SELECT id FROM screenings", conn))
    total_iep = len(pd.read_sql("SELECT plan_id FROM iep_plans", conn))
    total_logs = len(pd.read_sql("SELECT id FROM progress_logs", conn))
    
    kpi1.metric("Enrolled Cohort", f"{total_stu} Students")
    kpi2.metric("Intake Screenings", f"{total_scr} Records")
    kpi3.metric("Active IEP Goals", f"{total_iep} Targets")
    kpi4.metric("Logged Observations", f"{total_logs} Entries")
    
    st.write("")
    
    # 2. Closed-Loop 6-Step Workflow Pipeline
    st.subheader("The Closed-Loop 6-Step Educational Workflow Continuum")
    
    steps_html = """
    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 25px;">
        <div style="flex: 1; min-width: 150px; background: #EFF6FF; border: 1px solid #BFDBFE; border-top: 4px solid #2563EB; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #1D4ED8; text-transform: uppercase;">Step 1</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Intake & Screening</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Structured observation checklist; strictly non-diagnostic triage.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #DBEAFE; color: #1E40AF; padding: 2px 6px; border-radius: 4px; display: inline-block;">Teacher & Parent</div>
        </div>
        <div style="flex: 1; min-width: 150px; background: #FFFBEB; border: 1px solid #FDE68A; border-top: 4px solid #D97706; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #B45309; text-transform: uppercase;">Step 2</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Multisource Assessment</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Multidisciplinary meeting; reconciling school, home, and clinical data.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #FEF3C7; color: #92400E; padding: 2px 6px; border-radius: 4px; display: inline-block;">Counselor Lead</div>
        </div>
        <div style="flex: 1; min-width: 150px; background: #ECFDF5; border: 1px solid #A7F3D0; border-top: 4px solid #059669; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #047857; text-transform: uppercase;">Step 3</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Digital IEP Plan</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Measurable SMART targets with explicit institutional accountability.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #D1FAE5; color: #065F46; padding: 2px 6px; border-radius: 4px; display: inline-block;">Support Specialist</div>
        </div>
        <div style="flex: 1; min-width: 150px; background: #FAF5FF; border: 1px solid #E9D5FF; border-top: 4px solid #7C3AED; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #6D28D9; text-transform: uppercase;">Step 4</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Classroom Support</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Visual timetables, countdown timers, AAC symbols, and token boards.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #EDE9FE; color: #5B21B6; padding: 2px 6px; border-radius: 4px; display: inline-block;">Teacher & Aide</div>
        </div>
        <div style="flex: 1; min-width: 150px; background: #FDF2F8; border: 1px solid #FBCFE8; border-top: 4px solid #DB2777; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #BE185D; text-transform: uppercase;">Step 5</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Progress Tracking</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Longitudinal autonomy scores (1-5); time-series trend curves.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #FCE7F3; color: #9D174D; padding: 2px 6px; border-radius: 4px; display: inline-block;">Support Team</div>
        </div>
        <div style="flex: 1; min-width: 150px; background: #F8FAFC; border: 1px solid #CBD5E1; border-top: 4px solid #475569; border-radius: 8px; padding: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #334155; text-transform: uppercase;">Step 6</div>
            <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin: 4px 0;">Transition Passport</div>
            <div style="font-size: 11px; color: #64748B; line-height: 1.4;">Dossier handoff across academic terms preventing support fractures.</div>
            <div style="margin-top: 8px; font-size: 10px; background: #E2E8F0; color: #1E293B; padding: 2px 6px; border-radius: 4px; display: inline-block;">Counselor & Principal</div>
        </div>
    </div>
    """
    st.markdown(steps_html, unsafe_allow_html=True)
    
    # 3. Two columns: Integration Triangle & RACI Matrix
    col_triangle, col_raci = st.columns([1, 1])
    
    with col_triangle:
        st.subheader("The Three-Pillar Integration Model")
        st.markdown("""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px;">
            <div style="text-align: center; margin-bottom: 12px;">
                <div style="display: inline-block; background: #0284C7; color: white; padding: 10px 20px; border-radius: 20px; font-weight: 700; font-size: 15px;">
                    🎯 EARLY IDENTIFICATION
                </div>
            </div>
            <div style="display: flex; justify-content: space-around; align-items: center; margin: 15px 0;">
                <div style="background: #0D9488; color: white; padding: 12px 16px; border-radius: 20px; font-weight: 700; font-size: 14px; text-align: center; width: 42%;">
                    📋 ASSESSMENT<br><small style="font-weight: normal; font-size: 11px;">Educational Needs</small>
                </div>
                <div style="background: #E0E7FF; color: #3730A3; font-weight: bold; padding: 8px 14px; border-radius: 50%; font-size: 13px; text-align: center;">
                    CHILD<br>CENTER
                </div>
                <div style="background: #7C3AED; color: white; padding: 12px 16px; border-radius: 20px; font-weight: 700; font-size: 14px; text-align: center; width: 42%;">
                    🤝 INTERVENTION<br><small style="font-weight: normal; font-size: 11px;">Inside Mainstream Class</small>
                </div>
            </div>
            <hr style="margin: 12px 0; border: none; border-top: 1px dashed #CBD5E1;">
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #475569; text-align: center;">
                <span style="flex:1;">🔗 <b>Multisource Data</b></span>
                <span style="flex:1;">👥 <b>Multidisciplinary Roles</b></span>
                <span style="flex:1;">⚖️ <b>Clear Accountability</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_raci:
        st.subheader("RACI Responsibility Governance Matrix")
        raci_data = pd.DataFrame([
            {"Workflow Stage": "1. Risk Screening", "Teacher": "Responsible (R)", "Counselor": "Consulted (C)", "Support Specialist": "Informed (I)"},
            {"Workflow Stage": "2. Collaborative Assessment", "Teacher": "Consulted (C)", "Counselor": "Responsible (R)", "Support Specialist": "Consulted (C)"},
            {"Workflow Stage": "3. IEP Formulation", "Teacher": "Consulted (C)", "Counselor": "Accountable (A)", "Support Specialist": "Responsible (R)"},
            {"Workflow Stage": "4. Classroom Support", "Teacher": "Responsible (R)", "Counselor": "Accountable (A)", "Support Specialist": "Responsible (R)"},
            {"Workflow Stage": "5. Progress Tracking", "Teacher": "Responsible (R)", "Counselor": "Accountable (A)", "Support Specialist": "Responsible (R)"},
            {"Workflow Stage": "6. School Transition", "Teacher": "Consulted (C)", "Counselor": "Responsible (R)", "Support Specialist": "Consulted (C)"}
        ])
        st.dataframe(raci_data, use_container_width=True, hide_index=True)
        st.caption("*(R: Responsible | A: Accountable/Approver | C: Consulted | I: Informed)*")

# ==========================================
# STEP 0: STUDENT PROFILE MANAGEMENT
# ==========================================
elif step == "Step 0: Student Profile Management":
    st.header("Step 0: Enrolled Student Registry & Profile Management")
    st.write("Register pseudonymized student records, baseline strengths, behavioral triggers, and classroom accommodation plans.")
    
    col_entry, col_list = st.columns([1, 1])
    
    with col_entry:
        st.subheader("➕ Register / Update Student Dossier")
        with st.form("form_student_entry"):
            c_id, c_alias = st.columns(2)
            sid = c_id.text_input("Pseudonymized Student ID (e.g., HS-07):", placeholder="HS-07")
            alias = c_alias.text_input("Student Alias (e.g., Student K.M):", placeholder="Student K.M")
            grade = st.selectbox("Current Grade Level:", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"])
            strengths = st.text_area("Strengths & Special Interests:", placeholder="e.g., Strong visual recall, interest in transportation, ordered construction toys...")
            challenges = st.text_area("Behavioral Triggers & Barriers:", placeholder="e.g., Meltdowns during abrupt schedule shifts, auditory distress from school bell...")
            accommodations = st.text_area("Classroom Accommodations Setup:", placeholder="e.g., Provide noise-canceling headphones, 5-minute visual transition countdown timer...")
            
            submitted_student = st.form_submit_button("Save Student Profile")
            if submitted_student:
                if sid and alias:
                    c = conn.cursor()
                    c.execute("""
                        INSERT OR REPLACE INTO students (student_id, alias_name, grade, strengths, challenges, accommodations)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (sid.strip(), alias.strip(), grade, strengths, challenges, accommodations))
                    conn.commit()
                    st.success(f"Successfully saved profile for **{alias} ({sid})**!")
                    st.rerun()
                else:
                    st.error("Please provide at least a Student ID and Alias Name.")

    with col_list:
        st.subheader("Cohort Distribution by Grade Level")
        students_current = pd.read_sql("SELECT student_id, alias_name, grade, strengths, challenges, accommodations FROM students", conn)
        
        grade_counts = students_current['grade'].value_counts().reset_index()
        grade_counts.columns = ['Grade Level', 'Enrolled Count']
        fig_grade = px.bar(grade_counts, x='Grade Level', y='Enrolled Count', color='Grade Level', text='Enrolled Count')
        fig_grade.update_layout(height=230, showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_grade, use_container_width=True)
        st.dataframe(students_current, use_container_width=True)

# ==========================================
# STEP 1: INTAKE & STRUCTURED SCREENING
# ==========================================
elif step == "Step 1: Intake & Structured Screening":
    st.header("Step 1: Structured Risk Screening & Intake")
    st.warning("⚠️ **Data Ethics & Non-Diagnostic Guardrail:** This observational checklist identifies students requiring multidisciplinary evaluation. It **strictly does not produce clinical diagnoses** or replace medical practitioners.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Submit Structured Observational Intake")
        with st.form("screening_form"):
            students_df = pd.read_sql("SELECT student_id, alias_name FROM students", conn)
            sid_choice = st.selectbox("Select Student Profile:", students_df.apply(lambda r: f"{r['student_id']} - {r['alias_name']}", axis=1))
            real_sid = sid_choice.split(" - ")[0]
            context = st.selectbox("Primary Observation Context:", ["During Direct Instruction", "Recess & Free Play", "Small-Group Work", "Lesson Transitions", "Home Environment"])
            
            st.write("---")
            st.write("**Structured Behavioral Checklist (Informed by UCI Top Predictors):**")
            q1 = st.checkbox("Exhibits acute distress/hypersensitivity to sensory stimuli (school bell, bright lights, loud cafeteria)")
            q2 = st.checkbox("Demonstrates rigid adherence to routines; severe resistance during schedule or activity shifts")
            q3 = st.checkbox("Infrequent eye-gaze engagement; rarely responds to social name calling or peer greetings")
            q4 = st.checkbox("Significant difficulty interpreting social gestures or communicating basic needs to classmates")
            
            note = st.text_area("Detailed Observational Notes:")
            
            if st.form_submit_button("Submit Screening Intake"):
                score = sum([q1, q2, q3, q4])
                risk = "Requires Multidisciplinary Evaluation" if score >= 2 else "Routine Observational Monitoring"
                c = conn.cursor()
                c.execute("""INSERT INTO screenings (student_id, reporter_username, reporter_role, context, indicators_count, concern_note, risk_level, created_at)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (real_sid, current_username, current_role, context, score, note, risk, str(date.today())))
                conn.commit()
                st.success(f"Recorded! Triage outcome: **{risk}** (Indicator Count: {score}/4). Multidisciplinary case meeting triggered.")
                st.rerun()

    with col2:
        st.subheader("Screening Triage by Environmental Context")
        scrs = pd.read_sql("SELECT id, student_id, reporter_role, context, indicators_count, risk_level, created_at FROM screenings ORDER BY id DESC", conn)
        if not scrs.empty:
            fig_ctx = px.pie(scrs, names='context', title='Distribution of Observations Across School Environments', hole=0.4)
            fig_ctx.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_ctx, use_container_width=True)
        st.dataframe(scrs, use_container_width=True)

# ==========================================
# STEP 2: COLLABORATIVE ASSESSMENT
# ==========================================
elif step == "Step 2: Collaborative Assessment":
    st.header("Step 2: Multisource Collaborative Assessment & Case Conference")
    st.info("Multidisciplinary Integration: Juxtaposing classroom observations, parent developmental history, and clinical documentation to identify barriers and leverage personal strengths.")
    
    students_df = pd.read_sql("SELECT * FROM students", conn)
    chosen_id = st.selectbox("Select Student Dossier to Review:", students_df['student_id'].tolist())
    student_info = students_df[students_df['student_id'] == chosen_id].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div style="background-color:#F8FAFC; border: 1px solid #CBD5E1; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h4 style="color:#0F172A; margin-top:0;">📋 Comprehensive Profile: {student_info['alias_name']} ({student_info['student_id']})</h4>
            <span style="background-color:#DBEAFE; color:#1E40AF; padding:3px 8px; border-radius:12px; font-size:12px; font-weight:bold;">{student_info['grade']}</span>
            <hr style="margin:10px 0;">
            <p><b>🌟 Individual Strengths & Affinity:</b> <br><span style="color:#166534;">{student_info['strengths']}</span></p>
            <p><b>⚠️ Functional Challenges & Sensory Triggers:</b> <br><span style="color:#991B1B;">{student_info['challenges']}</span></p>
            <p><b>🛠 Established Classroom Accommodations:</b> <br>{student_info['accommodations']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.subheader("Multisource Observational Intake History")
        scr_history = pd.read_sql(f"SELECT reporter_role, context, indicators_count, risk_level, concern_note, created_at FROM screenings WHERE student_id='{chosen_id}'", conn)
        if not scr_history.empty:
            fig_bar = px.bar(scr_history, x='reporter_role', y='indicators_count', color='risk_level',
                             labels={'reporter_role': 'Reporting Stakeholder', 'indicators_count': 'Risk Indicator Count (0-4)'},
                             title="Reported Behavioral Indicators Across Roles")
            fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)
            st.dataframe(scr_history, use_container_width=True)
        else:
            st.caption("No prior observational screenings recorded for this student.")

# ==========================================
# STEP 3: DIGITAL IEP FORMULATION
# ==========================================
elif step == "Step 3: Digital IEP Formulation":
    st.header("Step 3: Digital Individualized Education Plan (IEP)")
    st.write("Formulate measurable SMART objectives with clearly delineated institutional accountability.")
    
    iep_df = pd.read_sql("""SELECT iep.plan_id, iep.student_id, s.alias_name, s.grade, iep.target_skill, 
                                   iep.strategy, s.accommodations, iep.lead_role, iep.approved_by, iep.status 
                            FROM iep_plans iep JOIN students s ON iep.student_id = s.student_id""", conn)
    
    c_st1, c_st2 = st.columns([1, 2])
    with c_st1:
        status_cnt = iep_df['status'].value_counts().reset_index()
        status_cnt.columns = ['Status', 'Count']
        fig_st = px.pie(status_cnt, names='Status', values='Count', hole=0.4, title="IEP Approval Status")
        fig_st.update_layout(height=220, margin=dict(l=5, r=5, t=30, b=5))
        st.plotly_chart(fig_st, use_container_width=True)
    with c_st2:
        role_cnt = iep_df['lead_role'].value_counts().reset_index()
        role_cnt.columns = ['Lead Role', 'Assigned Targets']
        fig_role = px.bar(role_cnt, x='Assigned Targets', y='Lead Role', orientation='h', title="Target Distribution by Professional Role")
        fig_role.update_layout(height=220, margin=dict(l=5, r=5, t=30, b=5))
        st.plotly_chart(fig_role, use_container_width=True)

    st.dataframe(iep_df, use_container_width=True)
    
    with st.expander("➕ Author or Update SMART IEP Target"):
        with st.form("new_iep"):
            f_sid = st.selectbox("Select Student:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            f_plan_id = f"IEP-{f_sid[-2:]}-M{date.today().strftime('%m')}"
            f_skill = st.text_input("Measurable SMART Objective:", placeholder="e.g., Complete seatwork independently for 15 minutes using visual timer")
            f_strategy = st.text_area("Pedagogical Strategy & Environmental Supports:")
            f_role = st.selectbox("Lead Role:", ["Homeroom / Subject Teacher", "Special Education Support Personnel", "School Counselor (Case Coordinator)", "Parent / Guardian"])
            
            can_appr = ROLE_PERMISSIONS[current_role]["can_approve"]
            f_appr = current_username if can_appr else "Pending Counselor Approval"
            f_status = "Approved" if can_appr else "Pending Review"
            
            if st.form_submit_button("Commit Objective to IEP Plan"):
                c = conn.cursor()
                c.execute("INSERT OR REPLACE INTO iep_plans VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (f_plan_id, f_sid, f_skill, f_strategy, f_role, f_appr, f_status))
                conn.commit()
                st.success("IEP target recorded successfully!")
                st.rerun()

# ==========================================
# STEPS 4 & 5: CLASSROOM INTERVENTION & PROGRESS TRACKING
# ==========================================
elif step == "Step 4 & 5: Classroom Intervention & Progress Tracking":
    st.header("Steps 4 & 5: Classroom Support & Real-Time Longitudinal Tracking")
    
    # Visual Support Toolbox
    with st.expander("🧩 Visual Support Toolbox (Classroom Schedule & Accommodations Simulator)", expanded=False):
        st.write("**Simulated Visual Schedule & Behavioral Cues for Mainstream Classrooms:**")
        v_col1, v_col2, v_col3, v_col4 = st.columns(4)
        v_col1.markdown("""
        <div style="text-align:center; padding:15px; border:2px dashed #0284C7; border-radius:8px; background:#F0F9FF;">
            <div style="font-size:30px;">📚</div>
            <b>1. Independent Reading</b><br><small>15 Mins - Individual Seatwork</small>
        </div>
        """, unsafe_allow_html=True)
        v_col2.markdown("""
        <div style="text-align:center; padding:15px; border:2px dashed #059669; border-radius:8px; background:#ECFDF5;">
            <div style="font-size:30px;">🧩</div>
            <b>2. Small-Group Work</b><br><small>10 Mins - Peer Puzzle Assembly</small>
        </div>
        """, unsafe_allow_html=True)
        v_col3.markdown("""
        <div style="text-align:center; padding:15px; border:2px dashed #D97706; border-radius:8px; background:#FFFBEB;">
            <div style="font-size:30px;">⏳</div>
            <b>3. Transition Prep</b><br><small>5-Min Warning (Visual Timer)</small>
        </div>
        """, unsafe_allow_html=True)
        v_col4.markdown("""
        <div style="text-align:center; padding:15px; border:2px dashed #7C3AED; border-radius:8px; background:#F5F3FF;">
            <div style="font-size:30px;">⭐️</div>
            <b>4. Token Reinforcement</b><br><small>Accumulate 3 Stars for Free Play</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    col_input, col_view = st.columns([1, 2])
    with col_input:
        st.subheader("Log Session Autonomy Rating")
        with st.form("log_form"):
            selected_student = st.selectbox("Student:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            current_plans = pd.read_sql(f"SELECT plan_id, target_skill FROM iep_plans WHERE student_id='{selected_student}'", conn)
            
            if not current_plans.empty:
                plan_choice = st.selectbox("Active IEP Target:", current_plans['plan_id'] + " - " + current_plans['target_skill'])
                real_pid = plan_choice.split(" - ")[0]
                real_skill = " - ".join(plan_choice.split(" - ")[1:])
            else:
                real_pid = "IEP-TEMP"
                real_skill = st.text_input("Target Skill:", value="Classroom adaptive functioning")
                
            rec_date = st.date_input("Observation Date:", date.today())
            score = st.slider("Autonomy & Independence Rating:", 1, 5, 3, 
                              help="1: 100% Hand-over-hand / Full physical prompt | 3: Visual / gestural prompt | 5: Fully autonomous")
            note_log = st.text_input("Observation Notes:")
            
            if st.form_submit_button("Log Autonomy Score"):
                c = conn.cursor()
                c.execute("INSERT INTO progress_logs (plan_id, student_id, logged_by, record_date, target_skill, score, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (real_pid, selected_student, current_username, str(rec_date), real_skill, score, note_log))
                conn.commit()
                st.success("Session autonomy logged successfully!")
                st.rerun()
                
    with col_view:
        st.subheader("Longitudinal Autonomy Progression Curve")
        df_chart = pd.read_sql(f"SELECT record_date, target_skill, score, notes, logged_by FROM progress_logs WHERE student_id='{selected_student}' ORDER BY record_date ASC", conn)
        if not df_chart.empty:
            fig = px.line(df_chart, x="record_date", y="score", color="target_skill", markers=True, 
                          title=f"Autonomy Trajectory for {selected_student}",
                          labels={"score": "Autonomy Rating (1-5)", "record_date": "Date", "target_skill": "IEP Objective"})
            fig.update_traces(line=dict(width=3))
            fig.update_yaxes(range=[0.5, 5.5], tickvals=[1, 2, 3, 4, 5])
            fig.add_hline(y=4.0, line_dash="dash", line_color="green", annotation_text="Autonomy Benchmark Threshold (>=4.0)")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_chart, use_container_width=True)
        else:
            st.info("No progress records logged yet for this student.")

# ==========================================
# STEP 6: REVIEW & TRANSITION PASSPORT
# ==========================================
elif step == "Step 6: Review & Transition Passport":
    st.header("Step 6: Periodic Review & Grade Transition Dossier")
    st.write("Ensuring uninterrupted educational support across academic years and school transfers.")
    
    # Transition Protocol Pipeline
    st.markdown("""
    <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 160px; background: #F8FAFC; border-top: 4px solid #0284C7; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <b style="color: #0369A1; font-size: 13px;">1. TERM-END EVALUATION</b><br>
            <small style="color: #475569;">Evaluate IEP objective mastery</small>
        </div>
        <div style="flex: 1; min-width: 160px; background: #F8FAFC; border-top: 4px solid #D97706; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <b style="color: #B45309; font-size: 13px;">2. CASE HANDOFF MEETING</b><br>
            <small style="color: #475569;">Conference with incoming teachers & parents</small>
        </div>
        <div style="flex: 1; min-width: 160px; background: #F8FAFC; border-top: 4px solid #059669; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <b style="color: #047857; font-size: 13px;">3. INCLUSION PASSPORT</b><br>
            <small style="color: #475569;">Package sensory triggers & strategies</small>
        </div>
        <div style="flex: 1; min-width: 160px; background: #F8FAFC; border-top: 4px solid #7C3AED; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0;">
            <b style="color: #6D28D9; font-size: 13px;">4. TRANSITION ONBOARDING</b><br>
            <small style="color: #475569;">Monitor first 4 weeks in new grade</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_viz1, col_viz2 = st.columns([1, 1])
    
    with col_viz1:
        st.subheader("Transition Readiness Multi-Axial Assessment")
        selected_trans_stu = st.selectbox(
            "Select Student for Radar Analysis:", 
            pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist(),
            index=5  # Default to HS-06 (Grade 5 transitioning to Grade 6)
        )
        
        categories = ['Sensory Regulation', 'Need Communication', 'Peer Reciprocity', 'Task Independence', 'Rule Compliance']
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[2, 2, 1, 3, 2],
            theta=categories,
            fill='toself',
            name='Term Baseline',
            line_color='#94A3B8'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[4, 4, 3, 5, 4],
            theta=categories,
            fill='toself',
            name='Post-Intervention (Ready)',
            line_color='#0284C7'
        ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            showlegend=True,
            height=280,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_viz2:
        st.subheader("Digital Inclusion Passport (Quick Handoff)")
        stu_row = pd.read_sql(f"SELECT * FROM students WHERE student_id='{selected_trans_stu}'", conn).iloc[0]
        
        st.markdown(f"""
        <div style="background:#FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px; padding: 14px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <b style="font-size:16px; color:#1E293B;">Student: {stu_row['alias_name']} ({stu_row['student_id']})</b>
                <span style="background:#E2E8F0; padding:2px 8px; border-radius:10px; font-size:12px;">{stu_row['grade']}</span>
            </div>
            <hr style="margin:8px 0;">
            <div style="margin-bottom:8px;">
                <span style="color:#15803D; font-weight:bold;">✅ Recommended DOs for Incoming Teachers:</span><br>
                <small style="color:#334155;">- {stu_row['accommodations']}<br>- Leverage special interests: {stu_row['strengths']}</small>
            </div>
            <div>
                <span style="color:#B91C1C; font-weight:bold;">⛔ Critical Environmental DON'Ts:</span><br>
                <small style="color:#334155;">- {stu_row['challenges']}<br>- Avoid abrupt schedule shifts without a visual countdown warning.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.subheader("Transition Dossier Archive")
    trans_df = pd.read_sql("""SELECT t.id, t.student_id, s.alias_name, s.grade, t.review_date, t.summary, t.transition_plan, u.full_name as reviewer 
                              FROM transition_reviews t 
                              JOIN students s ON t.student_id = s.student_id
                              LEFT JOIN users u ON t.reviewer_username = u.username""", conn)
    st.dataframe(trans_df, use_container_width=True)
    
    with st.expander("📝 Issue or Update Student Transition Dossier", expanded=False):
        with st.form("trans_form"):
            t_sid = st.selectbox("Select Student Profile:", pd.read_sql("SELECT student_id FROM students", conn)['student_id'].tolist())
            t_sum = st.text_area("Term-End Competency Summary & Progress Achieved:")
            t_plan = st.text_area("Mandatory Pedagogical & Environmental Recommendations for Incoming Teachers:")
            
            if st.form_submit_button("Publish Transition Passport"):
                c = conn.cursor()
                c.execute("INSERT INTO transition_reviews (student_id, reviewer_username, review_date, summary, transition_plan) VALUES (?, ?, ?, ?, ?)",
                          (t_sid, current_username, str(date.today()), t_sum, t_plan))
                conn.commit()
                st.success("Transition passport issued successfully!")
                st.rerun()

# ==========================================
# SYSTEM ANALYTICS & DATA EXPLORER
# ==========================================
elif step == "📊 System Analytics & Data Explorer":
    st.header("Comprehensive Proof-of-Concept (PoC) System Monitoring")
    st.markdown("Quantitative audit data for Design Science Research (DSR) evaluation:")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered Users", len(pd.read_sql("SELECT username FROM users", conn)))
    c2.metric("Enrolled Cohort", len(pd.read_sql("SELECT student_id FROM students", conn)))
    c3.metric("Active IEP Goals", len(pd.read_sql("SELECT plan_id FROM iep_plans", conn)))
    c4.metric("Logged Observations", len(pd.read_sql("SELECT id FROM progress_logs", conn)))
    
    st.divider()
    
    st.subheader("Multi-Dimensional System Analytics")
    col_chart_a, col_chart_b = st.columns(2)
    
    with col_chart_a:
        scr_summary = pd.read_sql("SELECT risk_level, COUNT(*) as total FROM screenings GROUP BY risk_level", conn)
        fig_risk = px.pie(scr_summary, values='total', names='risk_level', title='Screening Risk Stratification Distribution', color_discrete_sequence=px.colors.sequential.RdBu)
        fig_risk.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col_chart_b:
        avg_score = pd.read_sql("SELECT student_id, AVG(score) as avg_score FROM progress_logs GROUP BY student_id", conn)
        fig_avg = px.bar(avg_score, x='student_id', y='avg_score', text_auto='.2f', title='Mean Autonomy Score by Student (Scale 1-5)', color='avg_score', color_continuous_scale='Blues')
        fig_avg.update_layout(height=260, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_avg, use_container_width=True)

    st.subheader("1. Enrolled Benchmark Student Profiles")
    st.dataframe(pd.read_sql("SELECT * FROM students", conn), use_container_width=True)
    
    st.subheader("2. User Accounts & Role-Based Access Control (RBAC) Registry")
    st.dataframe(pd.read_sql("SELECT username, full_name, role, assigned_scope FROM users", conn), use_container_width=True)
    
    st.subheader("3. Comprehensive Intake & Screening Audit Log")
    st.dataframe(pd.read_sql("SELECT * FROM screenings ORDER BY id DESC", conn), use_container_width=True)
