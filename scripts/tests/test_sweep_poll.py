"""Offline scanner regressions. All upstream HTTP and Git responses are mocks."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

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
        (self.repo / "component-registry.yml").write_text(
            "components: {}\n", encoding="utf-8"
        )
        self.page = self.repo / "docs" / "example.md"
        self.page.write_text(BLOCK.format(sha=RECORDED), encoding="utf-8")

    def run_scanner(self, *, token=" offline-test-token "):
        output = io.StringIO()
        paths = {
            "REPO_ROOT": self.repo,
            "DOCS_DIR": self.repo / "docs",
            "REGISTRY_PATH": self.repo / "repo-registry.yml",
            "COMPONENT_REGISTRY_PATH": self.repo / "component-registry.yml",
            "TARGET_MANIFEST_PATH": self.repo / "target-manifest.yml",
        }
        with (
            patch.multiple(scanner, **paths),
            patch.dict(os.environ, {"GITHUB_TOKEN": token}),
            patch.object(
                scanner,
                "_github_get",
                side_effect=AssertionError("Unexpected upstream HTTP call"),
            ) as http,
            patch.object(
                scanner.urllib.request,
                "urlopen",
                side_effect=AssertionError("Unexpected provider HTTP call"),
            ),
            patch.object(
                subprocess,
                "run",
                side_effect=AssertionError("Unexpected upstream Git call"),
            ) as git,
            contextlib.redirect_stdout(output),
        ):
            code = scanner.main()
        self.assertEqual(git.call_args_list, [])
        report = json.loads(output.getvalue())
        report.setdefault("release_candidates", [])
        self.assertEqual(set(report), {
            "status", "generated_at", "records", "target_manifest_skipped",
            "migration_backlog", "release_candidates", "notices", "errors",
        })
        self.assertTrue(report.pop("generated_at"))
        return code, report, http.call_args_list

    def test_legacy_blocks_are_sorted_backlog_entries_without_upstream_lookup(self) -> None:
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

        code, report, http = self.run_scanner()

        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["records"], [])
        self.assertEqual(report["migration_backlog"], [
            {"location": location, "repo": "example", "ref": ref,
             "recorded_sha": recorded}
            for location, ref, recorded in [
                ("docs/example.md:1", "release/docs", RECORDED),
                ("docs/example.md:8", "release/docs", HEAD),
                ("docs/nested/tag.md:1", "v1.2.3", RECORDED),
            ]
        ])
        self.assertTrue(all(set(item) == {"location", "repo", "ref", "recorded_sha"}
                            for item in report["migration_backlog"]))
        self.assertEqual(http, [])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["notices"], [])

    def test_authenticated_403_retries_the_same_github_request_anonymously(self) -> None:
        auth_error = urllib.error.HTTPError(
            "https://api.github.com/mock",
            403,
            "Forbidden",
            {"x-github-request-id": "auth-request"},
            io.BytesIO(json.dumps({"message": "token refused"}).encode()),
        )
        with patch.object(
            scanner,
            "_github_get",
            side_effect=[auth_error, {"sha": HEAD}],
        ) as http:
            result = scanner.github_request("/repos/example/source/releases", "token")

        self.assertEqual(result, {"sha": HEAD})
        self.assertEqual(
            [attempt.args for attempt in http.call_args_list],
            [
                ("https://api.github.com/repos/example/source/releases", "token"),
                ("https://api.github.com/repos/example/source/releases", None),
            ],
        )

    def test_failed_authenticated_and_anonymous_reads_keep_both_diagnostics(self) -> None:
        errors = [
            urllib.error.HTTPError(
                "https://api.github.com/mock",
                403,
                "Forbidden",
                {
                    "x-github-request-id": request_id,
                    "x-ratelimit-remaining": remaining,
                },
                io.BytesIO(json.dumps({"message": message}).encode()),
            )
            for request_id, remaining, message in (
                ("auth-request", "4999", "token refused"),
                ("anonymous-request", "0", "quota exhausted"),
            )
        ]
        with patch.object(scanner, "_github_get", side_effect=errors) as http:
            with self.assertRaises(scanner.FailClosed) as raised:
                scanner.github_request("/repos/example/source/releases", "token")

        diagnostic = raised.exception.diagnostic
        self.assertEqual(diagnostic["kind"], "github_api_http_error")
        self.assertEqual(diagnostic["auth"]["body_message"], "token refused")
        self.assertEqual(diagnostic["auth"]["request_id"], "auth-request")
        self.assertEqual(diagnostic["anon"]["body_message"], "quota exhausted")
        self.assertEqual(diagnostic["anon"]["request_id"], "anonymous-request")
        self.assertEqual(diagnostic["anon"]["ratelimit_remaining"], "0")
        self.assertEqual(len(http.call_args_list), 2)

    def test_malformed_anonymous_retry_fails_closed_with_auth_diagnostic(self) -> None:
        auth_error = urllib.error.HTTPError(
            "https://api.github.com/mock",
            403,
            "Forbidden",
            {"x-github-request-id": "auth-request"},
            io.BytesIO(json.dumps({"message": "token refused"}).encode()),
        )
        malformed = json.JSONDecodeError("invalid fixture", "not-json", 0)
        with patch.object(scanner, "_github_get", side_effect=[auth_error, malformed]):
            with self.assertRaises(scanner.FailClosed) as raised:
                scanner.github_request("/repos/example/source/releases", "token")

        diagnostic = raised.exception.diagnostic
        self.assertEqual(diagnostic["kind"], "github_api_parse_error")
        self.assertEqual(diagnostic["auth"]["body_message"], "token refused")
        self.assertEqual(diagnostic["auth"]["request_id"], "auth-request")
        self.assertIn("invalid fixture", diagnostic["anon_parse_error"])

    def test_generic_provider_http_error_keeps_available_diagnostics(self) -> None:
        provider_error = urllib.error.HTTPError(
            "https://registry.npmjs.org/example",
            429,
            "Too Many Requests",
            {
                "x-github-request-id": "provider-request",
                "x-ratelimit-remaining": "0",
                "retry-after": "60",
            },
            io.BytesIO(json.dumps({"message": "quota exhausted"}).encode()),
        )
        with patch.object(scanner.urllib.request, "urlopen", side_effect=provider_error):
            with self.assertRaises(scanner.FailClosed) as raised:
                scanner._provider_json("https://registry.npmjs.org/example", "npm")

        diagnostic = raised.exception.diagnostic
        self.assertEqual(diagnostic["kind"], "npm_http_error")
        self.assertEqual(diagnostic["status"], 429)
        self.assertEqual(diagnostic["body_message"], "quota exhausted")
        self.assertEqual(diagnostic["request_id"], "provider-request")
        self.assertEqual(diagnostic["ratelimit_remaining"], "0")
        self.assertEqual(diagnostic["retry_after"], "60")

    def test_missing_component_registry_fails_closed_before_legacy_lookup(self) -> None:
        (self.repo / "component-registry.yml").unlink()

        code, report, http = self.run_scanner()

        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["records"], [])
        self.assertEqual(report["migration_backlog"], [])
        self.assertEqual(report["release_candidates"], [])
        self.assertEqual(report["errors"][0]["kind"], "component_registry_missing")
        self.assertEqual(http, [])

    def test_mixed_mode_page_separates_pins_from_legacy_backlog(self) -> None:
        self.page.write_text(
            BLOCK.format(sha=RECORDED).replace("current-merged-truth", "target-manifest")
            + BLOCK.format(sha=HEAD),
            encoding="utf-8",
        )
        code, report, http = self.run_scanner()
        self.assertEqual(code, 0)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["target_manifest_skipped"], [{
            "location": "docs/example.md:1", "repo": "example",
            "ref": "release/docs", "recorded_sha": RECORDED,
        }])
        self.assertEqual(report["migration_backlog"], [{
            "location": "docs/example.md:8", "repo": "example",
            "ref": "release/docs", "recorded_sha": HEAD,
        }])
        self.assertEqual(http, [])

    def test_malformed_verification_fails_closed_before_lookup(self) -> None:
        valid = BLOCK.format(sha=RECORDED)
        cases = [
            (valid.replace(f"  {key}: {value}\n", ""),
             "doc_block_missing_required_keys")
            for key, value in [
                ("source_repo", "example"), ("source_ref", "release/docs"),
                ("source_commit", RECORDED), ("verified_date", "2026-09-22"),
                ("verification_mode", "current-merged-truth"),
            ]
        ] + [
            (valid.replace("current-merged-truth", "unknown"),
             "doc_block_unknown_verification_mode"),
            (valid.replace("source_repo: example", "source_repo: unknown"),
             "doc_block_unknown_source_repo"),
            (valid.replace(f"source_commit: {RECORDED}", "source_commit: TBD"),
             "doc_block_invalid_source_commit"),
            (valid.replace("verified_date: 2026-09-22",
                           "verified_date: 2026-02-30"),
             "doc_block_invalid_verified_date"),
            (valid.replace("  verification_mode:",
                           "  source_repo: example\n  verification_mode:"),
             "doc_block_duplicate_key"),
            (valid.replace("  verification_mode:",
                           "  unsupported_field: value\n  verification_mode:"),
             "doc_block_unknown_keys"),
            (valid.replace("  verification_mode:",
                           "  this is not a field\n  verification_mode:"),
             "doc_block_unparseable_line"),
        ]
        for malformed, kind in cases:
            with self.subTest(kind=kind, block=malformed):
                self.page.write_text(valid + malformed, encoding="utf-8")
                code, report, http = self.run_scanner()
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "error")
                self.assertEqual(report["records"], [])
                self.assertEqual(report["target_manifest_skipped"], [])
                self.assertEqual(report["migration_backlog"], [])
                self.assertEqual(report["errors"][0]["kind"], kind)
                self.assertEqual(report["errors"][0]["location"], "docs/example.md:8")
                self.assertEqual(http, [])

    def test_retired_artifacts_are_not_read(self) -> None:
        skill_dir = self.repo / "skills" / "start"
        skill_dir.mkdir(parents=True)
        for name in ("SKILL.md", "version.json"):
            (skill_dir / name).write_text("invalid retired artifact", encoding="utf-8")
        code, report, http = self.run_scanner()
        self.assertEqual(code, 0)
        self.assertEqual(report["records"], [])
        self.assertEqual(len(report["migration_backlog"]), 1)
        self.assertEqual(http, [])

    def test_empty_docs_succeeds_without_upstream_requests(self) -> None:
        self.page.write_text("# No verification blocks\n", encoding="utf-8")
        code, report, http = self.run_scanner(token="")
        self.assertEqual(code, 0)
        self.assertEqual(report["records"], [])
        self.assertEqual(report["migration_backlog"], [])
        self.assertEqual(report["notices"][0]["kind"], "unauthenticated_mode")
        self.assertEqual(http, [])

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
        # Retiring the skill must not alter existing component data. New
        # components can be enrolled without rewriting this historical check.
        self.assertEqual(
            {key: value for key, value in current.items() if key != "components"},
            {key: value for key, value in original.items() if key != "components"},
        )
        for name, component in original["components"].items():
            with self.subTest(component=name):
                self.assertIn(name, current["components"])
                current_component = dict(current["components"][name])
                if name == "ant-cli":
                    self.assertIn("release_discovery", current_component)
                    del current_component["release_discovery"]
                self.assertEqual(current_component, component)


if __name__ == "__main__":
    unittest.main()
