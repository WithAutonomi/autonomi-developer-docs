#!/usr/bin/env python3
"""Repository-local ADR governance checks."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

ADR_DIR = Path("adr")
ADR_CONFIG = Path(".adr-kit.yaml")
ALLOWED_STATUSES = {"Proposed", "Accepted", "Superseded", "Deprecated", "Rejected"}
REQUIRED_SECTIONS = ["Context", "Decision", "Consequences", "Validation"]
FILENAME_RE = re.compile(r"^ADR-\d{4}-[a-z0-9][a-z0-9-]*\.md$")
STATUS_RE = re.compile(r"(?im)^\s*(?:[-*]\s*)?.*?Status.*?:\s*(.+?)\s*$")
ACCEPTANCE_RE = re.compile(
    r"(?im)^\s*[-*]\s+\*\*Acceptance:\*\*\s*"
    r"(Prospective|Retrospective)\s+—\s+(.+?)\s*$"
)


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(
            cmd, text=True, encoding="utf-8", stderr=subprocess.STDOUT
        ).strip()
    except subprocess.CalledProcessError as exc:
        detail = exc.output.strip() or f"exit {exc.returncode}"
        raise RuntimeError(f"{' '.join(cmd)} failed: {detail}") from exc


def status_of(text: str) -> str | None:
    match = STATUS_RE.search(text)
    return match.group(1).strip().strip("*").strip() if match else None


def base_ref() -> str | None:
    ref = os.environ.get("GITHUB_BASE_REF")
    if ref:
        base = f"origin/{ref}"
        run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"])
        return base

    before = os.environ.get("GITHUB_EVENT_BEFORE")
    if before and before != "0" * 40:
        run(["git", "rev-parse", "--verify", f"{before}^{{commit}}"])
        return before

    for default_branch in ("origin/main", "main"):
        try:
            run(["git", "rev-parse", "--verify", f"{default_branch}^{{commit}}"])
            return run(["git", "merge-base", "HEAD", default_branch])
        except RuntimeError:
            continue
    return None


def file_at(ref: str, path: Path) -> str:
    return run(["git", "show", f"{ref}:{path.as_posix()}"])


def file_bytes_at(ref: str, path: Path) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "show", f"{ref}:{path.as_posix()}"], stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.output.decode(errors="replace").strip() or f"exit {exc.returncode}"
        raise RuntimeError(f"git show {ref}:{path} failed: {detail}") from exc


def adr_directory_from_config(text: str, source: str) -> Path:
    match = re.search(r"(?m)^adr_directory:\s*['\"]?([^'\"\s]+)", text)
    if not match:
        raise RuntimeError(f"{source}: missing adr_directory")
    return Path(match.group(1))


def adr_paths_at(ref: str, directory: Path) -> list[Path]:
    output = run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", directory.as_posix()]
    )
    return [
        Path(name)
        for name in output.splitlines()
        if Path(name).parent == directory
        and Path(name).name.startswith("ADR-")
        and Path(name).suffix == ".md"
    ]


def changed_adr_paths_against_base(base: str) -> list[Path]:
    try:
        output = run(["git", "diff", "--name-only", f"{base}...HEAD"])
    except RuntimeError:
        output = run(["git", "diff", "--name-only", base, "HEAD"])
    return sorted(
        path
        for name in output.splitlines()
        if (path := Path(name)).parent == ADR_DIR
        and path.name.startswith("ADR-")
        and path.suffix == ".md"
        and path.is_file()
    )


def main() -> int:
    errors: list[str] = []

    try:
        current_directory = adr_directory_from_config(
            ADR_CONFIG.read_text(encoding="utf-8"), str(ADR_CONFIG)
        )
    except (OSError, RuntimeError) as exc:
        print(f"ADR governance failed:\n- cannot validate ADR configuration: {exc}")
        return 1

    if current_directory != ADR_DIR:
        print(
            "ADR governance failed:\n"
            f"- {ADR_CONFIG}: adr_directory is {current_directory}, "
            f"but the checker uses {ADR_DIR}"
        )
        return 1

    if not ADR_DIR.is_dir():
        print(f"ADR governance failed:\n- ADR directory does not exist: {ADR_DIR}")
        return 1

    adr_files = sorted(path for path in ADR_DIR.glob("ADR-*.md") if path.is_file())

    try:
        base = base_ref()
        base_directory = None
        base_paths: list[Path] = []
        base_files: dict[str, tuple[Path, bytes]] = {}
        if base:
            base_config = file_at(base, ADR_CONFIG)
            base_directory = adr_directory_from_config(
                base_config, f"{base}:{ADR_CONFIG}"
            )
            base_paths = adr_paths_at(base, base_directory)
            base_files = {
                path.name: (path, file_bytes_at(base, path)) for path in base_paths
            }
            files_to_validate = changed_adr_paths_against_base(base)
        else:
            files_to_validate = adr_files
    except RuntimeError as exc:
        print(f"ADR governance failed:\n- cannot establish comparison base: {exc}")
        return 1

    seen_numbers: dict[str, Path] = {}
    for path in adr_files:
        number = path.name.split("-", 2)[1]
        if number in seen_numbers:
            errors.append(
                f"{path}: duplicate ADR number also used by {seen_numbers[number]}"
            )
        seen_numbers[number] = path

    base_accepted_names = {
        name
        for name, (_, content) in base_files.items()
        if status_of(content.decode("utf-8")) == "Accepted"
    }
    for path in files_to_validate:
        if not FILENAME_RE.match(path.name):
            errors.append(f"{path}: filename must match ADR-NNNN-short-title.md")
        text = path.read_text(encoding="utf-8")
        status = status_of(text)
        if not status:
            errors.append(f"{path}: missing Status")
        elif status not in ALLOWED_STATUSES:
            allowed = ", ".join(sorted(ALLOWED_STATUSES))
            errors.append(f"{path}: invalid Status '{status}' (allowed: {allowed})")
        elif status == "Accepted" and path.name not in base_accepted_names:
            acceptance = ACCEPTANCE_RE.search(text)
            if (
                not acceptance
                or not acceptance.group(2).strip()
                or acceptance.group(2).lstrip().startswith("<")
            ):
                errors.append(
                    f"{path}: newly Accepted ADRs require Prospective or Retrospective "
                    "Acceptance metadata with a non-placeholder basis"
                )
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"(?im)^##\s+{re.escape(section)}\b", text):
                errors.append(f"{path}: missing required section '## {section}'")

    if base and base_directory:
        for old_path, old_bytes in base_files.values():
            old_text = old_bytes.decode("utf-8")
            if status_of(old_text) != "Accepted":
                continue
            # During the docs/adr -> adr transition, an unchanged Accepted ADR
            # maps by filename into the configured root-level directory.
            current_path = ADR_DIR / old_path.name
            if not current_path.is_file() or current_path.read_bytes() != old_bytes:
                errors.append(
                    f"{old_path}: Accepted ADRs are immutable. They may only move "
                    f"unchanged to {current_path}; create a superseding ADR instead."
                )

    if errors:
        print("ADR governance failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"ADR governance passed ({len(files_to_validate)} ADR file(s) checked).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
