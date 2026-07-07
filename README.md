# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Features

The scheduling engine (`Scheduler`, with helpers on `Task`/`Pet`) implements:

- **Priority sorting** — orders tasks HIGH → LOW, breaking ties so shorter tasks come first.
- **Sorting by time** — orders tasks by scheduled start time (minutes from midnight), with unscheduled tasks pushed to the end.
- **Filtering by pet and status** — returns tasks matching a completion status and/or pet name (case-insensitive), combined with AND.
- **Budget-aware planning** — greedily fits the highest-priority tasks into the owner's daily time budget.
- **Conflict warnings** — flags tasks booked at the same start time: HARD conflicts (same pet, can't be in two places) and soft conflicts (owner double-booked).
- **Daily/weekly recurrence** — completing a recurring task auto-spawns a fresh copy for its next occurrence; one-off tasks don't respawn.
- **Plan explanation** — produces a human-readable summary of the chosen plan and the time it consumes.

See [📐 Smarter Scheduling](#-smarter-scheduling) below for the methods and algorithmic details behind each feature.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
=== Today's Schedule ===
Plan for Alex (55/60 min):
  1. Clean litter box — HIGH, 20 min
  2. Morning walk — HIGH, 25 min
  3. Feed — MEDIUM, 10 min
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The tests in `tests/test_pawpal.py` cover the core scheduling behaviors:

- **Task basics** — `mark_complete()` flips a task's status; adding a task grows the pet's task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order, correctly placing a midnight task (`start_time=0`) first and pushing unscheduled tasks (`None`) to the end.
- **Recurrence logic** — completing a `daily` task marks it done and spawns a fresh, uncompleted copy for the next occurrence; a `once` task spawns nothing.
- **Conflict detection** — two tasks at the same start time are flagged as a **HARD** conflict (same pet) or **soft** conflict (different pets); a clean schedule produces no warnings.

Sample output from a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.11.5, pytest-7.4.0, pluggy-1.0.0
rootdir: .../ai110-module2show-pawpal-starter
collected 7 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 14%]
tests/test_pawpal.py::test_add_task_increases_count PASSED               [ 28%]
tests/test_pawpal.py::test_sort_by_time_is_chronological PASSED          [ 42%]
tests/test_pawpal.py::test_completing_daily_task_spawns_next_occurrence PASSED [ 57%]
tests/test_pawpal.py::test_completing_once_task_spawns_nothing PASSED    [ 71%]
tests/test_pawpal.py::test_detect_conflicts_flags_duplicate_times PASSED [ 85%]
tests/test_pawpal.py::test_detect_conflicts_clear_schedule PASSED        [100%]

============================== 7 passed in 0.01s ===============================
```

### Confidence Level: ⭐⭐⭐⭐☆ (4/5)

All 7 tests pass and cover the highest-risk logic: chronological sorting (including the `start_time=0` vs `None` edge case), recurrence spawning, and both conflict types. One star is withheld because a few edge cases remain untested — greedy budget packing near its limit, filtering combinations (`pet_name` + `completed`), repeated completion of already-spawned recurrences, and conflict detection based on overlapping *durations* rather than exact start-time matches. Reliable for the demonstrated behaviors; broaden coverage before relying on it in production.

## 📐 Smarter Scheduling

Beyond the basic priority-and-budget plan, PawPal+ implements four scheduling
behaviors. Each is a focused method on `Scheduler` (or `Task`/`Pet`).

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Priority sort orders HIGH→LOW, breaking ties by shorter duration. Time sort orders by `start_time` (minutes from midnight) and pushes unscheduled tasks (`None`) to the end. Both are non-mutating O(n log n) sorts. |
| Filtering (by pet / status) | `Scheduler.filter_tasks(completed=..., pet_name=...)` | Single O(n) pass; filters by completion status and/or pet name (case-insensitive), combining them with AND. `build_plan()` reuses it via `filter_tasks(completed=False)`. |
| Conflict detection | `Scheduler.detect_conflicts()` | Buckets scheduled, pending tasks by `start_time`; a slot with 2+ tasks is a conflict. **Same-pet** clashes are HARD (a pet can't be two places at once); **different-pet** clashes are soft (owner double-booked). Returns warning strings, never raises. Tradeoff: checks exact start-time matches only, not overlapping durations. |
| Recurring tasks | `Task.is_recurring()`, `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly` task via `complete_task()` marks it done and auto-spawns a fresh, uncompleted copy for the next occurrence. One-off (`once`) tasks return `None` and do not respawn. |

## 📸 Demo Walkthrough

### The interface

The Streamlit app (`app.py`) is organized top to bottom around a single session:

- **Owner & budget** — set the owner's name and a daily time budget (in minutes) that caps how much care fits in a day.
- **Pets** — add pets (name, species, age); each stays in memory for the session and shows its task count.
- **Tasks** — add tasks to a chosen pet with a title, duration, priority (low/medium/high), and recurrence (once/daily/weekly).
- **Task list** — filter tasks by status (all/pending/completed) and pet, and sort by **priority** or **start time**; a "Complete" button marks pending tasks done.
- **Build Schedule** — generates the day's plan, showing conflict warnings, a budget summary, and the ordered list of scheduled tasks.

### An example workflow

1. Enter the owner **Alex** with a **60-minute** daily budget.
2. Add a pet — **Rex** (dog) — then add another, **Milo** (cat).
3. Add tasks: Rex gets a *Morning walk* (HIGH, 25 min, daily) and *Give medication* (HIGH, 5 min, daily); Milo gets *Feed* (MEDIUM, 10 min, daily) and *Clean litter box* (HIGH, 20 min, daily).
4. In the task list, filter to **Rex** and sort by **priority** to see his most important tasks first.
5. Mark *Feed* complete — because it's a daily task, the app auto-adds a fresh copy for the next occurrence.
6. Click **Generate schedule** to view today's plan, along with any conflict warnings and how much of the 60-minute budget is used.

### Key Scheduler behaviors on display

- **Sorting** — the same task set reorders by priority (HIGH → LOW, shorter first on ties) or by start time (earliest first, unscheduled tasks last).
- **Filtering** — narrowing by pet and/or completion status combines the two predicates.
- **Conflict warnings** — two tasks at the same time for one pet raise a **HARD** conflict; across two pets they raise a **soft** (double-booked) conflict.
- **Recurrence** — completing a daily/weekly task spawns its next occurrence; a one-off task does not.
- **Budget-aware planning** — the plan greedily packs the highest-priority tasks until the daily minute budget is exhausted.

### Sample CLI output

Running the demo harness exercises every Scheduler method against a fixed set of pets and tasks:

```bash
python main.py
```

```
Completed 'Feed' -> spawned next occurrence: True

=== As entered (unsorted) ===
  18:00  Evening walk (HIGH, 25 min, pending)
  07:00  Morning walk (HIGH, 25 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)
  07:00  Give medication (HIGH, 5 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)
  12:00  Clean litter box (HIGH, 20 min, pending)
  08:00  Feed (MEDIUM, 10 min, done)
  08:00  Feed (MEDIUM, 10 min, pending)

=== Sorted by time ===
  07:00  Morning walk (HIGH, 25 min, pending)
  07:00  Give medication (HIGH, 5 min, pending)
  08:00  Feed (MEDIUM, 10 min, done)
  08:00  Feed (MEDIUM, 10 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)
  12:00  Clean litter box (HIGH, 20 min, pending)
  18:00  Evening walk (HIGH, 25 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)

=== Sorted by priority ===
  07:00  Give medication (HIGH, 5 min, pending)
  12:00  Clean litter box (HIGH, 20 min, pending)
  18:00  Evening walk (HIGH, 25 min, pending)
  07:00  Morning walk (HIGH, 25 min, pending)
  08:00  Feed (MEDIUM, 10 min, done)
  08:00  Feed (MEDIUM, 10 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)

=== Filter: pending only ===
  18:00  Evening walk (HIGH, 25 min, pending)
  07:00  Morning walk (HIGH, 25 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)
  07:00  Give medication (HIGH, 5 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)
  12:00  Clean litter box (HIGH, 20 min, pending)
  08:00  Feed (MEDIUM, 10 min, pending)

=== Filter: completed only ===
  08:00  Feed (MEDIUM, 10 min, done)

=== Filter: Rex's tasks ===
  18:00  Evening walk (HIGH, 25 min, pending)
  07:00  Morning walk (HIGH, 25 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)
  07:00  Give medication (HIGH, 5 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)

=== Filter: Rex's pending tasks ===
  18:00  Evening walk (HIGH, 25 min, pending)
  07:00  Morning walk (HIGH, 25 min, pending)
  --:--  Brush coat (LOW, 15 min, pending)
  07:00  Give medication (HIGH, 5 min, pending)
  12:00  Play fetch (MEDIUM, 15 min, pending)

=== Conflict Check ===
  ⚠️ HARD conflict at 07:00: Rex has 2 tasks at once ('Morning walk', 'Give medication').
  ⚠️ Soft conflict at 12:00: 2 tasks across pets Milo, Rex ('Play fetch', 'Clean litter box').

=== Today's Schedule ===
Plan for Alex (60/60 min):
  1. Give medication — HIGH, 5 min
  2. Clean litter box — HIGH, 20 min
  3. Evening walk — HIGH, 25 min
  4. Feed — MEDIUM, 10 min
```
