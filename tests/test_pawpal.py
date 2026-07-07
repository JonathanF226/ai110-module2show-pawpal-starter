"""Sample tests for PawPal+."""

from pawpal_system import Pet, Task, Priority


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
