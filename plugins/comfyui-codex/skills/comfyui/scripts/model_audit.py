#!/usr/bin/env python3
"""Audit ComfyUI workflow model references against live or fixture model lists."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from comfy_probe import (
    DEFAULT_MODEL_FOLDERS,
    classify_model_refs,
    extract_model_refs,
    inspect_workflow_shape,
    load_workflow,
    model_folder_summary,
    normalize_base_url,
)


def load_models_json(path: Path) -> dict[str, set[str]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("models JSON must be an object mapping folder names to lists")

    names_by_folder: dict[str, set[str]] = {}
    for folder, names in payload.items():
        if not isinstance(names, list):
            raise ValueError(f"models JSON folder {folder!r} must be a list")
        names_by_folder[str(folder)] = {str(name) for name in names}
    return names_by_folder


def split_refs(refs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    present = [ref for ref in refs if ref.get("status") == "present"]
    missing = [ref for ref in refs if ref.get("status") == "missing"]
    unverified = [ref for ref in refs if ref.get("status") == "unverified"]
    return present, missing, unverified


def summarize_refs(refs: list[dict[str, Any]]) -> dict[str, int]:
    present, missing, unverified = split_refs(refs)
    return {
        "missing": len(missing),
        "present": len(present),
        "total_refs": len(refs),
        "unverified": len(unverified),
    }


def model_names_from_args(args: argparse.Namespace, refs: list[dict[str, Any]]) -> dict[str, set[str]]:
    if args.models_json:
        return load_models_json(Path(args.models_json))

    folders = sorted({str(ref["folder"]) for ref in refs}) or list(DEFAULT_MODEL_FOLDERS)
    base_url = normalize_base_url(args.server)
    _summary, names_by_folder = model_folder_summary(base_url, folders, args.timeout)
    return names_by_folder


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    workflow_path = Path(args.workflow)
    workflow, load_issues = load_workflow(workflow_path)
    shape = inspect_workflow_shape(workflow)
    issues = [*load_issues, *shape.get("issues", [])]
    refs = extract_model_refs(workflow)
    checked_refs = classify_model_refs(refs, model_names_from_args(args, refs))
    present, missing, unverified = split_refs(checked_refs)

    report: dict[str, Any] = {
        "format": shape.get("format", "unknown"),
        "issues": issues,
        "missing_refs": missing,
        "model_refs": checked_refs,
        "present_refs": present,
        "summary": summarize_refs(checked_refs),
        "unverified_refs": unverified,
    }
    if not args.omit_path:
        report["path"] = str(workflow_path)
    return report


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare ComfyUI workflow model loader references against /models data."
    )
    parser.add_argument("workflow", help="Path to an API-format ComfyUI workflow JSON file.")
    parser.add_argument(
        "--server",
        default="http://127.0.0.1:8188",
        help="ComfyUI server base URL for live /models checks.",
    )
    parser.add_argument(
        "--models-json",
        help="Fixture JSON mapping model folders to filenames. Skips live server calls.",
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

    if report["issues"] or report["missing_refs"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
