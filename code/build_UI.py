import streamlit as st
import json
from datetime import time, date
from ics_parser import parse_ics_to_routine
from visualizer import build_dataframe, make_gantt_chart, load_data
from flow import weekly_schedule

st.set_page_config(page_title="Personal Scheduler", layout="centered")
st.title("🗓️ Personal Time Planner")


st.header("📆 Weekly Routine Activities")

routine_name = st.text_input("Routine Name", key="routine_name")
routine_category = st.selectbox("Category", ["Study", "Work", "Fitness", "Rest", "Social", "Other"], key="routine_cat")
routine_days = st.multiselect("Days of the Week", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key="routine_days")
routine_start = st.time_input("Start Time", value=time(9, 0), key="routine_start")
routine_end = st.time_input("End Time", value=time(10, 0), key="routine_end")

if st.button("➕ Add Routine Activity"):
    new_routine = {
        "activity_name": routine_name,
        "category": routine_category,
        "days": routine_days,
        "start_time": str(routine_start),
        "end_time": str(routine_end)
    }

    try:
        with open("data/routine.json", "r") as f:
            routine_data = json.load(f)
    except FileNotFoundError:
        routine_data = []

    routine_data.append(new_routine)
    with open("data/routine.json", "w") as f:
        json.dump(routine_data, f, indent=4)

    st.success(f"✅ Added routine: {routine_name} ({routine_days})")

st.subheader("📥 Import Weekly Routine from Google Calendar (.ics)")

uploaded_file = st.file_uploader("Upload your `.ics` file", type="ics")

if uploaded_file is not None:
    with open("data/calendar.ics", "wb") as f:
        f.write(uploaded_file.read())

    if st.button("📤 Import ICS File"):
        imported_items = parse_ics_to_routine("data/calendar.ics")
        st.success(f"✅ {len(imported_items)} activities imported from calendar.")
        st.json(imported_items)

# ---------- To-Do Task Section ----------
st.markdown("---")
st.header("📝 One-time To-Do Tasks")

task_name = st.text_input("Task Name", key="task_name")
task_duration = st.slider("Estimated Duration (hours)", 0.5, 8.0, step=0.5, key="task_duration")
task_deadline = st.date_input("Deadline", value=date.today(), key="task_deadline")
task_priority = st.select_slider("Priority", options=["Low", "Medium", "High"], key="task_priority")

if st.button("✅ Add Task"):
    new_task = {
        "task_name": task_name,
        "duration": task_duration,
        "deadline": str(task_deadline),
        "priority": task_priority
    }

    try:
        with open("data/tasks.json", "r") as f:
            task_data = json.load(f)
    except FileNotFoundError:
        task_data = []

    task_data.append(new_task)
    with open("data/tasks.json", "w") as f:
        json.dump(task_data, f, indent=4)

    st.success(f"📌 Task '{task_name}' added for {task_deadline}!")


# ---------- Visualization Section ----------
st.markdown("---")
st.title("📊 Weekly Gantt Chart")

if st.button("🚀 Run Weekly Scheduling Flow"):
    weekly_schedule()
    st.success("✅ Flow executed. Weekly tasks scheduled!")

    try:
        from visualizer import load_data
        routines, tasks = load_data()
        df = build_dataframe(routines, tasks)

        if df.empty:
            st.warning("No activities scheduled this week.")
        else:
            chart = make_gantt_chart(df)
            st.altair_chart(chart, use_container_width=True)

            with st.expander("📋 Raw Data"):
                st.dataframe(df)

    except Exception as e:
        st.error(f"⚠️ Failed to load chart: {e}")
