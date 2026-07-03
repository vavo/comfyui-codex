# Skill Evaluation Suite

Use this when validating whether the ComfyUI skill gives fast, grounded answers without browsing or needing a live GPU.

## Goal

The skill should handle routine ComfyUI requests from local references and scripts:

- Install and troubleshooting triage.
- API route guidance.
- Workflow JSON linting.
- Missing model checks.
- Missing custom-node resolution.
- Error explanation.
- Workflow tutorial routing.
- Hosted GPU playbooks.
- App Mode/interface guidance.

Browsing official docs is still correct when the user asks for latest behavior, exact current docs, or something volatile.

## Offline Validation Commands

Run from the repository root:

```bash
python3 -m unittest tests/test_comfy_tools.py
python3 -m py_compile plugins/comfyui-codex/skills/comfyui/scripts/*.py
python3 plugins/comfyui-codex/skills/comfyui/scripts/workflow_catalog.py \
  --catalog-json plugins/comfyui-codex/skills/comfyui/fixtures/golden_workflows/catalog.json \
  --omit-path
```

Plugin/skill validation:

```bash
PLUGIN_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator"
uv run --with pyyaml python "$PLUGIN_CREATOR_SKILL/scripts/validate_plugin.py" \
  plugins/comfyui-codex

SKILL_CREATOR_SKILL="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator"
uv run --with pyyaml python "$SKILL_CREATOR_SKILL/scripts/quick_validate.py" \
  plugins/comfyui-codex/skills/comfyui
```

## Pressure Prompts

Use these prompts to test routing:

```text
Use $comfyui. POST /prompt returns node_errors saying IPAdapterModelLoader does not exist. What should I do?
```

Expected behavior:

- Read `error-explainer-and-node-resolver.md`.
- Suggest `error_explainer.py` and `custom_node_resolver.py`.
- Route to Manager missing-node install and `/object_info` verification.
- Do not tell the user to reinstall ComfyUI first.

```text
Use $comfyui. My workflow references epicModel_v4.safetensors and says it is missing.
```

Expected behavior:

- Read model-routing/troubleshooting references.
- Use `model_audit.py` if workflow is available.
- Verify `/models/checkpoints`.
- Avoid guessing download URLs.

```text
Use $comfyui. Build a beginner text-to-image workflow and explain how to make it App Mode friendly.
```

Expected behavior:

- Read workflow tutorials plus MCP/App/interface guide.
- Use golden workflow library for local baseline.
- Mention selecting prompt/seed/size inputs and output preview/save nodes.

```text
Use $comfyui. I am on Runpod, the UI opens, but API calls fail and models disappear after restart.
```

Expected behavior:

- Read hosted GPU playbook.
- Separate public UI URL from API reachability.
- Check mounted volume, model folder, and `/system_stats`.
- Avoid provider-specific claims unless verified.

```text
Use $comfyui. Which model family should I use for image-to-video with low VRAM?
```

Expected behavior:

- Read model family decision guide.
- Ask for/runtime VRAM if absent.
- Explain tradeoff: video models are large; hosted GPU may be more realistic.

## Acceptance Criteria

The skill is working when:

- Answers name assumptions and lane.
- Uses local references for stable knowledge.
- Uses official docs for current behavior when browsing is requested.
- Runs read-only scripts when evidence would improve accuracy.
- Keeps local paths generic in repo docs and fixtures.
- Separates editor workflow JSON from API workflow JSON.
- Separates missing custom nodes from missing model files.
- Does not mutate ComfyUI, install nodes, download models, or queue jobs without explicit user intent.

## Regression Checks

Before committing:

- `python3 -m unittest tests/test_comfy_tools.py`
- `python3 -m py_compile plugins/comfyui-codex/skills/comfyui/scripts/*.py`
- `git diff --check`
- Search for local absolute paths:

```bash
rg -n "<local-user-home>|<local-checkout-name>" \
  README.md .gitignore tests plugins .agents -S --hidden --no-ignore
```

The path search should not report repository documentation or code. If it reports the ignored local design/spec under `docs/`, leave it ignored and do not stage it.
