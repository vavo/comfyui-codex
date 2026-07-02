# ComfyUI Troubleshooting

Use this reference when the user reports startup failures, generation errors, missing models, missing nodes, custom node conflicts, dependency failures, API errors, slow generation, or out-of-memory behavior.

Primary sources:
- https://docs.comfy.org/troubleshooting/overview
- https://docs.comfy.org/troubleshooting/custom-node-issues
- https://docs.comfy.org/development/core-concepts/custom-nodes
- https://docs.comfy.org/development/core-concepts/models
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/comfyui-server/startup-flags
- https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit

## First Evidence To Ask For

- Exact error text or "Show report" contents.
- ComfyUI startup log from the terminal.
- Workflow file, preferably API format for API issues.
- ComfyUI install style: Desktop, git clone, Windows portable, notebook, Docker, Runpod, or cloud provider.
- OS, GPU, VRAM, Python version, and whether CUDA/ROCm/Metal is involved.
- Recent changes: ComfyUI update, custom node install/update, model moved, Python packages changed.
- Whether the same issue happens with custom nodes disabled.

## Fast Triage

1. Does ComfyUI start?
2. Does the frontend load?
3. Does the default/basic workflow run?
4. Does the failing workflow use custom nodes?
5. Are all model filenames visible in the loader dropdowns or `/models/{folder}`?
6. Is the failure validation-time, execution-time, or output retrieval-time?
7. Is the API client using API-format workflow JSON?

## Startup Or Frontend Failure

Try a minimal startup from the ComfyUI folder:

```bash
python main.py --disable-auto-launch
```

If custom nodes are suspected:

```bash
python main.py --disable-all-custom-nodes
```

If disabling custom nodes makes the issue disappear, do not keep poking random settings. Isolate custom nodes.

## Custom Node Isolation

Prioritize frontend-extension conflicts when the UI is broken, blank, misaligned, unable to preview images, or unable to communicate with the backend. Disable third-party frontend extensions first if the UI is reachable, restart, then re-enable by halves until the issue returns.

For broader custom node issues, use binary search:

```bash
comfy-cli node bisect start
comfy-cli node bisect good
comfy-cli node bisect bad
comfy-cli node bisect reset
```

If not using Comfy CLI, manually move half of `custom_nodes` out of the active folder, restart, test, and repeat. Back up `custom_nodes` first.

## Missing Nodes

Common causes:

- The required custom node repository is not installed.
- The custom node is installed but failed to import.
- Dependencies were installed into the wrong Python environment.
- The custom node is outdated after a ComfyUI/frontend update.
- A node was renamed, removed, or moved by its maintainer.

Fix sequence:

1. Identify the missing node class names from the workflow or error.
2. Use ComfyUI Manager's missing-node tooling when available.
3. Install or update the custom node.
4. Install its dependencies using the Python environment that runs ComfyUI.
5. Restart ComfyUI and check the startup log for import errors.
6. Replace deprecated nodes only after confirming the original node is not recoverable.

Dependency-check pattern:

- Extract every workflow `class_type`.
- Compare against `/object_info`.
- Separate truly missing nodes from installed-but-import-failed nodes when Manager diagnostics or logs are available.
- For installable nodes, surface source repository/package if known.
- For unknown/private nodes, ask for the original workflow source or custom node repository.

## Missing Models

Check the exact loader node and expected folder. Typical folders live under `ComfyUI/models/`, such as `checkpoints`, `loras`, `vae`, `controlnet`, and `upscale_models`, but custom nodes can define their own expectations.

Fix sequence:

1. Confirm the required filename exactly, including extension and case.
2. Put the file in the folder expected by the loader/custom node docs.
3. If using `extra_model_paths.yaml`, verify indentation and absolute paths.
4. Restart or refresh ComfyUI so model lists update.
5. Confirm the file appears in the loader dropdown or `GET /models/{folder}`.

Do not assume a model is installed just because the file exists somewhere on disk. ComfyUI has to see it from the configured model path.

Common loader-to-folder checks:

- `CheckpointLoaderSimple.ckpt_name` -> `checkpoints`
- `LoraLoader.lora_name` -> `loras`
- `VAELoader.vae_name` -> `vae`
- `ControlNetLoader.control_net_name` -> `controlnet`
- `UpscaleModelLoader.model_name` -> `upscale_models`
- `CLIPLoader.clip_name` and `DualCLIPLoader.clip_name*` -> `clip`
- `UNETLoader.unet_name` -> `diffusion_models`

## Generation Fails

Use the report/error payload first:

- `node_errors` from `POST /prompt`: validation problem before execution.
- `execution_error` WebSocket message: runtime failure while executing.
- Terminal traceback: import, dependency, CUDA, filesystem, or model load failure.

Map the failure to the node ID and class. Then inspect that node's inputs, linked upstream nodes, model filenames, and custom node status.

## VRAM And Performance

Low-effort reductions:

- Lower resolution.
- Lower batch size.
- Close other GPU-heavy applications.
- Disable previews when useful: `python main.py --preview-method none`.
- Try low VRAM mode: `python main.py --lowvram`.
- CPU mode exists, but it is a last resort because it is usually painfully slow: `python main.py --cpu`.

Acceleration flags such as `--use-pytorch-cross-attention`, `--use-flash-attention`, and `--async-offload` can help in compatible environments. Verify compatibility before treating them as magic dust.

## API-Specific Failures

- Server unreachable: verify URL, port, container tunnel/proxy, notebook URL, and whether ComfyUI is running.
- Unknown node class: fetch `/object_info`; install missing custom nodes or export from the same target environment.
- Missing model: fetch `/models/{folder}` and compare exact names.
- No output in `/history`: check prompt ID and whether execution failed.
- `/view` fails: use the filename, subfolder, and type returned by history.
- WebSocket hangs: verify WebSocket URL and `client_id`; test direct local connection before debugging app code.

## Workflow Import Failures

When importing workflows into an agent skill layer:

- Detect API vs editor format first.
- Convert editor format only with a reachable target ComfyUI server when conversion depends on `/object_info`.
- Process bulk imports independently so one broken workflow does not poison the whole folder.
- Auto-rename conflicts instead of overwriting silently.
- Preserve import metadata: origin path, server ID, workflow ID, and conversion warnings.
- Re-run dependency checks after import and before first execution.

## Reporting Upstream

Before filing a ComfyUI core bug:

1. Reproduce with latest ComfyUI when safe.
2. Reproduce with custom nodes disabled.
3. Reproduce with a minimal workflow.
4. Include logs, workflow, exact steps, OS/GPU/Python details, and whether the issue is frontend, API, validation, or execution.

Most "ComfyUI is broken" reports turn into custom node or model path issues. Annoying, yes. Also usually true.
