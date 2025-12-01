import streamlit as st
import json
from datetime import datetime, time
from utils.storage import load_tasks, save_tasks, load_progress, save_progress
from utils.mailer import send_email
import base64
import os

st.set_page_config(page_title="Tanya’s Advent Calendar", page_icon="🎄", layout="wide")

# Background styling
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        encoded_string = base64.b64encode(file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpg;base64,{encoded_string.decode()});
            background-size: cover;
            color: white;
        }}
        .calendar-day {{
            border: 2px solid white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            font-size: 24px;
            cursor: pointer;
        }}
        .locked {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .completed {{
            background-color: rgba(0,255,0,0.3);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_local("assets/IMG_2841.jpeg")

# Load data
tasks = load_tasks()
progress = load_progress()

# Admin mode toggle
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# Header
st.markdown("<h1 style='text-align:center;'>🎅 Tanya’s Christmas Advent Calendar 🎁</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Welcome, Tanya! Santa and his elves are back with magical winter challenges just for you. Let’s make this December full of joy, creativity, and Christmas magic! ❄️</h3>", unsafe_allow_html=True)
st.write("---")

# --- Admin Login Section ---
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
    st.title("🎄 Admin Panel - Manage Tasks")
    selected_day = st.number_input("Day (1-24)", min_value=1, max_value=24, step=1)
    greeting = st.text_area("Greeting Message", tasks.get(str(selected_day), {}).get("greeting", ""))
    task = st.text_area("Task Description", tasks.get(str(selected_day), {}).get("task", ""))
    if st.button("Save Task"):
        tasks[str(selected_day)] = {"greeting": greeting, "task": task}
        save_tasks(tasks)
        st.success(f"Saved for Day {selected_day}.")
    st.stop()

# --- User View (Tanya) ---
current_time = datetime.now().time()
current_day = datetime.now().day

cols = st.columns(6)
day = 1

for i in range(4):
    row = st.columns(6)
    for j in range(6):
        if day <= 24:
            day_str = str(day)
            task_info = tasks.get(day_str, {})
            completed = progress.get(day_str, {}).get("completed", False)
            is_unlocked = (day <= current_day and current_time >= time(6, 0))

            css_class = "calendar-day"
            if not is_unlocked:
                css_class += " locked"
            elif completed:
                css_class += " completed"

            with row[j]:
                if st.button(f"Day {day}", key=f"day_{day}"):
                    if is_unlocked:
                        st.session_state["selected_day"] = day
                    else:
                        st.warning("You can open this task after 6:00 AM.")
            day += 1

# --- Daily View ---
if "selected_day" in st.session_state:
    day = str(st.session_state["selected_day"])
    task_info = tasks.get(day, {})
    greeting = task_info.get("greeting", "")
    task_text = task_info.get("task", "")

    st.write("---")
    st.markdown(f"## 🎁 Day {day}")
    st.markdown(f"**{greeting}**")
    st.markdown(f"### Task: {task_text}")

    uploaded_file = st.file_uploader("Upload your completed work (image, file, etc.)")
    link_input = st.text_input("Or paste a link here")

    if st.button("Completed! 🎉"):
        progress[day] = {
            "completed": True,
            "file": uploaded_file.name if uploaded_file else "",
            "link": link_input
        }
        save_progress(progress)
        send_email(day)
        st.balloons()
        st.success("Well done, Tanya! 🎈")

# --- Footer ---
st.write("---")
st.markdown("<h4 style='text-align:center;'>Made with ❤️ for Tanya by Santa 🎅</h4>", unsafe_allow_html=True)
