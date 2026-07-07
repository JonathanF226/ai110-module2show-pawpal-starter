"""Testing ground for PawPal+ — wires up an owner, pets, and tasks,
then prints today's schedule from the Scheduler."""

from pawpal_system import Owner, Pet, Task, Priority, Scheduler


def main() -> None:
    # Owner with a 60-minute daily care budget.
    owner = Owner(name="Alex", available_minutes=60)
    owner.scheduler = Scheduler(owner)

    # Two pets.
    rex = Pet(name="Rex", species="dog", age=3)
    milo = Pet(name="Milo", species="cat", age=5)
    owner.add_pet(rex)
    owner.add_pet(milo)

    # At least three tasks with different times/priorities.
    rex.add_task(Task("Morning walk", 25, Priority.HIGH, "daily"))
    rex.add_task(Task("Brush coat", 15, Priority.LOW, "weekly"))
    milo.add_task(Task("Feed", 10, Priority.MEDIUM, "daily"))
    milo.add_task(Task("Clean litter box", 20, Priority.HIGH, "daily"))

    # Print today's schedule.
    print("=== Today's Schedule ===")
    print(owner.scheduler.explain_plan())


if __name__ == "__main__":
    main()
