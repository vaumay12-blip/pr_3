"""ATDD: проверка приёмочных критериев через публичный интерфейс приложения."""
import pytest


def test_ac01_plan_project(manager):
    manager.add_task("A", "Анализ", 3)
    manager.add_task("B", "Разработка", 2)
    manager.add_task("C", "Документация", 4)
    manager.add_task("D", "Приёмка", 1)
    for target, prerequisite in [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]:
        manager.add_dependency(target, prerequisite)
    plan = manager.build_schedule()
    assert [(s.task_id, s.start, s.finish) for s in plan] == [
        ("A", 0, 3), ("B", 3, 5), ("C", 3, 7), ("D", 7, 8)]
    assert max(s.finish for s in plan) == 8


def test_ac02_independent_tasks_start_together(manager):
    manager.add_task("B", "Код", 5)
    manager.add_task("A", "Дизайн", 2)
    assert [(s.task_id, s.start, s.finish) for s in manager.build_schedule()] == [
        ("A", 0, 2), ("B", 0, 5)]


def test_ac03_invalid_dependency_preserves_valid_plan(manager):
    manager.add_task("A", "Анализ", 2)
    manager.add_task("B", "Код", 3)
    manager.add_dependency("B", "A")
    before = manager.build_schedule()
    with pytest.raises(ValueError, match="цикл"):
        manager.add_dependency("A", "B")
    assert manager.build_schedule() == before


def test_ac04_duplicate_link_does_not_delay_task(manager):
    manager.add_task("A", "Анализ", 2)
    manager.add_task("B", "Код", 1)
    for _ in range(3):
        manager.add_dependency("B", "A")
    assert manager.get_dependencies() == (("A", "B"),)
    assert manager.build_schedule()[-1].finish == 3


def test_ac05_empty_project_and_invalid_input(manager):
    assert manager.build_schedule() == []
    with pytest.raises(ValueError):
        manager.add_task("A", "Анализ", 0)
    assert manager.get_tasks() == ()
    manager.add_task("A", "Анализ", 1)
    with pytest.raises(ValueError, match="Неизвестная задача"):
        manager.add_dependency("A", "X")
    assert manager.build_schedule()[0].start == 0
