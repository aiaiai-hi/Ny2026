import streamlit as st
import json
from datetime import datetime, time
from utils.storage import load_tasks, save_tasks, load_progress, save_progress
from utils.mailer import send_email

# --- Streamlit Config ---
st.set_page_config(page_title="Tanya’s Advent Calendar", page_icon="🎄", layout="wide")

# --- Background + Snow + Music ---
def set_christmas_theme():
    st.markdown("""
    <style>
    .stApp {
        background-image: url("https://img.freepik.com/free-vector/christmas-background-with-snowflakes_1048-1841.jpg?t=st=1733000000~exp=1733500000~hmac=1c3435f9a37f056f564b54c141244e5c004937c6ad02cd79a790bfdaedb2f8f9&w=1480");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    /* Snowflake animation */
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
    }
    .snowflake:nth-of-type(1) { left: 10%; animation-delay: 1s, 1s; }
    .snowflake:nth-of-type(2) { left: 20%; animation-delay: 6s, .5s; }
    .snowflake:nth-of-type(3) { left: 30%; animation-delay: 4s, 2s; }
    .snowflake:nth-of-type(4) { left: 50%; animation-delay: 8s, 3s; }
    .snowflake:nth-of-type(5) { left: 60%; animation-delay: 2s, 2s; }
    .snowflake:nth-of-type(6) { left: 80%; animation-delay: 1s, 0s; }
    </style>

    <div class="snowflake">❄️</div>
    <div class="snowflake">❅</div>
    <div class="snowflake">❆</div>
    <div class="snowflake">❄️</div>
    <div class="snowflake">❅</div>
    <div class="snowflake">❆</div>

    <!-- Music player -->
    <audio id="bg-music" autoplay loop>
      <source src="https://cdn.pixabay.com/download/audio/2022/12/14/audio_4a4b3e46f0.mp3?filename=jingle-bells-christmas-hip-hop-13055.mp3" type="audio/mp3">
    </audio>
    <script>
      let audio = document.getElementById("bg-music");
      let isPlaying = true;
      function toggleMusic() {
        if (isPlaying) {{
          audio.pause();
          isPlaying = false;
        }} else {{
          audio.play();
          isPlaying = true;
        }}
      }
    </script>
    """, unsafe_allow_html=True)

set_christmas_theme()

# --- Load Data ---
tasks = load_tasks()
progress = load_progress()

if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# --- Header ---
st.markdown("<h1 style='text-align:center;'>🎅 Tanya’s Christmas Advent Calendar 🎁</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Welcome, Tanya! Santa and his elves are back with magical winter challenges just for you. Let’s make this December full of joy, creativity, and Christmas magic! ❄️</h3>", unsafe_allow_html=True)
st.write("---")

# --- Music control button ---
st.markdown("""
<div style='text-align:center;'>
    <button onclick='toggleMusic()' style='padding:10px 20px;border:none;border-radius:8px;background-color:#e74c3c;color:white;font-size:16px;cursor:pointer;'>
        🔊 Toggle Christmas Music
    </button>
</div>
""", unsafe_allow_html=True)

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

# --- Tanya’s View ---
current_time = datetime.now().time()
current_day = datetime.now().day

cols = st.columns(6)
day = 1

for i in range(4):
    row = st.columns(6)
    for j in range(6):
        if day <= 24:
            day_str = str(day)
            completed = progress.get(day_str, {}).get("completed", False)
            unlocked = (day <= current_day and current_time >= time(6, 0))

            button_label = f"🎁 Day {day}"
            if completed:
                button_label += " ✅"

            if row[j].button(button_label, key=f"day_{day}"):
                if unlocked:
                    st.session_state["selected_day"] = day
                else:
                    st.warning("You can open this task after 6:00 AM each day.")
            day += 1

# --- Selected Day View ---
if "selected_day" in st.session_state:
    day = str(st.session_state["selected_day"])
    task_info = tasks.get(day, {})
    greeting = task_info.get("greeting", "")
    task_text = task_info.get("task", "")

    st.write("---")
    st.markdown(f"## 🎄 Day {day}")
    st.markdown(f"**{greeting}**")
    st.markdown(f"### ✨ Task: {task_text}")

    uploaded_file = st.file_uploader("Upload your completed work (image, file, etc.)")
