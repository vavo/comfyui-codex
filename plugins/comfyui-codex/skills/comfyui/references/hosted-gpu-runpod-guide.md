# Hosted GPU and Runpod Playbook

Use this when the user is running ComfyUI in a hosted GPU pod, notebook, JupyterLab, SSH session, or browser-exposed container.

## Source Anchors

- Official ComfyUI server routes: https://docs.comfy.org/development/comfyui-server/comms_routes
- Official startup flags: https://docs.comfy.org/development/comfyui-server/startup-flags
- Official Manager/custom-node docs: https://docs.comfy.org/manager/install
- Official model docs: https://docs.comfy.org/development/core-concepts/models

Runpod-specific UI, pod images, network URLs, and storage behavior can change. Verify in the live pod instead of baking exact provider UI steps into the skill.

## Hosted Runtime Checklist

Collect:

- Public ComfyUI URL and local container URL if exposed.
- Whether the API route is reachable, not just the web UI.
- Jupyter/terminal access.
- Working directory that contains ComfyUI.
- Python executable or venv used to launch ComfyUI.
- Mounted volume path and available disk.
- GPU name, VRAM, driver/CUDA from `/system_stats` or terminal.
- Startup command and flags.
- Manager availability.
- Model folders and actual filenames.

## API Probe

From Codex or a shell that can reach the pod:

```bash
python3 scripts/comfy_doctor.py --server https://example-hosted-comfy-url
```

If the provider exposes the UI through a proxy, `/ws` or API POSTs may behave differently from the browser page. Confirm:

- `GET /system_stats`
- `GET /object_info`
- `GET /models`
- `GET /queue`

If the web UI loads but API calls fail, suspect proxy routing, auth, CORS, or wrong port before blaming the workflow.

## Model Storage

Hosted GPU failures often reduce to one of these:

- Model downloaded into a temporary container layer, not the mounted volume.
- Workflow references a filename that differs by one suffix or folder.
- Downloader ran out of disk space.
- Model is present but under the wrong ComfyUI folder.
- Pod restarted and lost non-persistent files.
- Extra model paths are configured differently than expected.

Use `model_audit.py` against live `/models/{folder}` where possible.

## Custom Nodes

Custom-node installs on hosted pods need extra care:

1. Confirm Manager is present and enabled.
2. Install into the ComfyUI instance running in the pod.
3. Install dependencies into the same Python environment.
4. Restart ComfyUI, not just refresh the browser.
5. Verify class names with `/object_info`.
6. Save the environment setup as a repeatable bootstrap if the pod is disposable.

If a custom node works in a browser workflow but API execution fails, compare the actual API-format workflow to the UI workflow. Some UI-only conveniences do not survive export cleanly.

## Disk and Download Triage

When downloads fail:

- Check free disk on container and mounted volume.
- Check partial files.
- Check whether downloader logs name a quota or permission error.
- Delete partial files only with user approval.
- Prefer resuming into persistent model folders.
- Confirm final filename exactly matches loader dropdown.

## Startup Flags

Hosted servers commonly need:

```bash
python main.py --listen 0.0.0.0 --port 8188 --disable-auto-launch
```

Use memory/VRAM flags only after seeing the actual failure. `--lowvram` can unblock a run and also make it slower; that tradeoff should be explicit.

## Support-Ready Summary

When escalating or asking the user for provider details, provide:

- Pod/runtime ID if the user gives it.
- ComfyUI URL with secrets redacted.
- Startup command.
- Exact failing endpoint and status.
- Workflow class types missing from `/object_info`.
- Model refs missing from `/models/{folder}`.
- Disk and VRAM evidence.
- Last relevant log lines.

This beats "the pod is broken", which is emotionally satisfying and operationally useless.
