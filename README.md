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
- **Installation reference**: Comfy Desktop, Windows Portable, manual install, Comfy CLI, Manager, custom nodes, dependencies, and security checks.
- **API integration reference**: local and Cloud APIs, submit/status/result loops, WebSocket events, and output retrieval.
- **Workflow authoring reference**: API JSON shape, patching rules, validation checklist, and a minimal text-to-image skeleton.
- **Troubleshooting reference**: startup, frontend, missing node, missing model, VRAM, API, and import-failure paths.
- **Beginner guide**: first-run checklist, core terms, workflow types, and good habits.
- **Agent workflow patterns**: local-first, template-first, workflow-as-skill patterns for agent automation.
- **Read-only probe script**: checks server reachability, model folders, workflow structure, missing classes, and model references.

**Quick Start:**

```bash
codex plugin marketplace add <repo-root>/.agents/plugins
codex plugin add comfyui-codex@personal
```

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
- [Probe Script](#probe-script)
- [Install In Codex](#install-in-codex)
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
                ├── references/
                │   ├── agent-workflow-patterns.md
                │   ├── api-integration.md
                │   ├── installation-manager-custom-nodes.md
                │   ├── new-user-guide.md
                │   ├── troubleshooting.md
                │   └── workflow-authoring.md
                └── scripts/
                    └── comfy_probe.py
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

`plugins/comfyui-codex/.codex-plugin/plugin.json` is the plugin manifest. It declares:

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
0.1.0+codex.20260702150656
```

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

1. Identify the lane: beginner onboarding, installation/Manager/custom nodes, workflow authoring, API integration, troubleshooting, or agent workflow packaging.
2. State assumptions.
3. Prefer evidence from the user's runtime.
4. Route into the smallest relevant reference file.
5. Use `scripts/comfy_probe.py` when local server or workflow inspection would help.
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

### Installation, Manager, And Custom Nodes

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/installation-manager-custom-nodes.md
```

Covers:

- Choosing Comfy Desktop, Windows Portable, manual install, Comfy CLI, hosted, or cloud paths.
- Install evidence to collect before giving commands.
- Desktop instance behavior and shared paths.
- Windows Portable embedded Python rules.
- Manual git/venv install shape.
- Comfy CLI install, node, and model commands.
- ComfyUI-Manager enablement, legacy mode, and CLI context.
- Custom node install methods: Manager, Git clone, ZIP fallback.
- Correct-environment dependency installation.
- Security and trust checks for third-party nodes.
- Manager and custom-node troubleshooting loops.

Use this when the user asks how to install ComfyUI, enable Manager, install missing workflow nodes, repair a node import failure, or decide which install path fits their machine.

### API Integration

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/api-integration.md
```

Covers:

- Choosing local Server API vs Comfy Cloud API.
- Local server routes.
- `POST /prompt`.
- `GET /history/{prompt_id}`.
- `GET /view`.
- `GET /object_info`.
- `GET /models/{folder}`.
- WebSocket status and progress messages.
- Partner node and API key handling.
- Agent-safe API contracts.
- Submit/status/result loops for chat agents.

Use this when the user is calling ComfyUI from code or asking why an API job failed.

### Workflow Authoring

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/workflow-authoring.md
```

Covers:

- API workflow format vs editor/GUI save format.
- Node input shape.
- Literal inputs vs links.
- Targeted workflow patching.
- Workflow validation.
- Workflow-as-skill packaging.
- Common exposed schema aliases.
- Minimal text-to-image API workflow skeleton.
- Review heuristics.

Use this when creating, modifying, converting, or reviewing workflow JSON.

### Troubleshooting

Reference:

```text
plugins/comfyui-codex/skills/comfyui/references/troubleshooting.md
```

Covers:

- Evidence to collect first.
- Startup and frontend failures.
- Running with custom nodes disabled.
- Custom node binary search.
- Missing node diagnosis.
- Missing model diagnosis.
- Loader-to-folder mapping.
- Generation failures.
- VRAM and performance issues.
- API-specific failures.
- Workflow import failures.
- Upstream bug reporting checklist.

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

## Probe Script

Script:

```text
plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py
```

The probe is read-only. It performs safe GET requests and local JSON inspection. It does not queue prompts, install dependencies, modify workflows, delete history, or download models.

### Basic Server Probe

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py \
  --server http://127.0.0.1:8188
```

It checks:

- `/system_stats`
- `/object_info`
- `/models`
- `/queue`
- Common model folders:
  - `checkpoints`
  - `loras`
  - `vae`
  - `controlnet`
  - `upscale_models`
  - `clip`
  - `clip_vision`
  - `diffusion_models`
  - `style_models`

### Workflow Probe

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py \
  --server http://127.0.0.1:8188 \
  --workflow /absolute/path/to/workflow.json
```

For workflows, it reports:

- Detected workflow format: `api`, `editor`, or `unknown`.
- Node count.
- Used class types.
- Missing class types when `/object_info` is reachable.
- Structural issues such as broken links.
- Whether an API workflow has an output node.
- Suggested agent-facing parameters.
- Referenced model files.
- Model reference status: `present`, `missing`, or `unverified`.

### Custom Model Folder Checks

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py \
  --server http://127.0.0.1:8188 \
  --model-folder checkpoints \
  --model-folder diffusion_models
```

Use this when a custom node expects a less common model folder.

### Exit Codes

- `0`: at least one endpoint responded and no workflow issue was detected.
- `1`: endpoint failure or workflow issue detected.
- `2`: invalid arguments, such as an empty server URL.

The script prints JSON either way. A nonzero exit is not automatically a disaster. It can be useful evidence.

## Install In Codex

This repository already contains a repo-local marketplace:

```text
<repo-root>/.agents/plugins/marketplace.json
```

If this marketplace is not configured in Codex yet, add the marketplace root:

```bash
codex plugin marketplace add <repo-root>/.agents/plugins
```

Then install the plugin from that marketplace:

```bash
codex plugin add comfyui-codex@personal
```

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

- `plugins/comfyui-codex/.codex-plugin/plugin.json`
- `plugins/comfyui-codex/skills/comfyui/SKILL.md`
- `plugins/comfyui-codex/skills/comfyui/agents/openai.yaml`
- `plugins/comfyui-codex/skills/comfyui/references/*.md`
- `plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py`
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

### Update The Probe Script

Keep `comfy_probe.py`:

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
  plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py
```

```bash
python3 plugins/comfyui-codex/skills/comfyui/scripts/comfy_probe.py --help
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
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
git diff --check -- .agents plugins README.md
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

Those are valid future additions, but they should be explicit features. For now, the plugin gives Codex reliable operating instructions and a read-only probe. That is the right boring foundation.

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

Those projects were used as reference material. This plugin does not vendor or mirror their packages.
