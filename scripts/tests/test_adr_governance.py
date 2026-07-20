from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "adr-governance.py"

VALID_ADR = """# ADR-{number}: Test decision

- **Status:** {status}
{acceptance}
## Context

Context.

## Decision

Decision.

## Consequences

Consequences.

## Validation

Validation.
"""


class AdrGovernanceIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp_dir.name)
        self.run_command("git", "init", "-q")
        self.run_command("git", "checkout", "-q", "-b", "main")
        self.run_command("git", "config", "user.name", "ADR test")
        self.run_command("git", "config", "user.email", "adr-test@example.com")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: adr\n", encoding="utf-8"
        )
        (self.repo / "adr").mkdir()
        self.write_adr("ADR-0001-existing-decision.md", "0001", "Accepted")
        self.commit("add existing ADR")
        self.main_sha = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "update-ref", "refs/remotes/origin/main", self.main_sha)
        self.run_command("git", "checkout", "-q", "-b", "feature")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_command(
        self, *command: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=self.repo,
            check=check,
            capture_output=True,
            text=True,
        )

    def write_adr(
        self,
        name: str,
        number: str,
        status: str,
        *,
        acceptance: bool = False,
    ) -> Path:
        path = self.repo / "adr" / name
        metadata = (
            "- **Acceptance:** Retrospective — confirmed by the decision owner.\n"
            if acceptance
            else ""
        )
        path.write_text(
            VALID_ADR.format(
                number=number, status=status, acceptance=metadata
            ),
            encoding="utf-8",
        )
        return path

    def commit(self, message: str) -> None:
        self.run_command("git", "add", ".")
        self.run_command("git", "commit", "-q", "-m", message)

    def run_governance(
        self, base_ref: str | None = "main"
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.pop("GITHUB_BASE_REF", None)
        env.pop("GITHUB_EVENT_BEFORE", None)
        if base_ref:
            env["GITHUB_BASE_REF"] = base_ref
        return subprocess.run(
            ["python3", "-I", str(SCRIPT)],
            cwd=self.repo,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_valid_adr_in_root_level_directory_passes(self) -> None:
        self.write_adr("ADR-0002-new-decision.md", "0002", "Proposed")

        result = self.run_governance()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 ADR file(s) checked", result.stdout)

    def test_missing_required_section_fails(self) -> None:
        path = self.write_adr("ADR-0002-broken.md", "0002", "Proposed")
        path.write_text("# ADR-0002: Broken\n\n- **Status:** Proposed\n", encoding="utf-8")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("missing required section", result.stdout)

    def test_invalid_status_fails(self) -> None:
        self.write_adr("ADR-0002-new-decision.md", "0002", "Draft")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid Status 'Draft'", result.stdout)

    def test_malformed_filename_fails(self) -> None:
        self.write_adr("ADR-0002-bad_title.md", "0002", "Proposed")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("filename must match", result.stdout)

    def test_duplicate_adr_numbers_fail(self) -> None:
        self.write_adr("ADR-0002-first.md", "0002", "Proposed")
        self.write_adr("ADR-0002-second.md", "0002", "Proposed")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("duplicate ADR number", result.stdout)

    def test_editing_accepted_adr_fails(self) -> None:
        path = self.repo / "adr" / "ADR-0001-existing-decision.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("Accepted ADRs are immutable", result.stdout)

    def test_renaming_accepted_adr_fails(self) -> None:
        old_path = self.repo / "adr" / "ADR-0001-existing-decision.md"
        old_path.rename(self.repo / "adr" / "ADR-0001-renamed-decision.md")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("Accepted ADRs are immutable", result.stdout)

    def test_new_accepted_adr_requires_acceptance_metadata(self) -> None:
        self.write_adr("ADR-0002-no-acceptance.md", "0002", "Accepted")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("newly Accepted ADRs require", result.stdout)

    def test_new_accepted_adr_with_acceptance_metadata_passes(self) -> None:
        self.write_adr(
            "ADR-0002-retrospective.md",
            "0002",
            "Accepted",
            acceptance=True,
        )

        result = self.run_governance()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepted_adr_can_be_corrected_across_introducing_branch_commits(self) -> None:
        path = self.write_adr(
            "ADR-0002-retrospective.md",
            "0002",
            "Accepted",
            acceptance=True,
        )
        self.commit("introduce retrospective ADR")
        path.write_text(
            path.read_text(encoding="utf-8").replace("Decision.", "Corrected decision."),
            encoding="utf-8",
        )
        self.commit("correct retrospective ADR")

        result = self.run_governance(base_ref=None)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_newly_accepted_existing_adr_requires_acceptance_metadata(self) -> None:
        path = self.write_adr("ADR-0002-proposed.md", "0002", "Proposed")
        self.commit("add proposed ADR")
        sha = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "update-ref", "refs/remotes/origin/main", sha)
        path.write_text(
            VALID_ADR.format(number="0002", status="Accepted", acceptance=""),
            encoding="utf-8",
        )

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("newly Accepted ADRs require", result.stdout)

    def test_missing_comparison_base_fails_closed(self) -> None:
        result = self.run_governance(base_ref="missing")

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot establish comparison base", result.stdout)

    def test_current_config_directory_must_match_checker_directory(self) -> None:
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: docs/adr\n", encoding="utf-8"
        )

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("adr_directory is docs/adr, but the checker uses adr", result.stdout)

    def test_missing_base_config_fails_closed(self) -> None:
        self.run_command("git", "checkout", "-q", "main")
        (self.repo / ".adr-kit.yaml").unlink()
        self.commit("remove base config")
        sha = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "update-ref", "refs/remotes/origin/main", sha)
        self.run_command("git", "checkout", "-q", "-B", "feature")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: adr\n", encoding="utf-8"
        )

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("cannot establish comparison base", result.stdout)

    def test_relocating_unchanged_accepted_adr_passes(self) -> None:
        self.run_command("git", "checkout", "-q", "main")
        (self.repo / "docs").mkdir()
        self.run_command("git", "mv", "adr", "docs/adr")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: docs/adr\n", encoding="utf-8"
        )
        self.commit("put ADRs in legacy directory")
        sha = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "update-ref", "refs/remotes/origin/main", sha)
        self.run_command("git", "checkout", "-q", "-B", "relocation")
        self.run_command("git", "mv", "docs/adr", "adr")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: adr\n", encoding="utf-8"
        )

        result = self.run_governance()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_relocating_modified_accepted_adr_fails(self) -> None:
        self.run_command("git", "checkout", "-q", "main")
        (self.repo / "docs").mkdir()
        self.run_command("git", "mv", "adr", "docs/adr")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: docs/adr\n", encoding="utf-8"
        )
        self.commit("put ADRs in legacy directory")
        sha = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "update-ref", "refs/remotes/origin/main", sha)
        self.run_command("git", "checkout", "-q", "-B", "relocation")
        self.run_command("git", "mv", "docs/adr", "adr")
        (self.repo / ".adr-kit.yaml").write_text(
            "adr_directory: adr\n", encoding="utf-8"
        )
        path = self.repo / "adr" / "ADR-0001-existing-decision.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nChanged.\n", encoding="utf-8")

        result = self.run_governance()

        self.assertEqual(result.returncode, 1)
        self.assertIn("Accepted ADRs are immutable", result.stdout)


if __name__ == "__main__":
    unittest.main()
