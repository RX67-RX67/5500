import json
from datetime import datetime, timedelta, time
from typing import List, Dict

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}

WORK_START = time(8, 0)
WORK_END = time(22, 0)
SLOT_MINUTES = 15

def parse_time(t: str) -> datetime.time:
    return datetime.strptime(t, "%H:%M").time()

def group_slots_by_date(slots: List[Dict]) -> Dict[str, List[Dict]]:
    grouped = {}
    for s in slots:
        grouped.setdefault(s["date"], []).append(s)
    for v in grouped.values():
        v.sort(key=lambda x: x["start_time"])
    return grouped

def time_range(start: time, end: time, step_minutes: int) -> List[time]:
    slots = []
    t = datetime.combine(datetime.today(), start)
    end_dt = datetime.combine(datetime.today(), end)
    while t < end_dt:
        slots.append(t.time())
        t += timedelta(minutes=step_minutes)
    return slots

def overlap(t1_start, t1_end, t2_start, t2_end):
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
            (base_slots[i], base_slots[i + 1]) for i in range(len(base_slots) - 1)
        ]

    for block in occupied_blocks:
        date = block["date"]
        occ_start = datetime.strptime(block["start_time"], "%H:%M").time()
        occ_end = datetime.strptime(block["end_time"], "%H:%M").time()

        new_slots = []
        for start, end in all_slots.get(date, []):
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

def schedule_tasks(tasks: List[Dict], free_slots: List[Dict]) -> List[Dict]:
    tasks = sorted(tasks, key=lambda t: (
        t["deadline"],
        PRIORITY_ORDER.get(t["priority"], 99)
    ))

    slots_by_day = group_slots_by_date(free_slots)
    used_slots = []  # (date, start_time, end_time)

    scheduled = []

    for task in tasks:
        duration_needed = int(task["duration"] * 60)  # in minutes
        found = False

        for date in sorted(slots_by_day.keys()):
            if date > task["deadline"]:
                break

            slots = slots_by_day[date]
            slot_sequence = []
            total_minutes = 0

            for s in slots:
                start = parse_time(s["start_time"])
                end = parse_time(s["end_time"])

                start_dt = datetime.combine(datetime.today(), start)
                end_dt = datetime.combine(datetime.today(), end)
                delta = (end_dt - start_dt).seconds // 60

                slot_sequence.append(s)
                total_minutes += delta

                if total_minutes >= duration_needed:
                    actual_start = parse_time(slot_sequence[0]["start_time"])
                    actual_start_dt = datetime.combine(datetime.today(), actual_start)
                    actual_end_dt = actual_start_dt + timedelta(minutes=duration_needed)

                    conflict = any(
                        date == u_date and overlap(actual_start_dt.time(), actual_end_dt.time(), u_start, u_end)
                        for u_date, u_start, u_end in used_slots
                    )
                    if conflict:
                        break

                    scheduled.append({
                        "task_name": task["task_name"],
                        "date": date,
                        "start_time": actual_start_dt.strftime("%H:%M"),
                        "end_time": actual_end_dt.strftime("%H:%M"),
                        "duration": task["duration"],
                        "deadline": task["deadline"],
                        "priority": task["priority"]
                    })

                    used_slots.append((date, actual_start_dt.time(), actual_end_dt.time()))

                    found = True
                    break

            if found:
                break

        if not found:
            scheduled.append({
                **task,
                "status": "unscheduled"
            })

    return scheduled
