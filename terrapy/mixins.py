import subprocess


class ProcessResults:
    def __init__(self, returncode, stdout, stderr) -> None:
        self.returncode = returncode
        self.successful = returncode == 0
        self.stdout = stdout
        self.stderr = stderr


class TerraformRun:
    def _subprocess_run(self, args, **kwargs):
        default_kwargs = {
            "cwd": self.cwd,
            "capture_output": True,
            "encoding": "utf-8",
            "timeout": None,
            "env": self.env if len(self.env) > 0 else None,
        }
        pass_kwargs = {**default_kwargs, **kwargs}
        return subprocess.run(args, **pass_kwargs)

    def _subprocess_stream(self, command, error_function=None, output_function=None, **kwargs):
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
