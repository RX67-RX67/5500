from datetime import datetime, timedelta
from icalendar import Calendar
import json

def parse_ics_to_routine(ics_path: str, output_path: str = "data/routine.json"):
    with open(ics_path, "rb") as f:
        gcal = Calendar.from_ical(f.read())

    routine_items = []

    today = datetime.today().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    try:
        with open(output_path, "r") as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []

    existing_keys = {
        (item["activity_name"], item["days"][0], item["start_time"])
        for item in existing
    }

    for component in gcal.walk():
        if component.name == "VEVENT":
            summary = str(component.get("summary"))
            start = component.get("dtstart")
            end = component.get("dtend")

            if not start or not end:
                print(f"⚠️ Skipped: Missing DTSTART or DTEND – {summary}")
                continue

            start = start.dt if hasattr(start, "dt") else start
            end = end.dt if hasattr(end, "dt") else end

            if not isinstance(start, datetime) or not isinstance(end, datetime):
                print(f"⚠️ Skipped: DTSTART/DTEND not datetime – {summary}")
                continue

            event_date = start.date()

            # test
            print(f"Event: {summary}, start={start}, parsed_date={event_date}")


            if not (start_of_week <= event_date <= end_of_week):
                continue

            if event_date.year != today.year:
                print(f"⏩ Skipped: {summary} is in year {event_date.year}, not this year")
                continue

            start_time = start.time()
            end_time = end.time()

            if end_time <= start_time:
                print(f"⚠️ Skipped: End before Start – {summary} ({start_time} → {end_time})")
                continue

            day = start.strftime("%a")[:3]
            item_key = (summary, day, start_time.strftime("%H:%M"))

            if item_key in existing_keys:
                print(f"⚠️ Skipped: Duplicate – {summary} on {day} at {start_time}")
                continue

            routine_items.append({
                "activity_name": summary,
                "category": "Imported",
                "days": [day],
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M")
            })

    merged = existing + routine_items

    with open(output_path, "w") as f:
        json.dump(merged, f, indent=4)

    return routine_items
