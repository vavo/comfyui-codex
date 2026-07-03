#!/usr/bin/env python3
"""Resolve missing ComfyUI class_type values to likely custom node packs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from comfy_probe import load_workflow, workflow_node_classes


DEFAULT_NEXT_CHECKS = [
    "Use ComfyUI-Manager's missing-node install flow when available, then restart ComfyUI.",
    "If a class remains unresolved, inspect the workflow source or ask the workflow author for the required custom node pack.",
    "After installation, verify the class appears in /object_info before running the workflow.",
]


def load_rules(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    rules = payload.get("rules") if isinstance(payload, dict) else None
    if not isinstance(rules, list):
        raise ValueError("resolver map must contain a rules list")

    cleaned: list[dict[str, str]] = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        match = str(rule.get("match", ""))
        value = str(rule.get("value", ""))
        package = str(rule.get("package", ""))
        if match and value and package:
            cleaned.append(
                {
                    "match": match,
                    "value": value,
                    "package": package,
                    "confidence": str(rule.get("confidence", "medium")),
                    "reason": str(rule.get("reason", "")),
                }
            )
    return cleaned


def classes_from_workflow(path: Path) -> list[str]:
    workflow, load_issues = load_workflow(path)
    if load_issues:
        raise ValueError("; ".join(load_issues))
    return sorted(workflow_node_classes(workflow))


def rule_matches(rule: dict[str, str], class_type: str) -> bool:
    match = rule["match"]
    value = rule["value"]
    if match == "exact":
        return class_type == value
    if match == "prefix":
        return class_type.startswith(value)
    if match == "contains":
        return value.lower() in class_type.lower()
    if match == "suffix":
        return class_type.endswith(value)
    return False


def resolve_one(class_type: str, rules: list[dict[str, str]]) -> dict[str, str] | None:
    for rule in rules:
        if rule_matches(rule, class_type):
            return {
                "class_type": class_type,
                "confidence": rule["confidence"],
                "match": rule["match"],
                "package": rule["package"],
                "reason": rule["reason"],
            }
    return None


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    rules = load_rules(Path(args.map_json))
    classes = list(args.class_type or [])
    if args.workflow:
        classes.extend(classes_from_workflow(Path(args.workflow)))
    classes = sorted(dict.fromkeys(classes))

    resolved: list[dict[str, str]] = []
    unresolved: list[str] = []
    for class_type in classes:
        match = resolve_one(class_type, rules)
        if match:
            resolved.append(match)
        else:
            unresolved.append(class_type)

    report: dict[str, Any] = {
        "next_checks": DEFAULT_NEXT_CHECKS,
        "resolved": resolved,
        "unresolved": unresolved,
    }
    if not args.omit_path:
        report["map_json"] = str(Path(args.map_json))
        if args.workflow:
            report["workflow"] = str(Path(args.workflow))
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map missing ComfyUI class_type values to likely custom node packs."
    )
    parser.add_argument("class_type", nargs="*", help="Missing ComfyUI class_type value.")
    parser.add_argument(
        "--workflow",
        help="Optional workflow JSON to extract class_type values from.",
    )
    parser.add_argument(
        "--map-json",
        required=True,
        help="JSON resolver map with exact/prefix/contains rules.",
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
    return 1 if report["unresolved"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
