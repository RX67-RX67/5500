import json
import pandas as pd
import altair as alt
from datetime import datetime, timedelta


def load_data():
    with open("data/expanded_routine.json") as f:
        routines = json.load(f)
    with open("data/scheduled_tasks.json") as f:
        tasks = json.load(f)
    return routines, tasks


def build_dataframe(routines, tasks):
    routine_df = pd.DataFrame([{
        "name": r["activity_name"],
        "type": "Routine",
        "date": r["date"],
        "start": r["start_time"],
        "end": r["end_time"]
    } for r in routines])

    task_df = pd.DataFrame([{
        "name": t["task_name"],
        "type": "Task",
        "date": t["date"],
        "start": t["start_time"],
        "end": t["end_time"]
    } for t in tasks if "status" not in t])  

    df = pd.concat([routine_df, task_df], ignore_index=True)
    df["start_dt"] = pd.to_datetime(df["date"] + " " + df["start"])
    df["end_dt"] = pd.to_datetime(df["date"] + " " + df["end"])
    return df


def make_gantt_chart(df):

    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_week_dt = datetime.combine(start_of_week, datetime.min.time())  
    end_of_week_dt = start_of_week_dt + timedelta(days=7)  



    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('start_dt:T', scale=alt.Scale(domain=[start_of_week,end_of_week_dt])),
        x2='end_dt:T',
        y=alt.Y('name:N', title="Activity", sort=alt.EncodingSortField(field="start_dt", order="ascending")),
        color=alt.Color('type:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title="Type")),
        tooltip=['name', 'type', 'date', 'start', 'end']
    ).properties(
        width=800,
        height=400,
        title="📊 Weekly Gantt Chart of Activities"
    )
    return chart


# Streamlit UI Hook
if __name__ == "__main__":
    import streamlit as st

    st.header("📊 Weekly Gantt Chart")

    try:
        routines, tasks = load_data()
        df = build_dataframe(routines, tasks)
        chart = make_gantt_chart(df)
        st.altair_chart(chart, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to generate chart: {e}")
