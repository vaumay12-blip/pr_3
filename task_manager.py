"""Менеджер зависимостей задач. Вариант 96. Итог после рефакторинга.

Направление ребра: предшественник -> зависимая задача.
Расписание строится в часах от 0 при неограниченных параллельных ресурсах.
"""
from dataclasses import dataclass
import heapq
import re


@dataclass(frozen=True)
class Task:
    """Неизменяемое описание задачи."""
    task_id: str
    title: str
    duration: int


@dataclass(frozen=True)
class ScheduleItem:
    """Начало и окончание задачи в относительных часах."""
    task_id: str
    title: str
    start: int
    finish: int


class TaskManager:
    """Хранит задачи и множества их непосредственных предшественников."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._dependencies: dict[str, set[str]] = {}

    def add_task(self, task_id: str, title: str, duration: int) -> Task:
        """Добавить уникальную задачу. Некорректный ввод вызывает ValueError."""
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

    def _require_task(self, task_id: str) -> None:
        """Проверка существования без изменения состояния."""
        if not isinstance(task_id, str) or task_id not in self._tasks:
            raise ValueError("Неизвестная задача: " + str(task_id))

    def add_dependency(self, task_id: str, prerequisite_id: str) -> None:
        """Установить связь; цикл отклоняется, повтор связи ничего не меняет."""
        self._require_task(task_id)
        self._require_task(prerequisite_id)
        if task_id == prerequisite_id:
            raise ValueError("Задача не может зависеть от самой себя")
        if prerequisite_id in self._dependencies[task_id]:
            return
        # Проверяется отдельная копия графа: при ошибке исходный граф сохраняется.
        candidate = {key: set(values) for key, values in self._dependencies.items()}
        candidate[task_id].add(prerequisite_id)
        self._topological_order(candidate)
        self._dependencies = candidate

    def get_tasks(self) -> tuple[Task, ...]:
        """Получить неизменяемый снимок задач в порядке идентификаторов."""
        return tuple(self._tasks[key] for key in sorted(self._tasks))

    def get_dependencies(self) -> tuple[tuple[str, str], ...]:
        """Получить пары (предшественник, зависимая задача), отсортированные по ID."""
        return tuple(sorted((p, task) for task, predecessors in self._dependencies.items() for p in predecessors))

    def _topological_order(self, dependencies: dict[str, set[str]]) -> list[str]:
        """Алгоритм Кана; среди готовых задач выбирается наименьший ID."""
        indegree = {key: len(predecessors) for key, predecessors in dependencies.items()}
        followers = {key: [] for key in dependencies}
        for task_id, predecessors in dependencies.items():
            for prerequisite_id in predecessors:
                followers[prerequisite_id].append(task_id)
        ready = [key for key, degree in indegree.items() if degree == 0]
        heapq.heapify(ready)
        order = []
        while ready:
            task_id = heapq.heappop(ready)
            order.append(task_id)
            for follower in followers[task_id]:
                indegree[follower] -= 1
                if indegree[follower] == 0:
                    heapq.heappush(ready, follower)
        if len(order) != len(dependencies):
            raise ValueError("Зависимость создаёт цикл")
        return order

    def build_schedule(self) -> list[ScheduleItem]:
        """Построить самое раннее расписание без ограничений на ресурсы."""
        order = self._topological_order(self._dependencies)
        finishes: dict[str, int] = {}
        schedule = []
        for task_id in order:
            task = self._tasks[task_id]
            start = max((finishes[p] for p in self._dependencies[task_id]), default=0)
            finish = start + task.duration
            schedule.append(ScheduleItem(task_id, task.title, start, finish))
            finishes[task_id] = finish
        return schedule
