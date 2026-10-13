"""SDD: каждая строка examples.csv автоматически становится тестом."""
import csv
import json
from pathlib import Path
import pytest

PATH = Path(__file__).resolve().parents[1] / "specifications" / "examples.csv"
with PATH.open(encoding="utf-8", newline="") as stream:
    EXAMPLES = list(csv.DictReader(stream))


@pytest.mark.parametrize("example", EXAMPLES, ids=[row["id"] for row in EXAMPLES])
def test_specification_example(manager, example):
    def execute():
        for task_id, duration in json.loads(example["tasks_json"]):
            manager.add_task(task_id, task_id, duration)
        for task_id, prerequisite_id in json.loads(example["dependencies_json"]):
            manager.add_dependency(task_id, prerequisite_id)
        return [[s.task_id, s.start, s.finish] for s in manager.build_schedule()]

    if example["expected_error"]:
        with pytest.raises(ValueError) as error:
            execute()
        assert str(error.value) == example["expected_error"]
    else:
        assert execute() == json.loads(example["expected_schedule_json"])
