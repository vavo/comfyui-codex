# ComfyUI Canvas Interface Guide

Use this reference when the user is new to the ComfyUI canvas, needs to understand node wiring, or wants a GUI workflow explained before API work.

Primary sources:
- https://docs.comfy.org/development/core-concepts/workflow
- https://docs.comfy.org/development/core-concepts/custom-nodes
- https://www.angry-shark-studio.com/blog/comfyui-tutorial-understanding-canvas/
- https://stable-diffusion-art.com/comfyui/

## Contents

- [Mental Model](#mental-model)
- [Node Anatomy](#node-anatomy)
- [Canvas Controls](#canvas-controls)
- [Reading A Workflow](#reading-a-workflow)
- [Editing A Workflow Safely](#editing-a-workflow-safely)
- [GUI To API Translation](#gui-to-api-translation)
- [Beginner Workflow Habits](#beginner-workflow-habits)

## Mental Model

ComfyUI workflows are data-flow graphs:

- Nodes do one focused job.
- Inputs are on the left.
- Outputs are on the right.
- Wires carry typed values between compatible sockets.
- Widget fields in the node body are literal parameters.
- The final result must reach an output node such as `SaveImage`, `PreviewImage`, video save/combine, audio save, or a WebSocket output node.

Do not teach the canvas as "buttons to click until it works." Teach it as a pipeline: load model, prepare inputs, encode prompts/images, sample/generate, decode/process, save.

## Node Anatomy

Each node has:

- **Input sockets**: values arriving from previous nodes, such as `MODEL`, `CLIP`, `VAE`, `LATENT`, `IMAGE`, `MASK`, or `CONDITIONING`.
- **Settings/widgets**: values the user types or selects directly, such as seed, steps, CFG, width, model filename, prompt, or filename prefix.
- **Output sockets**: values produced by the node and sent downstream.

Common node roles:

- Loader nodes choose model files.
- Encoder nodes turn text/images into conditioning or latents.
- Sampler nodes perform denoising/generation.
- Decoder nodes turn latents into visible images.
- Processor nodes resize, mask, upscale, combine, or transform values.
- Output nodes save or preview results.

## Canvas Controls

Useful user-facing controls:

- Zoom with mouse wheel or trackpad pinch.
- Pan by dragging empty canvas space.
- Double-click empty canvas to search/add nodes.
- Right-click for context actions.
- Drag from an output socket to a compatible input socket to wire nodes.
- Disconnect or delete a wire before inserting a processing node between two existing nodes.
- Drag generated workflow PNGs or workflow JSON files into ComfyUI to load embedded workflows when supported.
- Save important workflows as JSON, not only browser state.

If the user cannot find a node, teach double-click search before giving a full custom-node lecture.

## Reading A Workflow

Read left to right by dependency:

1. Identify model loaders.
2. Identify input sources: empty latent, loaded image, mask, control image, video frames, or audio.
3. Identify prompt and conditioning nodes.
4. Identify samplers or model execution nodes.
5. Identify VAE decode or output conversion nodes.
6. Identify post-processing: upscale, detailer, combine, save.
7. Identify output nodes.

For a failing workflow, annotate:

- Which node first reports the error.
- Which upstream node supplies the failing input.
- Which model/custom-node files are referenced.
- Which node IDs map to user-facing controls.

## Editing A Workflow Safely

Make small graph edits:

- To change prompt: edit prompt text node fields.
- To change size: edit latent/image source dimensions.
- To change seed/steps/CFG: edit sampler fields.
- To add image upscale: insert upscale loader and upscale node between image output and save node.
- To add LoRA: insert LoRA loader between checkpoint/model loader and prompt/sampler consumers.
- To add ControlNet: add control loader/preprocessor/apply node before sampler conditioning.

Do not rewrite a working graph to make one parameter change. That is how a one-minute edit becomes an archeology project.

## GUI To API Translation

Teach both shapes:

- GUI/editor workflow: canvas layout, widgets, links, groups, and visual metadata.
- API workflow: node IDs with `class_type` and `inputs`.

When the user wants automation:

1. Ask for API export if they gave a normal saved workflow.
2. Preserve the GUI workflow if they still need to visually edit it.
3. Use `workflow_lint.py` to classify and sanity-check offline.
4. Use `/object_info` to verify node classes live.

## Beginner Workflow Habits

- Save early and version useful workflows.
- Keep a known-good basic workflow untouched.
- Change one thing at a time when learning.
- Fix seeds for comparisons.
- Record model, VAE, LoRA, ControlNet, and upscaler filenames.
- Keep custom-node-heavy workflows separate from basic teaching examples.
- Avoid loading random complex workflows before understanding the default graph.

Good teaching prompt:

```text
Use $comfyui to explain this workflow from left to right and tell me which nodes I should edit for prompt, seed, model, size, and output filename.
```
