# MCP, App Mode, and Interface Guide

Use this when the user asks how Codex should operate ComfyUI through chat, MCP, Comfy Cloud, local API calls, or App Mode.

## Official Source Anchors

- Agent Tools / MCP: https://docs.comfy.org/agent-tools
- Interface overview: https://docs.comfy.org/interface/overview
- App Mode: https://docs.comfy.org/interface/app-mode
- Mask Editor: https://docs.comfy.org/interface/maskeditor
- Server routes: https://docs.comfy.org/development/comfyui-server/comms_routes
- WebSocket messages: https://docs.comfy.org/development/comfyui-server/comms_messages

## Mode Selection

Choose the operating mode before giving instructions:

| User goal | Best lane | What Codex should do |
| --- | --- | --- |
| "Generate from chat" with hosted GPUs | Comfy Cloud MCP | Point to Cloud MCP or Cloud API. Do not pretend this local plugin is a hosted GPU. |
| "Drive my local ComfyUI" | Local Server API | Use `/system_stats`, `/object_info`, `/models`, `/prompt`, `/history`, `/view`, and `/ws`. |
| "Make this workflow easy for non-technical users" | App Mode | Guide the user to select inputs, outputs, preview, and default view. |
| "Teach me the UI" | Interface/canvas | Explain sidebar, node library, model library, queue, assets, templates, and canvas controls. |
| "Inpaint this image" | Mask Editor + workflow | Use Mask Editor for mask creation, then inpaint workflow validation. |
| "Package workflow for Codex" | Skill/workflow wrapper | Expose friendly schema fields and keep API-format workflow fixtures local. |

The official docs describe first-party MCP options as Cloud MCP, Partner MCP, and Comfy CLI. Local ComfyUI can still be driven by agents through its running server API; first-party local MCP polish is separate from the existing API surface.

## Local ComfyUI API Interface Contract

Minimum read-only checks:

1. `GET /system_stats` to confirm server and device state.
2. `GET /object_info` to confirm node classes and accepted inputs.
3. `GET /models` and `GET /models/{folder}` to confirm exact model filenames.
4. `GET /queue` to understand execution state.
5. Optional `GET /extensions` to spot Manager/custom-node signals.

Execution loop:

1. `POST /prompt` with API-format workflow JSON.
2. Track `prompt_id`.
3. Listen on `/ws` for `status`, `execution_start`, `executing`, `progress`, `executed`, `execution_error`, and `execution_success`.
4. Read `GET /history/{prompt_id}`.
5. Fetch returned media with `/view`.

Do not use editor workflow JSON for `POST /prompt`. Export API format first.

## App Mode Guidance

App Mode is for hiding workflow complexity behind selected inputs and outputs. Use it when the user wants a workflow to be shared, repeated, or run from a cleaner interface.

Builder checklist:

1. Enter App Mode from the top-left menu or breadcrumb menu.
2. Select inputs: prompt fields, image upload fields, model selectors, seed, dimensions, or strength controls.
3. Select outputs: preview, save image, video, or other result nodes.
4. Preview the app layout.
5. Set the default view to App Mode when the workflow should open as an app.

App Mode is also useful on mobile/narrow screens because the UI can separate input, output, and asset panels. For debugging, switch back to node graph mode.

## Interface Guide Cheat Sheet

The user-facing UI has five concepts Codex should recognize:

- Main workflow canvas: node graph and links.
- Left/sidebar panels: assets, nodes, models, workflows, templates, queue/history depending on UI version.
- Model library: reflects local model folders after startup; refresh after downloading models.
- Queue controls: run, cancel, and inspect queued jobs.
- Runtime logs/console/help: where import failures, dependency problems, and startup errors usually surface.

For new users, teach the canvas from left to right:

1. Load model.
2. Encode prompt and negative prompt.
3. Create latent or load image.
4. Sample.
5. Decode or post-process.
6. Preview/save.

## Mask Editor Guidance

Use the built-in Mask Editor for inpaint/outpaint workflows when the user needs to create or modify a mask. It can be opened from a Load Image node, image overlay, or right-click menu. The editor has mask drawing, paint, eraser, bucket fill, color selection, undo/redo, transforms, opacity, and layer controls.

For inpaint debugging, ask for:

- Source image.
- Mask image or Mask Editor state.
- Inpaint model or workflow.
- Denoise value.
- Whether the masked area is white/black according to the workflow's node convention.

## MCP Boundaries for This Plugin

This repository currently provides a Codex plugin with skills, references, fixtures, and read-only scripts. It is not a live MCP server.

If adding an MCP server later, keep the first version boring:

- `inspect_server(server_url)`: read-only endpoint summary.
- `lint_workflow(workflow_json)`: offline lint.
- `audit_models(workflow_json, server_url)`: read-only model reference check.
- `explain_error(error_payload)`: local classifier.
- `resolve_custom_nodes(class_types)`: local map plus unresolved classes.

Approval-required actions should be separate:

- Queue prompt execution.
- Install custom nodes.
- Download models.
- Clear queue/history.
- Delete files.

That separation keeps Codex from "helpfully" running a 14 GB download because a workflow looked lonely.
