---
name: tasks
description: Guides the creation and management of Python-native task runner scripts using `invoke` and `uv`. Uses PEP 723 inline dependencies to replace Makefiles without requiring external virtual environments. Use when the user wants to automate local jobs, replace a Makefile, set up project scripts, or orchestrate CLI execution in a Python-centric ecosystem.
---

## tasks
This skill covers how to write, structure, and execute `tasks.py` scripts using Python's `invoke` library alongside `uv`. Makefiles have quirks like tab requirements, strange conditional syntaxes, and poor cross-platform support. In Python-heavy projects, using `invoke` with `uv` and PEP 723 inline dependencies provides a cleaner, self-contained, and more robust alternative.

The skill is organized into several key topics:
- **Core Principles**: The fundamental rules for zero-setup execution and explicit CLI usage.
- **File Structure**: The standard template every `tasks.py` should follow.
- **Task Formatting**: How to format task code so it is clear, showing exactly what command runs with what variables.
- **Best Practices**: Rules for command execution, handling output, environments, and path resolving.

## core-principles
1. **Zero External Setup**: The script must bring its own dependencies. By using `uv` and PEP 723 inline dependency declarations (`# /// script`), the script is 100% self-contained. No user should ever have to manually run `pip install invoke`.
2. **Explicit CLI Usage**: The module docstring must clearly show how to run the tasks using `uv run tasks.py <task>`.
3. **Environment Defaults**: Arguments map seamlessly to `os.getenv` defaults for CI/CD or local overrides.
4. **Context Propagation**: Always pass the `c` (Context) object as the first argument to tasks and execute commands via `c.run()`.
5. **Clear and Easy to Understand Code**: The code must be highly readable. A user opening the script must instantly see what variables exist, the exact command being constructed, and how it is run.

## task-formatting
To ensure the code is clear and easy to understand, format each task explicitly. Separate the command construction from its execution so that anyone reading the code can immediately see the command, how it runs, and what variables are used.

**Format Guidelines:**
1. **Clear Arguments**: Define variables logically in the function signature with defaults.
2. **Command Construction**: Assign the formatted command string to a `cmd` variable. This makes it instantly readable.
3. **Logging**: Print the command (or an informative message) before running so the user knows what is happening.
4. **Execution**: Pass the explicit `cmd` variable to `c.run()`.

**Example:**
```python
@task
def build_image(c, registry="my-registry", tag="latest"):
    """Build the docker container."""
    # 1. Variables are clearly defined in the signature
    
    # 2. Command is explicitly constructed
    cmd = f"docker build -t {registry}/my-app:{tag} ."
    
    # 3. Log the action
    print(f"Running: {cmd}")
    
    # 4. Execution
    with c.cd(ROOT_DIR):
        c.run(cmd, pty=True)
```

## file-structure
Every `tasks.py` script must follow this exact structure:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "invoke",
# ]
# ///
"""
Invoke tasks for local management and deployment.

Usage:
    uv run tasks.py --list
    uv run tasks.py build
    uv run tasks.py deploy --region us-east-1
"""

import os
from pathlib import Path
from invoke import task

# --- Configuration & Defaults ---
PROJECT_ID = os.getenv("PROJECT_ID", "default-project")
REGION = os.getenv("REGION", "us-central1")
ROOT_DIR = Path(__file__).resolve().parent

# --- Tasks ---
@task
def list_resources(c, project_id=PROJECT_ID):
    """List resources in the default or specified project."""
    cmd = f"gcloud compute instances list --project={project_id}"
    print(f"Running: {cmd}")
    c.run(cmd)

@task
def build(c, tag="v1"):
    """Build the docker container."""
    cmd = f"docker build -t my-app:{tag} ."
    print(f"Running: {cmd}")
    with c.cd(ROOT_DIR):
        c.run(cmd, pty=True)

@task(pre=[build])
def deploy(c, region=REGION):
    """Deploy the locally built resource (depends on build automatically)."""
    cmd = f"echo Deploying to {region}..."
    print(f"Running: {cmd}")
    c.run(cmd, pty=True)

# --- Entry point ---
if __name__ == "__main__":
    from invoke import Program
    Program().run()
```

## best-practices
### Task Definitions
- Decorate target functions with `@task`. 
- The first argument must always be `c` or `ctx`.
- Use proper docstrings. The first line of the docstring is displayed in `uv run tasks.py --list`.
- Use `snake_case` for task functions. Invoke automatically translates them to `kebab-case` CLI commands.

### Command Execution (`c.run`)
- Prefer `c.run(cmd, pty=True)` to stream standard output smoothly back to the terminal, preserving colors and interactive prompts.
- Set `warn=True` if a failing command is acceptable and shouldn't crash the standard execution flow.
- Set `hide=True` if you're capturing output but don't want to print it to the user.

### Handling Output
To parse command output silently:
```python
@task
def get_user(c):
    result = c.run("gcloud auth print-access-token", hide=True)
    token = result.stdout.strip()
```

### Environments & Arguments
Default variables mapped via `os.getenv` allows functionality identical to standard `Makefile` variable overrides (`PROJECT_ID=foo make build` -> `PROJECT_ID=foo uv run tasks.py build`).

### Path Resolving
NEVER use string concatenation or assume the Current Working Directory (CWD) is correctly aligned to the script location. Always resolve root paths relative to the script using `pathlib.Path` as shown in the File Structure topic.

## tasks-scripts
Utility scripts for tasks are usually embedded directly within the project's own repository (e.g., in `scripts/` directories) and called by the `tasks.py` script via `c.run("scripts/my-script.sh")`. The `tasks.py` acts as the primary orchestrator that triggers these target-specific shell or Python scripts.

## tasks-reference
There are no external reference files for this skill. The primary documentation for execution resides directly in the `tasks.py` module docstring of the project. The skill file is fully self-contained.

## examples
Here is an integrated example of replacing a standard Docker build/push Makefile flow with a `tasks.py` script:

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "invoke",
# ]
# ///
"""
Deployment tasks.

Usage:
    uv run tasks.py --list
    uv run tasks.py build --tag v2
    REGION=us-east-1 uv run tasks.py push
"""

import os
from pathlib import Path
from invoke import task

REGION = os.getenv("REGION", "us-central1")
PROJECT = os.getenv("PROJECT_ID", "my-project")
ROOT_DIR = Path(__file__).resolve().parent

@task
def list_images(c, region=REGION, project=PROJECT):
    """List Docker images in the registry."""
    cmd = f"gcloud artifacts docker images list {region}-docker.pkg.dev/{project}/repo"
    print(f"Running: {cmd}")
    c.run(cmd)

@task
def build(c, tag="v1"):
    """Build the docker container."""
    cmd = f"docker build -t my-app:{tag} ."
    print(f"Running: {cmd}")
    with c.cd(ROOT_DIR):
        c.run(cmd, pty=True)

@task(pre=[build])
def push(c, tag="v1", region=REGION, project=PROJECT):
    """Push the container to Artifact Registry."""
    image_uri = f"{region}-docker.pkg.dev/{project}/repo/my-app:{tag}"
    
    cmd_tag = f"docker tag my-app:{tag} {image_uri}"
    print(f"Running: {cmd_tag}")
    c.run(cmd_tag)
    
    cmd_push = f"docker push {image_uri}"
    print(f"Running: {cmd_push}")
    c.run(cmd_push, pty=True)

if __name__ == "__main__":
    from invoke import Program
    Program().run()
```
