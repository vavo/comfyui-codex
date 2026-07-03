---
name: comfyui
description: Build, run, inspect, install, and troubleshoot ComfyUI workflows and integrations using official docs plus proven agent workflow patterns. Use when Codex needs to help with ComfyUI installation paths, ComfyUI Manager, custom node installation or dependencies, ComfyUI Server API or Comfy Cloud API calls, API-format workflow JSON, editor workflow conversion, node graph creation or modification, workflow-as-skill packaging, missing models or custom nodes, VRAM/startup/runtime failures, or quick beginner how-to guidance for ComfyUI.
---

# ComfyUI

## Operating Mode

Start by naming the lane you are in: beginner onboarding, canvas/interface, MCP/App Mode, workflow tutorial, generation parameters, installation, hosted GPU, Manager/custom nodes, model/prompt routing, model-family selection, workflow authoring, golden workflow validation, API integration, error explanation, custom-node resolution, skill evaluation, or troubleshooting. State assumptions explicitly before changing files or telling the user to run commands, especially around local vs cloud execution, server URL, ComfyUI install path, OS, GPU/VRAM, and whether Codex can run the user's ComfyUI instance.

Prefer evidence over folklore. Collect the workflow JSON, exact error text, ComfyUI logs, installed custom nodes, model paths, server URL, and hardware details before diagnosis. If the user wants a broad guide, turn it into a small actionable artifact instead of dumping a wiki into chat.

## Resource Routing

Read only what the task needs:

- `references/installation-paths.md`: install matrix for Desktop, Windows Portable, manual git/venv, Comfy CLI, hosted runtimes, Cloud, startup flags, and first-run checks.
- `references/manager-custom-nodes.md`: Manager enablement/config, missing custom nodes, dependency repair, isolation, snapshots, custom-node authoring basics, and security checks.
- `references/mcp-app-interface-guide.md`: Comfy Agent Tools/MCP choices, local API interface contract, App Mode builder guidance, UI panels, Mask Editor, and future MCP boundary rules.
- `references/api-endpoints.md`: compact local Server API route map, WebSocket messages, submit/status/result loop, Cloud API caveats, and endpoint failure mapping.
- `references/api-integration.md`: integration strategy for local vs Cloud APIs, WebSocket monitoring, output retrieval, partner-node keys, and agent-safe API contracts.
- `references/canvas-interface-guide.md`: ComfyUI canvas mental model, node anatomy, GUI controls, wiring, reading workflows, and GUI-to-API translation.
- `references/generation-parameters.md`: seed, steps, CFG, sampler, scheduler, denoise, dimensions, batch, LoRA strength, ControlNet strength, and comparison workflow.
- `references/golden-workflow-library.md`: local API-format golden workflow catalog, fixture rules, validation flow, and missing fixture targets.
- `references/workflow-json-format.md`: API vs editor workflow JSON, node/link shape, validation checklist, and patching rules.
- `references/workflow-recipes.md`: starter patterns for txt2img, img2img, inpaint, LoRA, ControlNet, upscale, and result retrieval.
- `references/workflow-tutorials.md`: step-by-step tutorial patterns for txt2img, img2img, inpaint, outpaint, upscale, LoRA, LoRA stacking, ControlNet, text-to-video, and image-to-video.
- `references/workflow-authoring.md`: creating, converting, validating, and packaging workflows as agent-callable skills.
- `references/model-routing-and-prompting.md`: loader-to-folder map, model family routing, prompt inputs, LoRA/ControlNet guidance, and extra model paths.
- `references/model-family-decision-guide.md`: model family selection for SD 1.5, SDXL, modern transformer/edit/video families, LoRA, ControlNet, upscalers, VRAM tradeoffs, and prompting style.
- `references/error-explainer-and-node-resolver.md`: error categories, `node_errors`, missing classes, resolver map policy, Manager install flow, dependency/import failures, and reporting format.
- `references/hosted-gpu-runpod-guide.md`: hosted GPU and Runpod-style runtime checks, API proxy issues, persistent storage, downloads, model folders, custom nodes, startup flags, and support summaries.
- `references/skill-evaluation-suite.md`: offline validation commands, pressure prompts, expected routing behavior, acceptance criteria, and regression checks.
- `references/troubleshooting-playbooks.md`: step-by-step playbooks for server offline, API failures, node errors, missing classes/models, imports, VRAM, output retrieval, and workflow import failures.
- `references/troubleshooting.md`: broad troubleshooting overview and upstream reporting checklist.
- `references/new-user-guide.md`: concise explanations and first-run guidance for users new to ComfyUI.
- `references/agent-workflow-patterns.md`: repo-derived patterns from ComfyUI-Agent-Kit and ComfyUI_Skills_OpenClaw: local-first bootstrap, template-first graph building, schema aliases, dependency preflight, multi-server routing, and GUI/API format separation.

Use `scripts/comfy_probe.py`, `scripts/comfy_doctor.py`, `scripts/workflow_lint.py`, `scripts/model_audit.py`, `scripts/error_explainer.py`, `scripts/custom_node_resolver.py`, or `scripts/workflow_catalog.py` when local server evidence, offline workflow validation, error classification, custom-node resolution, golden fixture validation, or model-reference checks would help. These scripts are read-only unless ComfyUI itself logs routine GET requests.

## Core Workflow

1. Identify target runtime: local ComfyUI server, Comfy Desktop, portable Windows build, cloud notebook, Runpod/Jupyter, or Comfy Cloud.
2. For install work, identify install type, OS, GPU, Python environment, startup command, and whether Manager/custom nodes are involved before giving commands.
3. Establish the API surface: local defaults to `http://127.0.0.1:8188`; Cloud uses `https://cloud.comfy.org` with `X-API-Key`.
4. Bootstrap facts: collect `/system_stats`, `/object_info`, `/models`, configured workflow folders, available models, and whether the user expects local-first or Cloud behavior.
5. Inspect before editing: detect API vs editor workflow JSON, call safe GET endpoints, and compare workflow `class_type` values with `/object_info` when available.
6. For workflow changes, modify the smallest set of node inputs. Do not invent custom node class names; fetch node definitions or ask for the workflow/custom node source.
7. For agent-safe workflows, expose schema aliases such as `prompt`, `seed`, `width`, and `image`; do not make users reason about node IDs unless they ask.
8. For troubleshooting, isolate first: core ComfyUI vs model path vs custom node vs dependency vs GPU/VRAM. Custom nodes are common culprits, so test with them disabled before blaming core.
9. For hosted GPU work, separate browser UI reachability from API reachability, and verify persistent storage before assuming models survived a restart.
10. Verify the outcome with a real API call, workflow load, or deterministic local script when possible. If the user's runtime is unavailable, say exactly what remains unverified.

## Practical Defaults

- Use API-format JSON for programmatic execution, not the regular saved UI workflow format.
- Use `/object_info` as the source of truth for node classes, inputs, defaults, and allowed values.
- Use `/models/{folder}` and the loader node dropdown behavior to verify model names instead of guessing path names.
- Prefer official workflow templates or a known-good exported workflow before building raw graphs from scratch.
- Prefer the local golden workflow catalog for routine fixture-driven examples, then verify against live `/object_info` and `/models` when a server is available.
- Preserve both mental models: API format runs, editor/GUI format is what the canvas opens and lays out.
- Use WebSocket plus `/history/{prompt_id}` for production-ish local integrations; use plain `POST /prompt` only for fire-and-forget jobs.
- Keep API keys out of logs and commits. Redact `X-API-Key`, Comfy account keys, cloud tokens, and notebook URLs.
- Install Python dependencies into the Python environment that actually runs ComfyUI. Installing into system Python is the classic "looks busy, fixes nothing" move.

## Probe Script

Run from this skill folder or pass the absolute path:

```bash
python3 scripts/comfy_probe.py --server http://127.0.0.1:8188
python3 scripts/comfy_probe.py --server http://127.0.0.1:8188 --workflow /path/to/workflow_api.json
```

Use script output to ground follow-up advice: endpoint reachability, server stats, available model folders, workflow shape issues, suggested schema parameters, model references, missing model files, and missing node classes.

Additional offline/live helpers:

```bash
python3 scripts/workflow_lint.py /path/to/workflow.json
python3 scripts/model_audit.py /path/to/workflow_api.json --server http://127.0.0.1:8188
python3 scripts/comfy_doctor.py --server http://127.0.0.1:8188 --workflow /path/to/workflow_api.json
python3 scripts/error_explainer.py /path/to/comfy-error.json
python3 scripts/custom_node_resolver.py MissingClassName --map-json fixtures/custom_nodes/class_resolver.json
python3 scripts/workflow_catalog.py --catalog-json fixtures/golden_workflows/catalog.json
```

## Sources To Prefer

Prefer official docs and source repos for current behavior:

- ComfyUI docs: https://docs.comfy.org/
- ComfyUI repo: https://github.com/Comfy-Org/ComfyUI
- ComfyUI Manager repo: https://github.com/Comfy-Org/ComfyUI-Manager
- ComfyUI-Agent-Kit: https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- ComfyUI Skills OpenClaw: https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw
