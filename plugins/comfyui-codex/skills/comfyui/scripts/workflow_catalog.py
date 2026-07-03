#!/usr/bin/env python3
"""Validate a catalog of golden ComfyUI workflow fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from comfy_probe import inspect_workflow_shape, load_workflow


def load_catalog(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    workflows = payload.get("workflows") if isinstance(payload, dict) else None
    if not isinstance(workflows, list):
        raise ValueError("catalog JSON must contain a workflows list")
    return [item for item in workflows if isinstance(item, dict)]


def inspect_item(item: dict[str, Any], catalog_dir: Path, include_path: bool) -> dict[str, Any]:
    workflow_path = catalog_dir / str(item.get("path", ""))
    workflow, load_issues = load_workflow(workflow_path)
    shape = inspect_workflow_shape(workflow)
    issues = [*load_issues, *shape.get("issues", [])]

    report: dict[str, Any] = {
        "class_types": shape.get("class_types", []),
        "format": shape.get("format", "unknown"),
        "has_output_node": bool(shape.get("has_output_node", False)),
        "id": str(item.get("id", "")),
        "issues": issues,
        "node_count": shape.get("node_count", 0),
        "type": str(item.get("type", "uncategorized")),
        "warnings": shape.get("warnings", []),
    }
    if include_path:
        report["path"] = str(workflow_path)
    return report


def summarize_by_type(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        kind = str(item.get("type", "uncategorized"))
        counts[kind] = counts.get(kind, 0) + 1
    return dict(sorted(counts.items()))


def build_report(path: Path, include_path: bool) -> dict[str, Any]:
    raw_items = load_catalog(path)
    items = [inspect_item(item, path.parent, include_path) for item in raw_items]
    invalid = sum(1 for item in items if item["issues"] or item["format"] == "unknown")
    report: dict[str, Any] = {
        "by_type": summarize_by_type(items),
        "invalid": invalid,
        "items": items,
        "total": len(items),
        "valid": len(items) - invalid,
    }
    if include_path:
        report["catalog_path"] = str(path)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate golden ComfyUI workflow fixtures listed in a catalog JSON."
    )
    parser.add_argument("--catalog-json", required=True, help="Path to catalog JSON.")
    parser.add_argument(
        "--omit-path",
        action="store_true",
        help="Omit path fields for stable fixture output.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        report = build_report(Path(args.catalog_json), include_path=not args.omit_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["invalid"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
