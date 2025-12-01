import streamlit as st
import json
from datetime import datetime, time
from utils.storage import load_tasks, save_tasks, load_progress, save_progress
from utils.mailer import send_email

# --- App Config ---
st.set_page_config(page_title="Tanya’s Advent Calendar", page_icon="🎄", layout="wide")

# --- Snow Animation (no background image) ---
def add_snow_effect():
    st.markdown("""
    <style>
    .stApp {
        background-color: #fdfdfd;
        color: #222;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    /* Button styles */
    button[kind="secondary"] div p, button[kind="primary"] div p {
        color: #2c3e50 !important;
        font-weight: bold;
        font-size: 18px;
    }
    /* Snowflakes animation */
    @keyframes snowflakes-fall {
        0% {top: -10%;}
        100% {top: 100%;}
    }
    @keyframes snowflakes-shake {
        0%,100% {transform: translateX(0);}
        50% {transform: translateX(80px);}
    }
    .snowflake {
        position: fixed;
        top: -10%;
        z-index: 9999;
        user-select: none;
        animation-name: snowflakes-fall, snowflakes-shake;
        animation-duration: 10s, 3s;
        animation-timing-function: linear, ease-in-out;
        animation-iteration-count: infinite, infinite;
        color: #87CEFA;
        font-size: 24px;
    }
    .snowflake:nth-of-type(1) { left: 10%; animation-delay: 0s, 0s; }
    .snowflake:nth-of-type(2) { left: 20%; animation-delay: 2s, 2s; }
    .snowflake:nth-of-type(3) { left: 30%; animation-delay: 4s, 1s; }
    .snowflake:nth-of-type(4) { left: 50%; animation-delay: 1s, 0s; }
    .snowflake:nth-of-type(5) { left: 60%; animation-delay: 3s, 2s; }
    .snowflake:nth-of-type(6) { left: 80%; animation-delay: 2s, 1s; }
    </style>

    <div class="snowflake">❄️</div>
    <div class="snowflake">❅</div>
    <div class="snowflake">❆</div>
    <div class="snowflake">❄️</div>
    <div class="snowflake">❅</div>
    <div class="snowflake">❆</div>
    """, unsafe_allow_html=True)

add_snow_effect()

# --- Load Data ---
tasks = load_tasks()
progress = load_progress()

if "page" not in st.session_state:
    st.session_state.page = "calendar"  # default page

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# --- Header ---
st.markdown("<h1 style='text-align:center;'>🎅 Tanya’s Christmas Advent Calendar 🎁</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Welcome, Tanya! Santa and his elves are back with magical winter challenges just for you. Let’s make this December full of joy, creativity, and Christmas magic! ❄️</h3>", unsafe_allow_html=True)
st.write("---")

# --- Admin Login Sidebar ---
with st.sidebar:
    st.header("Parent Panel")
    if not st.session_state.admin_mode:
        username = st.text_input("Login")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "adm" and password == "321":
                st.session_state.admin_mode = True
                st.success("Logged in as Admin.")
            else:
                st.error("Incorrect login.")
    else:
        st.success("Admin mode active.")
        if st.button("Logout"):
            st.session_state.admin_mode = False

# --- Admin Panel ---
if st.session_state.admin_mode:
    st.title("🎄 Admin Panel - Manage Daily Greetings & Tasks")
    selected_day = st.number_input("Day (1-24)", min_value=1, max_value=24, step=1)
    greeting = st.text_area("Greeting Message", tasks.get(str(selected_day), {}).get("greeting", ""))
    task = st.text_area("Task Description", tasks.get(str(selected_day), {}).get("task", ""))
    if st.button("Save Task"):
        tasks[str(selected_day)] = {"greeting": greeting, "task": task}
        save_tasks(tasks)
        st.success(f"Saved content for Day {selected_day}.")
    st.stop()

# --- PAGES ---

def show_calendar():
    st.subheader("✨ Select your day below ✨")

    current_time = datetime.now().time()
    current_day = datetime.now().day
    day = 1

    for i in range(4):
        cols = st.columns(6)
        for j in range(6):
            if day <= 24:
                day_str = str(day)
                completed = progress.get(day_str, {}).get("completed", False)
                unlocked = (day <= current_day and current_time >= time(6, 0))
                label = f"Day {day} 🎁"
                if completed:
                    label += " ✅"

                if cols[j].button(label, key=f"day_{day}"):
                    if unlocked:
                        st.session_state.page = "day"
                        st.session_state.selected_day = day
                        st.rerun()
                    else:
                        st.warning("You can open this task after 6:00 AM each day.")
                day += 1


def show_day_page():
    day = str(st.session_state.selected_day)
    task_info = tasks.get(day, {})
    greeting = task_info.get("greeting", "")
    task_text = task_info.get("task", "")

    st.write("---")
    st.markdown(f"## 🎄 Day {day}")
    st.markdown(f"**{greeting}**")
    st.markdown(f"### ✨ Task: {task_text}")

    uploaded_file = st.file_uploader("Upload your completed work (image, file, etc.)")
    link_input = st.text_input("Or paste a link here")

    if st.button("✅ Completed!"):
        progress[day] = {
            "completed": True,
            "file": uploaded_file.name if uploaded_file else "",
            "link": link_input
        }
        save_progress(progress)
        send_email(day)
        st.balloons()
        st.success("🎈 Well done, Tanya! You’re amazing! 🎄")

    if st.button("⬅️ Back to Calendar"):
        st.session_state.page = "calendar"
        st.rerun()

# --- ROUTER ---
if st.session_state.page == "calendar":
    show_calendar()
elif st.session_state.page == "day":
    show_day_page()

st.write("---")
st.markdown("<h4 style='text-align:center;'>Made with ❤️ for Tanya by Santa 🎅</h4>", unsafe_allow_html=True)

