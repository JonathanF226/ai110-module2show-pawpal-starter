"""PawPal+ — pet care planning app.

Skeleton generated from diagrams/uml_draft.mmd.
Owner has a Pet, a Pet has many Tasks, a Scheduler builds a daily plan.
"""

from dataclasses import dataclass, field


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: str
    recurrence: str
    completed: bool = False

    def priority_rank(self) -> int:
        ...

    def mark_complete(self) -> None:
        ...

    def is_recurring(self) -> bool:
        ...


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    def get_tasks(self) -> list[Task]:
        ...


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pet: "Pet | None" = None

    def add_pet(self, pet: Pet) -> None:
        ...

    def set_available_minutes(self, minutes: int) -> None:
        ...

    def add_preference(self, preference: str) -> None:
        ...


@dataclass
class Scheduler:
    time_budget: int
    tasks: list[Task] = field(default_factory=list)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        ...

    def filter_by_budget(self, tasks: list[Task]) -> list[Task]:
        ...

    def build_plan(self) -> list[Task]:
        ...

    def explain_plan(self) -> str:
        ...
