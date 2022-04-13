import json
import os
import shutil
import subprocess


class ProcessResults:
    def __init__(self, returncode, stdout, stderr) -> None:
        self.returncode = returncode
        self.successful = returncode == 0
        self.stdout = stdout
        self.stderr = stderr


def subprocess_stream(command, error_function=None, output_function=None, **kwargs):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    stdout = ""
    stderr = ""
    while True:
        # Check for stdout changes.
        output = process.stdout.readline().decode("utf-8")
        if output != "":
            stdout += output
            if output_function:
                output_function(output)

        # Check for stderr changes.
        error = process.stderr.readline().decode("utf-8")
        if error != "":
            stderr += error
            if error_function:
                error_function(output)

        # Process is closed and we've read all of the outputs.
        if process.poll() is not None:
            if output == "" and error == "":
                break

    # Match the return object of subprocess.run.
    return ProcessResults(returncode=process.poll(), stdout=stdout, stderr=stderr)


class TerraformWorkspace:
    def __init__(self, path=None) -> None:

        self.terraform_path = shutil.which("terraform")
        if not self.terraform_path:
            raise Exception("Terraform binary is missing from system.")

        version_data_raw = subprocess.run(["terraform", "-version", "-json"], stdout=subprocess.PIPE).stdout.decode(
            "utf-8"
        )

        version_data = json.loads(version_data_raw)
        self.version = version_data["terraform_version"]
        self.is_outdated = version_data["terraform_outdated"]
        self.platform = version_data["platform"]
        self.provider_selections = version_data["provider_selections"]

        self.cwd = path if path != None else os.getcwd()
        self.env = {}

    def __subprocess_run_wrapper(self, args, **kwargs):
        default_kwargs = {
            "cwd": self.cwd,
            "capture_output": True,
            "encoding": "utf-8",
            "timeout": None,
            "env": self.env if len(self.env) > 0 else None,
        }
        pass_kwargs = {**default_kwargs, **kwargs}
        return subprocess.run(args, **pass_kwargs)

    def init(self):
        return self.__subprocess_run_wrapper([self.terraform_path, "init"])

    def validate(self):
        return self.__subprocess_run_wrapper(["terraform", "validate", "-json"])

    def plan(self, error_function=None, output_function=None, output_path=None):
        command = [
            self.terraform_path,
            "plan",
            "-json",
            "-detailed-exitcode",
            "-input=false",
        ]

        if output_path:
            command.append(f"-out={output_path}")

        results = subprocess_stream(
            command,
            cwd=self.cwd,
            error_function=error_function,
            output_function=output_function,
        )
        results.successful = results.returncode != 1
        return results

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

        return subprocess_stream(
            command,
            cwd=self.cwd,
            error_function=error_function,
            output_function=output_function,
        )

    def destroy(self):
        return self.__subprocess_run_wrapper([self.terraform_path, "destroy", "-json"])

    def output(self):
        return self.__subprocess_run_wrapper([self.terraform_path, "output", "-json"])

    def get(self, update=False):
        command = [self.terraform_path, "get"]
        if update:
            command.append("-update")
        return self.__subprocess_run_wrapper(command)
