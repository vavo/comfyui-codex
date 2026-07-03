# ComfyUI Troubleshooting Playbooks

Use this reference for step-by-step diagnosis of broken ComfyUI installs, workflows, API calls, custom nodes, and model references.

Primary sources:
- https://docs.comfy.org/troubleshooting/overview
- https://docs.comfy.org/troubleshooting/custom-node-issues
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/comfyui-server/startup-flags
- https://docs.comfy.org/development/core-concepts/models
- https://docs.comfy.org/development/core-concepts/custom-nodes

## Evidence Packet

Ask for or collect:

- Install type and OS.
- GPU, VRAM, Python version, and startup command.
- Full startup log.
- Workflow JSON, preferably API export for API issues.
- Exact error text, `node_errors`, or `execution_error`.
- Missing model filenames and missing node class names.
- Recent updates or installs.
- Whether the default workflow works.
- Whether custom nodes disabled changes the result.

## Server Offline

Symptoms:

- Browser cannot open ComfyUI.
- API returns connection refused or timeout.
- `comfy_probe.py` reports all endpoints offline.

Steps:

1. Confirm the startup command actually ran.
2. Read terminal logs for early crash.
3. Start without auto-launch:

```bash
python main.py --disable-auto-launch
```

4. Confirm host and port. Default is usually `127.0.0.1:8188`.
5. If running in Docker/notebook/Runpod, verify port exposure or proxy URL.
6. If custom nodes may crash startup, retry with:

```bash
python main.py --disable-all-custom-nodes
```

7. If the server starts after disabling nodes, move to the custom-node playbook.

## UI Loads But API Fails

Steps:

1. Check direct `GET /system_stats`.
2. Check `GET /object_info`.
3. Verify API client base URL matches browser URL.
4. Check proxy path rewriting for notebooks or hosted URLs.
5. Confirm CORS/proxy/WebSocket behavior only after direct routes are tested.
6. For Cloud, verify Cloud API auth and do not assume local routes.

## Validation `node_errors`

Symptoms:

- `POST /prompt` returns `error` and `node_errors`.
- Workflow never enters execution.

Steps:

1. Confirm workflow is API format.
2. Map each error to node ID and `class_type`.
3. Compare `class_type` values with `/object_info`.
4. Compare model loader filenames with `/models/{folder}`.
5. Check literal input values against `/object_info` constraints.
6. Patch only the failing inputs/classes.
7. Re-submit once.

Do not debug samplers or VRAM when validation failed before execution. Different floor of the building.

## Missing `class_type`

Steps:

1. Extract all workflow class names.
2. Fetch `/object_info`.
3. Missing classes = workflow classes not in `/object_info`.
4. Check startup logs for installed custom nodes that failed import.
5. Use Manager's Install Missing Custom Nodes when available.
6. If Manager cannot find a class, identify the original workflow source.
7. Install only the required node pack.
8. Restart and recheck `/object_info`.

If the node pack is installed but classes are missing, treat it as an import/dependency problem.

## Missing Model

Steps:

1. Identify loader node and input field.
2. Map field to model folder.
3. Fetch `/models/{folder}`.
4. Compare exact filename including extension and case.
5. If using extra paths, verify config and restart.
6. If hosted, check storage volume and download destination.
7. Reopen the workflow or requeue only after the file is visible.

Useful mapping lives in `model-routing-and-prompting.md`.

## Import Error Or Dependency Conflict

Steps:

1. Read the startup traceback.
2. Identify custom node package and missing/conflicting dependency.
3. Identify the Python executable that starts ComfyUI.
4. Run `python -m pip show <package>` from that exact Python.
5. Install or pin from the node's requirements.
6. Restart.
7. If multiple packages conflict, disable node packs and re-enable one at a time.

Installing into system Python while ComfyUI runs from embedded Python or a venv is the classic fake fix.

## VRAM Or Out Of Memory

Steps:

1. Confirm device and VRAM through `/system_stats`.
2. Reduce resolution.
3. Reduce batch size.
4. Lower frame count for video workflows.
5. Disable previews if useful:

```bash
python main.py --preview-method none
```

6. Try low VRAM mode:

```bash
python main.py --lowvram
```

7. Use CPU only as last resort:

```bash
python main.py --cpu
```

If OOM appears after adding a custom node, check whether it loads extra models or keeps tensors alive.

## Output Retrieval Failure

Symptoms:

- Generation completes but app cannot fetch files.
- `/view` returns 404.
- `/history/{prompt_id}` has no expected images.

Steps:

1. Fetch `/history/{prompt_id}`.
2. Find actual output node payload.
3. Use exact `filename`, `subfolder`, and `type`.
4. Confirm the workflow uses an output node such as `SaveImage`.
5. If using WebSocket image output, do not expect `SaveImage` files.
6. Check output directory permissions and storage.

## Workflow Import Failure

Steps:

1. Detect editor vs API format.
2. For API execution, request `File -> Export Workflow (API)`.
3. If class names are unknown, install custom nodes or use the source environment.
4. Import workflows one at a time.
5. Record missing classes and models per workflow.
6. Avoid overwriting existing workflows silently.

## Escalate Upstream

Only after:

- Reproduced on current ComfyUI when safe.
- Reproduced with custom nodes disabled.
- Reduced to a minimal workflow.
- Captured logs, workflow, platform details, and exact steps.

Most failures are custom nodes, dependencies, model paths, or workflow format mismatch. Irritating, but cheaper to verify than to reinstall everything.
