# ComfyUI API Endpoints

Use this reference for stable local ComfyUI Server API route shape. Verify exact payload details against the target server when possible.

Primary sources:
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/comfyui-server/comms_messages
- https://docs.comfy.org/development/comfyui-server/api-examples
- https://docs.comfy.org/development/cloud/openapi
- https://docs.comfy.org/development/comfyui-server/api-key-integration

## Local Server Defaults

- Default base URL: `http://127.0.0.1:8188`
- Default WebSocket: `ws://127.0.0.1:8188/ws?clientId=<uuid>`
- API workflow submission route: `POST /prompt`
- Source of truth for node classes and inputs: `GET /object_info`
- Source of truth for visible model names: `GET /models/{folder}`

Local Server API is normally unauthenticated. Comfy Cloud API uses Cloud authentication and should be treated as a separate API flavor.

## Endpoint Map

| Route | Method | Use | Notes |
| --- | --- | --- | --- |
| `/` | GET | Load web UI | Useful as a browser reachability check |
| `/ws` | WS | Real-time queue/execution messages | Match `clientId` with prompt payload |
| `/system_stats` | GET | Python, devices, VRAM, system facts | First runtime evidence check |
| `/features` | GET | Server feature/capability info | Useful for UI/client compatibility |
| `/extensions` | GET | Frontend extensions with web directories | Can hint at installed UI extensions |
| `/object_info` | GET | All node class definitions | Validate workflow classes and inputs |
| `/object_info/{node_class}` | GET | One node definition | Use for targeted schema checks |
| `/models` | GET | Available model folder categories | Follow with `/models/{folder}` |
| `/models/{folder}` | GET | Model names visible in one folder | Compare exact filenames |
| `/embeddings` | GET | Available embeddings | Prompt/text-encoder related checks |
| `/workflow_templates` | GET | Workflow template map | Useful for template-first workflow building |
| `/prompt` | GET | Queue/execution info | Do not confuse with submit |
| `/prompt` | POST | Validate and queue API workflow | Returns `prompt_id` and `number` or validation errors |
| `/queue` | GET | Running/pending queue state | Safe status check |
| `/queue` | POST | Clear/delete queue entries | Mutating; confirm intent |
| `/history` | GET | Queue history | Use for recent outputs |
| `/history/{prompt_id}` | GET | One prompt result | Primary output metadata source |
| `/history` | POST | Clear/delete history entries | Mutating; confirm intent |
| `/view` | GET | Retrieve output/input/temp file bytes | Use filename/subfolder/type from history |
| `/view_metadata` | GET | Retrieve model metadata | Useful for model inspection |
| `/upload/image` | POST | Upload input image | Mutating; needed for img2img/inpaint |
| `/upload/mask` | POST | Upload input mask | Mutating; needed for inpaint |
| `/interrupt` | POST | Stop current execution | Mutating; confirm intent |
| `/free` | POST | Unload/free memory | Mutating runtime state |
| `/userdata` and `/v2/userdata` | GET/POST/DELETE | User data file access | Treat as filesystem-affecting |

## Submit Loop

1. Generate a `client_id`.
2. Open WebSocket with that `client_id` when progress is needed.
3. Submit an API-format workflow with `POST /prompt`.
4. Capture `prompt_id`.
5. Watch WebSocket messages or poll `/history/{prompt_id}`.
6. Fetch outputs from `/view` using history metadata.

Minimal submit payload:

```json
{
  "prompt": {
    "1": {
      "class_type": "SaveImage",
      "inputs": {
        "images": ["2", 0],
        "filename_prefix": "ComfyUI"
      }
    }
  },
  "client_id": "uuid-generated-by-client"
}
```

The workflow under `prompt` must be API format. If validation fails, read `error` and `node_errors` before changing anything.

## WebSocket Messages

Expect JSON message types such as:

- `status`: queue/system status.
- `execution_start`: prompt execution started.
- `execution_cached`: cached nodes skipped.
- `executing`: current node; `node` can be `null` when complete.
- `progress`: node progress.
- `executed`: a node completed and may include UI payload.
- `execution_error`: failure details.
- `execution_success`: prompt execution completed.

Do not rely on one event type alone. Use WebSocket for progress and `/history/{prompt_id}` for final output metadata.

## Cloud Notes

Use Cloud docs/OpenAPI for current Cloud endpoints. Do not assume local unauthenticated routes, local files, or local model folders exist in Cloud. Cloud API uses API keys; redact `X-API-Key` and related account tokens.

## Failure Map

| Symptom | Likely boundary | First check |
| --- | --- | --- |
| Connection refused | Server not running or wrong URL | Browser and `/system_stats` |
| 404 on `/view` | Wrong file metadata | Use exact history filename/subfolder/type |
| Unknown `class_type` | Missing custom node | Compare workflow classes to `/object_info` |
| Missing model | Wrong folder/name | Compare loader value to `/models/{folder}` |
| WebSocket hangs | URL/proxy/client ID issue | Direct local WebSocket and matching `client_id` |
| `/history` empty | Prompt failed, wrong ID, or history cleared | Prompt response and server log |
