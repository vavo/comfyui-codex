# ComfyUI API Integration

Use this reference when the task involves calling ComfyUI from code, checking endpoint behavior, monitoring generation, retrieving outputs, or choosing between local Server API and Comfy Cloud API.

For a compact route table, read `api-endpoints.md` first. Use this file for integration strategy and operational loops.

Primary sources:
- https://docs.comfy.org/development/api-development/overview
- https://docs.comfy.org/development/comfyui-server/comms_overview
- https://docs.comfy.org/development/comfyui-server/comms_routes
- https://docs.comfy.org/development/comfyui-server/comms_messages
- https://docs.comfy.org/development/comfyui-server/api-examples
- https://docs.comfy.org/development/cloud/openapi
- https://docs.comfy.org/development/comfyui-server/api-key-integration
- https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw

## Choose The API

Use local ComfyUI Server API when the user controls the machine, models, custom nodes, and GPU. Default base URL is usually `http://127.0.0.1:8188`; launching ComfyUI starts the HTTP server. For headless local use, `python main.py --disable-auto-launch` starts without opening the browser.

Use Comfy Cloud API when the user wants managed GPUs and subscription-backed hosted execution. Cloud uses `https://cloud.comfy.org`, `X-API-Key`, and WebSocket updates at `wss://cloud.comfy.org/ws?clientId={uuid}&token={api_key}`. Treat the Cloud OpenAPI spec as experimental unless the docs say otherwise.

Both local and Cloud use API-format workflows. Do not submit regular UI save-format JSON unless the endpoint explicitly accepts it.

Agent-Kit's useful bias is local-first execution: the agent should discover the user's actual ComfyUI server, hardware, model paths, and templates before picking a graph. OpenClaw's useful bias is workflow-as-skill execution: hide graph internals behind stable parameters, preflight dependencies, then submit/poll/present results.

## Local Server Routes

Useful read-only checks:

- `GET /system_stats`: Python, device, and VRAM context.
- `GET /object_info`: all node class definitions and input metadata.
- `GET /object_info/{node_class}`: one node definition.
- `GET /models`: model folder categories.
- `GET /models/{folder}`: model filenames visible to a loader category.
- `GET /queue`: pending/running queue state.
- `GET /history/{prompt_id}`: outputs and execution results for one prompt.
- `GET /view?filename=...&subfolder=...&type=...`: retrieve saved output bytes.

Useful write or execution routes:

- `POST /prompt`: validate and queue an API-format workflow.
- `POST /queue`: clear pending/running queue items.
- `POST /interrupt`: stop the current execution.
- `POST /free`: request model unload/free-memory behavior.
- `POST /upload/image`: upload an input image for `LoadImage` style workflows.

## Submit And Monitor

For quick smoke tests, `POST /prompt` with a JSON body containing `prompt`. For integrations users will actually rely on, add a `client_id`, open `/ws?clientId=<uuid>`, queue the prompt, wait for execution messages, then read `/history/{prompt_id}` and fetch images through `/view`.

Typical local payload shape:

```json
{
  "prompt": {
    "3": {
      "class_type": "KSampler",
      "inputs": {
        "seed": 123,
        "model": ["4", 0]
      }
    }
  },
  "client_id": "uuid-generated-by-client"
}
```

The `/prompt` response should include a `prompt_id` and queue `number` when accepted. If validation fails, expect `error` and `node_errors`; read those before rewriting the workflow.

For chat agents, prefer an interactive submit/status pattern over a hidden shell loop:

1. Submit once and capture `prompt_id`.
2. Poll status/history as separate tool calls.
3. Tell the user when work is queued/running if it takes time.
4. On success, fetch outputs using the filenames, subfolders, and types returned by history.
5. On failure, map the error back to node ID, class, and input.

For scripts or CI, a blocking wrapper is fine. Keep that wrapper thin: load API workflow JSON, apply explicit overrides like `6.text` or `3.seed`, `POST /prompt`, wait for `/history/{prompt_id}`, then download `/view` outputs.

## WebSocket Events

Useful built-in message types include:

- `status`: queue state.
- `execution_start`: prompt execution begins.
- `execution_cached`: cached nodes will be skipped.
- `executing`: current node; `node` can become `None` when execution is complete.
- `progress`: node progress for nodes that report it.
- `executed`: UI payload from a node, not a generic "all nodes completed" signal.
- `execution_error`: failure details.
- `execution_success`: all nodes completed.

Do not assume every node emits `executed`. Use `executing`, `execution_success`, and `/history/{prompt_id}` for robust completion handling.

## Partner Nodes And Keys

Local workflows can include paid Partner Nodes. When calling headless/API flows, include the Comfy account key in `extra_data.api_key_comfy_org` only when needed. Redact it in logs, terminal output, tickets, screenshots, commits, and examples.

Cloud API authentication uses `X-API-Key`. Do not confuse that header with local unauthenticated Server API behavior or partner-node `extra_data`.

## Common API Failures

- Connection refused: ComfyUI server is not running, wrong host/port, container port not exposed, or notebook proxy URL is wrong.
- 400/validation failure: wrong workflow format, unknown `class_type`, invalid input value, missing model, or missing custom node.
- WebSocket connects but no useful events: mismatched `client_id`, wrong server URL, proxy stripping WebSocket upgrade, or code waiting for the wrong event type.
- `/history/{prompt_id}` empty: prompt failed early, wrong prompt ID, or history was cleared.
- `/view` 404: wrong filename/subfolder/type from history, output was not saved, or using `SaveImageWebsocket` instead of `SaveImage`.

## Agent-Safe API Contract

When turning a workflow into a callable skill or command, expose business parameters instead of graph internals:

- `prompt`, `negative_prompt`, `seed`, `width`, `height`, `steps`, `cfg`, `image`, `mask`, `filename_prefix`.
- Keep node IDs and raw input names in the implementation layer.
- Validate args as JSON before submission.
- Run a dependency preflight before first execution: installed node classes, missing custom nodes, and referenced model files.
- For multiple ComfyUI servers, route by explicit server ID plus health/VRAM facts, not by vibes and optimism, the industry's cheapest fuel.

## Integration Checklist

1. Confirm base URL and API flavor.
2. Fetch `/system_stats` and `/object_info`.
3. Confirm the workflow is API format.
4. Compare workflow `class_type` values against `/object_info`.
5. Check model filenames with `/models/{folder}` for every loader node.
6. Queue one minimal prompt and capture `prompt_id`.
7. Monitor via WebSocket or poll `/history/{prompt_id}`.
8. Retrieve outputs from history with `/view` or decode WebSocket image frames if using WebSocket image output.
