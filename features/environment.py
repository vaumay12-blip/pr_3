"""Изолированное состояние перед каждым BDD-сценарием."""
from implementation import load_implementation


def before_scenario(context, scenario):
    context.manager = load_implementation().TaskManager()
    context.error = None
    context.schedule = None
