from prefect import flow, task
from ics_parser import parse_ics_to_routine
from expand_routine import expand_routine
from get_free_slot import get_free_slots
from schedule import schedule_tasks
from build_validator import RoutineItem, TaskItem
import json
import os

@task
def clean_data():
    files_to_delete = [
        "data/calendar.ics",
        "data/expanded_routine.json",
        "data/free_slots.json",
        "data/scheduled_tasks.json"
    ]
    for f in files_to_delete:
        if os.path.exists(f):
            os.remove(f)
            print(f"✅ Deleted: {f}")

@task
def validate_routine():
    with open("data/routine.json") as f:
        raw = json.load(f)

    validated = []
    for r in raw:
        try:
            validated.append(RoutineItem(**r))
        except Exception as e:
            print(f"⚠️ Skipped invalid routine: {r['activity_name']} ({e})")

    print(f"✅ {len(validated)} routines validated.")

@task
def validate_tasks():
    with open("data/tasks.json") as f:
        raw = json.load(f)
    _ = [TaskItem(**t) for t in raw]
    print("✅ Task validation passed")

@task
def run_parse():
    if os.path.exists("data/calendar.ics"):
        parse_ics_to_routine("data/calendar.ics")
    else:
        print("⚠️ 'data/calendar.ics' not found. Skipping ICS parsing.")

@task
def run_expand():
    with open("data/routine.json") as f:
        raw = json.load(f)
        routines = [RoutineItem(**r) for r in raw]
    
    expanded = expand_routine(routines)

    with open("data/expanded_routine.json", "w") as f:
        json.dump(expanded, f, indent=4)

@task
def run_slots():
    with open("data/expanded_routine.json") as f:
        occupied_blocks = json.load(f)

    free_slots = get_free_slots(occupied_blocks)

    with open("data/free_slots.json", "w") as f:
        json.dump(free_slots, f, indent=4)

@task
def run_schedule():
    with open("data/tasks.json") as f:
        tasks = json.load(f)
    with open("data/free_slots.json") as f:
        free_slots = json.load(f)

    scheduled = schedule_tasks(tasks, free_slots)

    with open("data/scheduled_tasks.json", "w") as f:
        json.dump(scheduled, f, indent=4)

@flow(name="Weekly Schedule Flow")
def weekly_schedule():
    clean_data()
    run_parse()
    validate_routine()
    validate_tasks()
    run_expand()
    run_slots()
    run_schedule()

if __name__ == "__main__":
    weekly_schedule()
