# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
