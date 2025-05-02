# app/expand_routine.py

from datetime import datetime, timedelta, date, time
from typing import List, Dict
from build_validator import RoutineItem

WEEKDAY_MAP = {
    "Mon": 0,
    "Tue": 1,
    "Wed": 2,
    "Thu": 3,
    "Fri": 4,
    "Sat": 5,
    "Sun": 6,
}

def get_this_week_start(today: date = date.today()) -> date:

    return today - timedelta(days=today.weekday())

def expand_routine(routine_items: List[RoutineItem], week_start: date = None) -> List[Dict]:

    if week_start is None:
        week_start = get_this_week_start()

    expanded = []

    for item in routine_items:
        for day in item.days:
            if day not in WEEKDAY_MAP:
                continue
            delta_days = WEEKDAY_MAP[day]
            activity_date = week_start + timedelta(days=delta_days)

            expanded.append({
                "activity_name": item.activity_name,
                "category": item.category,
                "date": activity_date.isoformat(),
                "start_time": item.start_time.strftime("%H:%M"),
                "end_time": item.end_time.strftime("%H:%M")
            })

    return expanded


if __name__ == "__main__":
    import json
    from build_validator import RoutineItem

    with open("data/routine.json") as f:
        raw = json.load(f)
        routines = [RoutineItem(**r) for r in raw]

    blocks = expand_routine(routines)
    print(json.dumps(blocks, indent=2))

    with open("data/expanded_routine.json", "w") as f:
        json.dump(blocks, f, indent=2)
