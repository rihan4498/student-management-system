import streamlit as st
import json
import pandas as pd
from pathlib import Path
from abc import ABC, abstractmethod

DATABASE = "school_data.json"

# ----------------------------------------------------------------------------
# Data layer
# ----------------------------------------------------------------------------

def load_data():
    if Path(DATABASE).exists():
        with open(DATABASE, "r") as f:
            content = f.read()
            if content:
                return json.loads(content)
    return {"students": [], "teachers": []}


def save_data():
    with open(DATABASE, "w") as f:
        json.dump(st.session_state.data, f, indent=4)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data


class Persons(ABC):
    @staticmethod
    def validate_email(email):
        return "@" in email and "." in email

    @abstractmethod
    def get_role(self):
        pass

    @abstractmethod
    def register(self, **kwargs):
        pass


class Student(Persons):
    def get_role(self):
        return "student"

    def register(self, name, age, email, roll_no):
        if not self.validate_email(email):
            return False, "That email doesn't look valid."
        if not (name and age and email and roll_no):
            return False, "Every field is required."
        if any(s["roll_no"] == roll_no for s in data["students"]):
            return False, f"A student with roll no. {roll_no} already exists."
        data["students"].append(
            {"name": name, "age": age, "email": email, "roll_no": roll_no, "grades": {}}
        )
        save_data()
        return True, f"Student {name} registered successfully."

    def add_grade(self, roll_no, subject, marks):
        for s in data["students"]:
            if s["roll_no"] == roll_no:
                s["grades"][subject] = marks
                save_data()
                return True, f"Grade added for {s['name']}."
        return False, "No student found with that roll number."

    def find(self, roll_no):
        return next((s for s in data["students"] if s["roll_no"] == roll_no), None)


class Teacher(Persons):
    def get_role(self):
        return "teacher"

    def register(self, name, age, email, emp_id, subject):
        if not self.validate_email(email):
            return False, "That email doesn't look valid."
        if not (name and age and email and emp_id and subject):
            return False, "Every field is required."
        if any(t["emp_id"] == emp_id for t in data["teachers"]):
            return False, f"A teacher with employee ID {emp_id} already exists."
        data["teachers"].append(
            {"name": name, "age": age, "email": email, "emp_id": emp_id, "subject": subject}
        )
        save_data()
        return True, f"Teacher {name} registered successfully."

    def find(self, emp_id):
        return next((t for t in data["teachers"] if t["emp_id"] == emp_id), None)


stud = Student()
tech = Teacher()

# ----------------------------------------------------------------------------
# Visual identity — "Cohort": deep indigo base, gold primary accent, with
# coral (students) and teal (teachers) as meaningful role colors throughout.
# The dark theme is set in .streamlit/config.toml, NOT just CSS overrides —
# that's what guarantees every native widget (inputs, radio, metric,
# dataframe) renders with correct contrast instead of fighting Streamlit's
# own theme, which is what caused the invisible text before.
# ----------------------------------------------------------------------------

GOLD = "#F2C14E"
CORAL = "#FF6F59"
TEAL = "#2DD4BF"
INK = "#14122A"
SURFACE = "#1E1B3B"
MUTED = "#A9A4C9"

st.set_page_config(page_title="Cohort", page_icon="🔷", layout="wide")

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3, h4 {{ font-family: 'Space Grotesk', sans-serif !important; }}

    /* radio dots pick up the theme accent automatically */
    input[type="radio"] {{ accent-color: {GOLD}; }}

    .hero {{
        background: linear-gradient(135deg, #201C42 0%, {INK} 65%);
        border: 1px solid rgba(242, 193, 78, 0.25);
        border-radius: 16px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.6rem;
        display: flex;
        align-items: center;
        gap: 1.1rem;
    }}
    .hero-title {{ font-family: 'Space Grotesk', sans-serif; font-size: 2rem; font-weight: 700; color: #F7F5FF; margin: 0; }}
    .hero-sub {{ color: {MUTED}; font-size: 0.85rem; letter-spacing: 0.03em; margin: 0.15rem 0 0 0; }}

    .eyebrow {{
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 0.3rem;
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 20px;
    }}
    .eyebrow.student {{ color: {CORAL}; background: rgba(255,111,89,0.12); }}
    .eyebrow.teacher {{ color: {TEAL}; background: rgba(45,212,191,0.12); }}
    .eyebrow.neutral {{ color: {GOLD}; background: rgba(242,193,78,0.12); }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(30, 27, 59, 0.6);
        border-radius: 14px !important;
        border: 1px solid rgba(242, 193, 78, 0.18) !important;
        backdrop-filter: blur(6px);
        padding: 0.5rem 0.7rem;
        transition: border-color 0.2s ease;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: rgba(242, 193, 78, 0.4) !important;
    }}

    .stButton>button, .stFormSubmitButton>button {{
        background: linear-gradient(135deg, {GOLD}, #E0A62E);
        color: {INK};
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 1.4rem;
        box-shadow: 0 2px 12px rgba(242, 193, 78, 0.25);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }}
    .stButton>button:hover, .stFormSubmitButton>button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(242, 193, 78, 0.4);
    }}

    .id-row {{ display: flex; align-items: center; margin-bottom: 0.6rem; }}
    .stamp {{
        display: inline-flex; align-items: center; justify-content: center;
        width: 52px; height: 52px; border-radius: 14px;
        font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.2rem;
        color: {INK}; margin-right: 0.9rem; flex-shrink: 0;
    }}
    .id-name {{ font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #F7F5FF; font-weight: 600; margin: 0; }}
    .id-sub {{ font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: {MUTED}; margin: 0; }}

    [data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace; }}
    [data-testid="stMetricLabel"] {{ text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.06em; color: {MUTED}; }}

    [data-testid="stSidebar"] h2 {{ font-family: 'Space Grotesk', sans-serif !important; color: #F7F5FF !important; font-size: 1.1rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
        <svg width="52" height="52" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
            <circle cx="20" cy="20" r="13" fill="{GOLD}" opacity="0.92"/>
            <circle cx="33" cy="20" r="13" fill="{CORAL}" opacity="0.85"/>
            <circle cx="26" cy="33" r="13" fill="{TEAL}" opacity="0.85"/>
        </svg>
        <div>
            <p class="hero-title">Cohort</p>
            <p class="hero-sub">STUDENT &amp; TEACHER RECORDS, IN ONE PLACE</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Sidebar navigation
# ----------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## 🔷 Cohort")
    page = st.radio(
        "Navigate",
        [
            "🏠 Dashboard",
            "📝 Register Student",
            "🧑‍🏫 Register Teacher",
            "📊 Add Grades",
            "🔍 Student Details",
            "🔍 Teacher Details",
            "📋 All Students",
            "📋 All Teachers",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"{len(data['students'])} students · {len(data['teachers'])} teachers on file")


def stamp(initials, color):
    return f'<div class="stamp" style="background:{color};">{initials}</div>'


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------

if page == "🏠 Dashboard":
    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown('<span class="eyebrow student">Students</span>', unsafe_allow_html=True)
            st.metric("Total students", len(data["students"]))
    with c2:
        with st.container(border=True):
            st.markdown('<span class="eyebrow teacher">Teachers</span>', unsafe_allow_html=True)
            st.metric("Total teachers", len(data["teachers"]))
    with c3:
        with st.container(border=True):
            st.markdown('<span class="eyebrow neutral">Performance</span>', unsafe_allow_html=True)
            all_marks = [m for s in data["students"] for m in s["grades"].values()]
            overall_avg = sum(all_marks) / len(all_marks) if all_marks else 0
            st.metric("Overall average grade", f"{overall_avg:.1f}")

    st.write("")
    st.markdown("#### Recently registered")
    left, right = st.columns(2)
    with left:
        st.markdown('<span class="eyebrow student">Students</span>', unsafe_allow_html=True)
        if data["students"]:
            for s in data["students"][-5:][::-1]:
                st.markdown(f"— **{s['name']}** · roll no. `{s['roll_no']}`")
        else:
            st.caption("No students registered yet.")
    with right:
        st.markdown('<span class="eyebrow teacher">Teachers</span>', unsafe_allow_html=True)
        if data["teachers"]:
            for t in data["teachers"][-5:][::-1]:
                st.markdown(f"— **{t['name']}** · {t['subject']}")
        else:
            st.caption("No teachers registered yet.")

elif page == "📝 Register Student":
    with st.container(border=True):
        st.markdown('<span class="eyebrow student">New entry</span>', unsafe_allow_html=True)
        st.subheader("Register a Student")
        with st.form("register_student_form", clear_on_submit=True):
            name = st.text_input("Full name")
            col1, col2 = st.columns(2)
            age = col1.text_input("Age")
            roll_no = col2.text_input("Roll number")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Register student")
        if submitted:
            ok, msg = stud.register(name=name, age=age, email=email, roll_no=roll_no)
            (st.success if ok else st.error)(msg)

elif page == "🧑‍🏫 Register Teacher":
    with st.container(border=True):
        st.markdown('<span class="eyebrow teacher">New entry</span>', unsafe_allow_html=True)
        st.subheader("Register a Teacher")
        with st.form("register_teacher_form", clear_on_submit=True):
            name = st.text_input("Full name")
            col1, col2 = st.columns(2)
            age = col1.text_input("Age")
            emp_id = col2.text_input("Employee ID")
            subject = st.text_input("Subject taught")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Register teacher")
        if submitted:
            ok, msg = tech.register(name=name, age=age, email=email, emp_id=emp_id, subject=subject)
            (st.success if ok else st.error)(msg)

elif page == "📊 Add Grades":
    with st.container(border=True):
        st.markdown('<span class="eyebrow neutral">Grade book</span>', unsafe_allow_html=True)
        st.subheader("Add a Grade")
        with st.form("add_grade_form", clear_on_submit=True):
            roll_no = st.text_input("Student roll number")
            subject = st.text_input("Subject")
            marks = st.number_input("Marks", min_value=0.0, max_value=100.0, step=0.5)
            submitted = st.form_submit_button("Save grade")
        if submitted:
            ok, msg = stud.add_grade(roll_no, subject, marks)
            (st.success if ok else st.error)(msg)

elif page == "🔍 Student Details":
    with st.container(border=True):
        st.markdown('<span class="eyebrow student">Lookup</span>', unsafe_allow_html=True)
        st.subheader("Student Details")
        roll_no = st.text_input("Enter roll number")
        if roll_no:
            s = stud.find(roll_no)
            if s:
                initials = "".join(w[0].upper() for w in s["name"].split()[:2])
                st.markdown(
                    f"""
                    <div class="id-row">
                        {stamp(initials, CORAL)}
                        <div>
                            <p class="id-name">{s['name']}</p>
                            <p class="id-sub">ROLL NO. {s['roll_no']} · AGE {s['age']} · {s['email']}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                grades = s["grades"]
                avg = sum(grades.values()) / len(grades) if grades else 0
                st.metric("Average", f"{avg:.1f}")
                if grades:
                    st.bar_chart(pd.Series(grades, name="Marks"))
                else:
                    st.caption("No grades recorded yet.")
            else:
                st.error("No student found with that roll number.")

elif page == "🔍 Teacher Details":
    with st.container(border=True):
        st.markdown('<span class="eyebrow teacher">Lookup</span>', unsafe_allow_html=True)
        st.subheader("Teacher Details")
        emp_id = st.text_input("Enter employee ID")
        if emp_id:
            t = tech.find(emp_id)
            if t:
                initials = "".join(w[0].upper() for w in t["name"].split()[:2])
                st.markdown(
                    f"""
                    <div class="id-row">
                        {stamp(initials, TEAL)}
                        <div>
                            <p class="id-name">{t['name']}</p>
                            <p class="id-sub">EMP ID {t['emp_id']} · {t['subject']} · {t['email']}</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("No teacher found with that employee ID.")

elif page == "📋 All Students":
    st.markdown('<span class="eyebrow student">Full roll</span>', unsafe_allow_html=True)
    st.subheader("All Students")
    if data["students"]:
        rows = [
            {
                "Roll No.": s["roll_no"],
                "Name": s["name"],
                "Age": s["age"],
                "Email": s["email"],
                "Average": round(sum(s["grades"].values()) / len(s["grades"]), 1) if s["grades"] else None,
            }
            for s in data["students"]
        ]
        df = pd.DataFrame(rows)
        search = st.text_input("Filter by name or roll number")
        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["Roll No."].str.contains(search, case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No students registered yet.")

elif page == "📋 All Teachers":
    st.markdown('<span class="eyebrow teacher">Full roll</span>', unsafe_allow_html=True)
    st.subheader("All Teachers")
    if data["teachers"]:
        rows = [
            {"Emp ID": t["emp_id"], "Name": t["name"], "Age": t["age"], "Subject": t["subject"], "Email": t["email"]}
            for t in data["teachers"]
        ]
        df = pd.DataFrame(rows)
        search = st.text_input("Filter by name or employee ID")
        if search:
            df = df[df["Name"].str.contains(search, case=False) | df["Emp ID"].str.contains(search, case=False)]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.caption("No teachers registered yet.")