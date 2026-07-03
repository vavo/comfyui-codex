# ComfyUI Workflow Recipes

Use this reference for starter API-format graph patterns. Verify class schemas with `/object_info` and model names with `/models/{folder}` before submitting.

Primary sources:
- https://docs.comfy.org/development/api-development/workflow-api-format
- https://docs.comfy.org/development/comfyui-server/api-examples
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/core-concepts/models

## Text To Image

Core chain:

```text
CheckpointLoaderSimple -> CLIPTextEncode positive/negative
EmptyLatentImage -> KSampler -> VAEDecode -> SaveImage
```

Expose:

- `prompt`
- `negative_prompt`
- `seed`
- `steps`
- `cfg`
- `width`
- `height`
- `filename_prefix`

Minimal API skeleton:

```json
{
  "4": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": {
      "ckpt_name": "model.safetensors"
    }
  },
  "5": {
    "class_type": "EmptyLatentImage",
    "inputs": {
      "width": 512,
      "height": 512,
      "batch_size": 1
    }
  },
  "6": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "clip": ["4", 1],
      "text": "a clean product photo on a neutral background"
    }
  },
  "7": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "clip": ["4", 1],
      "text": "blurry, low quality"
    }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 123456,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": ["4", 0],
      "positive": ["6", 0],
      "negative": ["7", 0],
      "latent_image": ["5", 0]
    }
  },
  "8": {
    "class_type": "VAEDecode",
    "inputs": {
      "samples": ["3", 0],
      "vae": ["4", 2]
    }
  },
  "9": {
    "class_type": "SaveImage",
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": ["8", 0]
    }
  }
}
```

## Image To Image

Core change from txt2img:

```text
LoadImage -> VAEEncode -> KSampler.latent_image
```

Key input:

- `KSampler.inputs.denoise` below `1` preserves more of the source image.

Expose:

- `image`
- `prompt`
- `negative_prompt`
- `denoise`
- `seed`
- `steps`

API integration usually needs `POST /upload/image` first, then `LoadImage.inputs.image` references the uploaded filename.

## Inpaint

Core chain:

```text
LoadImage + mask -> VAEEncodeForInpaint or inpaint-specific conditioning -> KSampler -> VAEDecode -> SaveImage
```

Expose:

- `image`
- `mask`
- `prompt`
- `negative_prompt`
- `denoise`
- `seed`

Inpaint graphs vary by model family and custom nodes. Prefer a known-good template for the target model.

## LoRA

Core chain:

```text
CheckpointLoaderSimple -> LoraLoader -> CLIPTextEncode/KSampler
```

Loader field:

- `LoraLoader.inputs.lora_name` maps to `models/loras`.

Expose:

- `lora_name` only when the user should choose files.
- `strength_model`
- `strength_clip`

Default caution:

- Start moderate, then tune. Very high strength can overpower the base model or break composition.

## ControlNet

Core chain:

```text
ControlNetLoader + conditioning image/preprocessor -> ApplyControlNet -> KSampler
```

Loader field:

- `ControlNetLoader.inputs.control_net_name` maps to `models/controlnet`.

Expose:

- `control_image`
- `control_strength`
- `start_percent`
- `end_percent`

Always verify the control model matches the base model family and conditioning type.

## Upscale

Common routes:

- Pixel upscale: `UpscaleModelLoader -> ImageUpscaleWithModel -> SaveImage`
- Latent upscale: latent resize/upscale before another sampler pass

Loader field:

- `UpscaleModelLoader.inputs.model_name` maps to `models/upscale_models`.

Expose:

- `upscale_model`
- `scale`
- `filename_prefix`

Use pixel upscale for simple finishing. Use latent upscale when the workflow intentionally re-generates details.

## Submit And Retrieve Result

1. Validate workflow JSON offline.
2. Validate classes with `/object_info`.
3. Validate model names with `/models/{folder}`.
4. `POST /prompt`.
5. Capture `prompt_id`.
6. Wait for completion through WebSocket or `/history/{prompt_id}`.
7. Fetch image bytes from `/view`.

History output shape varies by output node, so read the actual `outputs` object instead of assuming image filenames sit in one fixed field.
