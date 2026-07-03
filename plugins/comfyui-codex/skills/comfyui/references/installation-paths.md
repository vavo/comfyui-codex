# ComfyUI Installation Paths

Use this reference when choosing, installing, updating, or repairing a ComfyUI runtime.

Primary sources:
- https://docs.comfy.org/installation/system_requirements
- https://docs.comfy.org/installation/desktop/overview
- https://docs.comfy.org/installation/comfyui_portable_windows
- https://docs.comfy.org/installation/manual_install
- https://docs.comfy.org/comfy-cli/getting-started
- https://docs.comfy.org/development/comfyui-server/startup-flags

## Decision Matrix

| User/runtime | Prefer | Why | Verify |
| --- | --- | --- | --- |
| New Windows user | Comfy Desktop or Windows Portable | Least setup friction; portable is self-contained | UI opens; `/system_stats` responds |
| New Apple Silicon macOS user | Comfy Desktop | Desktop handles install/runtime details | UI opens; Metal device appears in stats |
| Linux desktop/server | Manual install or Comfy CLI | Better source/runtime control | venv active; `python main.py` starts |
| Remote GPU, notebook, Docker, Runpod | Provider image first | Paths and Python env are provider-specific | server URL, logs, mounted storage |
| Automation/agent workflow | Comfy CLI or manual install | Repeatable commands and predictable paths | command outputs plus API probes |
| Managed execution | Comfy Cloud | No local GPU/runtime management | API key, Cloud workflow behavior |

If the user wants the easiest local path, recommend Desktop where supported. If they need current commits, custom patches, headless servers, or exact dependency control, use manual install or Comfy CLI.

## Evidence Before Commands

Collect or inspect:

- OS and CPU architecture.
- GPU and VRAM.
- Install type: Desktop, portable, manual, CLI, Docker, notebook, hosted, or Cloud.
- Python executable that actually starts ComfyUI.
- Startup command or launcher file.
- Full startup log.
- Whether the browser UI opens.
- Whether `GET /system_stats` and `GET /object_info` respond.
- Whether custom nodes are enabled.
- Disk and mounted-volume space for hosted runtimes.

Do not mix commands across install styles. Portable Python commands do not fix a venv install, and system `pip` does not fix an embedded Python install.

## Comfy Desktop

Use for users who want the least manual setup.

Key points:

- Desktop manages ComfyUI instances, updates, snapshots, environments, custom nodes, models, workflows, and settings.
- Official docs describe Desktop support for Windows and Apple Silicon macOS; check current docs before promising another platform.
- Desktop instances can have separate paths and environments.
- Desktop users should usually use Desktop's controls for install/update/snapshot operations before falling back to manual file surgery.

Repair loop:

1. Identify the selected Desktop instance.
2. Capture Desktop logs and the ComfyUI startup log.
3. Confirm the UI launches.
4. Probe the local server if exposed.
5. Disable custom nodes when startup or UI behavior is broken.
6. Restore or roll back from snapshot when a recent node/update caused the failure.

## Windows Portable

Use for Windows users who want a self-contained folder.

Key points:

- Portable builds use embedded Python under `python_embeded`.
- Start scripts usually wrap `ComfyUI/main.py`.
- Model folders and custom nodes live inside the portable tree unless extra paths are configured.
- Dependency installs must use the embedded Python.

Common checks:

```bat
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build
python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build --disable-all-custom-nodes
```

Dependency repair shape:

```bat
python_embeded\python.exe -m pip install -r ComfyUI\custom_nodes\<node-folder>\requirements.txt
```

## Manual Install

Use for Linux, servers, source checkouts, exact dependency control, and current commits.

Core shape:

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

Manual install repair loop:

1. Activate the environment that starts ComfyUI.
2. Verify Python and `pip` point to that environment.
3. Verify PyTorch matches GPU/driver requirements from current docs.
4. Install or reinstall ComfyUI requirements.
5. Start with `python main.py --disable-auto-launch`.
6. If custom nodes may be involved, retry with `--disable-all-custom-nodes`.
7. Probe `/system_stats` and `/object_info`.

## Comfy CLI

Use when the user wants repeatable terminal setup and management.

Typical shape:

```bash
python -m venv venv
source venv/bin/activate
pip install comfy-cli
comfy install
```

Useful lanes:

```bash
comfy launch
comfy node install <node-name>
comfy model download --url <url> --relative-path models/checkpoints
comfy node bisect start
```

After CLI work, still verify where ComfyUI was installed and which Python environment it uses. The CLI makes setup cleaner; it does not remove the need to check evidence.

## Hosted, Notebook, Docker, And Runpod

Treat hosted runtimes as separate deployments:

- Identify image/template, container path, mounted storage, exposed port, and proxy URL.
- Check both local disk and attached volume usage.
- Install dependencies inside the container/notebook environment that starts ComfyUI.
- Prefer provider logs plus ComfyUI logs over local assumptions.
- For remote API use, verify browser URL and API URL separately; notebook proxies can rewrite paths.

Common hosted failure pattern: model download fails because mounted storage is full, while local container disk still looks fine. Check the actual target volume.

## Startup Flags Worth Remembering

Stable flags to use during triage:

```bash
python main.py --disable-auto-launch
python main.py --listen 0.0.0.0 --port 8188
python main.py --disable-all-custom-nodes
python main.py --preview-method none
python main.py --lowvram
python main.py --cpu
```

Use `--listen 0.0.0.0` only when network exposure is intentional and protected. A public ComfyUI server with install-capable surfaces is not a cute productivity hack.

## First-Run Verification

After installation:

1. Browser UI opens.
2. `GET /system_stats` returns Python/device facts.
3. `GET /object_info` returns node definitions.
4. `GET /models` returns model folder categories.
5. Basic workflow queues and writes output.
6. Startup log has no custom-node import failures.

If any step fails, diagnose that boundary before adding custom nodes or downloading more models.
