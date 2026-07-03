# ComfyUI Manager And Custom Nodes

Use this reference when enabling Manager, installing missing nodes, repairing custom-node imports, or explaining custom-node safety.

Primary sources:
- https://docs.comfy.org/manager/install
- https://docs.comfy.org/manager/configuration
- https://docs.comfy.org/manager/legacy-ui
- https://docs.comfy.org/installation/install_custom_node
- https://docs.comfy.org/development/core-concepts/custom-nodes
- https://docs.comfy.org/troubleshooting/custom-node-issues

## Manager Enablement

Current docs describe Manager as built into current ComfyUI releases for most setups, but it may still need enabling.

Desktop:

- Manager is included and enabled by default in Comfy Desktop.
- Prefer Desktop UI controls for node operations and snapshots.

Manual install:

```bash
source venv/bin/activate
pip install -r manager_requirements.txt
python main.py --enable-manager
```

Windows portable:

```bat
python_embeded\python.exe -m pip install -r ComfyUI\manager_requirements.txt
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --enable-manager
```

Useful Manager flags:

```bash
python main.py --enable-manager
python main.py --enable-manager --enable-manager-legacy-ui
python main.py --enable-manager --disable-manager-ui
```

Use legacy git-clone Manager installs only for older setups that actually require them.

## Manager Configuration

Manager configuration depends on ComfyUI version and user directory. Newer Manager versions use a protected user path, while older versions used a Manager folder under the default user directory.

Important files and directories:

- `config.ini`: base Manager config.
- `channels.list`: custom channel lists.
- `pip_overrides.json`: package mapping overrides.
- `pip_blacklist.list`: blocked packages.
- `pip_auto_fix.list`: packages Manager may restore.
- `snapshots/`: saved Manager snapshots.
- `startup-scripts/`: Manager startup scripts.

When a Manager behavior seems blocked, check security level, network mode, risk level, and package allow/deny config before assuming the UI is broken.

## Custom Node Install Methods

Preferred order:

1. ComfyUI Manager for registry-listed nodes.
2. Git clone for unregistered nodes or pinned revisions.
3. ZIP download only when Git is unavailable.

All custom-node installs require:

- Node code under `ComfyUI/custom_nodes`.
- Python dependencies installed into the Python environment that runs ComfyUI.
- ComfyUI restart.
- Startup log check.
- `/object_info` check for expected classes.

Manager install flow:

1. Open Manager.
2. Choose Install Nodes or Install Missing Custom Nodes.
3. Search by node pack or missing class.
4. Review source and version.
5. Install.
6. Restart ComfyUI.
7. Check Manager and startup logs for import failures.

Manual git shape:

```bash
cd ComfyUI/custom_nodes
git clone <custom-node-repository-url>
cd <node-folder>
python -m pip install -r requirements.txt
```

That `python` must be the ComfyUI runtime Python.

ZIP install checks:

- Folder is not nested twice.
- Node folder contains Python files at the expected level.
- `requirements.txt` dependencies are installed in the active runtime.
- Restart happened after copy/install.

## Missing Nodes

Common causes:

- Required custom node pack is not installed.
- Installed pack failed to import.
- Dependencies were installed into the wrong Python.
- Node class was renamed, removed, or moved.
- Workflow came from a different ComfyUI/custom-node environment.
- Manager cannot map private/unregistered nodes.

Evidence loop:

1. Extract every workflow `class_type`.
2. Fetch `/object_info`.
3. Missing = workflow classes minus `/object_info` classes.
4. Check startup log for import failures from installed packs.
5. Use Manager's missing-node flow when available.
6. If no candidate appears, ask for the workflow source or original node pack.

Do not rename random classes in JSON. A class name is code, not copywriting.

## Dependency Repair

Wrong-environment symptoms:

- Node folder exists but node class is missing.
- `ModuleNotFoundError` in startup log.
- `pip show` says installed, but ComfyUI still fails.
- Manager says installed, but `/object_info` disagrees.

Repair:

1. Identify the Python executable that starts ComfyUI.
2. Run that exact Python with `-m pip`.
3. Install the node requirements.
4. Restart ComfyUI.
5. Read startup logs again.
6. Confirm `/object_info` contains expected classes.

Portable shape:

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\<node-folder>\requirements.txt
```

Manual shape:

```bash
source venv/bin/activate
python -m pip install -r custom_nodes/<node-folder>/requirements.txt
```

## Isolation And Rollback

When the UI or startup breaks after node changes:

1. Start with `--disable-all-custom-nodes`.
2. If core ComfyUI works, isolate nodes.
3. Use Manager disable/enable controls or `comfy node bisect`.
4. Without CLI support, move half the node folders out, restart, and repeat.
5. Restore from Manager/Desktop snapshot when available.
6. Pin or record known-good node commits after repair.

Keep models and workflows separate from disposable runtime folders. Nuking the runtime should not mean losing a model library.

## Custom Node Authoring Basics

For authoring or reviewing a simple custom node:

- Keep a node package under `custom_nodes/<package-name>`.
- Define Python classes with required ComfyUI node metadata.
- Expose mappings such as `NODE_CLASS_MAPPINGS` and display names.
- Keep dependencies in `requirements.txt`.
- Restart ComfyUI after code changes.
- Confirm the node appears in `/object_info`.
- Add minimal workflows that exercise the node.

For anything published, use the current registry and node documentation standards instead of copying an old random custom-node repo. Old examples often work right until they waste an afternoon.

## Security Checklist

Before installing:

- Prefer registry-listed or widely used nodes.
- Read the repository and requirements.
- Avoid obscure ZIPs and unknown install scripts.
- Be careful with nodes that download executables or modify shell profiles.
- Do not install untrusted nodes on public/shared GPU servers.
- Redact API keys from logs, screenshots, and workflow JSON.
- Snapshot before risky installs.

Manager improves ergonomics; it does not make arbitrary Python code harmless.
