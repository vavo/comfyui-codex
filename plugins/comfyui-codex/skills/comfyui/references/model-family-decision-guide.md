# Model Family Decision Guide

Use this when the user asks which model family, loader, workflow pattern, or prompt style fits a task.

## Official Source Anchors

- Models: https://docs.comfy.org/development/core-concepts/models
- Workflow concept: https://docs.comfy.org/development/core-concepts/workflow
- Server model routes: https://docs.comfy.org/development/comfyui-server/comms_routes
- Startup flags: https://docs.comfy.org/development/comfyui-server/startup-flags

## First Rule

Verify exact installed model filenames with:

```text
GET /models
GET /models/{folder}
```

Model availability changes by install, cloud image, mounted volume, and Manager downloads. This guide is routing logic, not a promise that a model exists.

## Family Routing

| Goal | Common family | Workflow shape | Notes |
| --- | --- | --- | --- |
| Fast general txt2img | SD 1.5-class | Checkpoint loader, CLIP prompt, latent, sampler, VAE decode | Low VRAM, huge custom-node ecosystem, older quality ceiling. |
| Higher quality still images | SDXL-class | SDXL checkpoint, larger latent, SDXL-aware prompting | More VRAM and slower than SD 1.5. |
| Modern prompt following | Flux-class or current transformer family | Separate diffusion/text encoders may appear | Check loader classes and model folder requirements. |
| Image edit/instruct | Edit-focused family | Load image, edit prompt, model-specific conditioning | Do not force txt2img assumptions onto edit workflows. |
| Video generation | Wan/Hunyuan/LTX/current video stack | Text/image conditioning, temporal model, video combine | Often custom nodes plus large model folders. |
| Inpaint/outpaint | Inpaint-capable model or conditioning | Image, mask, denoise, inpaint conditioning | Mask convention and denoise matter more than prompt poetry. |
| Upscale/detail | Upscale model plus optional sampler pass | UpscaleModelLoader or latent upscale, save | Separate "real" upscaler from hi-res second pass. |
| Style/person consistency | LoRA stack | Load base, chain LoRA loaders, prompt, sample | Strength stacking can fight itself. Test incrementally. |
| Pose/layout control | ControlNet/IP-Adapter-like workflow | Control image/adapter, strength, prompt, sampler | Custom nodes and preprocessors are common. |

## Loader to Folder Reminders

Core loader assumptions used by the scripts:

- `CheckpointLoaderSimple.ckpt_name` -> `checkpoints`
- `LoraLoader.lora_name` -> `loras`
- `VAELoader.vae_name` -> `vae`
- `ControlNetLoader.control_net_name` -> `controlnet`
- `UpscaleModelLoader.model_name` -> `upscale_models`
- `UNETLoader.unet_name` -> `diffusion_models`
- `CLIPLoader.clip_name` -> `clip`
- `CLIPVisionLoader.clip_name` -> `clip_vision`

When a family uses split files, audit every loader node. One missing text encoder can look like a model problem while the checkpoint sits there smugly present.

## Decision Questions

Ask:

1. Output type: image, edit, video, audio, 3D, or workflow packaging?
2. Runtime: local GPU, cloud GPU, hosted notebook, or Comfy Cloud?
3. VRAM and time budget?
4. Installed model folders from `/models`.
5. Need custom nodes: ControlNet, IP-Adapter, video combine, segmentation, background removal, face detail?
6. Need reproducibility or creative exploration?

## Prompting by Family

Stable general guidance:

- Keep the main subject and action early.
- Put style, camera, lighting, and quality modifiers after the core subject.
- Use negative prompt sparingly; do not paste a landfill unless the model family expects it.
- For SDXL/modern models, natural language often works better than tag soup.
- For LoRA, include the trigger word only when the LoRA was trained to require it.
- For image edit models, describe the edit operation, not a full replacement scene unless replacement is intended.

## When Codex Should Push Back

Push back when:

- User wants video on tiny VRAM and expects fast local runs.
- User wants LoRA stacking without checking whether LoRAs target the same base family.
- User wants to "fix prompt" when the workflow has missing models or classes.
- User wants API automation but only has editor-format workflow JSON.
- User wants a model recommendation but refuses to say local/cloud/runtime constraints.
