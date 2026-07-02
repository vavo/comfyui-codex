#!/usr/bin/env python3
"""Read-only ComfyUI local server probe and API workflow sanity checker."""

from __future__ import annotations

import argparse
import json
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
    if not isinstance(workflow, dict):
        return set()
    classes: set[str] = set()
    for node in workflow.values():
        if isinstance(node, dict) and isinstance(node.get("class_type"), str):
            classes.add(node["class_type"])
    return classes


def inspect_workflow_shape(workflow: Any) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []

    if not isinstance(workflow, dict):
        return {
            "node_count": 0,
            "class_types": [],
            "issues": ["workflow top-level JSON must be an object"],
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
        "node_count": len(workflow),
        "class_types": sorted(class_types),
        "issues": issues,
        "warnings": warnings,
    }


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


def model_folder_summary(base_url: str, folders: list[str], timeout: float) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for folder in folders:
        encoded = urllib.parse.quote(folder, safe="")
        result = get_json(base_url, f"/models/{encoded}", timeout)
        compact = compact_endpoint_result(result)
        payload = result.get("payload")
        if result.get("ok") and isinstance(payload, list):
            compact["models"] = payload[:50]
            if len(payload) > 50:
                compact["truncated"] = True
        summary[folder] = compact
    return summary


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
    report["model_folders"] = model_folder_summary(base_url, folders, args.timeout)

    if args.workflow:
        workflow_path = Path(args.workflow)
        workflow, load_issues = load_workflow(workflow_path)
        workflow_report = inspect_workflow_shape(workflow)
        workflow_report["path"] = str(workflow_path)
        workflow_report["load_issues"] = load_issues

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
        description="Probe a local ComfyUI server and optionally sanity-check an API-format workflow."
    )
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:8188",
        help="ComfyUI server base URL, default: http://127.0.0.1:8188",
    )
    parser.add_argument(
        "--workflow",
        help="Path to an API-format workflow JSON file to inspect.",
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
