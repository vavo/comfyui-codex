# ComfyUI Workflow Tutorials

Use this reference when the user asks for step-by-step tutorials for common workflow types. These are teaching templates, not guaranteed plug-and-play graphs for every model family.

Primary sources:
- https://docs.comfy.org/development/core-concepts/workflow
- https://docs.comfy.org/development/api-development/workflow-api-format
- https://docs.comfy.org/development/core-concepts/models
- https://stable-diffusion-art.com/comfyui/
- https://www.angry-shark-studio.com/blog/comfyui-tutorial-understanding-canvas/
- https://www.angry-shark-studio.com/blog/comfyui-tutorial-mastering-generation-parameters/

## Contents

- [Tutorial Method](#tutorial-method)
- [Text To Image](#text-to-image)
- [Image To Image](#image-to-image)
- [Inpaint](#inpaint)
- [Outpaint](#outpaint)
- [Upscale](#upscale)
- [LoRA Single](#lora-single)
- [LoRA Stacking](#lora-stacking)
- [ControlNet](#controlnet)
- [Text To Video](#text-to-video)
- [Image To Video](#image-to-video)
- [Tutorial Output Template](#tutorial-output-template)

## Tutorial Method

For every tutorial:

1. Start from a known-good template or basic workflow.
2. Identify required models and custom nodes.
3. Put models in the right folders.
4. Load workflow in the GUI first when teaching a human.
5. Export API workflow when automating.
6. Validate with `workflow_lint.py`.
7. Verify node classes with `/object_info`.
8. Verify model filenames with `/models/{folder}`.
9. Queue one small test.
10. Tune one parameter at a time.

## Text To Image

Goal: generate from prompt only.

Core graph:

```text
CheckpointLoaderSimple
  -> CLIPTextEncode positive/negative
  -> KSampler
EmptyLatentImage -> KSampler
KSampler -> VAEDecode -> SaveImage
```

Required:

- Checkpoint or separated model stack.
- VAE, usually from checkpoint output or separate VAE loader.
- Prompt and optional negative prompt.

User steps:

1. Load default image generation workflow or a known-good txt2img template.
2. Select a checkpoint/model.
3. Set width, height, and batch size in the latent node.
4. Enter prompt and negative prompt.
5. Set seed, steps, CFG, sampler, scheduler.
6. Queue once.
7. If it works, save the workflow JSON.
8. If automating, export API format and run `workflow_lint.py`.

Common failures:

- No model in checkpoint dropdown.
- Wrong resolution for model family.
- Missing VAE or washed-out colors.
- No output node.

## Image To Image

Goal: transform an input image with prompt guidance.

Core graph:

```text
LoadImage -> VAEEncode -> KSampler.latent_image
Checkpoint/CLIP prompt path -> KSampler
KSampler -> VAEDecode -> SaveImage
```

Required:

- Source image.
- Model/checkpoint.
- Prompt and optional negative prompt.
- Denoise value below full generation when preserving source structure.

User steps:

1. Load an img2img workflow.
2. Upload or select source image in `LoadImage`.
3. Select model.
4. Enter edit/restyle prompt.
5. Set denoise.
6. Queue.
7. If the source image is ignored, lower denoise.
8. If the image barely changes, raise denoise.

API note:

- Upload image with `/upload/image`.
- Set `LoadImage.inputs.image` to the uploaded filename.

## Inpaint

Goal: regenerate a masked area while preserving unmasked context.

Core graph:

```text
LoadImage + mask -> VAEEncodeForInpaint or inpaint conditioning
Prompt conditioning -> KSampler
KSampler -> VAEDecode -> SaveImage
```

Required:

- Source image.
- Mask.
- Inpaint-capable workflow for the model family.
- Prompt describing desired masked result.

User steps:

1. Load an inpaint template.
2. Upload image.
3. Create or load mask.
4. Prompt the replacement area, not the whole world unless required.
5. Tune denoise.
6. Queue low-resolution/small test first.
7. Check mask edge behavior.

Common failures:

- Mask is inverted.
- Mask is not connected.
- Denoise too low to repair area.
- Denoise too high destroys context.
- Inpaint workflow does not match model family.

## Outpaint

Goal: extend an image beyond its original border.

Core pattern:

```text
LoadImage -> pad/expand canvas -> mask new area
Image + mask -> inpaint/outpaint conditioning
Prompt -> sampler -> decode/save
```

Required:

- Source image.
- Canvas expansion/padding node.
- Mask for the new border area.
- Inpaint/outpaint-compatible workflow.

User steps:

1. Load an outpaint template for the target model.
2. Expand canvas in the desired direction.
3. Mask only the new/empty area and a small overlap into the original image.
4. Prompt what should continue into the new area.
5. Use enough denoise to synthesize the extension.
6. Queue.
7. If the seam is visible, increase overlap or adjust mask blur/feather when available.

Common failures:

- No overlap with original image.
- Prompt contradicts existing scene.
- Denoise too low for empty canvas.
- Workflow uses custom nodes that are missing.

## Upscale

Goal: increase resolution after a valid base image exists.

Three common routes:

- **AI/pixel upscale**: `UpscaleModelLoader -> ImageUpscaleWithModel -> SaveImage`.
- **Latent hi-res pass**: upscale latent/image, sample again with lower denoise.
- **Tile/Ultimate-style upscale**: split into tiles, upscale/detail, recombine; usually custom-node dependent.

AI upscale steps:

1. Put upscaler model in `models/upscale_models`.
2. Add `UpscaleModelLoader`.
3. Insert `ImageUpscaleWithModel` between decoded image and `SaveImage`.
4. Connect model output to upscaler.
5. Connect image through upscaler into save node.
6. Queue and compare with original.

Hi-res steps:

1. Generate a good base image.
2. Upscale latent or image.
3. Run a second sampler pass with lower denoise.
4. Decode and save.
5. Reduce size/tile if VRAM fails.

## LoRA Single

Goal: apply one trained style/subject adapter.

Core graph:

```text
CheckpointLoaderSimple -> LoraLoader -> KSampler model
LoraLoader CLIP -> CLIPTextEncode
```

Steps:

1. Put LoRA file in `models/loras`.
2. Select matching base model family.
3. Add or use `LoraLoader`.
4. Select `lora_name`.
5. Set `strength_model` and `strength_clip`.
6. Queue with fixed seed.
7. Tune strengths before changing prompt.

## LoRA Stacking

Goal: apply multiple LoRAs in sequence.

Core graph:

```text
CheckpointLoaderSimple
  -> LoraLoader A
  -> LoraLoader B
  -> sampler/prompt consumers
```

Rules:

- Chain LoRA loaders so each receives the previous model/CLIP output.
- Verify all LoRAs match the same base model family.
- Start with one LoRA working, then add the next.
- Lower strengths when styles fight or composition degrades.
- Keep seed fixed while comparing stack order and strength.

User steps:

1. Build txt2img with one LoRA.
2. Save working version.
3. Add second `LoraLoader` after the first.
4. Select second LoRA.
5. Queue same seed.
6. Tune strengths one LoRA at a time.
7. Save as a new workflow version.

## ControlNet

Goal: guide generation with structure from an image, pose, edge, depth, mask, or similar signal.

Core graph:

```text
Control image/preprocessor -> ApplyControlNet
ControlNetLoader -> ApplyControlNet
Prompt conditioning -> ApplyControlNet -> sampler positive
```

Steps:

1. Pick a ControlNet model matching base model family and control type.
2. Put model in `models/controlnet`.
3. Load or preprocess control image.
4. Apply ControlNet to conditioning.
5. Tune strength and start/end percent.
6. Queue with fixed seed.

Common failures:

- Control model family mismatch.
- Preprocessor output does not match control model.
- Strength too high or too low.
- Required custom preprocessor nodes missing.

## Text To Video

Goal: generate video from prompt.

Reality check:

- This is model-family and custom-node dependent.
- Workflows vary widely across Wan, AnimateDiff, LTX, Hunyuan, SVD-style, and other video stacks.
- Treat current templates/model docs as required.

Tutorial pattern:

1. Identify video model family and required custom nodes.
2. Verify model files and folders.
3. Start from an official or known-good template.
4. Set prompt, frame count, resolution, seed, and motion controls.
5. Run a short/low-resolution smoke test.
6. Inspect VRAM and output nodes.
7. Increase frames/resolution only after the smoke test works.

Common failures:

- Missing video custom nodes.
- Missing text encoder, VAE, diffusion model, or motion module.
- Frame count too high for VRAM.
- Output combine/save node missing.
- Prompt controls split across positive prompt, motion prompt, and image/video conditioning nodes.

## Image To Video

Goal: animate a source image.

Pattern:

1. Load source image.
2. Encode image through the model-specific image/video conditioning path.
3. Set prompt/motion controls.
4. Set frame count and resolution.
5. Generate short smoke test.
6. Save through video combine/save node.

If the workflow asks for a start frame and errors that the image does not exist, verify upload path, `LoadImage` filename, and API upload flow before changing model settings.

## Tutorial Output Template

When answering a tutorial request, use this shape:

```text
Goal:
Required models/custom nodes:
GUI steps:
API/export steps:
Parameters to expose:
Validation:
Common failures:
Next safe tweak:
```

Keep explanations practical. A tutorial should get the user to one working generation, not make them pass a graduate seminar in latent diffusion.
