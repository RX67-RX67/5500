from datetime import datetime, time, timedelta
import json
from typing import List, Dict

WORK_START = time(8, 0)
WORK_END = time(22, 0)
SLOT_MINUTES = 15

def time_range(start: time, end: time, step_minutes: int) -> List[time]:
    slots = []
    t = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while t < end_dt:
        slots.append(t.time())
        t += timedelta(minutes=step_minutes)
    return slots

def overlap(t1_start: time, t1_end: time, t2_start: time, t2_end: time) -> bool:
    return t1_start < t2_end and t2_start < t1_end

def get_free_slots(occupied_blocks: List[Dict]) -> List[Dict]:
    all_slots = {}

    def get_this_week_dates(start: datetime.date) -> List[str]:
        return [(start + timedelta(days=i)).isoformat() for i in range(7)]

    week_start = min(datetime.strptime(b["date"], "%Y-%m-%d").date() for b in occupied_blocks)
    all_dates = get_this_week_dates(week_start)

    for date_str in all_dates:
        base_slots = time_range(WORK_START, WORK_END, SLOT_MINUTES)
        all_slots[date_str] = [
            (base_slots[i], base_slots[i+1]) for i in range(len(base_slots) - 1)
        ]

    for block in occupied_blocks:
        date_str = block["date"]
        day_slots = all_slots.setdefault(date_str, [])

        base_slots = time_range(WORK_START, WORK_END, SLOT_MINUTES)
        for i in range(len(base_slots) - 1):
            start = base_slots[i]
            end = base_slots[i+1]
            day_slots.append((start, end))

    for block in occupied_blocks:
        date = block["date"]
        occ_start = datetime.strptime(block["start_time"], "%H:%M").time()
        occ_end = datetime.strptime(block["end_time"], "%H:%M").time()

        new_slots = []
        for start, end in all_slots[date]:
            if not overlap(start, end, occ_start, occ_end):
                new_slots.append((start, end))
        all_slots[date] = new_slots

    result = []
    for date, slots in all_slots.items():
        for start, end in slots:
            result.append({
                "date": date,
                "start_time": start.strftime("%H:%M"),
                "end_time": end.strftime("%H:%M")
            })

    return result

if __name__ == "__main__":
    with open("data/expanded_routine.json") as f:
        routine_blocks = json.load(f)

    free = get_free_slots(routine_blocks)
    print(json.dumps(free, indent=2))

    with open("data/free_slots.json", "w") as f:
        json.dump(free, f, indent=2)
