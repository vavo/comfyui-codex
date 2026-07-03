# ComfyUI Workflow JSON Format

Use this reference to distinguish editor workflow JSON from API workflow JSON and validate graph structure.

Primary sources:
- https://docs.comfy.org/development/api-development/workflow-api-format
- https://docs.comfy.org/development/core-concepts/workflow
- https://docs.comfy.org/development/comfyui-server/comms_routes

## Two JSON Shapes

| Shape | Used for | Typical markers | API-submittable |
| --- | --- | --- | --- |
| Editor/save format | Reopening visually in the frontend | Top-level `nodes`, `links`, layout/group/widget metadata | No, export or convert first |
| API format | `POST /prompt`, Cloud workflow execution, automation | Top-level numeric-string node IDs; each node has `class_type` and `inputs` | Yes |

API format omits layout metadata. Editor format carries canvas details. Keep both if the user needs a runnable API graph and a readable visual graph.

## API Node Shape

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "model.safetensors"
    },
    "_meta": {
      "title": "Load Checkpoint"
    }
  }
}
```

Rules:

- Top-level value is an object.
- Node IDs are strings.
- Each node value is an object.
- `class_type` is the ComfyUI node class name.
- `inputs` is an object.
- `_meta` is optional and useful for humans.

## Links

Input values are either literals or links.

Literal:

```json
"seed": 123456
```

Link:

```json
"model": ["4", 0]
```

Link rules:

- First item is source node ID as a string.
- Second item is source output index as a non-negative integer.
- Source node must exist.
- Output index must match the source node output schema from `/object_info` when that endpoint is available.

## Editor Format Markers

Editor/save format usually contains:

- `nodes`: list of node objects.
- `links`: list of link records.
- Layout fields such as positions and sizes.
- Groups, color, UI state, widget metadata, and extra frontend data.

For API execution, use the frontend's API export. Automated conversion is possible for simple graphs, but conversion can become fragile when widgets, custom nodes, or frontend-only metadata matter.

## Validation Checklist

Offline checks:

1. JSON parses.
2. Top-level value is an object.
3. Format is `api`, `editor`, or `unknown`.
4. API nodes contain `class_type`.
5. API `inputs` values are objects when present.
6. Links target existing node IDs.
7. Link output indexes are non-negative integers.
8. Workflow has an output node such as `SaveImage`, `PreviewImage`, `SaveVideo`, `SaveAudio`, or equivalent custom output.
9. Model loader fields can be extracted for audit.

Live checks:

1. Every `class_type` exists in `/object_info`.
2. Literal values match node input constraints from `/object_info`.
3. Loader filenames exist in `/models/{folder}`.
4. `POST /prompt` accepts the graph.
5. `/history/{prompt_id}` includes expected outputs.

## Patch Rules

- Preserve node IDs unless there is a real graph reason to change them.
- Patch the smallest input set that satisfies the request.
- Prompt text usually lives in `CLIPTextEncode.inputs.text` or a custom prompt node.
- Seeds usually live on sampler nodes.
- Size usually lives on latent/image source nodes.
- Model names live on loader nodes and must match visible model names.
- Do not invent class names. Fetch `/object_info` or ask for the custom node source.

## API Export Advice

If the user gives editor/save format and wants API execution:

1. Ask for `File -> Export Workflow (API)` when the frontend is available.
2. If not available, classify the JSON and explain conversion risk.
3. Convert only when the graph is simple enough to map safely.
4. Verify with offline lint first.
5. Verify live with `/object_info`, `/models`, and `POST /prompt` when possible.
