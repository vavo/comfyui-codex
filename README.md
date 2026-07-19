# ComfyUI Codex (Codex's ComfyUI Operator)

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-vavo-5F7FFF?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/vavo) [![Sponsor on GitHub](https://img.shields.io/badge/Sponsor%20on-GitHub-24292F?style=for-the-badge&logo=github)](https://github.com/sponsors/vavo) [![Support on Patreon](https://img.shields.io/badge/Support%20on-Patreon-FF424D?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/vavo)

> Turn Codex into a ComfyUI operator: install and repair ComfyUI, manage custom nodes, build API workflows, verify models, tune prompt inputs, and debug failures with runtime evidence instead of folklore.

`comfyui-codex` is a local Codex plugin that teaches Codex how to work with ComfyUI in a practical way: installation, ComfyUI-Manager, custom nodes, API integration, workflow JSON, troubleshooting, beginner onboarding, and agent-safe workflow execution.

The plugin is intentionally not a dumped encyclopedia. The trigger skill stays lean, then routes Codex into focused reference files when the task needs more detail. This keeps the context budget usable, which is a nice change from the usual "paste the entire internet and hope" strategy.

Project website: [github.com/vavo/comfyui-codex](https://github.com/vavo/comfyui-codex)

## Why ComfyUI Codex

- **Installation help without install-method soup**: Desktop, Windows Portable, manual git/venv, Comfy CLI, hosted runtimes, and Comfy Cloud get treated as different setups because, annoyingly, they are.
- **ComfyUI-Manager and custom nodes covered**: enablement, legacy mode, missing-node installs, dependency handling, snapshots, and import-failure triage.
- **API workflows that can actually run**: local Server API, Comfy Cloud API, WebSocket monitoring, `/history`, `/view`, `/object_info`, and `/models` checks.
- **Workflow repair before ritual reinstalling**: API/editor format detection, node-class validation, missing model checks, and targeted graph patching.
- **Agent-safe execution patterns**: wraps workflows with friendly parameters like `prompt`, `seed`, `width`, and `image` instead of making users poke node IDs for sport.
- **Evidence-first troubleshooting**: reads logs, runtime endpoints, workflow JSON, model folders, and custom-node state before guessing.

## What's In The Box?

- **One Codex skill**: `comfyui`, with concise routing and operational rules.
- **Local Knowledge Pack**: compact references for install paths, Manager/custom nodes, endpoints, canvas/interface, workflow tutorials, workflow JSON, recipes, models, prompting, parameters, and troubleshooting playbooks.
- **API integration reference**: local and Cloud APIs, submit/status/result loops, WebSocket events, endpoint triage, and output retrieval.
- **Workflow authoring reference**: API JSON shape, patching rules, validation checklist, recipes, and agent-safe packaging.
- **MCP/App/interface guide**: official MCP lanes, local API contract, App Mode builder flow, UI panels, and Mask Editor guidance.
- **Golden workflow library**: local API-format workflow fixtures for text-to-image, LoRA stacking, and upscaling, with catalog validation.
- **Error and custom-node resolvers**: classify ComfyUI error payloads and map known missing `class_type` values to likely node packs.
- **Model-family decision guide**: route SD 1.5, SDXL, modern image/edit/video families, LoRA, ControlNet, and upscalers by task and runtime.
- **Hosted GPU playbook**: Runpod/notebook-style API reachability, mounted storage, model persistence, custom-node, disk, and startup checks.
- **Skill evaluation suite**: pressure prompts, acceptance criteria, and offline validation commands so the skill can be tested without a live GPU.
- **Troubleshooting reference**: startup, frontend, missing node, missing model, VRAM, API, import-failure, and output-retrieval paths.
- **Beginner guide**: first-run checklist, core terms, workflow types, and good habits.
- **Agent workflow patterns**: local-first, template-first, workflow-as-skill patterns for agent automation.
- **Read-only tool suite**: `comfy_probe.py`, `comfy_doctor.py`, `workflow_lint.py`, `model_audit.py`, `error_explainer.py`, `custom_node_resolver.py`, and `workflow_catalog.py`.
- **Fixture/test suite**: sample workflows, server snapshots, expected JSON outputs, and offline unit tests.

**Quick Start:**

```bash
codex plugin marketplace add <repo-root>
codex plugin add comfyui-codex@personal
```

For Platform ZIP upload, upload the repository ZIP. The root `.codex-plugin/plugin.json` points at the packaged skill under `plugins/comfyui-codex/skills/`.

Then start a new Codex thread and try:

```text
Use $comfyui to debug my ComfyUI workflow.
```

## Contents

- [Why ComfyUI Codex](#why-comfyui-codex)
- [What's In The Box?](#whats-in-the-box)
- [What This Plugin Covers](#what-this-plugin-covers)
- [Repository Layout](#repository-layout)
- [Source Strategy](#source-strategy)
- [How Codex Uses The Skill](#how-codex-uses-the-skill)
- [Knowledge Areas](#knowledge-areas)
- [Tools And Fixtures](#tools-and-fixtures)
- [Install In Codex](#install-in-codex)
- [Upload To Platform](#upload-to-platform)
- [Use The Plugin](#use-the-plugin)
- [Development Workflow](#development-workflow)
- [Validation](#validation)
- [Update And Reinstall Flow](#update-and-reinstall-flow)
- [Operational Boundaries](#operational-boundaries)
- [Troubleshooting This Plugin](#troubleshooting-this-plugin)
- [Support](#support)
- [Sponsor](#sponsor)
- [Project Links](#project-links)
- [Resources Used / Kudos To](#resources-used--kudos-to)

## What This Plugin Covers

The plugin provides one Codex skill, `comfyui`, that should be used when a user asks Codex to:

- Explain ComfyUI to a new user.
- Choose between Comfy Desktop, Windows Portable, manual install, Comfy CLI, hosted, and cloud setup paths.
- Enable and troubleshoot ComfyUI-Manager.
- Install, update, disable, or diagnose custom nodes.
- Debug local ComfyUI startup, runtime, model, or custom-node problems.
- Diagnose ComfyUI API failures.
- Inspect ComfyUI workflow JSON.
- Create, patch, or validate API-format workflows.
- Convert the mental model between editor/GUI workflow format and API workflow format.
- Build or package workflows as agent-callable skills.
- Work with local ComfyUI Server API or Comfy Cloud API.
- Use evidence from `/system_stats`, `/object_info`, `/models`, `/history`, and related routes before guessing.
- Apply reusable agent workflow patterns without making users edit raw node IDs for normal tasks.

The main runtime assumption is simple: prefer current evidence from the user's actual ComfyUI instance over generic advice. If the server is reachable, inspect it. If it is not reachable, say what remains unverified.

## Repository Layout

```text
.
├── README.md
├── .codex-plugin/
│   └── plugin.json
├── .agents/
│   └── plugins/
│       └── marketplace.json
└── plugins/
    └── comfyui-codex/
        ├── .codex-plugin/
        │   └── plugin.json
        └── skills/
            └── comfyui/
                ├── SKILL.md
                ├── agents/
                │   └── openai.yaml
                ├── fixtures/
                │   ├── custom_nodes/
                │   ├── errors/
                │   ├── expected/
                │   ├── golden_workflows/
                │   ├── server/
                │   └── workflows/
                ├── references/
                │   ├── agent-workflow-patterns.md
                │   ├── api-endpoints.md
                │   ├── api-integration.md
                │   ├── canvas-interface-guide.md
                │   ├── error-explainer-and-node-resolver.md
                │   ├── generation-parameters.md
                │   ├── golden-workflow-library.md
                │   ├── hosted-gpu-runpod-guide.md
                │   ├── installation-manager-custom-nodes.md
                │   ├── installation-paths.md
                │   ├── manager-custom-nodes.md
                │   ├── mcp-app-interface-guide.md
                │   ├── model-family-decision-guide.md
                │   ├── model-routing-and-prompting.md
                │   ├── new-user-guide.md
                │   ├── skill-evaluation-suite.md
                │   ├── troubleshooting-playbooks.md
                │   ├── troubleshooting.md
                │   ├── workflow-authoring.md
                │   ├── workflow-json-format.md
                │   ├── workflow-tutorials.md
                │   └── workflow-recipes.md
                └── scripts/
                    ├── comfy_doctor.py
                    ├── comfy_probe.py
                    ├── custom_node_resolver.py
                    ├── error_explainer.py
                    ├── model_audit.py
                    ├── workflow_catalog.py
                    └── workflow_lint.py
└── tests/
    └── test_comfy_tools.py
```

### Marketplace

`.agents/plugins/marketplace.json` registers the local plugin entry:

- Plugin name: `comfyui-codex`
- Source path: `./plugins/comfyui-codex`
- Category: `Productivity`
- Installation policy: `AVAILABLE`
- Authentication policy: `ON_INSTALL`

This is a repo-local marketplace, not the default personal marketplace at `~/.agents/plugins/marketplace.json`.

### Plugin Manifest

There are two plugin manifests on purpose:

- `.codex-plugin/plugin.json`: root upload manifest for Platform ZIP uploads. It points `skills` at `./plugins/comfyui-codex/skills/`.
- `plugins/comfyui-codex/.codex-plugin/plugin.json`: nested manifest used by the repo-local marketplace entry.

Both declare:

- Plugin metadata and version.
- Author: `vavo` with profile URL `https://github.com/vavo`.
- Homepage/repository: `https://github.com/vavo/comfyui-codex`.
- The `./skills/` folder.
- User-facing Codex app metadata.
- Default prompts:
  - `Use $comfyui to debug my ComfyUI workflow.`
  - `Use $comfyui to build an API-format workflow.`
  - `Use $comfyui to explain ComfyUI to a beginner.`

Current version:

```text
0.1.0+codex.20260703023454
```

Keep these manifest versions in sync. Yes, duplicate metadata is annoying. The alternative is upload failure, which is more annoying and less useful.

The `+codex...` suffix is a cachebuster for local plugin iteration.

## Source Strategy

The plugin uses official docs, live runtime evidence, and small local references. The boring order matters.

Primary official source:

- https://docs.comfy.org

The skill references official docs for:

- Local ComfyUI Server API.
- Comfy Cloud API.
- ComfyUI installation paths.
- ComfyUI-Manager.
- Agent Tools / MCP.
- App Mode and interface guidance.
- Workflow API format.
- Core workflow concepts.
- Models and model folders.
- Custom nodes and dependency handling.
- Startup flags.
- WebSocket messages.
- Troubleshooting flow.

Official docs remain the first source for API behavior because ComfyUI changes. Niche blog snippets age like milk. The docs and the live server are better.

The local references store stable operating knowledge so Codex does not need to browse for routine tasks. Live server endpoints still win for installed nodes, model names, GPU state, queue state, and workflow validation.

## How Codex Uses The Skill

The skill entry point is:

```text
plugins/comfyui-codex/skills/comfyui/SKILL.md
```

Codex loads `SKILL.md` when the user asks about ComfyUI. That file tells Codex to:

1. Identify the lane: beginner onboarding, canvas/interface, workflow tutorial, generation parameters, installation, Manager/custom nodes, model/prompt routing, workflow authoring, API integration, troubleshooting, or agent workflow packaging.
2. State assumptions.
3. Prefer evidence from the user's runtime.
4. Route into the smallest relevant reference file.
5. Use the read-only scripts when local server evidence, workflow linting, or model auditing would help.
6. Verify with real API calls, workflow parsing, or deterministic local checks when possible.

The skill does not tell Codex to always run ComfyUI. It tells Codex to inspect and verify when feasible, and to be explicit when it cannot.

## Knowledge Areas

### Beginner Onboarding

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/new-user-guide.md
```

Covers:

- Plain-English explanation of ComfyUI.
- First successful run.
- Core terms: workflow, node, input, output, checkpoint, VAE, LoRA, ControlNet, custom node, queue, API format.
- Beginner workflow types: text-to-image, image-to-image, inpainting, LoRA, ControlNet, upscale.
- How users should ask Codex for useful help.

Use this when the user needs orientation, not raw API instructions.

### Installation Paths

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/installation-paths.md
```

Covers:

- Choosing Comfy Desktop, Windows Portable, manual install, Comfy CLI, hosted, or cloud paths.
- Install evidence to collect before giving commands.
- Runtime-specific startup commands.
- Stable startup flags.
- Hosted/notebook/Runpod path caveats.
- First-run verification.

Use this when the user asks how to install ComfyUI, repair startup, or decide which setup fits their machine.

### Manager And Custom Nodes

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/manager-custom-nodes.md
```

Covers:

- Manager enablement.
- Manager configuration.
- Missing-node installs.
- Custom-node dependency repair.
- Isolation, snapshots, and rollback.
- Custom node authoring basics.
- Security checks for third-party Python code.

Use this when the user asks about ComfyUI-Manager, custom nodes, import failures, or missing workflow node classes.

### API Endpoints

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/api-endpoints.md
```

Covers:

- Local Server API route map.
- `POST /prompt`, `/history`, `/view`, `/queue`, `/object_info`, `/models`, `/ws`.
- WebSocket message types.
- Local vs Cloud API caveats.
- Endpoint failure mapping.

Use this when the user needs exact API routes or a quick integration sanity check.

### API Integration

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/api-integration.md
```

Covers:

- Choosing local Server API vs Comfy Cloud API.
- Submit/status/result loops.
- Partner node and API key handling.
- Agent-safe API contracts.
- Chat-agent integration patterns.

Use this when the user is calling ComfyUI from code or asking why an API job failed.

### MCP, App Mode, And Interface

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/mcp-app-interface-guide.md
```

Covers:

- Official Comfy Agent Tools / MCP choices.
- Local API interface contract for Codex.
- App Mode input/output builder flow.
- Interface panels, model library, queue, assets, and templates.
- Mask Editor guidance for inpaint/outpaint work.
- Boundary notes for a future MCP server.

Use this when the user asks about MCP, App Mode, interface controls, local-vs-cloud agent operation, or making a workflow easier to run from chat.

### Canvas Interface

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/canvas-interface-guide.md
```

Covers:

- Node anatomy.
- Inputs, settings, outputs, and typed connections.
- Canvas controls and node search.
- Reading a workflow left to right.
- GUI workflow format vs API workflow format.
- Safe editing habits.

Use this when the user is learning ComfyUI's interface, needs a workflow explained visually, or is editing the canvas manually.

### Generation Parameters

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/generation-parameters.md
```

Covers:

- Seed behavior.
- Steps and diminishing returns.
- CFG.
- Sampler and scheduler comparisons.
- Denoise for img2img/inpaint/outpaint/hi-res.
- Width, height, batch, LoRA strength, and ControlNet strength.

Use this when the user asks why settings affect output quality, reproducibility, or speed.

### Workflow JSON And Recipes

References:

```text
plugins/comfyui-codex/skills/comfyui/references/workflow-json-format.md
plugins/comfyui-codex/skills/comfyui/references/workflow-recipes.md
```

Covers:

- API workflow format vs editor/GUI save format.
- Node object shape.
- Literal inputs vs links.
- Validation checklist.
- Starter recipes for txt2img, img2img, inpaint, LoRA, ControlNet, upscale, and result retrieval.

Use these when creating or linting workflow JSON.

### Golden Workflow Library

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/golden-workflow-library.md
```

Covers:

- Local API-format fixture catalog.
- Golden workflow rules.
- Current text-to-image, LoRA stacking, and upscale fixtures.
- Missing fixture targets for img2img, inpaint, outpaint, ControlNet, and video.
- Offline validation with `workflow_catalog.py`.

Use this when Codex needs a known-good local baseline instead of browsing docs or inventing raw graphs.

### Workflow Tutorials

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/workflow-tutorials.md
```

Covers:

- Text to image.
- Image to image.
- Inpaint.
- Outpaint.
- Upscale.
- LoRA single and LoRA stacking.
- ControlNet.
- Text to video and image to video tutorial patterns.
- Required models/custom nodes, GUI steps, API/export steps, validation, and common failures.

Use this when the user asks for a step-by-step how-to rather than a compact recipe.

### Workflow Authoring

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/workflow-authoring.md
```

Covers:

- Targeted workflow patching.
- Workflow-as-skill packaging.
- Common exposed schema aliases.
- Review heuristics.

Use this when modifying existing workflows or turning them into reusable agent-safe commands.

### Models And Prompting

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/model-routing-and-prompting.md
```

Covers:

- Loader-to-folder mapping.
- Model-family routing.
- Exact filename checks with `/models/{folder}`.
- Prompt and negative prompt conventions.
- LoRA, ControlNet, upscale, and extra model path guidance.

Use this when the user asks which model goes where, why a model is missing, or how to expose prompt controls.

### Model Family Decision Guide

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/model-family-decision-guide.md
```

Covers:

- Task-to-family routing for SD 1.5, SDXL, modern transformer/image-edit/video families, LoRA, ControlNet, and upscalers.
- VRAM/runtime tradeoffs.
- Loader-to-folder reminders.
- Prompting differences by family.
- When Codex should push back on unrealistic model/runtime choices.

Use this when the user asks what model family, workflow shape, or prompting style fits a task.

### Error Explainer And Custom Node Resolver

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/error-explainer-and-node-resolver.md
```

Covers:

- `node_errors` and WebSocket error categories.
- Missing custom node classes.
- Missing model files.
- Dependency import failures.
- Resolver map policy.
- Manager install and verification loop.

Use this when the user provides an error payload, traceback, missing `class_type`, or custom-node import failure.

### Hosted GPU And Runpod

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/hosted-gpu-runpod-guide.md
```

Covers:

- Browser URL vs API URL checks.
- Hosted proxy/tunnel problems.
- Jupyter/terminal evidence.
- Mounted volume and disk quota failures.
- Model persistence after pod restart.
- Custom-node install and dependency repair in hosted runtimes.

Use this when ComfyUI is running in a pod, notebook, cloud VM, or browser-hosted GPU environment.

### Troubleshooting

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/troubleshooting-playbooks.md
```

Covers:

- Evidence to collect first.
- Server offline.
- UI loads but API fails.
- Validation `node_errors`.
- Missing `class_type`.
- Missing models.
- Import errors and dependency conflicts.
- VRAM and out-of-memory failures.
- Output retrieval failures.
- Workflow import failures.

Use this when something is broken, slow, missing, or weird. So, most real ComfyUI work.

### Agent Workflow Patterns

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/agent-workflow-patterns.md
```

Covers:

- Source precedence.
- Local bootstrap patterns.
- Workflow-as-skill patterns.
- Codex operating loops for debugging, packaging, and building workflows.
- Attribution notes.

Use this when the user wants Codex to turn workflows into reusable agent skills, not just run one prompt.

### Skill Evaluation Suite

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/skill-evaluation-suite.md
```

Covers:

- Offline validation commands.
- Pressure prompts for missing nodes, missing models, App Mode, hosted GPUs, and model selection.
- Expected routing behavior.
- Acceptance criteria.
- Regression checks.

Use this when changing the plugin or checking whether the skill still answers quickly from local knowledge.

## Tools And Fixtures

All scripts are read-only. They do not queue prompts, install dependencies, modify workflows, clear history, or download models.

### Server Probe

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py \
  --server http://127.0.0.1:8188
```

Checks server reachability, `/system_stats`, `/object_info`, `/models`, `/queue`, common model folders, optional workflow shape, missing classes, suggested parameters, and model references.

### Doctor Script

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_doctor.py \
  --server http://127.0.0.1:8188 \
  --workflow <workflow-api.json>
```

Reports endpoint health, system stats, Manager/custom-node signals, model folder counts, missing workflow classes, and model-reference summary.

Offline snapshot mode:

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_doctor.py \
  --snapshot plugins/comfyui-codex/skills/comfyui/fixtures/server/server_snapshot.json \
  --workflow plugins/comfyui-codex/skills/comfyui/fixtures/workflows/basic_api.json \
  --omit-path
```

### Workflow Lint

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/workflow_lint.py \
  plugins/comfyui-codex/skills/comfyui/fixtures/workflows/basic_api.json
```

Detects API/editor/unknown format, node count, class types, broken links, output-node presence, and model loader references without a live server.

### Model Audit

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/model_audit.py \
  plugins/comfyui-codex/skills/comfyui/fixtures/workflows/basic_api.json \
  --server http://127.0.0.1:8188
```

Compares workflow model loader references against live `/models/{folder}` data.

Offline fixture mode:

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/model_audit.py \
  plugins/comfyui-codex/skills/comfyui/fixtures/workflows/missing_model_api.json \
  --models-json plugins/comfyui-codex/skills/comfyui/fixtures/server/models.json \
  --omit-path
```

### Error Explainer

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/error_explainer.py \
  plugins/comfyui-codex/skills/comfyui/fixtures/errors/node_errors_missing_class.json \
  --omit-path
```

Classifies ComfyUI error payloads/log excerpts into buckets such as `missing_custom_node`, `missing_model`, `dependency_import_error`, `vram_oom`, `server_unreachable`, and `output_retrieval`.

### Custom Node Resolver

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/custom_node_resolver.py \
  IPAdapterModelLoader \
  --map-json plugins/comfyui-codex/skills/comfyui/fixtures/custom_nodes/class_resolver.json \
  --omit-path
```

Maps known missing `class_type` values to likely custom node packs and leaves unknown classes unresolved instead of hallucinating a package name. Restraint. A rare and useful feature.

### Workflow Catalog

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/workflow_catalog.py \
  --catalog-json plugins/comfyui-codex/skills/comfyui/fixtures/golden_workflows/catalog.json \
  --omit-path
```

Validates the local golden workflow catalog and reports fixture counts by workflow type.

### Fixtures

Fixtures live under:

```text
plugins/comfyui-codex/skills/comfyui/fixtures/
```

They include:

- `workflows/basic_api.json`
- `workflows/broken_link_api.json`
- `workflows/editor_workflow.json`
- `workflows/missing_model_api.json`
- `errors/node_errors_missing_class.json`
- `custom_nodes/class_resolver.json`
- `golden_workflows/catalog.json`
- `golden_workflows/lora_stack_api.json`
- `golden_workflows/upscale_api.json`
- `server/models.json`
- `server/server_snapshot.json`
- `expected/*.json`

Run offline verification:

```bash
python3 -m unittest tests/test_comfy_tools.py
```

Expected result: 7 tests pass.

## Install In Codex

This repository already contains a repo-local marketplace:

```text
<repo-root>/.agents/plugins/marketplace.json
```

If this marketplace is not configured in Codex yet, add the repository root as the marketplace source:

```bash
codex plugin marketplace add <repo-root>
```

Codex expects the repository root here because it discovers the marketplace file at:

```text
<repo-root>/.agents/plugins/marketplace.json
```

Do not pass `<repo-root>/.agents/plugins` as the source; that directory contains the manifest, but it is not the supported marketplace root for the current Codex CLI.

Then install the plugin from that marketplace:

```bash
codex plugin add comfyui-codex@personal
```

## Upload To Platform

Use the repository ZIP from GitHub or create a ZIP where the repository root is the only top-level directory. The upload scanner accepts `.codex-plugin/plugin.json` at the ZIP root or inside that single top-level directory.

This repo includes a root upload manifest:

```text
<repo-root>/.codex-plugin/plugin.json
```

Do not upload only `.agents/plugins/` or only the nested `plugins/comfyui-codex/` folder unless the upload UI explicitly asks for a plugin folder instead of a repository ZIP.

If Codex reports a different marketplace name, read it from:

```bash
PLUGIN_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator"
python3 "$PLUGIN_CREATOR_SKILL/scripts/read_marketplace_name.py" \
  --marketplace-path .agents/plugins/marketplace.json
```

After installing or reinstalling a local plugin, start a new Codex thread before testing skill activation. Existing threads do not reliably pick up new plugin metadata and skill bodies.

## Use The Plugin

Example prompts:

```text
Use $comfyui to debug this workflow. Local server is http://127.0.0.1:8188 and POST /prompt returns node_errors.
```

```text
Use $comfyui to inspect this API workflow and tell me which models or custom nodes are missing.
```

```text
Use $comfyui to package this ComfyUI workflow as an agent-safe command with prompt, seed, width, and height parameters.
```

```text
Use $comfyui to explain ComfyUI to a new user and give them a first-run checklist.
```

```text
Use $comfyui to build a minimal API-format text-to-image workflow from a known-good template.
```

The best user requests include:

- Runtime: local ComfyUI, Desktop, portable, Docker, Runpod, notebook, or Cloud.
- Server URL.
- Workflow JSON or path.
- Exact error text.
- Startup logs when relevant.
- Model/checkpoint names.
- Installed custom nodes or missing node report.
- GPU/VRAM details for performance issues.

## Development Workflow

### Edit Scope

Keep edits scoped to:

- `.codex-plugin/plugin.json`
- `plugins/comfyui-codex/.codex-plugin/plugin.json`
- `plugins/comfyui-codex/skills/comfyui/SKILL.md`
- `plugins/comfyui-codex/skills/comfyui/agents/openai.yaml`
- `plugins/comfyui-codex/skills/comfyui/references/*.md`
- `plugins/comfyui-codex/skills/comfyui/scripts/*.py`
- `plugins/comfyui-codex/skills/comfyui/fixtures/**`
- `tests/test_comfy_tools.py`
- `.agents/plugins/marketplace.json` only through scaffold or marketplace-aware tooling

Do not put README-style auxiliary docs inside `plugins/comfyui-codex/skills/comfyui/`. Skill folders should stay lean and task-facing.

### Update Source Guidance

When updating knowledge:

1. Prefer official docs from `https://docs.comfy.org`.
2. Use live ComfyUI endpoint behavior when available.
3. Use existing agent-workflow prior art for reusable packaging patterns.
4. Put detailed material in `references/`.
5. Keep `SKILL.md` to routing and operational rules.
6. Avoid adding giant copied docs or third-party generated assets.

### Update The Tool Scripts

Keep tool scripts:

- Stdlib-only.
- Read-only by default.
- JSON-output oriented.
- Useful without a running ComfyUI server.
- Safe to run from any working directory.

If the script starts queuing prompts or installing dependencies, that should be a new explicit tool or mode, not a quiet expansion. Silent side effects are where good intentions go to become support tickets.

## Validation

Run these checks before handing off changes.

### Plugin Manifest Validation

```bash
PLUGIN_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator"
uv run --with pyyaml python \
  "$PLUGIN_CREATOR_SKILL/scripts/validate_plugin.py" \
  plugins/comfyui-codex
```

Expected output includes:

```text
Plugin validation passed
```

### Skill Validation

```bash
SKILL_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator"
uv run --with pyyaml python \
  "$SKILL_CREATOR_SKILL/scripts/quick_validate.py" \
  plugins/comfyui-codex/skills/comfyui
```

Expected output:

```text
Skill is valid!
```

The `uv run --with pyyaml` wrapper is intentional in this local environment. The validators import PyYAML, and using `uv` avoids mutating the project environment just to make a validator happy.

### Script Checks

```bash
python3 -m py_compile \
  plugins/comfyui-codex/skills/comfyui/scripts/*.py
```

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_doctor.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/workflow_lint.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/model_audit.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/error_explainer.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/custom_node_resolver.py --help
python3 plugins/comfyui-codex/skills/comfyui/scripts/workflow_catalog.py --help
```

Offline fixture suite:

```bash
python3 -m unittest tests/test_comfy_tools.py
```

Optional dead-port behavior check:

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py \
  --server http://127.0.0.1:9 \
  --timeout 0.1
```

Expected behavior: JSON output with connection-refused errors and exit code `1`.

### JSON And Whitespace Checks

```bash
python3 -m json.tool plugins/comfyui-codex/.codex-plugin/plugin.json >/dev/null
python3 -m json.tool .codex-plugin/plugin.json >/dev/null
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
git diff --check -- .agents .codex-plugin plugins README.md
```

### Clean Generated Python Cache

`py_compile` and some validation/import paths can create `__pycache__`. Remove it before committing:

```bash
rm -rf plugins/comfyui-codex/skills/comfyui/scripts/__pycache__
find . -name __pycache__ -o -name '*.pyc'
```

## Update And Reinstall Flow

For local plugin iteration, use the plugin-creator cachebuster script instead of manually inventing version suffixes:

```bash
PLUGIN_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator"
python3 "$PLUGIN_CREATOR_SKILL/scripts/update_plugin_cachebuster.py" \
  plugins/comfyui-codex
```

Then reinstall:

```bash
codex plugin add comfyui-codex@personal
```

If using a non-default marketplace name, replace `personal` with the actual marketplace name from `marketplace.json`.

Start a new Codex thread after reinstalling. This is the clean boundary for updated plugin and skill loading.

## Operational Boundaries

This plugin is a Codex knowledge and workflow-support package. It does not currently provide:

- A ComfyUI MCP server.
- A workflow template library clone.
- Model downloads.
- Custom node installation automation.
- A GUI for workflow management.
- A full ComfyUI client that queues generation jobs.
- A prompt recipe database for every model family.

Those are valid future additions, but they should be explicit features. For now, the plugin gives Codex reliable operating instructions, read-only diagnostics, offline linting, and fixture-backed checks. That is the right boring foundation.

## Troubleshooting This Plugin

### Skill Does Not Trigger

Check:

- Plugin is installed in Codex.
- New thread was started after install/reinstall.
- `SKILL.md` frontmatter is valid.
- Prompt explicitly names `$comfyui` if implicit triggering is not happening.

### Plugin Does Not Appear

Check:

- `.agents/plugins/marketplace.json` exists.
- Marketplace root is configured in Codex.
- Plugin source path resolves to `./plugins/comfyui-codex`.
- Manifest validates.

### Plugin Validation Fails

Likely causes:

- Invalid semver in `plugin.json`.
- Unsupported manifest fields.
- Missing required interface fields.
- Paths in manifest point to missing files.
- Leftover placeholders.

Run the validator command in [Validation](#validation) and fix the first concrete error.

### Skill Validation Fails

Likely causes:

- Invalid YAML frontmatter.
- Missing `name` or `description`.
- Skill folder name does not match skill name.
- Nonstandard frontmatter fields.

Run the skill validator and fix the reported line. No need for drama. YAML provides enough on its own.

### Probe Script Reports Everything Offline

Check:

- ComfyUI is running.
- Server URL and port are correct.
- Docker/notebook/Runpod proxy exposes the port.
- Browser can open the same base URL.
- Local firewall or tunnel is not blocking requests.

The probe reporting offline is not a plugin failure. It usually means the target ComfyUI server is offline or not reachable from the current machine.

## Maintenance Notes

- Commit plugin changes when the change set exceeds 200 changed lines.
- Push after commit to `origin/main` unless intentionally working elsewhere.
- Keep generated files out of git unless they are intentional plugin assets.
- Keep `README.md` at the repo root. Keep the skill folder focused on what Codex needs at runtime.

## Support

ComfyUI Codex is meant for real ComfyUI work: installs, broken custom nodes, workflow JSON, API runs, model-path confusion, and the usual "why is this node missing when I installed it" circus.

If something is wrong, open an issue with:

- ComfyUI install type.
- OS, GPU, VRAM, and Python version.
- Workflow JSON or exact prompt/task.
- Startup log or API error payload.
- Missing model or custom node names.
- What changed before it broke.

GitHub issues: https://github.com/vavo/comfyui-codex/issues

## Sponsor

[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor%20on-GitHub-24292F?style=for-the-badge&logo=github)](https://github.com/sponsors/vavo) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-vavo-5F7FFF?style=for-the-badge&logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/vavo) [![Support on Patreon](https://img.shields.io/badge/Support%20on-Patreon-FF424D?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/vavo)

If this saves you from a three-hour custom-node dependency ritual, sponsorship is cheaper than the coffee you were about to need.

## License

This local plugin manifest declares `MIT`.

Made with too much coffee by [vavo](https://github.com/vavo).

## Project Links

- GitHub repo: https://github.com/vavo/comfyui-codex
- Author: https://github.com/vavo
- Sponsor: https://github.com/sponsors/vavo
- Buy Me a Coffee: https://www.buymeacoffee.com/vavo
- Patreon: https://www.patreon.com/vavo

## Resources Used / Kudos To

- Official ComfyUI documentation: https://docs.comfy.org
- ComfyUI-Agent-Kit: https://github.com/SlavaSexton/ComfyUI-Agent-Kit
- ComfyUI Skills OpenClaw: https://github.com/HuangYuChuh/ComfyUI_Skills_OpenClaw
- Stable Diffusion Art ComfyUI guide: https://stable-diffusion-art.com/comfyui/
- Angry Shark Studio canvas tutorial: https://www.angry-shark-studio.com/blog/comfyui-tutorial-understanding-canvas/
- Angry Shark Studio generation parameters tutorial: https://www.angry-shark-studio.com/blog/comfyui-tutorial-mastering-generation-parameters/
- Angry Shark Studio beginner mistakes guide: https://www.angry-shark-studio.com/blog/comfyui-mistakes-beginners-make/

Those resources were used as reference material. This plugin does not vendor or mirror their packages.
