# ComfyUI Workflow Authoring

Use this reference when creating, converting, validating, or patching ComfyUI workflow JSON.

Primary sources:
- https://docs.comfy.org/development/api-development/workflow-api-format
- https://docs.comfy.org/development/core-concepts/workflow
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/core-concepts/models
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw

## Format Choice

ComfyUI has two common JSON shapes:

- Save format: intended for reopening and visually editing in the frontend. It includes layout and presentation metadata.
- API format: intended for API submission. It uses numeric-string node IDs, `class_type`, and `inputs`, without visual layout metadata.

For code, automation, Cloud API, and local `POST /prompt`, use API format. In the ComfyUI frontend, export it with `File -> Export Workflow (API)`.

Keep editor/GUI format in scope when the user wants to see or edit the graph in the canvas. API format runs; editor format carries positions, links, widgets, groups, and layout. If Codex builds a user-facing graph, produce or preserve the editor-format file too.

## API-Format Shape

Each node is keyed by a string node ID:

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "model.safetensors"
    }
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "clip": ["4", 1],
      "text": "a concise prompt"
    }
  }
}
```

Input values are either literals or links. Links are two-item arrays: `["source_node_id", output_index]`.

## Authoring Process

1. Start from a known-good exported API workflow when possible.
2. Prefer official ComfyUI workflow templates for a model/task before inventing a graph.
3. Fetch `/object_info` from the target server. That server knows the installed node classes and allowed inputs.
4. Check model loader values against `/models/{folder}` or the frontend dropdown. File names must match what ComfyUI sees.
5. Build the smallest graph that proves the goal, then add complexity one branch at a time.
6. Keep node IDs stable when patching existing workflows so API clients and tests can target known nodes.
7. For a visual workflow, lay nodes left-to-right by dependency stage and avoid overlaps; do not leave every node at `[0, 0]` and call it a graph.
8. Queue a dry run only after structural checks pass.

## Patching Existing Workflows

Prefer targeted edits:

- Prompt text: edit `CLIPTextEncode.inputs.text` or the relevant custom prompt node.
- Seed: edit sampler seed inputs.
- Size: edit latent/image source width and height inputs.
- Model: edit loader filename values, then verify against `/models/{folder}`.
- LoRA: edit the LoRA loader name and strength values; make sure the LoRA file exists in the visible LoRA folder.
- Output behavior: switch between `SaveImage`, preview nodes, or WebSocket image output depending on integration needs.

Do not rewrite a whole workflow just to change one prompt or seed. That is how small bugs audition for a starring role.

## Validation Checklist

- JSON parses.
- Top-level value is an object.
- Every node value is an object with `class_type` and `inputs`.
- Every link points to an existing node ID.
- Every linked output index is a non-negative integer.
- Every `class_type` exists in `/object_info`.
- Every model filename exists in the relevant `/models/{folder}` response or is documented by the custom node.
- The workflow uses API format, not frontend save format.
- The final tensor is wired to an output node such as `SaveImage`, `PreviewImage`, video save/combine, audio save, or WebSocket image output.
- If a GUI/editor workflow is delivered, node positions and groups are readable and non-overlapping.

## Workflow-As-Skill Packaging

Use this pattern when the user wants reusable agent commands rather than one-off workflow edits:

1. Store a normalized workflow by server/workflow ID.
2. Generate a schema that maps friendly parameter names to internal `node_id.field` targets.
3. Expose only parameters users should control.
4. Keep defaults for tuned sampler/model values unless the user asks to expose them.
5. Before first run, check dependencies: missing node classes, import failures, and missing models.
6. Execute with structured JSON args and record history/output paths.

Good exposed aliases: `prompt`, `negative_prompt`, `seed`, `steps`, `width`, `height`, `batch_size`, `image`, `mask`, `filename_prefix`.

Do not expose raw node IDs in normal user-facing prompts. Use them in diagnostics and implementation details.

## When Creating From Scratch

Ask for or infer these before building:

- Output goal: image, mask, video, metadata, or API-only intermediate result.
- Runtime: local server, cloud notebook, Runpod, Comfy Desktop, or Comfy Cloud.
- Available base model/checkpoint and model family.
- Required custom nodes and whether they are installed.
- Inputs: text prompt, negative prompt, image, mask, LoRA, ControlNet, dimensions, batch size.
- Integration pattern: saved files, `/history` plus `/view`, or WebSocket binary output.

If `/object_info` is unavailable, say that node availability is unverified and avoid custom node names unless the user supplied them.

## Minimal Text-To-Image Skeleton

This skeleton shows the API-format wiring pattern. Verify model names on the target server before submitting.

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "v1-5-pruned-emaonly.safetensors"
    }
  },
  "5": {
    "class_type": "EmptyLatentImage",
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    }
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "clip": ["4", 1],
      "text": "a clean product photo on a neutral background"
    }
  },
  "7": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "clip": ["4", 1],
      "text": "blurry, low quality"
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 123456,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    }
  },
  "8": {
    "class_type": "VAEDecode",
    "inputs": {
      "samples": ["3", 0],
      "vae": ["4", 2]
    }
  },
  "9": {
    "class_type": "SaveImage",
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": ["8", 0]
    }
  }
}
```

## Review Heuristics

- If a workflow has many custom nodes, identify the core generation path first, then secondary controls.
- If a workflow fails after a ComfyUI update, suspect custom node/frontend extension drift before rewriting the graph.
- If a user pasted save-format JSON, ask for an API export or convert only when the structure is clearly understood.
- If the API response includes `node_errors`, map each error back to the node ID and class before suggesting fixes.
