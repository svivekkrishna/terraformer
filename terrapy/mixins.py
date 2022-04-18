import subprocess
from logging import getLogger

from .exceptions import TerraformRuntimeError

logger = getLogger(__name__)


class ProcessResults:
    def __init__(self, returncode, stdout, stderr) -> None:
        self.returncode = returncode
        self.successful = returncode == 0
        self.stdout = stdout
        self.stderr = stderr


class TerraformRun:
    def _subprocess_run(self, args, raise_exception_on_failure=False, **kwargs):
        default_kwargs = {
            "cwd": self.cwd,
            "capture_output": True,
            "encoding": "utf-8",
            "timeout": None,
            "env": self.env if len(self.env) > 0 else None,
        }
        pass_kwargs = {**default_kwargs, **kwargs}
        results = subprocess.run(args, **pass_kwargs)

        ret_results = ProcessResults(results.returncode, results.stdout, results.stderr)

        if raise_exception_on_failure and not ret_results.successful:
            raise TerraformRuntimeError(f"An error occurred while running command '{' '.join(args)}'", ret_results)

        return ret_results

    def _subprocess_stream(self, command, error_function=None, output_function=None, **kwargs):
        logger.info(f"Running command '{command}'")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
        stdout = ""
        stderr = ""
        while True:
            # Check for stdout changes.
            output = process.stdout.readline().decode("utf-8")
            if output != "":
                stdout += output
                logger.info(stdout)
                if output_function:
                    output_function(output)

            # Check for stderr changes.
            error = process.stderr.readline().decode("utf-8")
            if error != "":
                stderr += error
                logger.warning(stderr)
                if error_function:
                    error_function(output)

            # Process is closed and we've read all of the outputs.
            if process.poll() is not None:
                if output == "" and error == "":
                    break

        # Match the return object of subprocess.run.
        return ProcessResults(returncode=process.poll(), stdout=stdout, stderr=stderr)
