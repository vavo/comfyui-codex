# Model Routing And Prompting

Use this reference when selecting models, checking model folders, tuning prompt inputs, or mapping loader nodes to files.

Primary sources:
- https://docs.comfy.org/development/core-concepts/models
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/api-development/workflow-api-format

## Source Of Truth

Use runtime evidence before advice:

1. `GET /models` for visible model folder categories.
2. `GET /models/{folder}` for exact filenames.
3. `/object_info` for loader node input names and allowed values.
4. Workflow loader nodes for referenced filenames.
5. Startup logs for failed model discovery or load errors.

Do not claim a model is installed because it exists somewhere on disk. ComfyUI must see it through its configured model paths.

## Loader To Folder Map

| Node class | Input field | Model folder |
| --- | --- | --- |
| `CheckpointLoaderSimple` | `ckpt_name` | `checkpoints` |
| `CheckpointLoader` | `ckpt_name` | `checkpoints` |
| `unCLIPCheckpointLoader` | `ckpt_name` | `checkpoints` |
| `LoraLoader` | `lora_name` | `loras` |
| `LoraLoaderModelOnly` | `lora_name` | `loras` |
| `VAELoader` | `vae_name` | `vae` |
| `ControlNetLoader` | `control_net_name` | `controlnet` |
| `DiffControlNetLoader` | `control_net_name` | `controlnet` |
| `UpscaleModelLoader` | `model_name` | `upscale_models` |
| `CLIPLoader` | `clip_name` | `clip` |
| `DualCLIPLoader` | `clip_name1`, `clip_name2` | `clip` |
| `UNETLoader` | `unet_name` | `diffusion_models` |
| `CLIPVisionLoader` | `clip_name` | `clip_vision` |
| `StyleModelLoader` | `style_model_name` | `style_models` |
| `GLIGENLoader` | `gligen_name` | `gligen` |
| `HypernetworkLoader` | `hypernetwork_name` | `hypernetworks` |

Custom nodes can define their own folders and fields. Use `/object_info` and the node docs when built-in mappings do not cover the class.

## Common Model Roles

- Checkpoint: base model bundle for common stable diffusion workflows.
- Diffusion model / UNet: model backbone for newer separated-model workflows.
- Text encoder / CLIP: turns prompt text into conditioning.
- VAE: encodes/decodes images and latents.
- LoRA: small adapter that modifies model behavior or style.
- ControlNet: guides generation with pose, depth, edges, masks, or other conditioning.
- Upscaler: increases image resolution after generation.
- CLIP vision: image encoding for image-conditioned workflows.
- Embedding: prompt token expansion or concept injection.

Do not force old checkpoint mental models onto newer separated workflows. Some graphs load diffusion model, text encoders, and VAE separately.

## Model Selection Heuristics

Ask for:

- Task: text-to-image, edit, inpaint, ControlNet, upscale, video, audio, or 3D.
- Runtime: local, hosted, Cloud, or partner nodes.
- Available model files from `/models`.
- Required custom nodes.
- VRAM budget.
- Whether quality, speed, fidelity, or style matching matters most.

Use:

- Base checkpoint/diffusion model for the task family.
- Matching VAE/text encoders for separated-model workflows.
- LoRAs only when they match the base model family.
- ControlNet models that match both conditioning type and model family.
- Upscalers after a valid base image exists.

If the user asks for "best model", answer with tradeoffs and what must be installed. "Best" without hardware and task context is just astrology with file extensions.

## Prompt Inputs

Common exposed parameters:

- `prompt`
- `negative_prompt`
- `seed`
- `steps`
- `cfg`
- `sampler_name`
- `scheduler`
- `width`
- `height`
- `batch_size`
- `denoise`
- `filename_prefix`

Prompt text usually sits in `CLIPTextEncode.inputs.text` or a custom prompt node. Negative prompts often use another `CLIPTextEncode` wired to sampler `negative`.

Patch prompt fields without rewiring the graph unless the user asked for a workflow change.

## Prompting Defaults

Stable heuristics:

- Keep the positive prompt concrete and task-specific.
- Put avoidances in negative prompt only when the model/workflow uses one.
- Preserve tuned sampler values from known-good workflows.
- Use fixed seeds for debugging and random seeds for exploration.
- Change one major factor at a time when diagnosing quality.

Model-family caveats:

- Some modern models prefer simpler natural-language prompts.
- Older SD-style checkpoints often respond to tag-like prompts and negative prompts.
- Image-edit models usually need explicit edit instructions plus the source image.
- ControlNet workflows need prompt text and correct conditioning image.

Do not blindly paste a huge negative prompt into every workflow. Sometimes it helps; sometimes it is just decorative technical debt.

## LoRA Guidance

Check:

- LoRA file exists in `loras`.
- LoRA matches base model family.
- Loader is wired into both model and CLIP when the workflow expects it.
- Strength values are reasonable for the LoRA.

Typical exposed values:

- `lora_name`
- `strength_model`
- `strength_clip`

If a LoRA makes outputs worse, lower strength before changing the entire workflow.

## ControlNet Guidance

Check:

- Control model exists in `controlnet`.
- Control type matches conditioning image.
- Preprocessor output is wired correctly.
- Control model matches base model family.
- Strength and start/end percent are not extreme by accident.

Expose:

- `control_image`
- `control_strength`
- `start_percent`
- `end_percent`

ControlNet failures often come from a mismatch between control model, preprocessor, and base model rather than prompt text.

## Extra Model Paths

For manual and portable installs, ComfyUI can load extra model paths from a root-level YAML config. Keep paths generic and do not overwrite Desktop-generated config blindly.

Checks:

- YAML indentation is valid.
- `base_path` exists.
- Folder keys match model categories.
- ComfyUI was restarted after edits.
- `/models/{folder}` shows the added files.

If a model is visible in the filesystem but missing from `/models/{folder}`, debug path config before editing workflow JSON.
