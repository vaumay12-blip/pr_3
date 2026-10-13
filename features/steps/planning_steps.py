"""Исполняемая связь между русским Gherkin и публичными методами."""
from behave import given, when, then


@given("заданы задачи")
def given_tasks(context):
    for row in context.table:
        context.manager.add_task(row["id"], row["название"], int(row["часы"]))


@given("заданы зависимости")
def given_dependencies(context):
    for row in context.table:
        context.manager.add_dependency(row["задача"], row["предшественник"])


@when("строится расписание")
def build_schedule(context):
    context.schedule = context.manager.build_schedule()


@then("получено расписание")
def check_schedule(context):
    actual = [(s.task_id, s.start, s.finish) for s in context.schedule]
    expected = [(r["id"], int(r["начало"]), int(r["конец"])) for r in context.table]
    assert actual == expected, (actual, expected)


@when('добавляется зависимость задачи "{task_id}" от "{prerequisite_id}"')
def add_dependency(context, task_id, prerequisite_id):
    try:
        context.manager.add_dependency(task_id, prerequisite_id)
    except ValueError as error:
        context.error = str(error)


@then('получена ошибка "{message}"')
def check_error(context, message):
    assert context.error == message, (context.error, message)


@then("сохранены зависимости")
def check_dependencies(context):
    expected = tuple(sorted((r["предшественник"], r["задача"]) for r in context.table))
    assert context.manager.get_dependencies() == expected
