from pathlib import Path

import pytest

from terrapy import TerraformWorkspace
from terrapy.plan import TerraformPlan

from .fixtures import PROVIDER_CACHE, workspace, workspace_environment


def test_version():
    workspace = TerraformWorkspace()
    assert isinstance(workspace.version, str), "Version should be a string."


def test_init(workspace_environment):
    workspace = TerraformWorkspace(workspace_environment)
    workspace.env["TF_PLUGIN_CACHE_DIR"] = PROVIDER_CACHE
    workspace.init()
    assert (Path(workspace_environment) / ".terraform").is_dir(), "Workspace has initialized."


def test_plan(workspace):
    results, plan = workspace.plan(error_function=print, output_function=print)
    assert results.successful, "Terraform plan succeeded."
    assert isinstance(plan, TerraformPlan), "Terraform plan returned on successfull plan."


def test_apply_interaction(workspace):
    results = workspace.apply(error_function=print, output_function=print)
    assert results.returncode == 1, "Terraform apply failed when interaction is required."


def test_apply_auto_approve(workspace):
    results = workspace.apply(auto_approve=True, error_function=print, output_function=print)
    assert results.returncode == 0, "Terraform apply succeeded."
