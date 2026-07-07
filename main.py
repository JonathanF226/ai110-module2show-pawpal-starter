"""Testing ground for PawPal+ — wires up an owner, pets, and tasks,
then exercises the Scheduler's sorting and filtering methods."""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def hhmm(minutes: int | None) -> str:
    """Format minutes-from-midnight as HH:MM (or '--:--' if unscheduled)."""
    if minutes is None:
        return "--:--"
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def show(title: str, tasks: list[Task]) -> None:
    """Print a labeled list of tasks."""
    print(f"\n=== {title} ===")
    if not tasks:
        print("  (none)")
        return
    for t in tasks:
        status = "done" if t.completed else "pending"
        print(
            f"  {hhmm(t.start_time)}  {t.name} "
            f"({t.priority.name}, {t.duration_minutes} min, {status})"
        )


def main() -> None:
    # Owner with a 60-minute daily care budget.
    owner = Owner(name="Alex", available_minutes=60)
    owner.scheduler = Scheduler(owner)

    # Two pets.
    rex = Pet(name="Rex", species="dog", age=3)
    milo = Pet(name="Milo", species="cat", age=5)
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Tasks added OUT OF TIME ORDER on purpose (start_time = minutes from midnight).
    rex.add_task(Task("Evening walk", 25, Priority.HIGH, "daily", start_time=18 * 60))
    rex.add_task(Task("Morning walk", 25, Priority.HIGH, "daily", start_time=7 * 60))
    milo.add_task(Task("Clean litter box", 20, Priority.HIGH, "daily", start_time=12 * 60))
    milo.add_task(Task("Feed", 10, Priority.MEDIUM, "daily", start_time=8 * 60))
    rex.add_task(Task("Brush coat", 15, Priority.LOW, "weekly"))  # unscheduled

    # Two tasks at the SAME time for the same pet -> hard conflict at 07:00.
    rex.add_task(Task("Give medication", 5, Priority.HIGH, "daily", start_time=7 * 60))
    # A task overlapping another pet's slot -> soft conflict at 12:00.
    rex.add_task(Task("Play fetch", 15, Priority.MEDIUM, "daily", start_time=12 * 60))

    # Complete a recurring task — auto-spawns the next occurrence.
    feed = milo.tasks[1]  # Feed (daily)
    spawned = milo.complete_task(feed)
    print(f"Completed '{feed.name}' -> spawned next occurrence: {spawned is not None}")

    sched = owner.scheduler
    all_tasks = owner.all_tasks()

    # Insertion order (as added — deliberately unsorted).
    show("As entered (unsorted)", all_tasks)

    # New sorting methods.
    show("Sorted by time", sched.sort_by_time(all_tasks))
    show("Sorted by priority", sched.sort_by_priority(all_tasks))

    # New filtering method.
    show("Filter: pending only", sched.filter_tasks(completed=False))
    show("Filter: completed only", sched.filter_tasks(completed=True))
    show("Filter: Rex's tasks", sched.filter_tasks(pet_name="Rex"))
    show("Filter: Rex's pending tasks", sched.filter_tasks(pet_name="Rex", completed=False))

    # Conflict detection.
    print("\n=== Conflict Check ===")
    conflicts = sched.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  No scheduling conflicts.")

    # The budget-limited daily plan.
    print("\n=== Today's Schedule ===")
    print(sched.explain_plan())


if __name__ == "__main__":
    main()
