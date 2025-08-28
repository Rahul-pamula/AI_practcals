# healthcare_scheduler_simple_fixed.py
from typing import List, Dict

SHIFTS = [
    ("Morning", "08:00 - 14:00"),
    ("Evening", "14:00 - 20:00"),
    ("Night", "20:00 - 08:00"),
]

SHIFT_NAMES = [s[0] for s in SHIFTS]


def parse_availability_input(line: str) -> List[str]:
    """Parse availability string into list of shift names."""
    if not line:
        return []
    parts = []
    for sep in [",", ";", "/", "|"]:
        line = line.replace(sep, ",")
    for token in line.split(","):
        tok = token.strip().lower()
        if not tok:
            continue
        if tok in ("all", "any", "*"):
            return SHIFT_NAMES[:]  # all shifts
        for s in SHIFT_NAMES:
            if tok == s.lower() or tok == s.lower().replace(" ", ""):
                parts.append(s)
                break
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def is_valid(schedule: Dict[str, Dict[str, str]], day: str, shift: str, staff: str,
             availability: Dict[str, Dict[str, List[str]]]) -> bool:
    if shift not in availability.get(staff, {}).get(day, []):
        return False
    if staff in schedule[day].values():
        return False
    return True


def find_best_schedule(days: List[str], staff_list: List[str],
                       availability: Dict[str, Dict[str, List[str]]]):
    vars_list = [(d, s) for d in days for s in SHIFT_NAMES]
    total_slots = len(vars_list)
    schedule = {d: {s: None for s in SHIFT_NAMES} for d in days}
    best = {"filled": -1, "schedule": None}

    def dfs(idx: int, current_filled: int):
        remaining = total_slots - idx
        if current_filled + remaining <= best["filled"]:
            return
        if idx == total_slots:
            if current_filled > best["filled"]:
                copy_sched = {d: {s: schedule[d][s]
                                  for s in SHIFT_NAMES} for d in days}
                best["filled"] = current_filled
                best["schedule"] = copy_sched
            return
        day, shift = vars_list[idx]
        for staff in staff_list:
            if is_valid(schedule, day, shift, staff, availability):
                schedule[day][shift] = staff
                dfs(idx + 1, current_filled + 1)
                schedule[day][shift] = None
        dfs(idx + 1, current_filled)

    dfs(0, 0)
    return best["schedule"], best["filled"], total_slots


def pretty_print(schedule: Dict[str, Dict[str, str]]):
    for d in schedule:
        print(f"\n{d}:")
        for s_name, s_time in SHIFTS:
            who = schedule[d][s_name]
            if who:
                print(f" {s_name} ({s_time}): Dr. {who}")
            else:
                print(f" {s_name} ({s_time}): [Unassigned]")


if __name__ == "__main__":
    print("=== Simple Healthcare Doctor Scheduler (fixed) ===")
    num_days = int(input("Enter number of days to schedule: ").strip() or "0")
    days = [f"Day{i+1}" for i in range(num_days)]

    print("\nShifts (fixed):")
    for name, times in SHIFTS:
        print(f" - {name}: {times}")

    num_doctors = int(input("\nEnter number of doctors: ").strip() or "0")
    staff_list: List[str] = []
    availability: Dict[str, Dict[str, List[str]]] = {}

    for i in range(num_doctors):
        name = input(f"\nEnter name of doctor {i+1}: ").strip() or f"Dr{i+1}"
        staff_list.append(name)
        availability[name] = {}
        for d in days:
            raw = input(
                f" Available shifts for Dr. {name} on {d} (comma separated; 'all' means all shifts): ").strip()
            parsed = parse_availability_input(raw)
            availability[name][d] = parsed

    final_schedule, filled, total = find_best_schedule(
        days, staff_list, availability)

    if final_schedule is None:
        print("No schedule could be produced.")
    else:
        print("\n=== Result ===")
        pretty_print(final_schedule)
        print(f"\nFilled shifts: {filled}/{total}")
        if filled < total:
            print(
                "Some shifts remain unassigned. Consider adding more doctors or increasing availability.")
