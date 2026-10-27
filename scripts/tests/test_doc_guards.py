"""Execute workflow Python against disposable Git histories; API tests are mocked.

Run: python3 -m unittest discover -s scripts/tests -p 'test_doc_guards.py' -v
Requires Python 3.10+ and the existing PyYAML dependency (CI uses Python 3.12).
No network or project commits are used.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import yaml

import test_release_following as release_fixtures


ROOT = Path(__file__).resolve().parents[2]
# Committed pre-retirement workflows, not a copy of their implementation.
BASELINE = "33c042d5a85322f226ae8e6385432137cd77603c"
GUARDS = ("sweep-guard", "prose-guard", "sweep-sha-reachability")
OLD_SHA = "a" * 40
NEW_SHA = "b" * 40
SUMMARY = "planning/sweeps/2026-09-22.md"
BROWSER_MANIFEST = """# Browser pin fixture.
scope:
  pages:
    - docs/pinned.md

sources:
  browser:
    source_ref: v1
    source_commit: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
"""
DOC = f"""# Store data

<!-- verification:
  source_repo: ant-sdk
  source_ref: release/v1
  source_commit: {OLD_SHA}
  verified_date: 2026-09-21
  verification_mode: current-merged-truth
-->

Store your data.
"""
PINNED = DOC.replace("current-merged-truth", "target-manifest")
REFRESHED = DOC.replace(OLD_SHA, NEW_SHA).replace("2026-09-21", "2026-09-22")
REGISTRY = "repos:\n  ant-sdk:\n    url: https://github.com/WithAutonomi/ant-sdk\n"
API = "https://api.github.com/repos/WithAutonomi/ant-sdk"
COMMIT_URL = f"{API}/commits/{NEW_SHA}"
COMPARE_URL = f"{API}/compare/{NEW_SHA}...release%2Fv1"


def load_workflow(name: str, baseline: bool = False) -> dict:
    path = f".github/workflows/{name}.yml"
    if baseline:
        text = subprocess.check_output(
            ["git", "show", f"{BASELINE}:{path}"], cwd=ROOT, text=True
        )
    else:
        text = (ROOT / path).read_text(encoding="utf-8")
    return yaml.safe_load(text)


def steps(workflow: dict) -> list[dict]:
    return next(iter(workflow["jobs"].values()))["steps"]


def embedded_python(workflow: dict) -> str:
    runs = [step["run"] for step in steps(workflow) if "<<'PY'" in step.get("run", "")]
    if len(runs) != 1:
        raise AssertionError("expected exactly one embedded Python guard")
    return runs[0].split("python3 - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]


class DocGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if sys.version_info < (3, 10):
            raise RuntimeError("The embedded workflows require Python 3.10+ (CI uses 3.12)")
        cls.current = {name: load_workflow(name) for name in GUARDS}
        cls.baseline = {name: load_workflow(name, baseline=True) for name in GUARDS}

    def history(self, changes=None, *, base_extra=None, renames=(), legacy=True,
                summary=True) -> None:
        temp = tempfile.TemporaryDirectory(prefix="doc-guard-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        # Fixture-only identity; do not read credentials or change Git config.
        self.env = {
            "PATH": os.environ["PATH"],
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "Guard fixture",
            "GIT_AUTHOR_EMAIL": "guard-fixture@example.invalid",
            "GIT_COMMITTER_NAME": "Guard fixture",
            "GIT_COMMITTER_EMAIL": "guard-fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-09-22T12:00:00Z",
            "GIT_COMMITTER_DATE": "2026-09-22T12:00:00Z",
            "GITHUB_STEP_SUMMARY": str(self.root / "summary.md"),
            "GITHUB_TOKEN": "mock-token-not-a-secret",
        }
        self.git("init", "-q")
        base_files = {
            "docs/page.md": DOC,
            "docs/pinned.md": PINNED,
            "repo-registry.yml": REGISTRY,
            "component-registry.yml": "components: {}\n",
            "scripts/protected.md": "Protected script fixture.\n",
            ".github/protected.md": "Protected workflow fixture.\n",
            "planning/sweeps/2026-09-21.md": "Previous summary.\n",
            "target-manifest.yml": BROWSER_MANIFEST,
            "scripts/validate_release_baselines.py": (
                ROOT / "scripts/validate_release_baselines.py"
            ).read_text(encoding="utf-8"),
        }
        if legacy:
            # Keep valid legacy files unchanged on BOTH sides for fair parity.
            base_files.update({
                "skills/start/version.json": json.dumps({
                    "version": "0.1.0-draft",
                    "published_date": "2026-09-21",
                    "verification_mode": "current-merged-truth",
                    "verified_commits": {"ant-sdk": OLD_SHA},
                }),
                "skills/start/SKILL.md": (
                    "---\nversion: 0.1.0-draft\nverified_date: '2026-09-21'\n"
                    "verification_mode: current-merged-truth\n"
                    f"verified_commits:\n  ant-sdk: {OLD_SHA}\n---\nLegacy skill.\n"
                ),
                "skills/start/CHANGELOG.md": "## [0.1.0-draft]\nInitial.\n",
            })
        base_files.update(base_extra or {})
        self.write_files({name: text for name, text in base_files.items() if text is not None})
        self.env["BASE_SHA"] = self.commit()
        self.write_files({SUMMARY: "Sweep summary.\n"} if summary else {})
        self.write_files(changes or {})
        for old, new in renames:
            (self.repo / new).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / old).rename(self.repo / new)
        self.env["HEAD_SHA"] = self.commit()

    def write_files(self, files: dict) -> None:
        for name, content in files.items():
            path = self.repo / name
            if content is None:
                path.unlink()
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    def git(self, *args: str) -> str:
        return subprocess.check_output(
            ["git", "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
            cwd=self.repo, env=self.env, text=True, stderr=subprocess.PIPE,
        ).strip()

    def commit(self) -> str:
        self.git("add", ".")
        self.git("commit", "-q", "--allow-empty", "-m", "Disposable guard fixture")
        return self.git("rev-parse", "HEAD")

    def run_guard(self, name: str, *, baseline=False, suffix="2026-09-22", branch=None):
        self.env["HEAD_REF"] = branch or f"claude/{name.removesuffix('-guard')}-{suffix}"
        Path(self.env["GITHUB_STEP_SUMMARY"]).write_text("", encoding="utf-8")
        workflow = (self.baseline if baseline else self.current)[name]
        result = subprocess.run(
            [sys.executable, "-c", embedded_python(workflow)],
            cwd=self.repo, env=self.env, text=True, capture_output=True,
        )
        return result, Path(self.env["GITHUB_STEP_SUMMARY"]).read_text(encoding="utf-8")

    def run_validator(self, branch="claude/sweep-2026-09-22"):
        return subprocess.run(
            [
                sys.executable,
                "-I",
                "scripts/validate_release_baselines.py",
                "--base-ref",
                self.env["BASE_SHA"],
                "--head-ref",
                self.env["HEAD_SHA"],
                "--branch",
                branch,
            ],
            cwd=self.repo,
            env=self.env,
            text=True,
            capture_output=True,
        )

    def promotion_history(self, *, prose=False, browser_manifest=BROWSER_MANIFEST,
                          page_overrides=None, manifest_override=None,
                          record=True) -> dict:
        entry = release_fixtures.valid_entry(Path("."))
        entry["promotion"]["record"] = SUMMARY
        release_section = yaml.safe_dump(
            {"release_baselines": {"schema_version": 1, "entries": {"ant-cli/stable": entry}}},
            sort_keys=False,
        )
        head_manifest = browser_manifest + "\n" + release_section
        current = release_fixtures.verification_block()
        promoted = release_fixtures.verification_block(
            release_fixtures.COMMIT, "ant-cli-v0.3.12", "target-manifest"
        )
        base_extra = {
            "target-manifest.yml": BROWSER_MANIFEST,
            "component-registry.yml": yaml.safe_dump(
                {"components": release_fixtures.components()}, sort_keys=False
            ),
            "repo-registry.yml": yaml.safe_dump(
                {"repos": release_fixtures.repos()}, sort_keys=False
            ),
            "docs/cli/command-reference.md": current,
            "docs/cli/use-the-cli.md": current,
        }
        changes = {
            "target-manifest.yml": manifest_override or head_manifest,
            "docs/cli/command-reference.md": promoted,
            "docs/cli/use-the-cli.md": promoted,
        }
        if prose:
            changes["docs/cli/use-the-cli.md"] += "\nRendered CLI guidance.\n"
        changes.update(page_overrides or {})
        self.history(changes, base_extra=base_extra, legacy=False, summary=record)
        return entry

    def assert_envelopes(self, sweep: bool, prose: bool, *, suffix="2026-09-22",
                         compare=True, diagnostic="") -> None:
        for name, accepted in zip(GUARDS[:2], (sweep, prose)):
            with self.subTest(guard=name):
                result, summary = self.run_guard(name, suffix=suffix)
                self.assertEqual(result.returncode, 0 if accepted else 1, result.stderr)
                self.assertIn("clean envelope" if accepted else "failures", summary)
                if not accepted and diagnostic:
                    self.assertIn(diagnostic, result.stderr)
                if compare:
                    old, old_summary = self.run_guard(name, baseline=True, suffix=suffix)
                    self.assertEqual((result.returncode, result.stderr, summary),
                                     (old.returncode, old.stderr, old_summary))

    def test_workflow_contract_and_removed_skill_code(self) -> None:
        for name in GUARDS:
            with self.subTest(guard=name):
                current = self.current[name]
                self.assertEqual(current["name"], name)
                self.assertIn("pull_request", current[True])
                self.assertNotIn("if", steps(current)[1])
                self.assertNotIn("if", steps(current)[2])
                code = embedded_python(current)
                compile(code, name, "exec")
                for retired in ("skills/start", "verified_commits", "frontmatter",
                                "resolve_default_branch", "default_branch_cache", "linked-release"):
                    self.assertNotIn(retired, code)
                if name == "sweep-sha-reachability":
                    self.assertIn("import yaml", code)
                    self.assertIn("import json", code)
                    self.assertIn("validate_release_tag", code)
                    self.assertIn("show(BASE, REGISTRY_PATH)", code)
                    self.assertNotIn("show(HEAD, REGISTRY_PATH)", code)
                    self.assertNotIn("skipped (target-manifest pin)", code)
                else:
                    self.assertNotIn("import yaml", code)
                    self.assertNotIn("import json", code)
                    self.assertIn("release-sensitive changes are branch-protected", code)
                    self.assertTrue(any(
                        step.get("name") == "Validate atomic release promotion"
                        for step in steps(current)
                    ))
        repository_tests = load_workflow("repository-tests")
        repository_runs = [
            step.get("run", "") for step in steps(repository_tests)
        ]
        self.assertIn(
            "python3 -I scripts/validate_release_baselines.py", repository_runs
        )

    def test_actual_branch_scope_shell(self) -> None:
        self.history(legacy=False)
        for name in GUARDS:
            for branch, expected in (
                ("claude/sweep-2026-09-22", "updater" if name == "sweep-sha-reachability" else "sweep"),
                ("claude/prose-2026-09-22", "updater" if name == "sweep-sha-reachability" else "prose"),
                ("feature/retirement", "other"),
            ):
                with self.subTest(guard=name, branch=branch):
                    output = self.root / "output"
                    output.write_text("", encoding="utf-8")
                    result = subprocess.run(
                        ["bash", "-c", steps(self.current[name])[0]["run"]],
                        env={**self.env, "HEAD_REF": branch, "GITHUB_OUTPUT": str(output)},
                        cwd=self.repo, capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(output.read_text(), f"family={expected}\n")

    def test_valid_refresh_without_retired_skill(self) -> None:
        self.history({"docs/page.md": REFRESHED}, legacy=False)
        self.assertFalse((self.repo / "skills").exists())
        self.assert_envelopes(True, True, compare=False)

    def test_valid_prose_without_retired_skill_or_summary(self) -> None:
        self.history({"docs/page.md": DOC.replace("Store your data.", "Retrieve data.")},
                     legacy=False, summary=False)
        result, _ = self.run_guard("prose-guard")
        self.assertEqual(result.returncode, 0, result.stderr)
        old, _ = self.run_guard("prose-guard", baseline=True)
        self.assertEqual(old.returncode, 1)
        self.assertIn("verified_commits missing on base", old.stderr)

    def test_metadata_and_prose_decision_parity(self) -> None:
        for text, sweep in ((REFRESHED, True),
                            (DOC.replace("Store your data.", "Retrieve data."), False),
                            (DOC.replace("release/v1", "main"), False),
                            (DOC + f"source_commit: {NEW_SHA}\n", False)):
            with self.subTest(text=text):
                self.history({"docs/page.md": text})
                self.assert_envelopes(sweep, True)

    def test_doc_add_delete_and_rename_parity(self) -> None:
        for changes, renames in (({"docs/new.md": DOC}, ()),
                                 ({"docs/page.md": None}, ()),
                                 ({}, (("docs/page.md", "docs/moved.md"),))):
            with self.subTest(changes=changes, renames=renames):
                self.history(changes, renames=renames)
                self.assert_envelopes(False, True, diagnostic="unexpected diff status")

    def test_target_manifest_byte_immutability_parity(self) -> None:
        for text in (PINNED.replace(OLD_SHA, NEW_SHA),
                     PINNED.replace("2026-09-21", "2026-09-22"),
                     PINNED.replace("target-manifest", "current-merged-truth"),
                     PINNED.replace("  source_repo", "   source_repo"),
                     PINNED.replace("-->", "  future_field: value\n-->"),
                     "# Removed pin\n", PINNED + PINNED, None):
            with self.subTest(text=text):
                self.history({"docs/pinned.md": text})
                self.assert_envelopes(False, False, compare=False)
        self.history({"docs/page.md": DOC + PINNED})
        self.assert_envelopes(False, False, diagnostic="target-manifest", compare=False)

    def test_unchanged_pin_alongside_refresh_or_prose_parity(self) -> None:
        for text, sweep in ((REFRESHED + PINNED, True),
                            ((DOC + PINNED).replace("Store your data.", "Read data."), False)):
            with self.subTest(text=text):
                self.history({"docs/page.md": text}, base_extra={"docs/page.md": DOC + PINNED})
                self.assert_envelopes(sweep, True)

    def test_valid_atomic_release_promotion_and_metadata_prose_separation(self) -> None:
        self.promotion_history()
        sweep, _ = self.run_guard("sweep-guard")
        prose_delegate, _ = self.run_guard("prose-guard", branch="claude/sweep-2026-09-22")
        strict = self.run_validator()
        self.assertEqual(sweep.returncode, 0, sweep.stderr)
        self.assertEqual(prose_delegate.returncode, 0, prose_delegate.stderr)
        self.assertEqual(strict.returncode, 0, strict.stderr)
        self.assertIn("atomic promotion", strict.stdout)

        self.promotion_history(prose=True)
        sweep, _ = self.run_guard("sweep-guard")
        prose, _ = self.run_guard("prose-guard")
        strict = self.run_validator("claude/prose-2026-09-22")
        self.assertEqual(sweep.returncode, 1)
        self.assertIn("outside any", sweep.stderr)
        self.assertEqual(prose.returncode, 0, prose.stderr)
        self.assertEqual(strict.returncode, 0, strict.stderr)

    def test_release_promotion_preserves_browser_manifest_and_blocks_byte_for_byte(self) -> None:
        mutated_browser = BROWSER_MANIFEST.replace("source_ref: v1", "source_ref: v2")
        self.promotion_history(browser_manifest=mutated_browser)
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("sources subtree changed", result.stderr)

        changed_browser_block = PINNED.replace(OLD_SHA, NEW_SHA)
        self.promotion_history(page_overrides={"docs/pinned.md": changed_browser_block})
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("scoped_pages", result.stderr)

    def test_release_promotion_requires_exact_block_entry_and_record_correspondence(self) -> None:
        wrong = release_fixtures.verification_block(
            "f" * 40, "ant-cli-v0.3.12", "target-manifest"
        )
        self.promotion_history(
            page_overrides={"docs/cli/use-the-cli.md": wrong}
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not match release baseline", result.stderr)

        self.promotion_history(record=False)
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("promotion.record", result.stderr)

    def test_first_cli_promotion_requires_ant_core_dependency_evidence(self) -> None:
        entry = release_fixtures.valid_entry(Path("."))
        entry["promotion"]["record"] = SUMMARY
        del entry["shipped_dependencies"]
        release_section = yaml.safe_dump(
            {
                "release_baselines": {
                    "schema_version": 1,
                    "entries": {"ant-cli/stable": entry},
                }
            },
            sort_keys=False,
        )
        self.promotion_history(
            manifest_override=BROWSER_MANIFEST + "\n" + release_section
        )

        result = self.run_validator()

        self.assertEqual(result.returncode, 1)
        self.assertIn("shipped_dependencies", result.stderr)

    def test_unrelated_branch_rejects_every_release_sensitive_change(self) -> None:
        cases = (
            {"target-manifest.yml": BROWSER_MANIFEST + "\nrelease_baselines: {}\n"},
            {"docs/pinned.md": PINNED.replace(OLD_SHA, NEW_SHA)},
            {"planning/sweeps/2026-09-21.md": "Changed promotion evidence.\n"},
        )
        for changes in cases:
            with self.subTest(changes=changes):
                self.history(changes, legacy=False, summary=False)
                for name in GUARDS[:2]:
                    result, _ = self.run_guard(name, branch="feature/release-change")
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("claude/sweep-*", result.stderr)
                    self.assertIn("claude/prose-*", result.stderr)

    def test_unrelated_branch_rejects_registry_and_verification_change_pair(self) -> None:
        untrusted_registry = REGISTRY.replace(
            "https://github.com/WithAutonomi/ant-sdk",
            "https://github.com/attacker/untrusted",
        )
        self.history(
            {
                "docs/page.md": REFRESHED,
                "repo-registry.yml": untrusted_registry,
            },
            legacy=False,
            summary=False,
        )
        for name in GUARDS[:2]:
            with self.subTest(guard=name):
                result, _ = self.run_guard(
                    name, branch="feature/registry-and-verification-change"
                )
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn("repo-registry.yml", result.stderr)

        calls = self.assert_reachability(
            {COMMIT_URL: {}, COMPARE_URL: {"status": "ahead"}},
            True,
            compare=False,
        )
        self.assertEqual(calls, [COMMIT_URL, COMPARE_URL])

    def test_unrelated_branch_passes_without_release_sensitive_changes(self) -> None:
        self.history({"README.md": "Ordinary branch change.\n"}, legacy=False, summary=False)
        for name in GUARDS[:2]:
            with self.subTest(guard=name):
                result, summary = self.run_guard(name, branch="feature/ordinary-change")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("protected-change scan clean", summary)

    def test_release_promotion_block_rejects_an_added_field(self) -> None:
        promoted = release_fixtures.verification_block(
            release_fixtures.COMMIT, "ant-cli-v0.3.12", "target-manifest"
        ).replace("  source_repo:", "  component: ant-cli\n  source_repo:")
        self.promotion_history(
            page_overrides={"docs/cli/use-the-cli.md": promoted}
        )
        sweep, _ = self.run_guard("sweep-guard")
        strict = self.run_validator()
        self.assertEqual(sweep.returncode, 1)
        self.assertIn("outside the allowed verification fields", sweep.stderr)
        self.assertEqual(strict.returncode, 1)
        self.assertIn("unknown fields: component", strict.stderr)

    def test_routine_contract_keeps_collision_and_manual_review_identity(self) -> None:
        policy = (ROOT / "planning/routines/upstream-sweep.md").read_text(encoding="utf-8")
        prompt = (ROOT / "planning/routines/upstream-sweep-prompt.md").read_text(encoding="utf-8")
        for text in (policy, prompt):
            self.assertIn('startswith("claude/sweep-")', text)
            self.assertIn('startswith("claude/prose-")', text)
            self.assertIn("Fingerprint:", text)
            self.assertIn("recorded_sha", text)
            self.assertIn("head_sha", text)
            self.assertIn("issue body", text)
            self.assertIn("dated", text)
            self.assertNotIn("Release Fingerprint:", text)
            self.assertNotIn("Installer Fingerprint:", text)

    def test_summary_required_only_for_sweep_parity(self) -> None:
        self.history({"docs/page.md": REFRESHED}, summary=False)
        self.assert_envelopes(False, True, diagnostic="no planning/sweeps/")

    def test_summary_creation_and_date_parity(self) -> None:
        cases = (
            ({SUMMARY: "Edit existing summary.\n"}, {SUMMARY: "Existing.\n"}),
            ({"planning/sweeps/2026-09-21.md": None}, {}),
            ({"planning/sweeps/2026-09-23.md": "Wrong date.\n"}, {}),
            ({"planning/sweeps/not-a-date.md": "Invalid name.\n"}, {}),
        )
        for changes, base in cases:
            with self.subTest(changes=changes):
                self.history(changes, base_extra=base, summary=False)
                self.assert_envelopes(False, False)
        self.history(renames=(("planning/sweeps/2026-09-21.md", SUMMARY),), summary=False)
        self.assert_envelopes(False, False, diagnostic="must be added")

    def test_branch_date_format_and_slug_parity(self) -> None:
        self.history({"docs/page.md": REFRESHED})
        for suffix in ("2026-09-22", "2026-09-22-retry-2", "2026-9-22", "2026-09-22-BAD"):
            with self.subTest(suffix=suffix):
                valid = suffix in ("2026-09-22", "2026-09-22-retry-2")
                self.assert_envelopes(valid, valid, suffix=suffix)

    def test_protected_and_outside_paths_parity(self) -> None:
        for path in ("scripts/protected.md", ".github/protected.md", "repo-registry.yml",
                     "component-registry.yml", "README.md",
                     "docs/image.svg", "planning/outside.md"):
            with self.subTest(path=path):
                self.history({path: "Changed.\n"})
                self.assert_envelopes(False, False)

        self.history({"target-manifest.yml": "Changed.\n"})
        self.assertEqual(self.run_guard("sweep-guard")[0].returncode, 0)
        self.assertEqual(self.run_guard("prose-guard")[0].returncode, 0)
        self.assertEqual(self.run_validator().returncode, 1)

    def test_rename_both_sides_protected_parity(self) -> None:
        for protected in ("scripts/protected.md", ".github/protected.md", "repo-registry.yml",
                          "component-registry.yml"):
            for old, new in ((protected, "docs/moved.md"), ("docs/page.md", protected)):
                with self.subTest(old=old, new=new):
                    # The destination must not exist, to exercise a genuine R100 diff.
                    extra = {protected: None} if new == protected else {}
                    self.history(base_extra=extra, renames=((old, new),))
                    self.assertIn("R100", self.git("diff", "--name-status",
                                                  f"{self.env['BASE_SHA']}..{self.env['HEAD_SHA']}"))
                    self.assert_envelopes(False, False, diagnostic="infrastructure file")

    def test_retired_paths_are_no_longer_allowed(self) -> None:
        for path in ("skills/start/SKILL.md", "skills/start/version.json", "skills/start/CHANGELOG.md"):
            with self.subTest(path=path):
                self.history({path: "Unexpected artifact.\n"}, legacy=False)
                self.assert_envelopes(False, False, compare=False)

    def test_git_diff_failure_is_not_a_clean_envelope(self) -> None:
        self.history()
        self.env["BASE_SHA"] = "nonexistent-fixture-ref"
        for name in GUARDS[:2]:
            with self.subTest(guard=name):
                result, summary = self.run_guard(name)
                old, _ = self.run_guard(name, baseline=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.returncode, old.returncode)
                self.assertIn("CalledProcessError", result.stderr)
                self.assertNotIn("clean envelope", summary)

    def run_mocked_reachability(self, responses: dict, *, baseline=False):
        """Only HTTP is mocked; registry parsing, Git and guard Python are real."""
        self.env["HEAD_REF"] = "claude/sweep-2026-09-22"
        summary_path = Path(self.env["GITHUB_STEP_SUMMARY"])
        summary_path.write_text("", encoding="utf-8")
        calls = []

        def urlopen(request, timeout):
            self.assertEqual(timeout, 30)
            calls.append(request.full_url)
            self.assertIn(request.full_url, responses, "unexpected HTTP request (network blocked)")
            response = responses[request.full_url]
            if isinstance(response, Exception):
                raise response
            body = io.BytesIO(json.dumps(response).encode())
            body.status = 200
            return body

        workflow = (self.baseline if baseline else self.current)["sweep-sha-reachability"]
        stdout, stderr = io.StringIO(), io.StringIO()
        previous = Path.cwd()
        try:
            os.chdir(self.repo)
            with patch.dict(os.environ, self.env, clear=True), \
                    patch("urllib.request.urlopen", side_effect=urlopen), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    exec(compile(embedded_python(workflow), "reachability-workflow", "exec",
                                 dont_inherit=True), {})
                    code = 0
                except SystemExit as exc:
                    code = exc.code
        finally:
            os.chdir(previous)
        return code, stderr.getvalue(), summary_path.read_text(encoding="utf-8"), calls

    def assert_reachability(self, responses: dict, accepted: bool, *, diagnostic="",
                            compare=True):
        result = self.run_mocked_reachability(responses)
        code, stderr, summary, calls = result
        self.assertEqual(code, 0 if accepted else 1, stderr)
        self.assertIn("all SHAs reachable" if accepted else "failures", summary)
        if diagnostic:
            self.assertIn(diagnostic, stderr + summary)
        if compare:
            self.assertEqual(result, self.run_mocked_reachability(responses, baseline=True))
        return calls

    def test_mocked_reachability_declared_ref_and_ancestry(self) -> None:
        self.history({"docs/page.md": REFRESHED}, legacy=False)
        for status in ("ahead", "identical", "behind", "diverged", "unknown"):
            with self.subTest(status=status):
                calls = self.assert_reachability(
                    {COMMIT_URL: {}, COMPARE_URL: {"status": status}},
                    status in ("ahead", "identical"),
                )
                self.assertEqual(calls, [COMMIT_URL, COMPARE_URL])

    def test_mocked_reachability_peels_release_tag_to_exact_manifest_commit(self) -> None:
        self.promotion_history()
        api = "https://api.github.com/repos/WithAutonomi/ant-client"
        ref_url = f"{api}/git/ref/tags/ant-cli-v0.3.12"
        tag_url = f"{api}/git/tags/{'a' * 40}"
        responses = {
            ref_url: {"object": {"type": "tag", "sha": "a" * 40}},
            tag_url: {
                "object": {"type": "commit", "sha": release_fixtures.COMMIT}
            },
        }
        calls = self.assert_reachability(
            responses, True, diagnostic="exact release tags validated", compare=False
        )
        self.assertEqual(calls, [ref_url, tag_url, ref_url, tag_url])

        responses[tag_url] = {"object": {"type": "commit", "sha": "f" * 40}}
        self.assert_reachability(
            responses, False, diagnostic="not recorded commit", compare=False
        )

    def test_mocked_reachability_http_and_network_errors(self) -> None:
        self.history({"docs/page.md": REFRESHED})
        for url in (COMMIT_URL, COMPARE_URL):
            for error in (urllib.error.HTTPError(url, 404, "Not found", {}, None),
                          urllib.error.HTTPError(url, 403, "Forbidden", {}, None),
                          urllib.error.URLError("offline fixture")):
                with self.subTest(url=url, error=error):
                    responses = {COMMIT_URL: {}, COMPARE_URL: {"status": "ahead"}, url: error}
                    self.assert_reachability(responses, False)

    def test_mocked_reachability_empty_compare_fails(self) -> None:
        self.history({"docs/page.md": REFRESHED})
        self.assert_reachability({COMMIT_URL: {}, COMPARE_URL: {}}, False,
                                 diagnostic="compare")

    def test_mocked_reachability_bad_metadata_and_registry(self) -> None:
        for text, registry, diagnostic in (
            (REFRESHED.replace("  source_ref: release/v1\n", ""), REGISTRY, "missing required keys"),
            (REFRESHED.replace("ant-sdk", "unknown"), REGISTRY, "repo not in repo-registry"),
            (REFRESHED, REGISTRY.replace("github.com", "example.invalid"), "unparseable url"),
            (REFRESHED, "repos: [", "YAML parse error"),
        ):
            with self.subTest(diagnostic=diagnostic):
                self.history({"docs/page.md": text}, base_extra={"repo-registry.yml": registry})
                self.assertEqual(self.assert_reachability({}, False, diagnostic=diagnostic), [])

    def test_mocked_reachability_rejects_unenrolled_pin_and_ignores_unchanged_blocks(self) -> None:
        self.history({"docs/pinned.md": PINNED.replace(OLD_SHA, NEW_SHA)}, legacy=False)
        self.assertEqual(
            self.assert_reachability(
                {}, False, diagnostic="correspond to exactly one release baseline", compare=False
            ),
            [],
        )
        self.history({"docs/page.md": DOC.replace("Store your data.", "Read data.")}, legacy=False)
        self.assertEqual(self.assert_reachability({}, True, compare=False), [])

    def test_mocked_reachability_pin_still_requires_keys(self) -> None:
        self.history({"docs/pinned.md": PINNED.replace("  source_ref: release/v1\n", "")})
        self.assert_reachability({}, False, diagnostic="missing required keys")

    def test_mocked_reachability_reports_release_provenance_failure_alongside_failure(self) -> None:
        self.history({"docs/page.md": REFRESHED.replace("ant-sdk", "unknown"),
                      "docs/pinned.md": PINNED.replace(OLD_SHA, NEW_SHA)})
        self.assert_reachability(
            {}, False, diagnostic="correspond to exactly one release baseline", compare=False
        )

    def test_mocked_reachability_checks_new_and_renamed_docs(self) -> None:
        for changes, renames in (({"docs/new.md": REFRESHED}, ()),
                                 ({"docs/page.md": REFRESHED}, (("docs/page.md", "docs/moved.md"),))):
            with self.subTest(renames=renames):
                self.history(changes, renames=renames)
                self.assertEqual(self.assert_reachability(
                    {COMMIT_URL: {}, COMPARE_URL: {"status": "ahead"}}, True),
                    [COMMIT_URL, COMPARE_URL])


if __name__ == "__main__":
    unittest.main()
