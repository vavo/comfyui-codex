# Golden Workflow Library

Use this when creating, reviewing, or testing known-good workflow patterns without a live ComfyUI server.

## Official Source Anchors

- Workflow concept: https://docs.comfy.org/development/core-concepts/workflow
- Workflow API format: https://docs.comfy.org/development/api-development/workflow-api-format
- Built-in workflow templates: https://docs.comfy.org/interface/workflow_templates
- Server routes: https://docs.comfy.org/development/comfyui-server/comms_routes

## Purpose

Golden workflows are small API-format fixtures that give Codex a local baseline for:

- Text-to-image.
- Image-to-image.
- Inpaint/outpaint.
- Upscale.
- LoRA and LoRA stacking.
- ControlNet.
- Video workflows.
- Result retrieval.

They are not a model download catalog. They are structural examples for linting, patching, and skill packaging.

## Current Fixture Catalog

Catalog:

```text
fixtures/golden_workflows/catalog.json
```

Validate it:

```bash
python3 scripts/workflow_catalog.py \
  --catalog-json fixtures/golden_workflows/catalog.json
```

Current entries:

- `txt2img-basic`: uses the existing minimal API workflow fixture.
- `lora-stack-basic`: chains two `LoraLoader` nodes before sampling.
- `upscale-basic`: load image, load upscaler, upscale, save.

## Fixture Rules

Keep fixtures:

- API-format JSON, not editor save format.
- Small enough to inspect in a code review.
- Generic model filenames such as `example-base-model.safetensors`.
- Free of local absolute paths.
- Structurally valid under `workflow_lint.py`.
- Paired with expected output when a script depends on them.

Do not put private workflow secrets, account IDs, notebook URLs, cloud keys, or local paths in fixtures.

## What Makes a Workflow "Golden"

A fixture is golden when:

1. `workflow_lint.py` reports API format and no broken links.
2. It has at least one output node.
3. Class names are stable core classes or intentionally documented custom nodes.
4. Model references are examples, not hidden requirements.
5. It can be used to teach or patch a workflow without opening the online docs.

## Missing Library Targets

Add these as fixtures when useful:

- `img2img-basic`: `LoadImage`, encode image to latent, sample with denoise below 1.0, decode, save.
- `inpaint-basic`: image plus mask path, inpaint conditioning, moderate denoise.
- `outpaint-basic`: padding/expand image canvas, mask edge area, inpaint.
- `controlnet-canny-basic`: ControlNet loader plus preprocessor or prepared control image.
- `video-text-basic`: text-to-video template using the currently chosen video stack.
- `video-image-basic`: image-to-video template with explicit frame count, resolution, and model family.

Video and ControlNet fixtures should name their custom node requirement clearly. Silent custom-node assumptions are how workflow sharing turns into archaeology.

## Codex Usage Pattern

When asked to build a workflow:

1. Prefer an official template or local golden fixture.
2. Patch only the required inputs.
3. Run `workflow_lint.py`.
4. If live server exists, compare classes with `/object_info`.
5. Run `model_audit.py` if model filenames are known.
6. Export user-facing parameters such as `prompt`, `negative_prompt`, `seed`, `width`, `height`, `steps`, `cfg`, `denoise`, and `image`.

When asked to debug a workflow:

1. Detect API vs editor format.
2. Compare against the closest golden fixture.
3. Explain only the structural delta that matters.
4. Avoid rewriting the entire graph unless the workflow is unrecoverable.
