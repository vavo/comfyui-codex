# ComfyUI New User Guide

Use this reference when the user wants a quick how-to, mental model, beginner checklist, or a simple explanation of how ComfyUI works.

Primary sources:
- https://docs.comfy.org/development/core-concepts/workflow
- https://docs.comfy.org/development/core-concepts/models
- https://docs.comfy.org/development/core-concepts/custom-nodes
- https://docs.comfy.org/development/comfyui-server/comms_overview

## Plain-English Model

ComfyUI is a node graph for generation workflows. A workflow is a graph: nodes do work, links pass outputs into inputs, and the queue runs the graph. A model file provides the weights; loader nodes select those files; sampler nodes generate latent results; decoder/output nodes turn them into images, files, or API-visible outputs.

The app can be used visually in the browser or programmatically through HTTP and WebSocket APIs.

## First Successful Run

1. Install or launch ComfyUI.
2. Open the local UI, commonly `http://127.0.0.1:8188`.
3. Download a compatible checkpoint/model.
4. Put the model in the expected `ComfyUI/models/` subfolder, commonly `checkpoints` for basic text-to-image.
5. Load or create a basic workflow.
6. Choose the model in the loader node.
7. Enter prompt text.
8. Queue the workflow.
9. Save the workflow once it works.

If a model was copied while ComfyUI was open, refresh/restart if it does not appear in dropdowns.

## Core Terms

- Workflow: the whole graph.
- Node: one operation in the graph.
- Input: a setting or connection on a node.
- Output: data produced by a node for downstream nodes.
- Checkpoint: main model weights.
- VAE: model component that decodes latent data into images.
- LoRA: small style/concept adapter applied to a base model.
- ControlNet: conditioning model for pose, edges, depth, and similar controls.
- Custom node: third-party extension that adds node types or UI features.
- Queue: execution list for workflows.
- API format: workflow JSON shape used by code and `POST /prompt`.

## Beginner Workflow Types

- Text-to-image: prompt plus checkpoint generates an image.
- Image-to-image: starts from an input image and changes it.
- Inpainting: edits a masked part of an image.
- LoRA workflow: applies a trained concept/style to a base model.
- ControlNet workflow: follows structure from pose, depth, line art, or similar controls.
- Upscale workflow: improves resolution or detail after generation.

## Good Habits

- Save known-good workflows before experimenting.
- Add one new custom node pack at a time.
- Keep model files organized by type.
- Record exact model and LoRA filenames when sharing workflows.
- Prefer ComfyUI Manager for custom nodes when available.
- Treat random custom nodes like code from the internet, because that is exactly what they are.
- Keep API workflows under version control when building apps.

## How To Ask Codex For Help

Best prompts include:

- Goal: what output the workflow should produce.
- Runtime: local, Desktop, portable, Runpod, notebook, Docker, or Cloud.
- Workflow JSON or screenshot.
- Exact error report or terminal log.
- Model/checkpoint names.
- Installed custom nodes if relevant.
- Hardware details for performance or VRAM issues.

Weak prompt: "ComfyUI broken."

Useful prompt: "Use $comfyui to debug this API workflow. Local server is at http://127.0.0.1:8188. POST /prompt returns node_errors for node 12. Here is the JSON and startup log."

## When To Use The API

Use the API when another app needs to generate images, when batch jobs are needed, or when Codex should patch and test workflow JSON. Use the visual UI when designing or exploring graphs. The practical route is often: design visually, export API format, then automate.
