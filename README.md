# terraformer

terraformer is a Python wrapper around the Terraform CLI.

## Usage

### Quick Start

terraformer usage centers around the Workspace object, which can be used to run the typical Terraform commands in that workspace. Just like with the CLI you have to initialize the workspace before you can run plans or applies.

```python
from terraformer import Workspace

workspace = Workspace(path="./")
workspace.init()

results, plan = workspace.plan()

if !results.successful:
  raise Exception(f"Terraform run failed without output: {results.stdout}")

if plan.deletions > 0:
  raise Exception("Deletions not expected from this plan")

results, apply_log = workspace.apply(plan_path=plan.plan_path, auto_approve=True)

if !results.successful:
  print("Terraform Apply was not successful.")

for resource_name, resource_data in apply_log.resources.items():
  print(f"${resource_name}: ${resource['message']}")

for output_name, output_data in apply_log.outputs.items():
  print(f"{output_name}:\n")
  print(yaml.dumps(output_data))
  print("\n\n\n")
```

The plan step can be skipped if you are auto approving.

```python
from terraformer import Workspace

workspace = Workspace(path="./")
workspace.init()
results, apply_log = workspace.apply(auto_approve=True)
```


### Installation

terraformer can be installed with pip.

```bash
pip install terraformer
```

In addition to terraformer you should have the Terraform binary installed on your system.
