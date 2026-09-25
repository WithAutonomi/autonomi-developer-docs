"""Offline scanner regressions. All upstream HTTP and Git responses are mocks."""

from __future__ import annotations

import ast
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import types
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import call, patch

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "sweep_poll.py"
BASELINE = "33c042d5a85322f226ae8e6385432137cd77603c"
RECORDED = "a" * 40
HEAD = "b" * 40
BLOCK = """<!-- verification:
  source_repo: example
  source_ref: release/docs
  source_commit: {sha}
  verified_date: 2026-09-22
  verification_mode: current-merged-truth
-->
"""

spec = importlib.util.spec_from_file_location("sweep_poll", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class SweepPollTest(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.repo = Path(temp_dir.name)
        (self.repo / "docs").mkdir()
        (self.repo / "repo-registry.yml").write_text(
            "repos:\n  example:\n    url: https://github.com/example/source.git\n",
            encoding="utf-8",
        )
        self.page = self.repo / "docs" / "example.md"
        self.page.write_text(BLOCK.format(sha=RECORDED), encoding="utf-8")

    def run_scanner(self, module=scanner, *, token=" offline-test-token ",
                    responses=None, git_result=None):
        output = io.StringIO()
        paths = {
            "REPO_ROOT": self.repo,
            "DOCS_DIR": self.repo / "docs",
            "REGISTRY_PATH": self.repo / "repo-registry.yml",
        }
        # Only the historical scanner has these paths; point it at the fixture too.
        if hasattr(module, "VERSION_JSON_PATH"):
            paths["VERSION_JSON_PATH"] = self.repo / "skills/start/version.json"
            paths["SKILL_MD_PATH"] = self.repo / "skills/start/SKILL.md"
        with (
            patch.multiple(module, **paths),
            patch.dict(os.environ, {"GITHUB_TOKEN": token}),
            patch.object(module, "_github_get", return_value={"sha": HEAD},
                         side_effect=responses) as http,
            patch.object(module.subprocess, "run", return_value=git_result,
                         side_effect=None if git_result else
                         AssertionError("Unexpected upstream Git call")) as git,
            contextlib.redirect_stdout(output),
        ):
            code = module.main()
        report = json.loads(output.getvalue())
        self.assertEqual(set(report), {
            "status", "generated_at", "records", "target_manifest_skipped",
            "notices", "errors",
        })
        self.assertTrue(report.pop("generated_at"))
        return code, report, http.call_args_list, git.call_args_list

    def test_docs_without_skills_keep_records_and_declared_refs(self) -> None:
        self.assertFalse((self.repo / "skills").exists())
        self.page.write_text(
            BLOCK.format(sha=RECORDED) + BLOCK.format(sha=HEAD), encoding="utf-8"
        )
        nested = self.repo / "docs" / "nested"
        nested.mkdir()
        (nested / "tag.md").write_text(
            BLOCK.format(sha=RECORDED).replace("release/docs", "v1.2.3"),
            encoding="utf-8",
        )

        code, report, http, git = self.run_scanner()

        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["records"], [
            {"location": location, "scope": "docs", "repo": "example",
             "ref": ref, "recorded_sha": recorded, "head_sha": HEAD,
             "drifted": recorded != HEAD}
            for location, ref, recorded in [
                ("docs/example.md:1", "release/docs", RECORDED),
                ("docs/example.md:8", "release/docs", HEAD),
                ("docs/nested/tag.md:1", "v1.2.3", RECORDED),
            ]
        ])
        self.assertEqual(http, [
            call("https://api.github.com/repos/example/source/commits/release%2Fdocs",
                 "offline-test-token"),
            call("https://api.github.com/repos/example/source/commits/v1.2.3",
                 "offline-test-token"),
        ])
        self.assertEqual(git, [])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["notices"], [])

    def test_target_manifest_is_reported_without_upstream_lookup(self) -> None:
        self.page.write_text(
            BLOCK.format(sha=RECORDED).replace("current-merged-truth", "target-manifest"),
            encoding="utf-8",
        )
        code, report, http, git = self.run_scanner()
        self.assertEqual(code, 0)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["target_manifest_skipped"], [{
            "location": "docs/example.md:1", "repo": "example",
            "ref": "release/docs", "recorded_sha": RECORDED,
        }])
        self.assertEqual((http, git), ([], []))

    def test_malformed_verification_fails_closed_before_lookup(self) -> None:
        valid = BLOCK.format(sha=RECORDED)
        cases = [
            (valid.replace(f"  {key}: {value}\n", ""),
             "doc_block_missing_required_keys")
            for key, value in [
                ("source_repo", "example"), ("source_ref", "release/docs"),
                ("source_commit", RECORDED), ("verification_mode", "current-merged-truth"),
            ]
        ] + [
            (valid.replace("current-merged-truth", "unknown"),
             "doc_block_unknown_verification_mode"),
            (valid.replace("source_repo: example", "source_repo: unknown"),
             "doc_block_unknown_source_repo"),
        ]
        for malformed, kind in cases:
            with self.subTest(kind=kind, block=malformed):
                self.page.write_text(valid + malformed, encoding="utf-8")
                code, report, http, git = self.run_scanner()
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "error")
                self.assertEqual(report["records"], [])
                self.assertEqual(report["target_manifest_skipped"], [])
                self.assertEqual(report["errors"][0]["kind"], kind)
                self.assertEqual(report["errors"][0]["location"], "docs/example.md:8")
                self.assertEqual((http, git), ([], []))

    def test_retired_artifacts_are_not_read(self) -> None:
        skill_dir = self.repo / "skills" / "start"
        skill_dir.mkdir(parents=True)
        for name in ("SKILL.md", "version.json"):
            (skill_dir / name).write_text("invalid retired artifact", encoding="utf-8")
        code, report, http, _ = self.run_scanner()
        self.assertEqual(code, 0)
        self.assertEqual(len(report["records"]), 1)
        self.assertEqual(report["records"][0]["scope"], "docs")
        self.assertEqual(len(http), 1)

    def test_empty_docs_succeeds_without_upstream_requests(self) -> None:
        self.page.write_text("# No verification blocks\n", encoding="utf-8")
        code, report, http, git = self.run_scanner(token="")
        self.assertEqual(code, 0)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["notices"][0]["kind"], "unauthenticated_mode")
        self.assertEqual((http, git), ([], []))

    def test_missing_head_sha_fails_closed(self) -> None:
        code, report, _, git = self.run_scanner(responses=[{}])
        self.assertEqual(code, 2)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["errors"][0]["kind"], "github_head_sha_missing")
        self.assertEqual(git, [])

    def test_git_sha_fallback_preserves_declared_ref(self) -> None:
        code, report, _, git = self.run_scanner(
            responses=urllib.error.URLError("offline mock outage"),
            git_result=subprocess.CompletedProcess(
                [], 0, f"{HEAD}\trefs/heads/release/docs\n", ""
            ),
        )
        self.assertEqual(code, 0)
        self.assertEqual(report["records"][0]["head_sha"], HEAD)
        self.assertEqual(git, [call(
            ["git", "ls-remote", "--exit-code",
             "https://github.com/example/source.git", "release/docs"],
            capture_output=True, text=True, timeout=30, check=False,
        )])

    def test_exhausted_auth_anonymous_and_git_fallbacks_keep_diagnostics(self) -> None:
        errors = [
            urllib.error.HTTPError(
                "https://api.github.com/mock", 403, "Forbidden",
                {"x-github-request-id": request_id, "x-ratelimit-remaining": "0",
                 "retry-after": "60"},
                io.BytesIO(json.dumps({"message": message}).encode()),
            )
            for request_id, message in [("auth-mock", "mock token refused"),
                                        ("anon-mock", "mock quota exhausted")]
        ]
        code, report, http, git = self.run_scanner(
            responses=errors,
            git_result=subprocess.CompletedProcess([], 128, "", "mock Git unavailable"),
        )
        self.assertEqual(code, 2)
        self.assertEqual(report["records"], [])
        diagnostic = report["errors"][0]
        self.assertEqual(diagnostic["kind"], "github_api_http_error")
        self.assertEqual(diagnostic["auth"]["body_message"], "mock token refused")
        self.assertEqual(diagnostic["anon"]["request_id"], "anon-mock")
        self.assertEqual(diagnostic["anon"]["ratelimit_remaining"], "0")
        self.assertEqual(diagnostic["anon"]["retry_after"], "60")
        self.assertEqual(diagnostic["git_ls_remote"]["ref"], "release/docs")
        self.assertIn("mock Git unavailable", diagnostic["git_ls_remote"]["error"])
        self.assertEqual([args.args[1] for args in http], ["offline-test-token", None])
        self.assertEqual(len(git), 1)

    def test_docs_reports_match_pre_retirement_baseline(self) -> None:
        result = subprocess.run(
            ["git", "show", f"{BASELINE}:scripts/sweep_poll.py"],
            cwd=SCRIPT.parent, capture_output=True, text=True, check=False,
        )
        if result.returncode:
            self.skipTest(f"Baseline history unavailable: {result.stderr.strip()}")
        baseline = types.ModuleType("baseline_sweep_poll")
        baseline.__file__ = str(SCRIPT)
        exec(compile(result.stdout, str(SCRIPT), "exec"), baseline.__dict__)
        original_functions = {
            node.name: ast.get_source_segment(result.stdout, node)
            for node in ast.parse(result.stdout).body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))
        }
        current = SCRIPT.read_text(encoding="utf-8")
        for node in ast.parse(current).body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name != "main":
                self.assertEqual(ast.get_source_segment(current, node),
                                 original_functions[node.name], node.name)
        valid = BLOCK.format(sha=RECORDED)
        for content in (
            valid + BLOCK.format(sha=HEAD),
            valid.replace("release/docs", "v1.2.3"),
            valid.replace("release/docs", HEAD),
            valid + valid.replace("current-merged-truth", "target-manifest"),
            valid.replace("  source_ref: release/docs\n", ""),
            valid.replace("current-merged-truth", "unknown"),
            valid.replace("source_repo: example", "source_repo: unknown"),
            "# No verification blocks\n",
        ):
            with self.subTest(content=content):
                self.page.write_text(content, encoding="utf-8")
                self.assertEqual(
                    self.run_scanner(token=""),
                    self.run_scanner(baseline, token=""),
                )
        self.page.write_text(valid, encoding="utf-8")
        for git_result in (
            subprocess.CompletedProcess([], 0, f"{HEAD}\trefs/heads/release/docs\n", ""),
            subprocess.CompletedProcess([], 128, "", "mock Git unavailable"),
        ):
            with self.subTest(git_returncode=git_result.returncode):
                options = {"responses": urllib.error.URLError("offline mock outage"),
                           "git_result": git_result}
                self.assertEqual(self.run_scanner(**options),
                                 self.run_scanner(baseline, **options))

    def test_registry_retains_all_non_skill_fields(self) -> None:
        result = subprocess.run(
            ["git", "show", f"{BASELINE}:component-registry.yml"],
            cwd=SCRIPT.parent, capture_output=True, text=True, check=False,
        )
        if result.returncode:
            self.skipTest(f"Baseline history unavailable: {result.stderr.strip()}")
        original = yaml.safe_load(result.stdout)
        removed = 0
        for component in original["components"].values():
            if "feeds_skills" in component:
                del component["feeds_skills"]
                removed += 1
        self.assertEqual(removed, 25)
        current = yaml.safe_load(
            (SCRIPT.parent.parent / "component-registry.yml").read_text(encoding="utf-8")
        )
        self.assertEqual(current, original)


if __name__ == "__main__":
    unittest.main()
