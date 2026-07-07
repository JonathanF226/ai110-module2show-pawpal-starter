"""Sample tests for PawPal+."""

from pawpal_system import Owner, Pet, Scheduler, Task, Priority


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed from False to True."""
    task = Task("Walk", 20, Priority.HIGH, "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Task Addition: adding a task grows the pet's task count by one."""
    pet = Pet("Rex", "dog", 3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Feed", 10, Priority.MEDIUM, "daily"))
    assert len(pet.get_tasks()) == 1


def _owner_with(pet: Pet) -> Owner:
    """Build an owner (with scheduler) that owns the given pet."""
    owner = Owner(name="Alex", available_minutes=60)
    owner.scheduler = Scheduler(owner)
    owner.add_pet(pet)
    return owner


def test_sort_by_time_is_chronological():
    """Sorting Correctness: sort_by_time returns tasks earliest-first,
    with unscheduled tasks pushed to the end."""
    pet = Pet("Rex", "dog", 3)
    evening = Task("Evening walk", 25, Priority.HIGH, "daily", start_time=18 * 60)
    morning = Task("Morning walk", 25, Priority.HIGH, "daily", start_time=7 * 60)
    midnight = Task("Midnight check", 5, Priority.LOW, "daily", start_time=0)
    unscheduled = Task("Brush coat", 15, Priority.LOW, "weekly")
    for t in (evening, morning, midnight, unscheduled):
        pet.add_task(t)
    owner = _owner_with(pet)

    ordered = owner.scheduler.sort_by_time(pet.get_tasks())

    assert ordered == [midnight, morning, evening, unscheduled]


def test_completing_daily_task_spawns_next_occurrence():
    """Recurrence Logic: completing a daily task marks it done and adds a
    fresh, uncompleted next occurrence for the following day."""
    pet = Pet("Rex", "dog", 3)
    feed = Task("Feed", 10, Priority.MEDIUM, "daily", start_time=8 * 60)
    pet.add_task(feed)

    spawned = pet.complete_task(feed)

    assert feed.completed is True
    assert spawned is not None
    assert spawned.completed is False
    assert spawned is not feed
    assert spawned.name == feed.name
    assert spawned.recurrence == feed.recurrence
    assert spawned.start_time == feed.start_time
    assert len(pet.get_tasks()) == 2


def test_completing_once_task_spawns_nothing():
    """Recurrence Logic: a one-off task has no next occurrence."""
    pet = Pet("Rex", "dog", 3)
    vet = Task("Vet visit", 30, Priority.HIGH, "once", start_time=9 * 60)
    pet.add_task(vet)

    spawned = pet.complete_task(vet)

    assert vet.completed is True
    assert spawned is None
    assert len(pet.get_tasks()) == 1


def test_detect_conflicts_flags_duplicate_times():
    """Conflict Detection: two tasks at the same start time are flagged —
    HARD for the same pet, soft across different pets."""
    rex = Pet("Rex", "dog", 3)
    milo = Pet("Milo", "cat", 5)

    # Same pet, same time -> hard conflict at 07:00.
    rex.add_task(Task("Morning walk", 25, Priority.HIGH, "daily", start_time=7 * 60))
    rex.add_task(Task("Give medication", 5, Priority.HIGH, "daily", start_time=7 * 60))
    # Different pets, same time -> soft conflict at 12:00.
    rex.add_task(Task("Play fetch", 15, Priority.MEDIUM, "daily", start_time=12 * 60))
    milo.add_task(Task("Clean litter box", 20, Priority.HIGH, "daily", start_time=12 * 60))

    owner = Owner(name="Alex", available_minutes=60)
    owner.scheduler = Scheduler(owner)
    owner.add_pet(rex)
    owner.add_pet(milo)

    warnings = owner.scheduler.detect_conflicts()

    assert len(warnings) == 2
    assert any("HARD" in w and "07:00" in w for w in warnings)
    assert any("Soft" in w and "12:00" in w for w in warnings)


def test_detect_conflicts_clear_schedule():
    """Conflict Detection: no duplicate times -> no warnings."""
    pet = Pet("Rex", "dog", 3)
    pet.add_task(Task("Morning walk", 25, Priority.HIGH, "daily", start_time=7 * 60))
    pet.add_task(Task("Evening walk", 25, Priority.HIGH, "daily", start_time=18 * 60))
    owner = _owner_with(pet)

    assert owner.scheduler.detect_conflicts() == []
