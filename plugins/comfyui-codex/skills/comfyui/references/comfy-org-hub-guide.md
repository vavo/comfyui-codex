# Comfy.org Learning, Agent, MCP, and Workflow Hub

Use this reference for Comfy.org learning paths, Comfy Agent/MCP choices, and current
workflow-gallery routing. The gallery and model catalog change frequently, so
use the linked page for the current inventory and treat the workflow-specific
details below as routing guidance, not a frozen guarantee.

Primary sources:
- Learning hub: https://comfy.org/learning
- MCP product guide: https://comfy.org/mcp
- Workflow gallery: https://comfy.org/hub/workflows/
- Comfy Agent Tools docs: https://docs.comfy.org/agent-tools
- Comfy MCP docs: https://docs.comfy.org/agent-tools/mcp.md

## Contents

- [Learning Hub](#learning-hub)
- [Comfy Agent](#comfy-agent)
- [MCP Choice](#mcp-choice)
- [MCP Capabilities](#mcp-capabilities)
- [Workflow Gallery](#workflow-gallery)
- [LTX-2.5 Workflows](#ltx-25-workflows)
- [MiniMax H3 Workflows](#minimax-h3-workflows)
- [Agent Routing Checklist](#agent-routing-checklist)

## Learning Hub

The Learning hub is organized by discipline and workflow type. Use it as a
human-friendly teaching index, then use the local references and scripts in
this skill for precise execution or debugging.

### Beginner sequence

Recommend this order for a new user:

1. **Node graph basics**: learn nodes, links, loaders, conditioning, sampling,
   decoding, preview, and save nodes.
2. **Text to image and image to image**: learn the basic generation loop and
   how an input image changes the latent path.
3. **LoRA, ControlNet, and style transfer**: add one conditioning mechanism at
   a time and keep a fixed seed while comparing changes.
4. **Inpainting, outpainting, and upscaling**: learn masks, canvas expansion,
   denoise, and post-processing.
5. **Image to video and motion control**: only after the image workflow and
   model/file routing are understood.

The page currently groups material into Basics, VFX, Animations, and Ads. Its
examples include sky replacement, clean plates, deaging, frame adjustments,
character sheets, keyframe exploration, compositing, moodboards, storyboards,
product photography, talent casting, and B-roll. These are useful use-case
labels when choosing a template, but they do not replace checking the graph's
actual node and model dependencies.

### Teaching rule

When teaching from the hub:

1. Start with a linked tutorial or template instead of an empty canvas.
2. Explain the graph from input to output: source, model, conditioning,
   sampler/generator, decode, and save.
3. Run one small test before changing multiple parameters.
4. Save the working graph before adding custom nodes or extra model stages.
5. Export API format before asking an agent or script to run the workflow.

## Comfy Agent

Comfy Agent is ComfyUI's built-in assistant for understanding, building,
editing, and running a selected workflow while the user can see the canvas.
The official agent-tools matrix currently describes it as generally available
on Comfy Cloud, with Comfy Desktop support coming later.

Route to Comfy Agent when the user wants canvas-aware help with the workflow
already open in ComfyUI. It requires a Comfy account and currently works with
Cloud models and Cloud-supported custom nodes. It is a different lane from
Comfy MCP: MCP connects an external agent, while Comfy Agent is inside the
ComfyUI product. For local files, private custom nodes, or reproducible scripts,
use local MCP or the local Server API instead.

## MCP Choice

Comfy MCP lets an MCP-compatible agent search, build, submit, monitor, and
retrieve Comfy workflows. Choose the connection from the runtime and the
user's authorization boundary.

| Need | Choose | Connection and boundary |
| --- | --- | --- |
| No local GPU or simplest first run | Comfy Cloud MCP | Add `https://cloud.comfy.org/mcp` as a remote MCP server/custom connector and authenticate with OAuth when prompted. Workloads run on Comfy Cloud GPUs. |
| Existing local ComfyUI | Local Comfy MCP | The client launches the open-source `comfy-mcp` server over stdio. It drives the user's own ComfyUI, models, custom nodes, and GPU. |
| Terminal scripts, batches, or CI | Comfy CLI | Use the terminal-native CLI path documented by Comfy. Keep credentials out of shell history and logs. |
| A coding agent already connected to local ComfyUI | Local Server API | Use the existing `/system_stats`, `/object_info`, `/models`, `/prompt`, `/history`, `/view`, and `/ws` contract. MCP is optional. |

The cloud and local connections can be used side by side. They authenticate
independently: cloud uses account authentication, while local operation does
not require an account for the user's own ComfyUI. Partner models can require
Comfy account authentication or credits even from a local setup.

For new users, Cloud is usually the shortest path. Choose local when the user
already has ComfyUI, needs local files/custom nodes, or is working primarily in
a coding agent. Large open-weight models may be impractical on an Apple GPU;
route those jobs to a suitable cloud or hosted GPU when the user agrees.

## MCP Capabilities

Once connected, an agent can expose these workflows as natural-language tools:

- Generate images, video, audio, and 3D assets.
- Upscale images, remove backgrounds, and perform image edits.
- Search models, nodes, rankings, and workflow templates.
- Read, submit, monitor, save, and rerun workflow graphs.
- Queue batches and retrieve every result.
- Upload/download inputs and outputs where the client supports it.
- Turn a workflow into a shareable app with only selected inputs exposed.

### Cost and approval boundary

- Local runs on the user's hardware are free apart from the user's own
  infrastructure. Partner models may consume account credits.
- Cloud connection/search can be free, but cloud generation uses Cloud credits
  and requires a subscription tier according to the current product page.
- Ask for confirmation immediately before paid generations, model downloads,
  large batches, or other costly actions.
- Never put OAuth tokens, API keys, notebook URLs, or account credentials in a
  workflow fixture, README, issue, screenshot, or log.

### Output locations

- Cloud outputs land in the Comfy Cloud asset library and can be downloaded or
  reopened on the canvas.
- Local outputs land in the configured ComfyUI output folder and can be copied
  elsewhere by the agent after the user specifies the destination.

## Workflow Gallery

The gallery is a discovery surface, not a static dependency lockfile. It
supports search and separates node graphs from Comfy Apps. Use the gallery to
find a task-shaped starting point, then inspect the downloaded workflow before
execution.

Gallery workflow checklist:

1. Confirm the media type: image, video, audio, 3D, edit, upscale, or app.
2. Read the workflow description for input count, output type, duration,
   resolution, frame rate, and audio behavior.
3. Download the workflow and identify whether it is API or editor format.
4. Check model files, partner-node requirements, and custom-node classes.
5. Validate offline with `workflow_lint.py`.
6. Validate live with `/object_info` and `/models/{folder}`.
7. Run a small test before committing to a long video or batch.

The gallery inventory is dynamic and can change as templates are added,
removed, or reclassified. Do not cache or quote a workflow count as a stable
capability claim.

## LTX-2.5 Workflows

LTX-2.5 appears in the gallery for image-to-video, text-to-video, first/last
frame-to-video (FLF2V), and Pro variants. Use the gallery search for the latest
template rather than hard-coding a filename or node UUID.

### LTX-2.5 image to video

Reference workflow: https://comfy.org/workflows/b37902cee452-b37902cee452/

The featured workflow is a deliberately small image-to-video pipeline:

```text
LoadImage -> ResolutionSelector -> LTX-2.5 generator -> SaveVideo
```

Operational facts from the template:

- Input is one still image.
- `ResolutionSelector` preserves aspect ratio and selects model-friendly
  dimensions that are multiples of 32.
- The LTX-2.5 generator creates a coherent motion sequence from the image.
- `SaveVideo` writes an MP4.
- Duration/frame count, FPS, and motion controls are the first parameters to
  expose in an agent wrapper.
- The template is presented as locally deployable, so verify the installed
  LTX stack and VRAM before assuming local execution is practical.

The workflow description presents LTX-2.5 as a keyframes-first pixel-diffusion
pipeline intended to preserve subject identity, lighting, and scene structure
while adding motion. Treat that as model/template guidance; judge stability
from the actual output and keep the input frame, seed, resolution, and duration
recorded for reproducibility.

### LTX-2.5 routing

- Start with image-to-video when the user has a strong source frame and wants
  controlled motion.
- Use text-to-video when there is no source image and the prompt should define
  the scene.
- Use FLF2V when the user can provide both a starting and ending frame and
  wants a directed transition.
- Use a Pro or Partner workflow only after checking its account, node, and
  model requirements.
- Keep frame count and resolution modest for the first smoke test. Video memory
  grows with spatial size, temporal length, and model stack.

## MiniMax H3 Workflows

MiniMax H3 is represented in the gallery as text-to-video, image-to-video, and
reference-to-video workflows. The product pages describe it as an omni-modal
generator that can synthesize video and native stereo audio in one pass.

### MiniMax H3 text to video

Reference: use the current MiniMax H3 text-to-video card from the [workflow
gallery](https://comfy.org/hub/workflows/). The older direct route is volatile
and has returned 404 during live checks.

Use this when the user has no input files:

- One text prompt produces one video output.
- The template describes roughly 15 seconds at up to 2K and 24 FPS; verify
  current limits in the downloaded workflow or live deployment.
- Native stereo audio can include voice, sound effects, and music.
- The workflow uses MiniMax H3 video and audio VAEs and `SaveVideo` multiplexes
  the result into one MP4.
- Resolution presets are constrained to model-valid dimensions and multiples
  of 32. Examples shown by the template include `960x544`, `1152x640`, and
  `1216x672`.

Prompting should specify subject, action, camera movement, pacing, environment,
and desired audio cues. Keep the first prompt short enough to isolate model
behavior. If audio is unwanted, check the workflow's audio path and current
node options before assuming the output can be made silent by prompt wording.

### MiniMax H3 image to video

Reference workflow: https://comfy.org/workflows/a781503cf508-a781503cf508/

Use this when a still image should define the subject and overall style:

- One input image produces one video output.
- Optional text or reference media can steer motion, style, or sound.
- `GetImageSize`, a size-preserving image group, `ResolutionSelector`, and
  `ImageScaleToTotalPixels` keep aspect ratio and model-friendly pixel budgets
  under control.
- The generated MP4 can contain video plus model-generated audio.
- The current template names these model assets:
  `minimax_h3_fl2va_pruned_int8_convrot.safetensors` for `UNETLoader`,
  `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` for `CLIPLoader` with
  `type: minimax`, `minimax_h3_video_vae_fp16.safetensors` for the video VAE,
  and `minimax_h3_audio_vae_fp32.safetensors` for the audio VAE.
- For a local run, verify these exact filenames through `/models` and the live
  `/object_info` schema. The gallery's prepared Cloud workflow is not a promise
  that every asset or node is available in a local install.

### MiniMax H3 reference to video

Reference workflow: https://comfy.org/workflows/46a303cbccf9-46a303cbccf9/

Use this when identity, motion, camera, style, or voice must be guided by
multiple references:

- The template accepts a text prompt, up to nine reference images, three short
  reference videos, and three audio clips.
- It produces one MP4 with native stereo audio in a single generation pass.
- The product page describes output up to 2K, 24 FPS, and roughly 15 seconds;
  confirm current limits before promising them.
- A seeded noise/sampling path is used for reproducible comparisons when the
  same inputs and settings are retained.
- Resolution selection remains subject to aspect-ratio and multiple-of-32
  constraints.

Choose references by role instead of uploading a random pile: identity images
for appearance, video for motion, and audio for voice or sound. Fewer strong
references are easier to diagnose than a full reference dump.

### MiniMax H3 preflight

Before a local run, verify:

1. The required H3 generator/custom node class exists in `/object_info`.
2. The current H3 model stack exists in the expected folders: diffusion model,
   CLIP/text encoder, video VAE, and audio VAE.
3. The selected resolution and duration fit available VRAM and disk space.
4. The user wants audio and has authorized any partner/cloud cost.
5. `SaveVideo` or the equivalent output node is connected.

If a model or generator is hosted through a partner integration, use the
workflow's current authentication and billing instructions. Do not substitute
an open-weight local model merely because the node name looks similar.

## Agent Routing Checklist

For a request mentioning one of these pages:

1. Identify whether the user wants to learn, discover a template, use Comfy Agent, connect MCP,
   run locally, or run in the cloud.
2. Route learning requests to the beginner sequence and the matching local
   tutorial reference.
3. Route cloud requests to Comfy Cloud MCP and state the authentication/cost
   boundary before execution.
4. Route local requests to `comfy-mcp` or the local Server API based on the
   client's available tools.
5. For LTX-2.5 or MiniMax H3, start from the gallery template and audit its
   exact node classes, model files, dimensions, audio/video outputs, and format.
6. Use `workflow_lint.py`, `model_audit.py`, and `comfy_doctor.py` before a
   costly or long-running job.
7. Record the source URL, workflow filename/ID, model filenames, seed, prompt,
   dimensions, FPS, duration, and output path in the run summary.
