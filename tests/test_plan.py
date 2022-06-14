from pathlib import Path

import pytest

PLAN_FILE = Path(__file__).parent.absolute() / "terraform" / "plans" / "test.plan"


@pytest.fixture
def plan(workspace):
    results, plan = workspace.plan()
    return plan


def test_load(plan):
    assert plan.format_version == "1.1"
    assert plan.deletions == 0, "Nothing to delete."
    assert plan.modifications == 0, "Nothing to modify."
    assert plan.creations == 7, "Creating 7 resources."


def test_reload(plan):
    plan._parse_changes([{"address": "1", "type": "test", "change": {"actions": ["delete"]}}])
    assert plan.format_version == "1.1"
    assert plan.deletions == 1, "Deleting 1 resources."
    assert plan.modifications == 0, "Nothing to modify."
    assert plan.creations == 7, "Creating 7 resources."
