#!/usr/bin/env python3
"""Offline ComfyUI workflow JSON linter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from comfy_probe import extract_model_refs, inspect_workflow_shape, load_workflow


def build_report(path: Path, include_path: bool) -> dict[str, Any]:
    workflow, load_issues = load_workflow(path)
    shape = inspect_workflow_shape(workflow)
    issues = [*load_issues, *shape.get("issues", [])]

    report: dict[str, Any] = {
        "class_types": shape.get("class_types", []),
        "format": shape.get("format", "unknown"),
        "has_output_node": bool(shape.get("has_output_node", False)),
        "issues": issues,
        "model_refs": extract_model_refs(workflow),
        "node_count": shape.get("node_count", 0),
        "warnings": shape.get("warnings", []),
    }
    if include_path:
        report["path"] = str(path)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate ComfyUI API/editor workflow JSON without a running server."
    )
    parser.add_argument("workflow", help="Path to a ComfyUI workflow JSON file.")
    parser.add_argument(
        "--omit-path",
        action="store_true",
        help="Omit path fields for stable fixture output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(Path(args.workflow), include_path=not args.omit_path)
    print(json.dumps(report, indent=2, sort_keys=True))

    if report["issues"]:
        return 1
    if report["format"] == "unknown":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
