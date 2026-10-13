"""Загрузка этапа разработки; без параметра используется итоговая версия."""
import importlib.util
import os
from pathlib import Path
import sys


def load_implementation():
    root = Path(__file__).resolve().parent
    path = root / os.environ.get("TASK_MANAGER_IMPL", "task_manager.py")
    spec = importlib.util.spec_from_file_location("selected_task_manager", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
