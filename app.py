"""Консольное приложение. python app.py; готовый пример: python app.py --demo."""
import argparse
from task_manager import TaskManager


def show_schedule(manager):
    schedule = manager.build_schedule()
    if not schedule:
        print("Список задач пуст")
        return
    print("\nID | Название | Начало, ч | Конец, ч")
    for item in schedule:
        print(f"{item.task_id} | {item.title} | {item.start} | {item.finish}")
    print("Общая длительность:", max(item.finish for item in schedule), "ч")


def demo():
    manager = TaskManager()
    for task in [("A", "Анализ", 3), ("B", "Разработка", 2), ("C", "Документация", 4), ("D", "Приёмка", 1)]:
        manager.add_task(*task)
    for task_id, prerequisite in [("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")]:
        manager.add_dependency(task_id, prerequisite)
    print("Менеджер зависимостей задач — вариант 96")
    print("Зависимости: A -> B, A -> C, B -> D, C -> D")
    show_schedule(manager)
    before = manager.build_schedule()
    print("\nПопытка добавить зависимость A от D:")
    try:
        manager.add_dependency("A", "D")
    except ValueError as error:
        print("Ошибка:", error)
    print("Расписание сохранено:", manager.build_schedule() == before)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        demo()
        return
    manager = TaskManager()
    print("Менеджер зависимостей задач. Вариант 96")
    print("Время — целые часы от начала проекта; независимые задачи параллельны.")
    while True:
        print("\n1 — добавить задачу; 2 — добавить зависимость; 3 — задачи и связи; 4 — расписание; 0 — выход")
        try:
            choice = input("Выбор: ").strip()
            if choice == "0":
                break
            if choice == "1":
                task_id = input("ID (латинская буква в начале): ").strip()
                title = input("Название: ")
                duration = int(input("Длительность в часах: "))
                manager.add_task(task_id, title, duration)
                print("Задача добавлена")
            elif choice == "2":
                task_id = input("ID зависимой задачи: ").strip()
                prerequisite = input("ID её предшественника: ").strip()
                manager.add_dependency(task_id, prerequisite)
                print("Зависимость установлена")
            elif choice == "3":
                for task in manager.get_tasks():
                    print(f"{task.task_id}: {task.title}, {task.duration} ч")
                if not manager.get_tasks():
                    print("Список задач пуст")
                for prerequisite, task_id in manager.get_dependencies():
                    print(f"{prerequisite} -> {task_id}")
            elif choice == "4":
                show_schedule(manager)
            else:
                print("Выберите пункт от 0 до 4")
        except ValueError as error:
            print("Ошибка:", error)
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена")
            break


if __name__ == "__main__":
    main()
