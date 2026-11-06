"""pipeline/high_rpm_scheduler.py — Calculates high-RPM publication timestamps for US/Tier-1 peak viewing hours.

High-RPM Markets: United States, United Kingdom, Canada, Australia, Germany.
Key Timezone Anchor: US Eastern Time (America/New_York).

Optimal Publication Windows (EST -> UTC):
  - 1 Video Daily:
      Slot 1: 14:00 EST (19:00 UTC) — Afternoon prime time.
  - 3 Videos Daily:
      Slot 1: 11:30 EST (16:30 UTC) — US lunch peak + UK evening commute.
      Slot 2: 15:30 EST (20:30 UTC) — US afternoon commute.
      Slot 3: 19:30 EST (00:30 UTC next day) — US prime evening.
  - 5 Shorts Daily:
      Slot 1: 09:00 EST (14:00 UTC) — US morning peak.
      Slot 2: 12:00 EST (17:00 UTC) — US lunch peak.
      Slot 3: 15:00 EST (20:00 UTC) — US afternoon peak.
      Slot 4: 18:00 EST (23:00 UTC) — US evening dinner rush.
      Slot 5: 21:00 EST (02:00 UTC next day) — US night wind-down + Australia morning.
"""
import datetime, zoneinfo

EST = zoneinfo.ZoneInfo("America/New_York")
UTC = zoneinfo.ZoneInfo("UTC")

SCHEDULE_WINDOWS = {
    1: [(14, 0)],
    3: [(11, 30), (15, 30), (19, 30)],
    5: [(9, 0), (12, 0), (15, 0), (18, 0), (21, 0)],
}


def calculate_schedule_times(quota: int = 1, reference_dt: datetime.datetime = None) -> list[dict]:
    """Calculates scheduled release timestamps for the given daily quota."""
    if quota not in SCHEDULE_WINDOWS:
        quota = 1

    if reference_dt is None:
        reference_dt = datetime.datetime.now(UTC)
    else:
        if reference_dt.tzinfo is None:
            reference_dt = reference_dt.replace(tzinfo=UTC)

    ref_est = reference_dt.astimezone(EST)
    windows = SCHEDULE_WINDOWS[quota]
    schedule = []

    for idx, (hour, minute) in enumerate(windows):
        target_est = ref_est.replace(hour=hour, minute=minute, second=0, microsecond=0)
        # If the target window has already passed by more than 15 minutes today, schedule for tomorrow
        if target_est < ref_est - datetime.timedelta(minutes=15):
            target_est += datetime.timedelta(days=1)

        target_utc = target_est.astimezone(UTC)
        schedule.append({
            "slot_index": idx + 1,
            "total_slots": quota,
            "est_time_str": target_est.strftime("%Y-%m-%d %I:%M %p %Z"),
            "iso_publish_time": target_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target_hour_est": hour,
            "market_note": f"Slot {idx+1}/{quota} aligned for US/Tier-1 peak traffic at {hour:02d}:{minute:02d} EST"
        })

    return schedule


if __name__ == "__main__":
    import json, sys
    q = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(json.dumps(calculate_schedule_times(q), indent=2))
