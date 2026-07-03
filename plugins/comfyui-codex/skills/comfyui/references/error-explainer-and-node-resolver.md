# Error Explainer and Custom Node Resolver

Use this when a user provides `POST /prompt` errors, `node_errors`, startup logs, missing class types, or custom-node import failures.

## Official Source Anchors

- Server routes and `node_errors`: https://docs.comfy.org/development/comfyui-server/comms_routes
- WebSocket error messages: https://docs.comfy.org/development/comfyui-server/comms_messages
- Custom nodes: https://docs.comfy.org/development/core-concepts/custom-nodes
- Install custom nodes: https://docs.comfy.org/installation/install_custom_node
- Manager install: https://docs.comfy.org/manager/install
- Manager configuration: https://docs.comfy.org/manager/configuration

## Tools

Error classification:

```bash
python3 scripts/error_explainer.py /path/to/comfy-error.json
```

Custom node class mapping:

```bash
python3 scripts/custom_node_resolver.py IPAdapterModelLoader \
  --map-json fixtures/custom_nodes/class_resolver.json
```

Workflow extraction mode:

```bash
python3 scripts/custom_node_resolver.py \
  --workflow /path/to/workflow.json \
  --map-json fixtures/custom_nodes/class_resolver.json
```

These tools do not install anything. They classify evidence and suggest the next check.

## Error Buckets

| Bucket | Evidence | First action |
| --- | --- | --- |
| `validation_node_errors` | `POST /prompt` returns `node_errors` | Read the node id, class type, and message before changing files. |
| `missing_custom_node` | class type does not exist or missing node class | Use Manager missing-node install, resolver map, then verify `/object_info`. |
| `missing_model` | checkpoint/LoRA/VAE/controlnet/upscaler filename missing | Run `model_audit.py`; compare against `/models/{folder}`. |
| `dependency_import_error` | `ModuleNotFoundError`, `ImportError`, failed startup import | Install dependency into the ComfyUI runtime environment, not random system Python. |
| `vram_oom` | CUDA/MPS out-of-memory, VRAM failures | Lower memory pressure, free models, restart, or use startup memory flags. |
| `server_unreachable` | timeout, connection refused, proxy/tunnel issue | Confirm URL, port, hosted proxy, and `/system_stats`. |
| `output_retrieval` | `/view` 404 or missing output file | Read `/history/{prompt_id}` and use returned filename/subfolder/type. |

## Missing Class Flow

1. Collect workflow JSON and exact `node_errors`.
2. Extract missing `class_type` values.
3. Run `custom_node_resolver.py`.
4. If resolved, install via ComfyUI-Manager when available.
5. Restart ComfyUI.
6. Verify the class appears in `/object_info`.
7. Re-run `workflow_lint.py` and then the workflow.

Do not claim a mapping is certain unless it is exact. Workflows can use renamed, forked, or private node packs.

## Resolver Map Policy

Resolver data lives in:

```text
fixtures/custom_nodes/class_resolver.json
```

Keep the map compact:

- Exact class matches get `high` confidence.
- Prefix matches get `high` only for widely used prefixes.
- Contains matches usually get `medium`.
- Unknown classes stay unresolved.

Do not add broad rules like `Loader -> SomePack`. That is how a tool becomes wrong faster, with confidence.

## Manager and Security Notes

Comfy Desktop includes Manager by default per official docs. Other installs may require enabling or installing Manager separately.

For third-party custom nodes:

- Prefer Manager and registry-backed metadata when possible.
- Review repository age, issues, install instructions, and dependency list.
- Avoid custom-node packs that require broad system changes unless the user accepts that risk.
- Snapshot or note current node versions before heavy updates.
- Treat custom nodes as arbitrary Python code.

## What To Report Back

Good output:

- Missing classes.
- Likely node pack and confidence.
- Whether `/object_info` verifies the class.
- Whether dependency import errors remain after restart.
- Exact next command or Manager action.

Bad output:

- "Install all missing custom nodes" with no class list.
- "Reinstall ComfyUI" as the first move.
- Guessing model folders from filenames when `/models/{folder}` is available.
