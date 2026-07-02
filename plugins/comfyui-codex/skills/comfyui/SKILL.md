---
name: comfyui
description: Build, run, inspect, and troubleshoot ComfyUI workflows and integrations. Use when Codex needs to help with ComfyUI Server API or Comfy Cloud API calls, API-format workflow JSON, node graph creation or modification, missing models or custom nodes, VRAM/startup/runtime failures, ComfyUI Manager/custom node dependency issues, or quick beginner how-to guidance for ComfyUI.
---

# ComfyUI

## Operating Mode

Start by naming the lane you are in: beginner onboarding, workflow authoring, API integration, or troubleshooting. State assumptions explicitly before changing files or telling the user to run commands, especially around local vs cloud execution, server URL, ComfyUI install path, OS, GPU/VRAM, and whether Codex can run the user's ComfyUI instance.

Prefer evidence over folklore. Collect the workflow JSON, exact error text, ComfyUI logs, installed custom nodes, model paths, server URL, and hardware details before diagnosis. If the user wants a broad guide, turn it into a small actionable artifact instead of dumping a wiki into chat.

## Resource Routing

Read only what the task needs:

- `references/api-integration.md`: local server API, Comfy Cloud API, WebSocket monitoring, image retrieval, endpoint triage.
- `references/workflow-authoring.md`: creating, converting, validating, and patching API-format workflow JSON.
- `references/troubleshooting.md`: startup failures, missing models, missing nodes, custom node conflicts, dependency problems, VRAM/performance issues.
- `references/new-user-guide.md`: concise explanations and first-run guidance for users new to ComfyUI.

Use `scripts/comfy_probe.py` when a local ComfyUI server is reachable or the user provides an API-format workflow file. The script is read-only unless ComfyUI itself logs routine GET requests.

## Core Workflow

1. Identify target runtime: local ComfyUI server, Comfy Desktop, portable Windows build, cloud notebook, Runpod/Jupyter, or Comfy Cloud.
2. Establish the API surface: local defaults to `http://127.0.0.1:8188`; Cloud uses `https://cloud.comfy.org` with `X-API-Key`.
3. Inspect before editing: call safe GET endpoints, read workflow JSON structurally, and compare workflow `class_type` values with `/object_info` when available.
4. For workflow changes, modify the smallest set of node inputs. Do not invent custom node class names; fetch node definitions or ask for the workflow/custom node source.
5. For troubleshooting, isolate first: core ComfyUI vs model path vs custom node vs dependency vs GPU/VRAM. Custom nodes are common culprits, so test with them disabled before blaming core.
6. Verify the outcome with a real API call, workflow load, or deterministic local script when possible. If the user's runtime is unavailable, say exactly what remains unverified.

## Practical Defaults

- Use API-format JSON for programmatic execution, not the regular saved UI workflow format.
- Use `/object_info` as the source of truth for node classes, inputs, defaults, and allowed values.
- Use `/models/{folder}` and the loader node dropdown behavior to verify model names instead of guessing path names.
- Use WebSocket plus `/history/{prompt_id}` for production-ish local integrations; use plain `POST /prompt` only for fire-and-forget jobs.
- Keep API keys out of logs and commits. Redact `X-API-Key`, Comfy account keys, cloud tokens, and notebook URLs.
- Install Python dependencies into the Python environment that actually runs ComfyUI. Installing into system Python is the classic "looks busy, fixes nothing" move.

## Probe Script

Run from this skill folder or pass the absolute path:

```bash
python3 scripts/comfy_probe.py --server http://127.0.0.1:8188
python3 scripts/comfy_probe.py --server http://127.0.0.1:8188 --workflow /path/to/workflow_api.json
```

Use its output to ground follow-up advice: endpoint reachability, server stats, available model folders, workflow shape issues, and missing node classes.

## Sources To Prefer

Prefer official docs and source repos for current behavior:

- ComfyUI docs: https://docs.comfy.org/
- ComfyUI repo: https://github.com/Comfy-Org/ComfyUI
- ComfyUI Manager repo: https://github.com/Comfy-Org/ComfyUI-Manager
