"""PawPal+ — pet care planning app.

Skeleton generated from diagrams/uml_draft.mmd.
Owner owns a Pet and a Scheduler; a Pet has many Tasks; the Scheduler reads
the Owner's constraints and the Pet's tasks to build a daily plan.
"""

from dataclasses import dataclass, field
from enum import IntEnum


class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: Priority
    recurrence: str
    completed: bool = False
    start_time: int | None = None  # minutes from midnight; None = unscheduled

    def priority_rank(self) -> int:
        """Numeric rank of this task's priority (higher = more important)."""
        return int(self.priority)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_recurring(self) -> bool:
        """True if the task repeats rather than being a one-off."""
        return self.recurrence.strip().lower() not in ("", "none", "once")

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy for this task's next occurrence.

        Returns None for one-off tasks. The copy keeps name, duration,
        priority, recurrence, and start_time, but resets completed to False —
        it represents the same task on its next day/week.
        """
        if not self.is_recurring():
            return None
        return Task(
            name=self.name,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            completed=False,
            start_time=self.start_time,
        )


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete; auto-add its next occurrence if recurring.

        Returns the newly created next-occurrence task (or None for one-offs).
        """
        task.mark_complete()
        nxt = task.next_occurrence()
        if nxt is not None:
            self.add_task(nxt)
        return nxt

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)
    scheduler: "Scheduler | None" = None

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def set_available_minutes(self, minutes: int) -> None:
        """Set the daily time budget the owner has for pet care."""
        if minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        self.available_minutes = minutes

    def add_preference(self, preference: str) -> None:
        """Record an owner preference, avoiding duplicates."""
        if preference not in self.preferences:
            self.preferences.append(preference)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class Scheduler:
    owner: Owner

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered high priority first, then shorter duration.

        Algorithm: one stable sort (O(n log n)) on a tuple key. `-priority_rank`
        makes higher priority sort first (descending); `duration_minutes` breaks
        ties so shorter tasks come first. Non-mutating — returns a new list.
        """
        return sorted(
            tasks,
            key=lambda t: (-t.priority_rank(), t.duration_minutes),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by scheduled start time (earliest first).

        Algorithm: a single stable sort (Timsort, O(n log n)) on a tuple key.
        The first element (`start_time is None`) is a boolean that sorts False
        before True, pushing unscheduled tasks to the end; the second element
        orders the scheduled tasks by their start_time. Non-mutating — returns
        a new list and leaves the input untouched.
        """
        return sorted(
            tasks,
            key=lambda t: (t.start_time is None, t.start_time or 0),
        )

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return the owner's tasks filtered by completion status and/or pet.

        Both filters are optional and combine (AND). With no arguments,
        returns every task across all pets.

        - completed=True/False keeps only tasks with that completion status.
        - pet_name keeps only tasks belonging to the pet with that name
          (case-insensitive).

        Algorithm: a single linear pass (O(n) over all tasks) applying each
        active predicate; a task is kept only if it passes every filter. Iterates
        owner.pets directly rather than the flat all_tasks() list because Task has
        no back-reference to its pet, so pet identity is only available here.
        """
        result: list[Task] = []
        for pet in self.owner.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.get_tasks():
                if completed is not None and task.completed != completed:
                    continue
                result.append(task)
        return result

    def filter_by_budget(self, tasks: list[Task]) -> list[Task]:
        """Greedily keep tasks that fit within the owner's time budget.

        Algorithm: a single greedy pass (O(n)) in the given order, taking each
        task whose duration fits the remaining budget and subtracting it. Assumes
        the caller has already sorted by priority, so higher-priority tasks get
        first claim. Greedy, not optimal — it will skip a task that doesn't fit
        and never revisit it, even if a smaller later task could have filled the
        gap better (this is the classic knapsack tradeoff, traded for simplicity).
        """
        remaining = self.owner.available_minutes
        selected: list[Task] = []
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def detect_conflicts(self) -> list[str]:
        """Lightweight check for tasks scheduled at the same start time.

        Groups pending, scheduled tasks by start_time and flags any slot
        holding more than one task. Same-pet clashes are hard conflicts
        (a pet can't be in two places); different-pet clashes are soft
        (the owner is double-booked). Returns a list of warning strings —
        empty if the schedule is clear. Never raises.
        """
        # Collect (pet_name, task) pairs for scheduled, pending tasks.
        by_time: dict[int, list[tuple[str, Task]]] = {}
        for pet in self.owner.pets:
            for task in pet.get_tasks():
                if task.completed or task.start_time is None:
                    continue
                by_time.setdefault(task.start_time, []).append((pet.name, task))

        warnings: list[str] = []
        for start in sorted(by_time):
            group = by_time[start]
            if len(group) < 2:
                continue
            hhmm = f"{start // 60:02d}:{start % 60:02d}"
            pets = {pet_name for pet_name, _ in group}
            names = ", ".join(f"'{t.name}'" for _, t in group)
            if len(pets) == 1:
                warnings.append(
                    f"⚠️ HARD conflict at {hhmm}: {pets.pop()} has "
                    f"{len(group)} tasks at once ({names})."
                )
            else:
                warnings.append(
                    f"⚠️ Soft conflict at {hhmm}: {len(group)} tasks across "
                    f"pets {', '.join(sorted(pets))} ({names})."
                )
        return warnings

    def build_plan(self) -> list[Task]:
        """Build today's plan: pending tasks, prioritized and budget-limited."""
        pending = self.filter_tasks(completed=False)
        return self.filter_by_budget(self.sort_by_priority(pending))

    def explain_plan(self) -> str:
        """Human-readable summary of the plan and the time it consumes."""
        plan = self.build_plan()
        if not plan:
            return "No tasks fit today's schedule."
        used = sum(t.duration_minutes for t in plan)
        lines = [
            f"Plan for {self.owner.name} "
            f"({used}/{self.owner.available_minutes} min):"
        ]
        for i, task in enumerate(plan, 1):
            lines.append(
                f"  {i}. {task.name} — {task.priority.name}, "
                f"{task.duration_minutes} min"
            )
        return "\n".join(lines)
