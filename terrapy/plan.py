import json
import shutil
import subprocess

from .mixins import TerraformRun

MODIFICATION_ACTIONS = ["create", "update", "delete"]
DELETION_ACTIONS = ["delete"]


class TerraformPlan(TerraformRun):
    def __init__(self, cwd, plan_path) -> None:
        # confirm file exists

        self.cwd = cwd
        self.env = {}

        terraform_path = shutil.which("terraform")
        command = [terraform_path, "show", "-json", plan_path]
        results = self._subprocess_run(command)

        if results.returncode != 0:
            print(results.stdout)
            print(results.stderr)
            raise Exception()

        plan_details = json.loads(results.stdout)
        self.raw_plan = plan_details
        self.terraform_version = plan_details["terraform_version"]
        self.format_version = plan_details["format_version"]

        if self.format_version != "1.0":
            raise Exception()

        self.changes = {}
        for changeset in plan_details["resource_changes"]:
            self.changes[changeset["address"]] = TerraformChange(changeset)


class TerraformChange:
    def __init__(self, changeset) -> None:
        self.address = changeset["address"]
        self.type = changeset["type"]
        self.actions = changeset["change"]["actions"]

    def will_delete(self):
        return len(list(set(self.actions) & set(DELETION_ACTIONS))) > 0

    def will_modify(self):
        return len(list(set(self.actions) & set(MODIFICATION_ACTIONS))) > 0