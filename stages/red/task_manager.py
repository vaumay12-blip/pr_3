"""Этап RED: интерфейс определён, функциональность ещё не реализована."""


class TaskManager:
    def add_task(self, task_id, title, duration):
        raise NotImplementedError("Добавление задачи ещё не реализовано")

    def add_dependency(self, task_id, prerequisite_id):
        raise NotImplementedError("Зависимости ещё не реализованы")

    def get_tasks(self):
        raise NotImplementedError("Просмотр задач ещё не реализован")

    def get_dependencies(self):
        raise NotImplementedError("Просмотр зависимостей ещё не реализован")

    def build_schedule(self):
        raise NotImplementedError("Планирование ещё не реализовано")
