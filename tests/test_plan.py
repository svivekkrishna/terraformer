from pathlib import Path

import pytest

from terraformer import plan as plan_module
from terraformer.plan import TerraformPlan

PLAN_FILE = Path(__file__).parent.absolute() / "terraform" / "plans" / "test.plan"


@pytest.fixture
def plan(workspace):
    results, plan = workspace.plan()
    return plan


def test_load(plan):
    assert plan.format_version.startswith("1.")
    assert plan.deletions == 0, "Nothing to delete."
    assert plan.modifications == 0, "Nothing to modify."
    assert plan.creations == 7, "Creating 7 resources."


def test_reload(plan):
    plan._parse_changes(
        [
            {
                "address": "1",
                "type": "test",
                "change": {
                    "actions": ["delete"],
                    "before": {"triggers": {"bundle_url": ""}},
                    "after": None,
                    "after_unknown": {"id": False, "triggers": {}},
                    "before_sensitive": False,
                    "after_sensitive": {"triggers": {}},
                },
            }
        ]
    )
    assert plan.format_version == "1.1"
    assert plan.deletions == 1, "Deleting 1 resources."
    assert plan.modifications == 0, "Nothing to modify."
    assert plan.creations == 7, "Creating 7 resources."


def test_plan_json():
    plan_from_json = TerraformPlan(cwd="", plan_path="tests/terraform/plans/sensitive_plan.json", is_json=True)
    assert plan_from_json.deletions == 0, "Nothing to delete."
    assert plan_from_json.creations == 1, "Creating 1 resource."
    assert (
        plan_from_json.changes["test"].after_sanitized.get("nested_property").get("sensitive_value")
        == plan_module.SANITIZE_REPLACE_WITH
    )
    assert (
        plan_from_json.changes["test"].after_sanitized.get("generated_value")
        == plan_module.KNOWN_AFTER_APPLY_REPLACE_WITH
    )
