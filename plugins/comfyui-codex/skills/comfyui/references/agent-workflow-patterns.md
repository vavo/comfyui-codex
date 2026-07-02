# Agent Workflow Patterns

Use this reference when building ComfyUI support for Codex as an agent workflow, not just answering a single API question.

Primary sources:
- https://docs.comfy.org/
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw

Both referenced repos are MIT-licensed at the time inspected. Use their patterns and source links; do not vendor their full docs, model indexes, UI bundles, or scripts into this skill.

## Source Precedence

1. Official ComfyUI docs and live `/object_info` from the target server.
2. The user's actual workflow JSON, logs, model folders, and hardware.
3. Repo-derived agent patterns from Agent-Kit and OpenClaw.
4. General model folklore, only when clearly labeled as unverified.

## Agent-Kit Patterns To Reuse

- Local-first bootstrap: discover server URL, ComfyUI path, GPU/VRAM, RAM, disk, installed models, and workflow folder before choosing workflows.
- Template-first graph building: prefer official workflow templates or known-good exported workflows, then parameterize.
- Model/task routing: pick by media type, model family, local vs cloud/API availability, and hardware fit.
- Validate graph structure against `/object_info` before execution.
- Keep API and GUI formats distinct: API format queues runs; editor format opens in the canvas.
- For GUI output, lay nodes left-to-right by pipeline stage and avoid node/group overlap.
- Run small/low-cost smoke tests before full-size renders.
- For named models, use model-specific prompting guidance from official docs/model cards where available.

## OpenClaw Patterns To Reuse

- Treat a reusable workflow as a skill with stable inputs, not as raw graph surgery.
- Use IDs like `<server_id>/<workflow_id>` for multi-server routing.
- Store each workflow with its execution JSON, schema/parameter mapping, and history.
- Expose friendly schema aliases such as `prompt`, `seed`, `image`, `mask`, `width`, and `height`.
- Never expose node IDs to normal users; keep them for diagnostics.
- Run dependency checks before first execution: missing node classes, import failures, missing models.
- Use submit/status/result loops for chat agents so progress can be reported between polls.
- Keep CLI/JSON interfaces stable enough that agents can call them without interpreting UI state.

## Codex Operating Loops

### Debug A Workflow

1. Read the error, workflow JSON, and runtime facts.
2. Run `scripts/comfy_probe.py --workflow <file>` against the target server if reachable.
3. Classify failure: workflow format, missing class, missing model, invalid link, validation error, runtime traceback, output retrieval.
4. Patch the smallest node input or dependency issue.
5. Verify with `/prompt`, `/history/{prompt_id}`, `/view`, or a dry-run validation path.

### Package A Workflow For Agents

1. Normalize workflow JSON and preserve the original.
2. Generate friendly schema aliases.
3. Keep tuned defaults hidden unless useful to expose.
4. Add dependency preflight.
5. Add execution history/output handling.
6. Document the exact server assumptions.

### Build A New Workflow

1. Pick template or known-good source.
2. Identify stages: loaders, conditioning, latent/image source, sampler, decode, post-process, save.
3. Wire only matching types: `MODEL`, `CLIP`, `VAE`, `CONDITIONING`, `LATENT`, `IMAGE`, `MASK`, `AUDIO`.
4. Insert converters when needed: `CLIPTextEncode`, `VAEEncode`, `VAEDecode`, image scale/upscale nodes.
5. Add an output node or the job can succeed with nothing useful to fetch.
6. Validate against live `/object_info` and model folders.

## Attribution Notes

This skill uses official ComfyUI documentation for API and workflow facts. It uses Agent-Kit and OpenClaw as design references for agent workflows: local bootstrap, template-first graph assembly, schema aliases, dependency preflight, submit/status polling, multi-server IDs, and GUI/API separation.
