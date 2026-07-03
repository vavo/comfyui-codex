#!/usr/bin/env python3
"""Classify ComfyUI error payloads and logs into actionable buckets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


NEXT_CHECKS = {
    "missing_custom_node": [
        "Resolve missing class_type values with custom_node_resolver.py or ComfyUI-Manager's missing-node install flow.",
        "Verify /object_info after restart; missing classes should appear there before the workflow can run.",
        "Install or repair the custom node in the Python environment that actually runs ComfyUI.",
    ],
    "missing_model": [
        "Compare workflow model filenames against /models/{folder} with model_audit.py.",
        "Put the model in the folder expected by the loader node, then refresh or restart ComfyUI.",
    ],
    "dependency_import_error": [
        "Install missing Python dependencies into the environment that starts ComfyUI.",
        "Restart ComfyUI and check startup logs for the same import error.",
    ],
    "vram_oom": [
        "Reduce resolution, batch size, steps, or model size; use a lower-VRAM startup flag if appropriate.",
        "Free model memory or restart the runtime before retrying.",
    ],
    "server_unreachable": [
        "Confirm the ComfyUI server URL, port, tunnel/proxy, and startup logs.",
        "Check /system_stats before trying workflow-specific debugging.",
    ],
    "output_retrieval": [
        "Inspect /history/{prompt_id} for output filenames, subfolder, and type.",
        "Use /view only with filenames returned by history or preview output.",
    ],
}


PATTERNS = {
    "missing_custom_node": (
        re.compile(r"class(?:_type)?\s+['\"]?([A-Za-z0-9_:-]+)['\"]?\s+(?:does not exist|not found)", re.I),
        re.compile(r"unknown node class\s+['\"]?([A-Za-z0-9_:-]+)['\"]?", re.I),
    ),
    "missing_model": (
        re.compile(r"(?:checkpoint|lora|vae|controlnet|upscale model).*?(?:not found|missing|does not exist)", re.I),
        re.compile(r"\.(?:safetensors|ckpt|pth|pt|bin)\b.*?(?:not found|missing|does not exist)", re.I),
    ),
    "dependency_import_error": (
        re.compile(r"(?:ModuleNotFoundError|ImportError|No module named)", re.I),
    ),
    "vram_oom": (
        re.compile(r"(?:CUDA out of memory|OutOfMemoryError|MPS backend out of memory|VRAM)", re.I),
    ),
    "server_unreachable": (
        re.compile(r"(?:connection refused|timed out|name or service not known|failed to establish)", re.I),
    ),
    "output_retrieval": (
        re.compile(r"(?:/view|output).*?(?:not found|missing|404)", re.I),
    ),
}


def load_payload(path: Path) -> tuple[Any, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def first_message(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        message = value.get("message") or value.get("details") or value.get("type")
        return str(message) if message is not None else json.dumps(value, sort_keys=True)
    return str(value)


def node_error_evidence(payload: Any) -> tuple[list[str], list[dict[str, str]]]:
    categories: list[str] = []
    evidence: list[dict[str, str]] = []
    if not isinstance(payload, dict) or not isinstance(payload.get("node_errors"), dict):
        return categories, evidence

    categories.append("validation_node_errors")
    for node_id, node_error in sorted(payload["node_errors"].items(), key=lambda item: str(item[0])):
        if not isinstance(node_error, dict):
            continue
        class_type = str(node_error.get("class_type", ""))
        messages = node_error.get("errors")
        if not isinstance(messages, list):
            messages = [node_error]
        for item in messages:
            message = first_message(item)
            evidence.append(
                {
                    "class_type": class_type,
                    "kind": "node_error",
                    "message": message,
                    "node_id": str(node_id),
                }
            )
            if is_missing_class(message, class_type):
                categories.append("missing_custom_node")
            if matches_category("missing_model", message):
                categories.append("missing_model")
    return categories, evidence


def is_missing_class(message: str, class_type: str) -> bool:
    if not message:
        return False
    if any(pattern.search(message) for pattern in PATTERNS["missing_custom_node"]):
        return True
    lower = message.lower()
    return bool(class_type and class_type.lower() in lower and "does not exist" in lower)


def matches_category(category: str, text: str) -> bool:
    return any(pattern.search(text) for pattern in PATTERNS.get(category, ()))


def text_categories(text: str) -> list[str]:
    found: list[str] = []
    for category in PATTERNS:
        if matches_category(category, text):
            found.append(category)
    return found


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out


def build_report(path: Path, include_path: bool) -> dict[str, Any]:
    payload, text = load_payload(path)
    categories, evidence = node_error_evidence(payload)
    categories.extend(text_categories(text))
    categories = sorted(unique(categories))

    if not evidence and text.strip():
        evidence.append(
            {
                "kind": "text",
                "message": text.strip()[:500],
            }
        )

    next_checks: list[str] = []
    for category in categories:
        next_checks.extend(NEXT_CHECKS.get(category, []))
    next_checks = unique(next_checks)

    report: dict[str, Any] = {
        "categories": categories or ["unknown_error"],
        "evidence": evidence[:10],
        "next_checks": next_checks
        or ["Collect the exact ComfyUI error payload, startup logs, workflow JSON, and server URL."],
        "severity": "blocking" if categories else "unknown",
    }
    if include_path:
        report["path"] = str(path)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Explain a ComfyUI error payload or log using stable local playbooks."
    )
    parser.add_argument("error_file", help="Path to JSON error payload or text log excerpt.")
    parser.add_argument(
        "--omit-path",
        action="store_true",
        help="Omit path fields for stable fixture output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(Path(args.error_file), include_path=not args.omit_path)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["severity"] == "blocking" else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
