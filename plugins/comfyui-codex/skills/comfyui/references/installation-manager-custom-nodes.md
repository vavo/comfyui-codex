# ComfyUI Installation, Manager, And Custom Nodes

Use this reference when the user asks how to install, update, enable, or diagnose ComfyUI itself, ComfyUI-Manager, custom nodes, or custom-node dependencies.

Primary sources:
- https://docs.comfy.org/installation/system_requirements
- https://docs.comfy.org/installation/desktop/overview
- https://docs.comfy.org/installation/desktop/windows
- https://docs.comfy.org/installation/desktop/macos
- https://docs.comfy.org/installation/desktop/linux
- https://docs.comfy.org/installation/comfyui_portable_windows
- https://docs.comfy.org/installation/manual_install
- https://docs.comfy.org/comfy-cli/getting-started
- https://docs.comfy.org/manager/install
- https://docs.comfy.org/manager/configuration
- https://docs.comfy.org/manager/legacy-ui
- https://docs.comfy.org/installation/install_custom_node
- https://docs.comfy.org/development/core-concepts/custom-nodes
- https://docs.comfy.org/troubleshooting/custom-node-issues
- https://github.com/Comfy-Org/ComfyUI-Manager

## Contents

- [Decision Tree](#decision-tree)
- [Install Evidence To Collect](#install-evidence-to-collect)
- [Install Paths](#install-paths)
- [Comfy Desktop](#comfy-desktop)
- [Windows Portable](#windows-portable)
- [Manual Install](#manual-install)
- [Comfy CLI](#comfy-cli)
- [ComfyUI-Manager](#comfyui-manager)
- [Custom Nodes](#custom-nodes)
- [Dependency Handling](#dependency-handling)
- [Security And Trust](#security-and-trust)
- [Troubleshooting Installation](#troubleshooting-installation)
- [Troubleshooting Manager And Custom Nodes](#troubleshooting-manager-and-custom-nodes)
- [What To Avoid](#what-to-avoid)

## Decision Tree

Choose the install path by user and runtime:

- New Windows or Apple Silicon macOS user: prefer Comfy Desktop unless they need bleeding-edge commits or a custom server environment.
- Windows user who wants a self-contained folder: use Windows Portable.
- Linux user: use manual install or Comfy CLI; Comfy Desktop Linux prebuilds may not be available depending on the current release.
- Advanced local/server user: use manual install with a virtual environment.
- Automation or repeatable setup user: consider Comfy CLI, then verify what it installed.
- Runpod, notebook, Docker, or remote GPU user: identify the image/template first; do not assume local Desktop or portable paths apply.

Be explicit when an instruction is platform-specific. Most support mistakes come from applying Windows portable commands to a venv install, or installing dependencies into system Python while ComfyUI runs from a separate Python. Impressive only in the sense that it wastes time consistently.

## Install Evidence To Collect

Before giving install or repair steps, ask for or inspect:

- Install type: Desktop, Windows Portable, manual git clone, Comfy CLI, Docker, notebook, Runpod, or Cloud.
- OS and CPU architecture.
- GPU type and VRAM: NVIDIA CUDA, AMD ROCm, Intel XPU, Apple Silicon Metal, CPU-only, or other accelerator.
- Python version and path that actually starts ComfyUI.
- ComfyUI folder path, if local.
- Startup command or launcher file.
- Full terminal startup log.
- Whether ComfyUI opens in the browser.
- Whether `/system_stats` and `/object_info` respond.
- Whether Manager is enabled.
- Whether the failing workflow uses custom nodes.
- Exact missing node classes or missing model filenames.

If the user only says "install ComfyUI", ask for OS, GPU, and install preference first. If they want the shortest path, recommend Desktop where supported.

## Install Paths

Common installation choices:

- Comfy Desktop: launcher and multi-install manager. It handles the ComfyUI installation, Python environment, dependencies, updates, snapshots, and multiple isolated instances.
- Windows Portable: extracted folder with embedded Python. Good for self-contained Windows use.
- Manual install: git clone plus a Python virtual environment. Good for Linux, servers, development, and users who need exact dependency control.
- Comfy CLI: command-line tool for installing and managing ComfyUI, models, and custom nodes.
- Cloud or hosted runtimes: use provider-specific setup first, then debug with server routes and logs.

Do not claim one path is universal. ComfyUI's install surface is now several products wearing one coat.

## Comfy Desktop

Use for users who want the least manual dependency work.

Key points:

- Desktop manages ComfyUI instances rather than requiring a separate ComfyUI install.
- It supports Windows and Apple Silicon macOS in the official desktop docs; check current Linux support before recommending a prebuilt Linux desktop app.
- Each instance has its own environment, custom nodes, models, workflows, and settings.
- Desktop can manage updates and snapshots.
- Desktop has shared model/input/output paths in settings.

When helping a Desktop user:

1. Confirm they installed the app for the correct OS.
2. Open Desktop and create or select an installation.
3. Launch the instance.
4. Confirm the local UI opens.
5. If debugging, collect Desktop logs and the instance path.
6. For custom-node isolation, use the Desktop setting to disable custom nodes when available, or run the server manually with `--disable-all-custom-nodes`.

Useful prompts:

```text
Use $comfyui to help install Comfy Desktop on Windows. I have an NVIDIA GPU and want the easiest setup.
```

```text
Use $comfyui to debug my Comfy Desktop instance. It opens but the workflow reports missing custom nodes.
```

## Windows Portable

Use for Windows users who want a portable folder with embedded Python.

Key points:

- The portable build includes `python_embeded`.
- Users typically start it with `run_nvidia_gpu.bat` or `run_cpu.bat`.
- Dependency commands must use the embedded Python, not system Python.
- Portable custom nodes live under `ComfyUI/custom_nodes` inside the portable folder.
- Portable model folders live under `ComfyUI/models` unless extra paths are configured.

Common checks:

```bat
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --disable-all-custom-nodes
```

When installing custom-node dependencies manually:

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\<node-folder>\requirements.txt
```

Replace `<node-folder>` with the actual custom node folder. Do not use `pip` from another Python and then wonder why ComfyUI cannot import the package.

## Manual Install

Use for Linux, servers, source checkouts, and users who need current commits or dependency control.

Core flow:

1. Install system prerequisites: Git, Python, and platform GPU prerequisites.
2. Create a virtual environment or Conda environment.
3. Clone the ComfyUI repository.
4. Activate the environment.
5. Install GPU/PyTorch dependencies appropriate for the hardware.
6. Install ComfyUI requirements.
7. Start ComfyUI.

Example shape:

```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
cd ComfyUI
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py --disable-auto-launch
```

Windows activation differs:

```bat
venv\Scripts\activate
```

GPU notes:

- NVIDIA: match PyTorch CUDA wheels to the current ComfyUI docs and driver support.
- AMD Linux: use ROCm guidance from current docs.
- Apple Silicon: use Metal-supported PyTorch and macOS guidance.
- CPU-only works but is slow; present it as fallback, not a happy path.

Never guess the right PyTorch command for a user's GPU if current docs or logs are available. PyTorch/CUDA advice ages like unrefrigerated soup.

## Comfy CLI

Use when the user prefers terminal setup or wants repeatable install/manage commands.

Typical shape:

```bash
python -m venv venv
source venv/bin/activate
pip install comfy-cli
comfy install
```

Windows activation:

```bat
venv\Scripts\activate
```

Useful CLI lanes from the official docs:

```bash
comfy node install <NODE_NAME>
comfy model download --url <url> --relative-path models/checkpoints
```

When using Comfy CLI, still verify:

- Where ComfyUI was installed.
- Which Python environment it uses.
- Whether Manager/cm-cli is involved for node operations.
- Whether models landed in folders visible to the target ComfyUI instance.

## ComfyUI-Manager

Use Manager for most custom-node work.

Current docs describe Manager as built into current ComfyUI releases for most setups, but it may need to be enabled depending on install type.

For manual installs:

```bash
source venv/bin/activate
pip install -r manager_requirements.txt
python main.py --enable-manager
```

Windows activation:

```bat
venv\Scripts\activate
```

For Windows Portable, use the embedded Python and start with Manager enabled:

```bat
python_embeded\python.exe -m pip install -r ComfyUI\manager_requirements.txt
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --enable-manager
```

Manager flags:

```bash
python main.py --enable-manager
python main.py --enable-manager --enable-manager-legacy-ui
python main.py --enable-manager --disable-manager-ui
```

Legacy git-clone Manager install still exists for older setups:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Comfy-Org/ComfyUI-Manager comfyui-manager
cd comfyui-manager
pip install -r requirements.txt
```

Prefer current built-in Manager enablement when it applies. Use legacy clone instructions only when the user's install actually needs them.

Manager capabilities:

- Install custom nodes from the registry.
- Install missing custom nodes reported by imported workflows.
- Update installed custom nodes.
- Disable, enable, uninstall, or repair custom nodes.
- Install dependencies during node installation.
- Use snapshots to preserve or restore custom-node install state.
- Use `cm-cli` for headless Manager operations.

Manager caveats:

- Not every node is in the registry.
- Nightly/development versions may be unstable or security-restricted.
- Uninstalling a node may not remove Python dependencies.
- Missing-node lookup can fail when a node is private, renamed, unregistered, or deleted.
- Headless installs may need CLI or manual git install.
- Manager's direct Git URL and pip install behavior can be restricted by security configuration.

## Custom Nodes

Custom nodes extend ComfyUI with third-party node classes or UI features. Treat them as executable code, because that is exactly what they are.

Install methods:

1. ComfyUI-Manager: preferred for registered nodes.
2. Git clone: useful for unregistered nodes or specific revisions.
3. ZIP download: fallback when Git is unavailable; loses normal version-control behavior.

Manager install flow:

1. Open Manager.
2. Choose Install Nodes or Install Missing Custom Nodes.
3. Search or review missing-node candidates.
4. Prefer stable versions over nightly unless the workflow requires nightly.
5. Install.
6. Wait for dependency installation.
7. Restart ComfyUI.
8. Check Manager or startup logs for `import failed`.

Manual git flow:

```bash
cd ComfyUI/custom_nodes
git clone <custom-node-repository-url>
cd <node-folder>
pip install -r requirements.txt
```

That last `pip` must be from the Python environment that runs ComfyUI.

Manual ZIP flow:

1. Download ZIP from the node repository.
2. Extract it.
3. Copy the extracted node folder into `ComfyUI/custom_nodes`.
4. Avoid nested folders such as `custom_nodes/SomeNode-main/SomeNode-main`.
5. Install dependencies in the correct ComfyUI Python environment.
6. Restart ComfyUI.

After any custom-node install:

- Restart ComfyUI.
- Read startup logs.
- Confirm the node package is recognized.
- Confirm `/object_info` includes the expected node classes.
- Reopen or requeue the workflow.

## Dependency Handling

Dependency mistakes are the most common custom-node support problem.

Rules:

- Install node dependencies into the Python environment that starts ComfyUI.
- For Desktop, use Desktop's terminal or instance environment when available.
- For Windows Portable, use `python_embeded\python.exe`.
- For manual installs, activate the venv or Conda env first.
- For Docker/notebook/Runpod, install into the container or notebook environment that runs ComfyUI, not the local laptop.
- Restart ComfyUI after installing dependencies.

Symptoms of wrong-environment installs:

- Node folder exists but node classes are missing.
- Startup log shows import errors.
- `ModuleNotFoundError` for a dependency that `pip` claims is installed elsewhere.
- Manager reports installed but workflow still has unknown node classes.
- `/object_info` does not include expected classes.

Dependency diagnosis:

1. Locate the Python executable used by ComfyUI.
2. Run `python -m pip show <package>` from that exact Python.
3. Compare startup log import errors with `requirements.txt`.
4. Reinstall using that exact Python.
5. Restart and inspect logs again.

## Security And Trust

Before installing custom nodes:

- Prefer registry-listed or widely used nodes from trusted authors.
- Read the repository and requirements.
- Avoid obscure ZIPs from unknown sources.
- Be suspicious of install scripts that download executables, alter shell profiles, or require broad credentials.
- Keep API keys out of screenshots, logs, and workflow JSON.
- Do not install untrusted nodes on public or shared GPU servers.
- On remote servers, be careful with Manager Git URL and pip install permissions.

For production-ish installs:

- Pin known-good versions.
- Save a snapshot or record commit hashes.
- Keep a minimal reproducible workflow for testing.
- Add one node pack at a time.
- Restart and test after each install.

## Troubleshooting Installation

If ComfyUI will not start:

1. Identify install type.
2. Capture the exact startup command and full log.
3. Try a minimal startup:

```bash
python main.py --disable-auto-launch
```

4. If custom nodes may be involved:

```bash
python main.py --disable-all-custom-nodes
```

5. Check Python version and active environment.
6. Check GPU/PyTorch compatibility.
7. Check disk space.
8. Check whether the browser can open the local UI.
9. If the server starts, probe `/system_stats` and `/object_info`.

Portable equivalent:

```bat
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --disable-all-custom-nodes
```

If disabling custom nodes makes startup work, stop reinstalling ComfyUI and isolate the custom-node set.

## Troubleshooting Manager And Custom Nodes

If Manager is missing:

- Confirm Manager is enabled with `--enable-manager` when required.
- Confirm Manager dependencies were installed in the correct environment.
- Check whether the user is on Desktop, portable, or manual install.
- For older installs, check whether legacy Manager is installed under the expected custom node folder.
- Restart ComfyUI and refresh the browser.

If a custom node is missing:

1. Extract missing `class_type` names from the workflow or error.
2. Compare them with `/object_info`.
3. Use Manager's Install Missing Custom Nodes when available.
4. If Manager cannot find it, search the workflow source or original node repository.
5. Install only the required node pack.
6. Restart and check startup logs.
7. Recheck `/object_info`.

If a node is installed but import fails:

- Read the startup log, not just the UI.
- Check the node folder is not nested incorrectly.
- Check dependency packages in the active ComfyUI Python.
- Update the custom node only after saving current state or snapshot.
- If an update caused the issue, roll back the node or ComfyUI to a known-good revision.

If multiple custom nodes may be broken:

- Use Manager disable/enable controls when available.
- Use `comfy-cli node bisect` when available.
- Otherwise move half the custom-node folders out of `custom_nodes`, restart, test, and repeat.
- Back up before moving folders.

If dependency conflicts accumulate:

- Avoid blind `pip install --upgrade`.
- Prefer a snapshot, clean environment, or fresh install plus known node list.
- Reinstall nodes one at a time.
- Keep model files and workflows separate from the disposable runtime when possible.

## What To Avoid

- Do not tell users to reinstall ComfyUI as the first answer to a custom-node import error.
- Do not install dependencies into system Python unless system Python is truly what runs ComfyUI.
- Do not mix Desktop, portable, and manual-install paths.
- Do not assume ComfyUI-Manager is a normal old custom node on every current install.
- Do not claim a node is installed unless `/object_info`, Manager status, or startup logs prove it.
- Do not use raw GitHub ZIPs as the default path when Manager can install the node.
- Do not expose public ComfyUI servers with permissive Manager install surfaces.
