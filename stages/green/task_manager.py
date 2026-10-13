"""Этап GREEN: простая рабочая реализация с повторным просмотром задач."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Task:
    task_id: str
    title: str
    duration: int


@dataclass(frozen=True)
class ScheduleItem:
    task_id: str
    title: str
    start: int
    finish: int


class TaskManager:
    def __init__(self):
        self._tasks = {}
        self._dependencies = {}

    def add_task(self, task_id, title, duration):
        if not isinstance(task_id, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", task_id.strip()):
            raise ValueError("Некорректный идентификатор задачи")
        task_id = task_id.strip()
        if task_id in self._tasks:
            raise ValueError("Задача уже существует: " + task_id)
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Название задачи не должно быть пустым")
        if type(duration) is not int or duration <= 0:
            raise ValueError("Длительность должна быть положительным целым числом")
        task = Task(task_id, title.strip(), duration)
        self._tasks[task_id] = task
        self._dependencies[task_id] = set()
        return task

    def add_dependency(self, task_id, prerequisite_id):
        for key in [task_id, prerequisite_id]:
            if not isinstance(key, str) or key not in self._tasks:
                raise ValueError("Неизвестная задача: " + str(key))
        if task_id == prerequisite_id:
            raise ValueError("Задача не может зависеть от самой себя")
        # Идём от предшественника по его предшественникам до целевой задачи.
        stack = [prerequisite_id]
        visited = set()
        while stack:
            current = stack.pop()
            if current == task_id:
                raise ValueError("Зависимость создаёт цикл")
            if current not in visited:
                visited.add(current)
                stack.extend(self._dependencies[current])
        self._dependencies[task_id].add(prerequisite_id)

    def get_tasks(self):
        return tuple(self._tasks[key] for key in sorted(self._tasks))

    def get_dependencies(self):
        return tuple(sorted((p, t) for t, prerequisites in self._dependencies.items() for p in prerequisites))

    def build_schedule(self):
        result = []
        finishes = {}
        remaining = set(self._tasks)
        while remaining:
            ready = sorted(key for key in remaining if self._dependencies[key] <= finishes.keys())
            if not ready:
                raise ValueError("Зависимость создаёт цикл")
            key = ready[0]
            task = self._tasks[key]
            start = max((finishes[p] for p in self._dependencies[key]), default=0)
            finish = start + task.duration
            result.append(ScheduleItem(key, task.title, start, finish))
            finishes[key] = finish
            remaining.remove(key)
        return result
