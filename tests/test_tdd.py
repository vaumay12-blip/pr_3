"""TDD: тесты написаны до реализации; один экземпляр на каждый случай."""
from dataclasses import FrozenInstanceError
import pytest


def test_empty_manager(manager):
    assert manager.get_tasks() == ()
    assert manager.get_dependencies() == ()
    assert manager.build_schedule() == []


def test_add_and_normalize_task(manager):
    task = manager.add_task(" A ", " Анализ ", 3)
    assert (task.task_id, task.title, task.duration) == ("A", "Анализ", 3)
    assert manager.get_tasks() == (task,)


@pytest.mark.parametrize("task_id", ["", " ", "1A", "A B", None, 42])
def test_invalid_id(manager, task_id):
    with pytest.raises(ValueError):
        manager.add_task(task_id, "Работа", 1)
    assert manager.get_tasks() == ()


@pytest.mark.parametrize("title", ["", " ", None, 42])
def test_invalid_title(manager, title):
    with pytest.raises(ValueError):
        manager.add_task("A", title, 1)


@pytest.mark.parametrize("duration", [0, -1, 1.5, "2", True, None])
def test_invalid_duration(manager, duration):
    with pytest.raises(ValueError):
        manager.add_task("A", "Работа", duration)


def test_duplicate_task_is_rejected(manager):
    manager.add_task("A", "Первая", 2)
    with pytest.raises(ValueError):
        manager.add_task("A", "Вторая", 4)
    assert manager.get_tasks()[0].title == "Первая"


def test_task_snapshot_is_immutable(manager):
    task = manager.add_task("A", "Анализ", 2)
    with pytest.raises(FrozenInstanceError):
        task.duration = 99
    assert manager.get_tasks()[0].duration == 2


def test_single_task_schedule(manager):
    manager.add_task("A", "Анализ", 3)
    slot = manager.build_schedule()[0]
    assert (slot.task_id, slot.title, slot.start, slot.finish) == ("A", "Анализ", 0, 3)


@pytest.mark.parametrize("target, prerequisite", [("X", "A"), ("A", "X")])
def test_unknown_dependency_endpoint(manager, target, prerequisite):
    manager.add_task("A", "Анализ", 2)
    with pytest.raises(ValueError, match="Неизвестная задача"):
        manager.add_dependency(target, prerequisite)
    assert manager.get_dependencies() == ()


def test_self_dependency(manager):
    manager.add_task("A", "Анализ", 2)
    with pytest.raises(ValueError, match="самой себя"):
        manager.add_dependency("A", "A")
    assert manager.get_dependencies() == ()


def test_dependency_direction_and_duplicate(manager):
    manager.add_task("A", "Анализ", 2)
    manager.add_task("B", "Код", 3)
    manager.add_dependency("B", "A")
    manager.add_dependency("B", "A")
    assert manager.get_dependencies() == (("A", "B"),)
    slots = manager.build_schedule()
    assert [(s.task_id, s.start, s.finish) for s in slots] == [("A", 0, 2), ("B", 2, 5)]


def test_direct_cycle_is_rejected_without_mutation(manager):
    manager.add_task("A", "Анализ", 2)
    manager.add_task("B", "Код", 3)
    manager.add_dependency("B", "A")
    with pytest.raises(ValueError, match="цикл"):
        manager.add_dependency("A", "B")
    assert manager.get_dependencies() == (("A", "B"),)
    assert manager.build_schedule()[-1].finish == 5


def test_transitive_cycle_is_rejected(manager):
    for key in "ABC":
        manager.add_task(key, key, 1)
    manager.add_dependency("B", "A")
    manager.add_dependency("C", "B")
    with pytest.raises(ValueError, match="цикл"):
        manager.add_dependency("A", "C")
    assert manager.get_dependencies() == (("A", "B"), ("B", "C"))


def test_parallel_tasks_join_at_latest_finish(manager):
    for key, duration in [("A", 3), ("B", 2), ("C", 4), ("D", 1)]:
        manager.add_task(key, key, duration)
    for target, prerequisite in [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]:
        manager.add_dependency(target, prerequisite)
    assert [(s.task_id, s.start, s.finish) for s in manager.build_schedule()] == [
        ("A", 0, 3), ("B", 3, 5), ("C", 3, 7), ("D", 7, 8)]


def test_ready_task_order_is_lexicographic(manager):
    for key in ["C", "B", "A"]:
        manager.add_task(key, key, 1)
    manager.add_dependency("B", "A")
    assert [s.task_id for s in manager.build_schedule()] == ["A", "B", "C"]
    assert [t.task_id for t in manager.get_tasks()] == ["A", "B", "C"]


def test_schedule_is_repeatable_and_result_list_is_independent(manager):
    manager.add_task("A", "Анализ", 2)
    first = manager.build_schedule()
    assert first == manager.build_schedule()
    first.clear()
    assert len(manager.build_schedule()) == 1
