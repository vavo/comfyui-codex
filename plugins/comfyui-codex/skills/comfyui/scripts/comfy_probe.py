#!/usr/bin/env python3
"""Read-only ComfyUI local server probe and workflow sanity checker."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MODEL_FOLDERS = (
    "checkpoints",
    "loras",
    "vae",
    "controlnet",
    "upscale_models",
    "clip",
    "clip_vision",
    "diffusion_models",
    "style_models",
)


MODEL_LOADER_MAP: dict[str, dict[str, str]] = {
    "CheckpointLoaderSimple": {"ckpt_name": "checkpoints"},
    "CheckpointLoader": {"ckpt_name": "checkpoints"},
    "unCLIPCheckpointLoader": {"ckpt_name": "checkpoints"},
    "LoraLoader": {"lora_name": "loras"},
    "LoraLoaderModelOnly": {"lora_name": "loras"},
    "ControlNetLoader": {"control_net_name": "controlnet"},
    "DiffControlNetLoader": {"control_net_name": "controlnet"},
    "VAELoader": {"vae_name": "vae"},
    "UpscaleModelLoader": {"model_name": "upscale_models"},
    "CLIPLoader": {"clip_name": "clip"},
    "DualCLIPLoader": {"clip_name1": "clip", "clip_name2": "clip"},
    "UNETLoader": {"unet_name": "diffusion_models"},
    "StyleModelLoader": {"style_model_name": "style_models"},
    "CLIPVisionLoader": {"clip_name": "clip_vision"},
    "GLIGENLoader": {"gligen_name": "gligen"},
    "HypernetworkLoader": {"hypernetwork_name": "hypernetworks"},
}

OUTPUT_NODE_HINTS = (
    "SaveImage",
    "PreviewImage",
    "SaveAnimatedWEBP",
    "SaveAudio",
    "SaveVideo",
    "SaveImageWebsocket",
    "VHS_VideoCombine",
)


def normalize_base_url(raw: str) -> str:
    value = raw.strip().rstrip("/")
    if not value:
        raise ValueError("server URL is empty")
    if "://" not in value:
        value = f"http://{value}"
    return value


def get_json(base_url: str, path: str, timeout: float) -> dict[str, Any]:
    url = f"{base_url}{path}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            text = body.decode("utf-8", errors="replace")
            try:
                payload: Any = json.loads(text) if text else None
            except json.JSONDecodeError:
                payload = text[:1000]
            return {
                "ok": True,
                "status": response.status,
                "url": url,
                "payload": payload,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "url": url,
            "error": body[:2000],
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "status": None,
            "url": url,
            "error": str(exc.reason),
        }
    except TimeoutError:
        return {
            "ok": False,
            "status": None,
            "url": url,
            "error": "request timed out",
        }


def load_workflow(path: Path) -> tuple[Any | None, list[str]]:
    issues: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, [f"cannot read workflow: {exc}"]
    try:
        return json.loads(text), issues
    except json.JSONDecodeError as exc:
        return None, [f"workflow JSON parse error at line {exc.lineno}, column {exc.colno}: {exc.msg}"]


def workflow_node_classes(workflow: Any) -> set[str]:
    fmt = detect_workflow_format(workflow)
    if fmt == "editor":
        classes: set[str] = set()
        for node in workflow.get("nodes", []):
            if isinstance(node, dict) and isinstance(node.get("type"), str):
                classes.add(node["type"])
        return classes
    if not isinstance(workflow, dict) or fmt != "api":
        return set()
    classes: set[str] = set()
    for node in workflow.values():
        if isinstance(node, dict) and isinstance(node.get("class_type"), str):
            classes.add(node["class_type"])
    return classes


def detect_workflow_format(workflow: Any) -> str:
    if not isinstance(workflow, dict) or not workflow:
        return "unknown"
    if isinstance(workflow.get("nodes"), list) and isinstance(workflow.get("links"), list):
        return "editor"
    if all(isinstance(key, str) and isinstance(value, dict) and "class_type" in value for key, value in workflow.items()):
        return "api"
    return "unknown"


def iter_api_nodes(workflow: Any):
    if detect_workflow_format(workflow) != "api":
        return
    for node_id, node in workflow.items():
        if isinstance(node, dict):
            yield str(node_id), node


def inspect_workflow_shape(workflow: Any) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    fmt = detect_workflow_format(workflow)

    if not isinstance(workflow, dict):
        return {
            "format": "unknown",
            "node_count": 0,
            "class_types": [],
            "issues": ["workflow top-level JSON must be an object"],
            "warnings": [],
        }

    if fmt == "editor":
        node_types = sorted(
            {
                str(node.get("type"))
                for node in workflow.get("nodes", [])
                if isinstance(node, dict) and node.get("type")
            }
        )
        return {
            "format": "editor",
            "node_count": len(workflow.get("nodes", [])),
            "class_types": node_types,
            "issues": [],
            "warnings": [
                "editor workflow format detected; export or convert to API format before POST /prompt"
            ],
        }

    if fmt != "api":
        return {
            "format": "unknown",
            "node_count": len(workflow),
            "class_types": [],
            "issues": ["workflow is neither ComfyUI API format nor editor format"],
            "warnings": [],
        }

    class_types: set[str] = set()
    for node_id, node in workflow.items():
        if not isinstance(node_id, str):
            issues.append(f"node key {node_id!r} is not a string")
        if not isinstance(node, dict):
            issues.append(f"node {node_id!r} is not an object")
            continue

        class_type = node.get("class_type")
        if not isinstance(class_type, str) or not class_type:
            issues.append(f"node {node_id!r} is missing class_type")
        else:
            class_types.add(class_type)

        inputs = node.get("inputs")
        if inputs is None:
            warnings.append(f"node {node_id!r} has no inputs object")
            continue
        if not isinstance(inputs, dict):
            issues.append(f"node {node_id!r} inputs is not an object")
            continue

        for input_name, value in inputs.items():
            if is_link(value):
                source_id, output_index = value
                if source_id not in workflow:
                    issues.append(
                        f"node {node_id!r} input {input_name!r} links to missing node {source_id!r}"
                    )
                if output_index < 0:
                    issues.append(
                        f"node {node_id!r} input {input_name!r} has negative output index {output_index}"
                    )

    return {
        "format": "api",
        "node_count": len(workflow),
        "class_types": sorted(class_types),
        "has_output_node": has_output_node(workflow),
        "issues": issues,
        "warnings": warnings,
    }


def has_output_node(workflow: Any) -> bool:
    for _node_id, node in iter_api_nodes(workflow) or []:
        class_type = str(node.get("class_type", ""))
        if class_type in OUTPUT_NODE_HINTS or class_type.startswith(("Save", "Preview")):
            return True
    return False


def is_link(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and isinstance(value[1], int)
    )


def compact_endpoint_result(result: dict[str, Any]) -> dict[str, Any]:
    if not result.get("ok"):
        return {
            "ok": False,
            "status": result.get("status"),
            "error": result.get("error"),
        }

    payload = result.get("payload")
    summary: dict[str, Any] = {"ok": True, "status": result.get("status")}
    if isinstance(payload, dict):
        summary["type"] = "object"
        summary["key_count"] = len(payload)
        summary["sample_keys"] = sorted(str(key) for key in list(payload.keys())[:20])
    elif isinstance(payload, list):
        summary["type"] = "array"
        summary["count"] = len(payload)
        summary["sample"] = payload[:20]
    else:
        summary["type"] = type(payload).__name__
        summary["value"] = payload
    return summary


def model_folder_summary(
    base_url: str, folders: list[str], timeout: float
) -> tuple[dict[str, Any], dict[str, set[str]]]:
    summary: dict[str, Any] = {}
    names_by_folder: dict[str, set[str]] = {}
    for folder in folders:
        encoded = urllib.parse.quote(folder, safe="")
        result = get_json(base_url, f"/models/{encoded}", timeout)
        compact = compact_endpoint_result(result)
        payload = result.get("payload")
        if result.get("ok") and isinstance(payload, list):
            names_by_folder[folder] = {str(item) for item in payload}
            compact["models"] = payload[:50]
            if len(payload) > 50:
                compact["truncated"] = True
        summary[folder] = compact
    return summary, names_by_folder


def extract_model_refs(workflow: Any) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for node_id, node in iter_api_nodes(workflow) or []:
        class_type = str(node.get("class_type", ""))
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for field, folder in MODEL_LOADER_MAP.get(class_type, {}).items():
            value = inputs.get(field)
            if isinstance(value, str) and value:
                refs.append(
                    {
                        "node_id": node_id,
                        "class_type": class_type,
                        "field": field,
                        "folder": folder,
                        "filename": value,
                    }
                )
    return refs


def classify_model_refs(
    refs: list[dict[str, Any]], names_by_folder: dict[str, set[str]]
) -> list[dict[str, Any]]:
    checked: list[dict[str, Any]] = []
    for ref in refs:
        folder = str(ref["folder"])
        filename = str(ref["filename"])
        item = dict(ref)
        if folder not in names_by_folder:
            item["status"] = "unverified"
        elif filename in names_by_folder[folder]:
            item["status"] = "present"
        else:
            item["status"] = "missing"
        checked.append(item)
    return checked


def suggest_parameters(workflow: Any) -> list[dict[str, Any]]:
    params: list[dict[str, Any]] = []
    seen_names: set[str] = set()
    for node_id, node in iter_api_nodes(workflow) or []:
        class_type = str(node.get("class_type", ""))
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for field, value in inputs.items():
            if is_link(value):
                continue
            suggestion = parameter_suggestion(class_type, field, value)
            if suggestion is None:
                continue
            name = unique_name(suggestion["name"], node_id, seen_names)
            suggestion.update(
                {
                    "name": name,
                    "node_id": node_id,
                    "field": field,
                    "class_type": class_type,
                    "current_value": value,
                }
            )
            params.append(suggestion)
    return params


def parameter_suggestion(class_type: str, field: str, value: Any) -> dict[str, Any] | None:
    lower_class = class_type.lower()
    if field in {"text", "prompt"} and ("text" in lower_class or "prompt" in lower_class or "cliptextencode" in lower_class):
        return {
            "name": "prompt",
            "type": "string",
            "required": True,
            "description": "Text prompt exposed to the agent or user",
        }
    if field == "seed":
        return {
            "name": "seed",
            "type": "int",
            "required": False,
            "description": "Random seed for reproducibility",
        }
    if field in {"steps", "cfg", "denoise", "width", "height", "batch_size", "size"}:
        return {
            "name": field,
            "type": value_type(value),
            "required": False,
            "description": f"Workflow parameter: {field}",
        }
    if field in {"sampler_name", "scheduler", "filename_prefix"}:
        return {
            "name": field,
            "type": "string",
            "required": False,
            "description": f"Workflow parameter: {field}",
        }
    if class_type == "LoadImage" and field == "image":
        return {
            "name": "image",
            "type": "image",
            "required": True,
            "description": "Input image uploaded before execution",
        }
    return None


def value_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "int"
    if isinstance(value, float):
        return "float"
    return "string"


def unique_name(base: str, node_id: str, seen: set[str]) -> str:
    clean = re.sub(r"[^\w]+", "_", base.strip().lower()).strip("_") or "param"
    name = clean
    if name in seen:
        name = f"{clean}_{node_id}"
    counter = 2
    while name in seen:
        name = f"{clean}_{node_id}_{counter}"
        counter += 1
    seen.add(name)
    return name


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    base_url = normalize_base_url(args.server)
    report: dict[str, Any] = {
        "server": base_url,
        "endpoints": {},
        "model_folders": {},
    }

    endpoint_paths = {
        "system_stats": "/system_stats",
        "object_info": "/object_info",
        "models": "/models",
        "queue": "/queue",
    }
    raw_results: dict[str, dict[str, Any]] = {}
    for name, path in endpoint_paths.items():
        result = get_json(base_url, path, args.timeout)
        raw_results[name] = result
        report["endpoints"][name] = compact_endpoint_result(result)

    folders = args.model_folder or list(DEFAULT_MODEL_FOLDERS)
    model_summary, names_by_folder = model_folder_summary(base_url, folders, args.timeout)
    report["model_folders"] = model_summary

    if args.workflow:
        workflow_path = Path(args.workflow)
        workflow, load_issues = load_workflow(workflow_path)
        workflow_report = inspect_workflow_shape(workflow)
        workflow_report["path"] = str(workflow_path)
        workflow_report["load_issues"] = load_issues
        workflow_report["suggested_parameters"] = suggest_parameters(workflow)
        model_refs = extract_model_refs(workflow)
        workflow_report["model_refs"] = classify_model_refs(model_refs, names_by_folder)

        object_info = raw_results.get("object_info", {}).get("payload")
        if isinstance(object_info, dict):
            known_classes = set(str(key) for key in object_info.keys())
            used_classes = workflow_node_classes(workflow)
            workflow_report["missing_class_types"] = sorted(used_classes - known_classes)
            workflow_report["verified_against_object_info"] = True
        else:
            workflow_report["missing_class_types"] = []
            workflow_report["verified_against_object_info"] = False

        report["workflow"] = workflow_report

    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe a local ComfyUI server and optionally sanity-check a ComfyUI workflow."
    )
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:8188",
        help="ComfyUI server base URL, default: http://127.0.0.1:8188",
    )
    parser.add_argument(
        "--workflow",
        help="Path to an API-format or editor-format workflow JSON file to inspect.",
    )
    parser.add_argument(
        "--model-folder",
        action="append",
        help="Model folder to query with /models/{folder}. Repeatable. Defaults to common folders.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="HTTP timeout in seconds, default: 3.0",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = build_report(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))

    endpoints = report.get("endpoints", {})
    any_endpoint_ok = any(item.get("ok") for item in endpoints.values() if isinstance(item, dict))
    workflow = report.get("workflow")
    workflow_has_issues = isinstance(workflow, dict) and (
        workflow.get("issues") or workflow.get("load_issues") or workflow.get("missing_class_types")
    )

    if workflow_has_issues:
        return 1
    if not any_endpoint_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
