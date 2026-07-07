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

    def priority_rank(self) -> int:
        """Numeric rank of this task's priority (higher = more important)."""
        return int(self.priority)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_recurring(self) -> bool:
        """True if the task repeats rather than being a one-off."""
        return self.recurrence.strip().lower() not in ("", "none", "once")


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
        """Return tasks ordered high priority first, then shorter duration."""
        return sorted(
            tasks,
            key=lambda t: (-t.priority_rank(), t.duration_minutes),
        )

    def filter_by_budget(self, tasks: list[Task]) -> list[Task]:
        """Greedily keep tasks that fit within the owner's time budget."""
        remaining = self.owner.available_minutes
        selected: list[Task] = []
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def build_plan(self) -> list[Task]:
        """Build today's plan: pending tasks, prioritized and budget-limited."""
        pending = [t for t in self.owner.all_tasks() if not t.completed]
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
