#!/usr/bin/env python3
"""Read-only ComfyUI server/workflow doctor with offline snapshot support."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from comfy_probe import (
    DEFAULT_MODEL_FOLDERS,
    classify_model_refs,
    compact_endpoint_result,
    extract_model_refs,
    get_json,
    inspect_workflow_shape,
    load_workflow,
    model_folder_summary,
    normalize_base_url,
    workflow_node_classes,
)


ENDPOINT_PATHS = {
    "extensions": "/extensions",
    "models": "/models",
    "object_info": "/object_info",
    "queue": "/queue",
    "system_stats": "/system_stats",
}


def load_snapshot(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("snapshot must be a JSON object")
    return payload


def fetch_live(base_url: str, timeout: float) -> dict[str, dict[str, Any]]:
    endpoints: dict[str, dict[str, Any]] = {}
    for name, route in ENDPOINT_PATHS.items():
        endpoints[name] = get_json(base_url, route, timeout)
    return endpoints


def endpoint_health(endpoints: dict[str, Any]) -> dict[str, int]:
    ok = sum(1 for result in endpoints.values() if isinstance(result, dict) and result.get("ok"))
    failed = sum(1 for result in endpoints.values() if isinstance(result, dict) and not result.get("ok"))
    return {"failed": failed, "ok": ok}


def summarize_system(system_stats: dict[str, Any] | None) -> dict[str, Any]:
    payload = system_stats.get("payload") if isinstance(system_stats, dict) else None
    if not isinstance(payload, dict):
        return {"device_count": 0, "python_version": None}

    system = payload.get("system")
    devices = payload.get("devices")
    python_version = None
    if isinstance(system, dict):
        python_version = system.get("python_version") or system.get("python")
    return {
        "device_count": len(devices) if isinstance(devices, list) else 0,
        "python_version": python_version,
    }


def detect_manager(endpoints: dict[str, Any]) -> dict[str, Any]:
    signals: list[str] = []
    extensions = endpoints.get("extensions", {}).get("payload") if isinstance(endpoints.get("extensions"), dict) else None
    if isinstance(extensions, list) and any("manager" in str(item).lower() for item in extensions):
        signals.append("extensions")

    object_info = endpoints.get("object_info", {}).get("payload") if isinstance(endpoints.get("object_info"), dict) else None
    if isinstance(object_info, dict) and any("manager" in str(key).lower() for key in object_info):
        signals.append("object_info")

    return {
        "signals": signals,
        "status": "detected" if signals else "unverified",
    }


def summarize_model_folders(model_folders: dict[str, set[str]]) -> dict[str, dict[str, int]]:
    return {
        folder: {"count": len(names)}
        for folder, names in sorted(model_folders.items())
    }


def snapshot_model_folders(snapshot: dict[str, Any]) -> dict[str, set[str]]:
    raw = snapshot.get("model_folders", {})
    if not isinstance(raw, dict):
        return {}
    folders: dict[str, set[str]] = {}
    for folder, names in raw.items():
        if isinstance(names, list):
            folders[str(folder)] = {str(name) for name in names}
    return folders


def live_model_folders(base_url: str, folders: list[str], timeout: float) -> dict[str, set[str]]:
    _summary, names_by_folder = model_folder_summary(base_url, folders, timeout)
    return names_by_folder


def summarize_model_refs(refs: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "missing": sum(1 for ref in refs if ref.get("status") == "missing"),
        "present": sum(1 for ref in refs if ref.get("status") == "present"),
        "total_refs": len(refs),
        "unverified": sum(1 for ref in refs if ref.get("status") == "unverified"),
    }


def workflow_report(path: Path, endpoints: dict[str, Any], model_folders: dict[str, set[str]]) -> dict[str, Any]:
    workflow, load_issues = load_workflow(path)
    shape = inspect_workflow_shape(workflow)
    issues = [*load_issues, *shape.get("issues", [])]

    object_info = endpoints.get("object_info", {}).get("payload") if isinstance(endpoints.get("object_info"), dict) else None
    if isinstance(object_info, dict):
        known_classes = {str(key) for key in object_info}
        missing_class_types = sorted(workflow_node_classes(workflow) - known_classes)
    else:
        missing_class_types = []

    refs = classify_model_refs(extract_model_refs(workflow), model_folders)
    return {
        "format": shape.get("format", "unknown"),
        "issues": issues,
        "missing_class_types": missing_class_types,
        "model_summary": summarize_model_refs(refs),
        "node_count": shape.get("node_count", 0),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    if args.snapshot:
        snapshot = load_snapshot(Path(args.snapshot))
        endpoints = snapshot.get("endpoints", {})
        if not isinstance(endpoints, dict):
            raise ValueError("snapshot endpoints must be an object")
        server = str(snapshot.get("server", "snapshot"))
        mode = "snapshot"
        names_by_folder = snapshot_model_folders(snapshot)
    else:
        server = normalize_base_url(args.server)
        mode = "live"
        endpoints = fetch_live(server, args.timeout)
        folders = args.model_folder or list(DEFAULT_MODEL_FOLDERS)
        names_by_folder = live_model_folders(server, folders, args.timeout)

    report: dict[str, Any] = {
        "endpoint_health": endpoint_health(endpoints),
        "manager": detect_manager(endpoints),
        "mode": mode,
        "model_folders": summarize_model_folders(names_by_folder),
        "server": server,
        "system": summarize_system(endpoints.get("system_stats") if isinstance(endpoints, dict) else None),
    }

    if args.workflow:
        report["workflow"] = workflow_report(Path(args.workflow), endpoints, names_by_folder)
        if not args.omit_path:
            report["workflow"]["path"] = str(Path(args.workflow))

    if not args.omit_path and args.snapshot:
        report["snapshot"] = str(Path(args.snapshot))

    if mode == "live":
        report["endpoints"] = {
            name: compact_endpoint_result(result)
            for name, result in sorted(endpoints.items())
            if isinstance(result, dict)
        }

    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Probe ComfyUI server health, Manager/custom-node signals, model folders, and optional workflow fit."
    )
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:8188",
        help="ComfyUI server base URL for live checks.",
    )
    parser.add_argument(
        "--snapshot",
        help="Offline snapshot JSON containing endpoints and model_folders.",
    )
    parser.add_argument(
        "--workflow",
        help="Optional workflow JSON to validate against endpoint/model evidence.",
    )
    parser.add_argument(
        "--model-folder",
        action="append",
        help="Model folder to query in live mode. Repeatable.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="HTTP timeout in seconds for live server checks.",
    )
    parser.add_argument(
        "--omit-path",
        action="store_true",
        help="Omit path fields for stable fixture output.",
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

    if report["endpoint_health"]["ok"] == 0:
        return 1
    workflow = report.get("workflow")
    if isinstance(workflow, dict) and (
        workflow.get("issues")
        or workflow.get("missing_class_types")
        or workflow.get("model_summary", {}).get("missing", 0)
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
