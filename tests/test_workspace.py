import shutil
import tempfile
from os.path import exists
from pathlib import Path

import pytest

from terrapy import TerraformWorkspace

WORKSPACE_TEMPLATE = Path(__file__).parent.absolute() / "workspace"

# Speed up `init` functions by caching providers locally.
# This will be deleted between runs.
PROVIDER_CACHE = tempfile.mkdtemp()


@pytest.fixture
def workspace_environment(tmpdir):
    shutil.copytree(WORKSPACE_TEMPLATE, tmpdir, dirs_exist_ok=True)
    return tmpdir


@pytest.fixture
def workspace(workspace_environment):
    workspace = TerraformWorkspace(workspace_environment)
    workspace.env["TF_PLUGIN_CACHE_DIR"] = PROVIDER_CACHE
    workspace.init()
    return workspace


def test_version():
    workspace = TerraformWorkspace()
    assert isinstance(workspace.version, str), "Version should be a string."


def test_init(workspace_environment):
    workspace = TerraformWorkspace(workspace_environment)
    workspace.env["TF_PLUGIN_CACHE_DIR"] = PROVIDER_CACHE
    workspace.init()
    assert (Path(workspace_environment) / ".terraform").is_dir(), "Workspace has initialized."


def test_plan(workspace):
    results = workspace.plan(error_function=print, output_function=print)
    assert results.successful, "Terraform plan succeeded."


def test_apply_interaction(workspace):
    results = workspace.apply(error_function=print, output_function=print)
    assert results.returncode == 1, "Terraform apply failed when interaction is required."


def test_apply_auto_approve(workspace):
    results = workspace.apply(auto_approve=True, error_function=print, output_function=print)
    assert results.returncode == 0, "Terraform apply succeeded."
