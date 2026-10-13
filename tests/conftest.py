"""Каждый тест получает новый экземпляр менеджера."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from implementation import load_implementation


@pytest.fixture
def manager():
    return load_implementation().TaskManager()
