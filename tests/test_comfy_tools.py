from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "comfyui-codex" / "skills" / "comfyui"
SCRIPTS = SKILL / "scripts"
FIXTURES = SKILL / "fixtures"


def run_json(script: str, *args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"{script} did not emit JSON\nexit={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
        ) from exc
    return proc.returncode, payload


def expected(name: str) -> dict:
    return json.loads((FIXTURES / "expected" / name).read_text(encoding="utf-8"))


class ComfyToolTests(unittest.TestCase):
    def test_workflow_lint_reports_valid_api_workflow(self) -> None:
        code, payload = run_json(
            "workflow_lint.py",
            str(FIXTURES / "workflows" / "basic_api.json"),
            "--omit-path",
        )

        self.assertEqual(code, 0)
        self.assertEqual(payload, expected("workflow_lint_basic.json"))

    def test_workflow_lint_rejects_broken_links(self) -> None:
        code, payload = run_json(
            "workflow_lint.py",
            str(FIXTURES / "workflows" / "broken_link_api.json"),
            "--omit-path",
        )

        self.assertEqual(code, 1)
        self.assertEqual(payload, expected("workflow_lint_broken_link.json"))

    def test_model_audit_detects_missing_model_from_fixture(self) -> None:
        code, payload = run_json(
            "model_audit.py",
            str(FIXTURES / "workflows" / "missing_model_api.json"),
            "--models-json",
            str(FIXTURES / "server" / "models.json"),
            "--omit-path",
        )

        self.assertEqual(code, 1)
        self.assertEqual(payload, expected("model_audit_missing.json"))

    def test_comfy_doctor_uses_snapshot_without_live_server(self) -> None:
        code, payload = run_json(
            "comfy_doctor.py",
            "--snapshot",
            str(FIXTURES / "server" / "server_snapshot.json"),
            "--workflow",
            str(FIXTURES / "workflows" / "basic_api.json"),
            "--omit-path",
        )

        self.assertEqual(code, 0)
        self.assertEqual(payload, expected("comfy_doctor_snapshot.json"))

    def test_error_explainer_classifies_missing_custom_node(self) -> None:
        code, payload = run_json(
            "error_explainer.py",
            str(FIXTURES / "errors" / "node_errors_missing_class.json"),
            "--omit-path",
        )

        self.assertEqual(code, 1)
        self.assertEqual(payload, expected("error_explainer_missing_class.json"))

    def test_custom_node_resolver_maps_known_classes_and_flags_unknown(self) -> None:
        code, payload = run_json(
            "custom_node_resolver.py",
            "IPAdapterModelLoader",
            "MadeUpPrivateNode",
            "--map-json",
            str(FIXTURES / "custom_nodes" / "class_resolver.json"),
            "--omit-path",
        )

        self.assertEqual(code, 1)
        self.assertEqual(payload, expected("custom_node_resolver_mixed.json"))

    def test_workflow_catalog_validates_golden_workflows(self) -> None:
        code, payload = run_json(
            "workflow_catalog.py",
            "--catalog-json",
            str(FIXTURES / "golden_workflows" / "catalog.json"),
            "--omit-path",
        )

        self.assertEqual(code, 0)
        self.assertEqual(payload, expected("workflow_catalog.json"))


if __name__ == "__main__":
    unittest.main()
