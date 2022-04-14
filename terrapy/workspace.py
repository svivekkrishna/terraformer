import json
import os
import shutil
import subprocess
import tempfile

from .mixins import TerraformRun
from .plan import TerraformPlan


class TerraformWorkspace(TerraformRun):
    def __init__(self, path=None) -> None:

        self.terraform_path = shutil.which("terraform")
        if not self.terraform_path:
            raise Exception("Terraform binary is missing from system.")

        version_data_raw = subprocess.run(
            ["terraform", "-version", "-json"], stdout=subprocess.PIPE
        ).stdout.decode("utf-8")

        version_data = json.loads(version_data_raw)
        self.version = version_data["terraform_version"]
        self.is_outdated = version_data["terraform_outdated"]
        self.platform = version_data["platform"]
        self.provider_selections = version_data["provider_selections"]

        self.cwd = path if path != None else os.getcwd()
        self.env = {}

    def init(self):
        return self._subprocess_run([self.terraform_path, "init"])

    def validate(self):
        return self._subprocess_run(["terraform", "validate", "-json"])

    def plan(self, error_function=None, output_function=None, output_path=None):

        save_plan = True
        if not output_path:
            save_plan = False
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "terraform.plan")

        command = [
            self.terraform_path,
            "plan",
            "-json",
            "-detailed-exitcode",
            "-input=false",
            f"-out={output_path}",
        ]

        results = self._subprocess_stream(
            command,
            cwd=self.cwd,
            error_function=error_function,
            output_function=output_function,
        )

        if results.returncode != 1:
            results.successful = True
            plan = TerraformPlan(cwd=self.cwd, plan_path=output_path)
        else:
            results.successful = False
            plan = None

        if not save_plan:
            shutil.rmtree(temp_dir)

        return results, plan

    def apply(
        self,
        error_function=None,
        output_function=None,
        auto_approve=False,
        plan_file=None,
    ):

        command = [self.terraform_path, "apply", "-json"]

        if plan_file:
            command.append(plan_file)
        if auto_approve:
            command.append("-auto-approve")

        return self._subprocess_stream(
            command,
            cwd=self.cwd,
            error_function=error_function,
            output_function=output_function,
        )

    def destroy(self):
        return self._subprocess_run([self.terraform_path, "destroy", "-json"])

    def output(self):
        return self._subprocess_run([self.terraform_path, "output", "-json"])

    def get(self, update=False):
        command = [self.terraform_path, "get"]
        if update:
            command.append("-update")
        return self._subprocess_run(command)
