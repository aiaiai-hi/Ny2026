import streamlit as st
import json
import os
from datetime import datetime, time
from utils.storage import load_tasks, save_tasks, load_progress, save_progress

# --- App Config ---
st.set_page_config(page_title="Tanya’s Advent Calendar", page_icon="🎄", layout="wide")

# --- Constants ---
ANSWERS_FILE = "data/answers.json"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Snow Animation ---
def add_snow_effect():
    st.markdown("""
    <style>
    .stApp {
        background-color: #fdfdfd;
        color: #222;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    button[kind="secondary"] div p, button[kind="primary"] div p {
        color: #2c3e50 !important;
        font-weight: bold;
        font-size: 18px;
    }
    @keyframes snowflakes-fall { 0%{top:-10%;}100%{top:100%;} }
    @keyframes snowflakes-shake { 0%,100%{transform:translateX(0);}50%{transform:translateX(80px);} }
    .snowflake {
        position: fixed; top:-10%; z-index:9999; user-select:none;
        animation-name:snowflakes-fall,snowflakes-shake;
        animation-duration:10s,3s; animation-timing-function:linear,ease-in-out;
        animation-iteration-count:infinite,infinite; color:#87CEFA; font-size:24px;
    }
    .snowflake:nth-of-type(1){left:10%;animation-delay:0s,0s;}
    .snowflake:nth-of-type(2){left:20%;animation-delay:2s,2s;}
    .snowflake:nth-of-type(3){left:30%;animation-delay:4s,1s;}
    .snowflake:nth-of-type(4){left:50%;animation-delay:1s,0s;}
    .snowflake:nth-of-type(5){left:60%;animation-delay:3s,2s;}
    .snowflake:nth-of-type(6){left:80%;animation-delay:2s,1s;}
    </style>
    <div class="snowflake">❄️</div><div class="snowflake">❅</div><div class="snowflake">❆</div>
    <div class="snowflake">❄️</div><div class="snowflake">❅</div><div class="snowflake">❆</div>
    """, unsafe_allow_html=True)

add_snow_effect()

# --- Utility: Load/Save Answers ---
def load_answers():
    if not os.path.exists(ANSWERS_FILE):
        return {}
    with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_answers(data):
    with open(ANSWERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- Data ---
tasks = load_tasks()
progress = load_progress()
answers = load_answers()

if "page" not in st.session_state:
    st.session_state.page = "calendar"
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# --- Header ---
st.markdown("<h1 style='text-align:center;'>🎅 Tanya’s Christmas Advent Calendar 🎁</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Welcome, Tanya! Santa and his elves are back with magical winter challenges just for you. Let’s make this December full of joy, creativity, and Christmas magic! ❄️</h3>", unsafe_allow_html=True)
st.write("---")

# --- 🎥 Christmas Intro Video ---
video_path = "assets/-4523155194360961279.mp4"

# Проверяем, существует ли файл
if os.path.exists(video_path):
    # Используем встроенный компонент Streamlit — он работает на всех устройствах
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    st.video(video_bytes, start_time=0)
else:
    # Если видео нет или не загрузилось — показываем fallback изображение
    st.image(
        "https://cdn.pixabay.com/photo/2017/12/15/13/40/christmas-3026684_960_720.jpg",
        use_container_width=True,
        caption="🎄 Merry Christmas, Tanya!"
    )

# --- Sidebar Admin ---
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

# --- Admin Page ---
if st.session_state.admin_mode:
    st.title("🎄 Admin Panel - Manage Daily Greetings & Tasks")
    selected_day = st.number_input("Day (1–31)", min_value=1, max_value=31, step=1)
    greeting = st.text_area("Greeting Message", tasks.get(str(selected_day), {}).get("greeting", ""))
    task = st.text_area("Task Description", tasks.get(str(selected_day), {}).get("task", ""))
    if st.button("Save Task"):
        tasks[str(selected_day)] = {"greeting": greeting, "task": task}
        save_tasks(tasks)
        st.success(f"Saved for Day {selected_day}")
    st.stop()

# --- Progress bar ---
def show_progress_bar():
    total_days = 31
    completed_days = sum(1 for d in progress if progress[d].get("completed"))
    percent = round((completed_days / total_days) * 100, 1)
    st.markdown(f"### 🎯 You’ve completed **{completed_days} of {total_days} days** ({percent}%)")
    st.progress(percent / 100)
    st.write("---")

# --- Calendar Page ---
def show_calendar():
    show_progress_bar()
    st.subheader("✨ Select your day below ✨")
    current_time = datetime.now().time()
    current_day = datetime.now().day
    total_days = 31
    day = 1
    while day <= total_days:
        cols = st.columns(6)
        for j in range(6):
            if day <= total_days:
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

# --- Day Page ---
def show_day_page():
    day = str(st.session_state.selected_day)
    task_info = tasks.get(day, {})
    greeting = task_info.get("greeting", "")
    task_text = task_info.get("task", "")

    st.markdown(f"<h2 style='text-align:center;'>🎄 Day {day}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:32px;text-align:center;color:#2c3e50;font-weight:bold;margin-top:10px;'>{greeting}</p>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align:center;margin-top:20px;'>✨ Task: {task_text}</h3>", unsafe_allow_html=True)

    prev_answer = answers.get(day, {}).get("text", "")
    prev_file = answers.get(day, {}).get("file", "")

    user_input = st.text_area("Enter your text or link:", value=prev_answer, height=150)
    uploaded_file = st.file_uploader("Upload your completed work (image, file, etc.)")

    if st.button("💾 Save Answer"):
        answers[day] = answers.get(day, {})
        answers[day]["text"] = user_input
        if uploaded_file:
            save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            answers[day]["file"] = save_path
        save_answers(answers)
        st.success("✅ Answer saved!")

    if day in answers:
        st.markdown("### 📝 Your Saved Answer:")
        if answers[day].get("text"):
            st.info(answers[day]["text"])
        if answers[day].get("file"):
            file_path = answers[day]["file"]
            file_name = os.path.basename(file_path)
            st.markdown(f"📎 Attached file: `{file_name}`")
            with open(file_path, "rb") as f:
                st.download_button("⬇️ Download File", data=f, file_name=file_name)
            if st.button("🗑️ Delete File"):
                try:
                    os.remove(file_path)
                    answers[day]["file"] = ""
                    save_answers(answers)
                    st.warning("File deleted!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting file: {e}")

    if st.button("✅ Completed!"):
        progress[day] = {"completed": True}
        save_progress(progress)
        st.balloons()
        st.success("🎈 Well done, Tanya! You’re amazing! 🎄")

    if st.button("⬅️ Back to Calendar"):
        st.session_state.page = "calendar"
        st.rerun()

# --- Router ---
if st.session_state.page == "calendar":
    show_calendar()
elif st.session_state.page == "day":
    show_day_page()

st.write("---")
st.markdown("<h4 style='text-align:center;'>Made with ❤️ for Tanya by Santa 🎅</h4>", unsafe_allow_html=True)
