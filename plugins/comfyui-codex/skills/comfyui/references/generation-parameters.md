# ComfyUI Generation Parameters

Use this reference when the user asks how seed, steps, CFG, sampler, scheduler, denoise, size, batch, or LoRA/control strengths affect generation.

Primary sources:
- https://docs.comfy.org/development/api-development/workflow-api-format
- https://docs.comfy.org/development/core-concepts/models
- https://www.angry-shark-studio.com/blog/comfyui-tutorial-mastering-generation-parameters/
- https://www.angry-shark-studio.com/blog/comfyui-mistakes-beginners-make/

## Contents

- [Operating Rule](#operating-rule)
- [Seed](#seed)
- [Steps](#steps)
- [CFG](#cfg)
- [Sampler And Scheduler](#sampler-and-scheduler)
- [Denoise](#denoise)
- [Width, Height, And Batch](#width-height-and-batch)
- [Prompt And Negative Prompt](#prompt-and-negative-prompt)
- [LoRA Strength](#lora-strength)
- [ControlNet Strength](#controlnet-strength)
- [Comparison Checklist](#comparison-checklist)

## Operating Rule

Preserve parameters from known-good model templates unless the user is debugging or intentionally tuning. For comparisons, change one parameter at a time and keep seed, model, prompt, sampler, scheduler, and size fixed.

## Seed

Purpose:

- Controls the starting noise/composition.
- Same seed plus same graph/settings should reproduce the same base result.
- Different seeds can produce very different compositions with the same prompt.

Use:

- Random seed for exploration.
- Fixed seed for debugging, comparisons, prompt refinement, and reproducing a good composition.
- Increment/decrement for quickly sampling different compositions while other settings stay fixed.

Agent advice:

- Ask for seed when reproducing a result.
- Keep seed fixed while changing prompt, LoRA strength, CFG, denoise, or upscale steps.
- Do not call seed `+1` a small variation; it is a new noise start.

## Steps

Purpose:

- Number of denoising/refinement passes.
- More steps usually cost more time and hit diminishing returns.

Heuristics:

- Fast previews: 12-20 steps.
- General image generation: 20-35 steps.
- Final/high-detail pass: 30-45 steps when the sampler/model benefits.
- Very high values are rarely worth it without model-specific evidence.

Tuning loop:

1. Fix seed and prompt.
2. Try 20, 30, and 40 steps.
3. Stop increasing when visual improvement stalls.
4. Use model docs/templates when a model family expects a specific range.

## CFG

Purpose:

- Controls how strongly generation follows text conditioning in many SD-style workflows.

Heuristics:

- Lower CFG can be more natural but less literal.
- Higher CFG can follow prompt more aggressively but may create harsh artifacts.
- Many older SD workflows sit around mid single digits to high single digits.
- Some newer model families prefer lower or different guidance patterns; use templates and model docs.

Tuning:

- Keep seed fixed.
- Change CFG in small jumps.
- If image looks overcooked, harsh, or brittle, lower CFG before rewriting prompt.

## Sampler And Scheduler

Purpose:

- Sampler controls the denoising algorithm.
- Scheduler controls how noise levels progress across steps.

Rules:

- Use workflow/model defaults unless the user is comparing samplers.
- Do not change sampler, scheduler, steps, and CFG all at once.
- If a custom workflow has tuned sampler settings, preserve them.

Comparison pattern:

1. Keep seed/prompt/model/size fixed.
2. Change sampler only.
3. Reset, then change scheduler only.
4. Compare speed, texture, contrast, and artifact behavior.

## Denoise

Purpose:

- Controls how much the sampler changes the starting latent/image.
- `1.0` means full generation from noise in txt2img-style workflows.
- Lower values preserve more of the source for img2img, inpaint, outpaint, and hi-res passes.

Heuristics:

- Img2img subtle edit: low to moderate denoise.
- Img2img major restyle: moderate to high denoise.
- Inpaint: enough to repair masked area without destroying context.
- Outpaint: often moderate/high enough to synthesize new area, but mask/conditioning matter.
- Hi-res fix/latent upscale: often below full denoise so structure survives.

If a source image is being ignored, reduce denoise. If the edit cannot change enough, increase it.

## Width, Height, And Batch

Rules:

- Use dimensions appropriate for the model family and VRAM.
- SD1.5-era workflows often start around 512-pixel training scales.
- SDXL/Flux/newer workflows often expect larger pixel counts or family-specific defaults.
- Bad aspect ratios or pixel counts can cause distorted subjects.
- Batch size multiplies memory use.

Troubleshooting:

- OOM: reduce width, height, batch size, frame count, or upscale tile size.
- Weird anatomy/composition: check model family resolution first.
- Inconsistent results: fix seed and dimensions before comparing prompt changes.

## Prompt And Negative Prompt

Prompt:

- Put the desired subject, action, style, composition, and constraints in the positive prompt.
- For image-edit models, write the edit instruction plainly.
- For ControlNet, describe the desired result, not just the control image.

Negative prompt:

- Use only if the workflow/model benefits from it.
- Keep it targeted; giant inherited negative prompts can hide the real issue.
- If negative prompt changes do nothing, verify it is actually wired to sampler `negative`.

## LoRA Strength

Common fields:

- `strength_model`
- `strength_clip`

Rules:

- Verify LoRA matches the base model family.
- Start with moderate strength.
- Stack LoRAs one at a time.
- If composition collapses, lower strengths before changing model or prompt.
- If a LoRA does nothing, check filename, loader wiring, and whether both model/CLIP paths are connected as expected.

## ControlNet Strength

Common fields:

- `strength`
- `start_percent`
- `end_percent`

Rules:

- Match control model to base model family.
- Match preprocessor/control image to the control type.
- Too much strength can make output rigid or ugly.
- Too little strength can make control ineffective.

## Comparison Checklist

For any tuning task:

1. Save the workflow.
2. Fix seed.
3. Fix model files.
4. Fix size.
5. Change one parameter.
6. Queue.
7. Record output and setting.
8. Repeat.

If the user is lost, make a table of experiments instead of dumping parameter theory.
