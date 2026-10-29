"""Offline fixture coverage for released-software discovery and validation."""

from __future__ import annotations

import base64
import copy
import contextlib
import importlib.util
import io
import json
import hashlib
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

import yaml


SCRIPTS = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scanner = load_module("release_scanner", "sweep_poll.py")
validator = load_module("release_validator", "validate_release_baselines.py")

COMMIT = "6096b1c8caf6688d6825fcb9ff61fa1b590d984b"
OLD_COMMIT = "1" * 40
INSTALL_COMMITS = ("2" * 40, "3" * 40)
INSTALL_BLOBS = ("4" * 40, "5" * 40)
META_INTEGRITY = "sha512-" + base64.b64encode(bytes(range(64))).decode("ascii")
PLATFORM_INTEGRITY = "sha512-" + base64.b64encode(b"p" * 64).decode("ascii")
TARGETS = {
    "aarch64-apple-darwin": "tar.gz",
    "aarch64-unknown-linux-musl": "tar.gz",
    "x86_64-apple-darwin": "tar.gz",
    "x86_64-pc-windows-msvc": "zip",
    "x86_64-unknown-linux-musl": "tar.gz",
}
PACKAGES = {
    "aarch64-apple-darwin": "@withautonomi/ant-darwin-arm64",
    "aarch64-unknown-linux-musl": "@withautonomi/ant-linux-arm64",
    "x86_64-apple-darwin": "@withautonomi/ant-darwin-x64",
    "x86_64-pc-windows-msvc": "@withautonomi/ant-win32-x64",
    "x86_64-unknown-linux-musl": "@withautonomi/ant-linux-x64",
}
MAPPED = [
    "index.md",
    "cli/use-the-cli.md",
    "cli/command-reference.md",
    "guides/overview.md",
    "guides/build-read-only-features.md",
    "guides/deploy-to-mainnet.md",
    "guides/prepare-a-wallet-for-uploads.md",
    "reference/source-repositories.md",
    "reference/glossary.md",
]


def discovery_config() -> dict:
    return {
        "github": {
            "tag_pattern": r"^ant-cli-v(?P<version>(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))$",
            "reject_drafts": True,
            "reject_prereleases": True,
            "checksum_asset": "SHA256SUMS.txt",
            "platforms": dict(TARGETS),
        },
        "npm": {
            "package": "@withautonomi/ant",
            "dist_tag": "latest",
            "platform_packages": dict(PACKAGES),
        },
        "installers": [
            {
                "platform": "linux-macos",
                "ref": "main",
                "path": "install.sh",
                "url": "https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.sh",
            },
            {
                "platform": "windows",
                "ref": "main",
                "path": "install.ps1",
                "url": "https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.ps1",
            },
        ],
    }


def components() -> dict:
    return {
        "ant-cli": {
            "repo": "ant-client",
            "kind": "rust-binary",
            "path": "ant-cli/",
            "topics": ["cli", "node-management"],
            "release_discovery": {"stable": discovery_config()},
            "feeds_pages": list(MAPPED),
        },
        "ant-core": {
            "repo": "ant-client",
            "kind": "rust-crate",
            "path": "ant-core/",
            "topics": ["data-types"],
            "feeds_pages": [page for page in MAPPED if not page.startswith("cli/")],
        },
    }


def repos() -> dict:
    return {
        "ant-client": {
            "class": "broad-source",
            "url": "https://github.com/WithAutonomi/ant-client",
        }
    }


def asset(name: str, asset_id: int, tag: str = "ant-cli-v0.3.12") -> dict:
    return {
        "name": name,
        "id": asset_id,
        "browser_download_url": f"https://github.com/WithAutonomi/ant-client/releases/download/{tag}/{name}",
        "digest": f"sha256:{asset_id:064x}",
        "download_count": 99,
    }


def release(version: str = "0.3.12", *, release_id: int = 312, draft=False, prerelease=False) -> dict:
    tag = f"ant-cli-v{version}"
    assets = [asset("SHA256SUMS.txt", 1, tag)]
    next_id = 2
    for target, extension in TARGETS.items():
        name = f"ant-{version}-{target}.{extension}"
        assets.extend((asset(name, next_id, tag), asset(f"{name}.sig", next_id + 1, tag)))
        next_id += 2
    return {
        "id": release_id,
        "url": f"https://api.github.com/repos/WithAutonomi/ant-client/releases/{release_id}",
        "html_url": f"https://github.com/WithAutonomi/ant-client/releases/tag/{tag}",
        "tag_name": tag,
        "published_at": "2026-10-25T12:34:56Z",
        "draft": draft,
        "prerelease": prerelease,
        "assets": assets,
    }


def npm_meta(version: str = "0.3.12", commit: str = COMMIT) -> dict:
    return {
        "version": version,
        "gitHead": commit,
        "dist": {"integrity": META_INTEGRITY},
        "optionalDependencies": {package: version for package in PACKAGES.values()},
    }


def npm_platform(version: str = "0.3.12", commit: str = COMMIT) -> dict:
    return {
        "version": version,
        "gitHead": commit,
        "dist": {"integrity": PLATFORM_INTEGRITY},
    }


def github_router(releases_pages=None, *, commit: str = COMMIT, installer_blobs=INSTALL_BLOBS):
    pages = releases_pages or {1: [release()], 2: []}

    def request(path: str, token=None):
        if "/releases?" in path:
            page = int(path.rsplit("page=", 1)[1])
            return copy.deepcopy(pages.get(page, []))
        if "/git/ref/tags/" in path:
            return {"object": {"type": "tag", "sha": "a" * 40}}
        if "/git/tags/" in path:
            return {"object": {"type": "commit", "sha": commit}}
        if "/commits?" in path:
            index = 0 if "install.sh" in path else 1
            return [{"sha": INSTALL_COMMITS[index]}]
        if "/contents/" in path:
            index = 0 if "install.sh" in path else 1
            installer_path = "install.sh" if index == 0 else "install.ps1"
            return {
                "sha": installer_blobs[index],
                "html_url": f"https://github.com/WithAutonomi/ant-client/blob/{INSTALL_COMMITS[index]}/{installer_path}",
            }
        raise AssertionError(f"unexpected GitHub request: {path}")

    return request


def npm_router(*, version="0.3.12", commit=COMMIT, meta=None, platform_overrides=None):
    root = {"dist-tags": {"latest": version}}
    meta_value = copy.deepcopy(meta if meta is not None else npm_meta(version, commit))
    overrides = platform_overrides or {}

    def request(package: str, selected=None):
        if selected is None:
            return copy.deepcopy(root)
        if package == "@withautonomi/ant":
            return copy.deepcopy(meta_value)
        return copy.deepcopy(overrides.get(package, npm_platform(version, commit)))

    return request


def verification_block(commit=OLD_COMMIT, ref="main", mode="current-merged-truth") -> str:
    return f"""<!-- verification:
  source_repo: ant-client
  source_ref: {ref}
  source_commit: {commit}
  verified_date: 2026-10-01
  verification_mode: {mode}
-->
"""


def baseline_asset(raw: dict) -> dict:
    return {
        "name": raw["name"],
        "id": raw["id"],
        "url": raw["browser_download_url"],
        "digest": raw["digest"],
    }


def valid_entry(root: Path, version="0.3.12", commit=COMMIT) -> dict:
    selected = release(version)
    by_name = {item["name"]: item for item in selected["assets"]}
    platforms = {}
    for target, extension in TARGETS.items():
        name = f"ant-{version}-{target}.{extension}"
        platforms[target] = {
            "archive": baseline_asset(by_name[name]),
            "signature": baseline_asset(by_name[f"{name}.sig"]),
        }
    npm_platforms = {
        target: {
            "package": package,
            "version": version,
            "metadata_url": f"https://registry.npmjs.org/{package.replace('/', '%2F')}/{version}",
            "integrity": PLATFORM_INTEGRITY,
            "git_head": commit,
        }
        for target, package in PACKAGES.items()
    }
    return {
        "component": "ant-cli",
        "context": "stable",
        "version": version,
        "source": {"repo": "ant-client", "tag": f"ant-cli-v{version}", "commit": commit},
        "github_release": {
            "id": selected["id"],
            "api_url": selected["url"],
            "release_url": selected["html_url"],
            "published_at": selected["published_at"],
            "draft": False,
            "prerelease": False,
            "checksum_asset": baseline_asset(by_name["SHA256SUMS.txt"]),
            "platforms": platforms,
        },
        "npm": {
            "package": "@withautonomi/ant",
            "dist_tag": "latest",
            "version": version,
            "metadata_url": f"https://registry.npmjs.org/@withautonomi%2Fant/{version}",
            "integrity": META_INTEGRITY,
            "git_head": commit,
            "platforms": npm_platforms,
        },
        "installers": [
            {
                "platform": platform,
                "url": url,
                "source_commit": source_commit,
                "blob_sha": blob,
                "evidence_url": f"https://github.com/WithAutonomi/ant-client/blob/{source_commit}/{path}",
                "selected_version": version,
            }
            for platform, url, source_commit, blob, path in (
                ("linux-macos", "https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.sh", INSTALL_COMMITS[0], INSTALL_BLOBS[0], "install.sh"),
                ("windows", "https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.ps1", INSTALL_COMMITS[1], INSTALL_BLOBS[1], "install.ps1"),
            )
        ],
        "shipped_dependencies": {
            "ant-core": {
                "version": version,
                "source_repo": "ant-client",
                "source_commit": commit,
                "evidence_url": f"https://github.com/WithAutonomi/ant-client/blob/{commit}/ant-core/Cargo.toml",
            }
        },
        "scoped_pages": ["docs/cli/command-reference.md", "docs/cli/use-the-cli.md"],
        "promotion": {"record": "planning/sweeps/2026-10-26.md"},
    }


class FixtureRepo(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for page in MAPPED:
            path = self.root / "docs" / page
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(verification_block(), encoding="utf-8")
        record = self.root / "planning/sweeps/2026-10-26.md"
        record.parent.mkdir(parents=True)
        record.write_text("audit fixture\n", encoding="utf-8")


class ReleaseBaselineValidatorTest(FixtureRepo):
    def validate(self, manifest, component_data=None):
        validator.validate_manifest_data(
            manifest,
            {"components": component_data or components()},
            {"repos": repos()},
            self.root,
        )

    def test_unchanged_browser_only_manifest_is_accepted(self) -> None:
        self.validate({"scope": {"pages": ["docs/browser.md"]}, "sources": {"browser": {"untranslated": True}}})

    def test_repository_ant_cli_discovery_configuration_matches_contract(self) -> None:
        registry = yaml.safe_load((SCRIPTS.parent / "component-registry.yml").read_text(encoding="utf-8"))
        ant_cli = registry["components"]["ant-cli"]
        self.assertEqual(ant_cli["release_discovery"], {"stable": discovery_config()})
        self.assertEqual(ant_cli["feeds_pages"], MAPPED)

    def test_valid_entry_and_two_component_identities_sharing_repo_commit(self) -> None:
        entry = valid_entry(self.root)
        self.validate({"scope": {}, "sources": {}, "release_baselines": {"schema_version": 1, "entries": {"ant-cli/stable": entry}}})

        other_components = components()
        other_components["other-cli"] = copy.deepcopy(other_components["ant-cli"])
        other_components["other-cli"]["feeds_pages"] = ["other.md"]
        other_components["other-cli"]["release_discovery"]["stable"]["github"]["tag_pattern"] = other_components["ant-cli"]["release_discovery"]["stable"]["github"]["tag_pattern"]
        (self.root / "docs/other.md").write_text(verification_block(), encoding="utf-8")
        other = copy.deepcopy(entry)
        other["component"] = "other-cli"
        other["scoped_pages"] = ["docs/other.md"]
        self.validate({"scope": {}, "sources": {}, "release_baselines": {"schema_version": 1, "entries": {"ant-cli/stable": entry, "other-cli/stable": other}}}, other_components)

    def test_first_cli_requires_ant_core_but_other_components_may_omit_dependencies(self) -> None:
        cli = valid_entry(self.root)
        del cli["shipped_dependencies"]
        with self.assertRaisesRegex(
            validator.ValidationError, r"shipped_dependencies"
        ):
            self.validate(
                {
                    "scope": {},
                    "sources": {},
                    "release_baselines": {
                        "schema_version": 1,
                        "entries": {"ant-cli/stable": cli},
                    },
                }
            )

        other_components = components()
        other_components["other-cli"] = copy.deepcopy(other_components["ant-cli"])
        other_components["other-cli"]["feeds_pages"] = ["other.md"]
        (self.root / "docs/other.md").write_text(
            verification_block(), encoding="utf-8"
        )
        other = valid_entry(self.root)
        other["component"] = "other-cli"
        other["scoped_pages"] = ["docs/other.md"]
        del other["shipped_dependencies"]
        self.validate(
            {
                "scope": {},
                "sources": {},
                "release_baselines": {
                    "schema_version": 1,
                    "entries": {"other-cli/stable": other},
                },
            },
            other_components,
        )

    def test_shipped_dependency_evidence_requires_commit_as_blob_ref(self) -> None:
        invalid_urls = (
            f"https://github.com/WithAutonomi/ant-client/blob/main/ant-core/Cargo.toml?commit={COMMIT}",
            f"https://github.com/WithAutonomi/ant-client/blob/main/ant-core/{COMMIT}.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/./ant-core/Cargo.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/../main/ant-core/Cargo.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/%2e/ant-core/Cargo.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/%2e%2e/main/ant-core/Cargo.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/..\\main/ant-core/Cargo.toml",
            f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/..%5Cmain/ant-core/Cargo.toml",
        )
        for evidence_url in invalid_urls:
            with self.subTest(evidence_url=evidence_url):
                broken = valid_entry(self.root)
                broken["shipped_dependencies"]["ant-core"][
                    "evidence_url"
                ] = evidence_url
                manifest = {
                    "scope": {},
                    "sources": {},
                    "release_baselines": {
                        "schema_version": 1,
                        "entries": {"ant-cli/stable": broken},
                    },
                }
                with self.assertRaisesRegex(
                    validator.ValidationError,
                    r"evidence_url: must identify the immutable source commit",
                ):
                    self.validate(manifest)

    def test_shipped_dependency_evidence_requires_exact_github_host(self) -> None:
        broken = valid_entry(self.root)
        broken["shipped_dependencies"]["ant-core"]["evidence_url"] = (
            f"https://example.com/WithAutonomi/ant-client/blob/{COMMIT}/ant-core/Cargo.toml"
        )
        manifest = {
            "scope": {},
            "sources": {},
            "release_baselines": {
                "schema_version": 1,
                "entries": {"ant-cli/stable": broken},
            },
        }
        with self.assertRaisesRegex(
            validator.ValidationError,
            r"evidence_url: must identify the immutable source commit",
        ):
            self.validate(manifest)

    def test_promoted_blocks_require_exact_five_field_schema(self) -> None:
        entry = valid_entry(self.root)
        manifest = {
            "scope": {},
            "sources": {},
            "release_baselines": {
                "schema_version": 1,
                "entries": {"ant-cli/stable": entry},
            },
        }
        promoted = verification_block(
            entry["source"]["commit"], entry["source"]["tag"], "target-manifest"
        )
        for page in entry["scoped_pages"]:
            (self.root / page).write_text(promoted, encoding="utf-8")
        validator.validate_manifest_page_blocks(manifest, self.root)

        page = self.root / entry["scoped_pages"][0]
        cases = (
            (promoted.replace("  verified_date: 2026-10-01\n", ""), "missing fields: verified_date"),
            (promoted.replace("  source_repo:", "  component: ant-cli\n  source_repo:"), "unknown fields: component"),
        )
        for malformed, diagnostic in cases:
            with self.subTest(diagnostic=diagnostic):
                page.write_text(malformed, encoding="utf-8")
                with self.assertRaisesRegex(validator.ValidationError, diagnostic):
                    validator.validate_manifest_page_blocks(manifest, self.root)
                page.write_text(promoted, encoding="utf-8")

    def test_github_published_at_requires_complete_rfc3339_utc_datetime(self) -> None:
        valid = valid_entry(self.root)
        valid["github_release"]["published_at"] = "2026-10-23T00:17:25Z"
        self.validate(
            {
                "scope": {},
                "sources": {},
                "release_baselines": {
                    "schema_version": 1,
                    "entries": {"ant-cli/stable": valid},
                },
            }
        )

        for published_at in (
            "2026-10-23 00:17:25Z",
            "20261023T001725Z",
            "2026-10-25Z",
            "2026-10-23T00:17Z",
            123,
            "not-a-timestampZ",
            "2026-02-30T00:17:25Z",
            "2026-10-23T24:17:25Z",
            "2026-10-23T00:17:25+00:00",
        ):
            with self.subTest(published_at=published_at):
                malformed = valid_entry(self.root)
                malformed["github_release"]["published_at"] = published_at
                manifest = {
                    "scope": {},
                    "sources": {},
                    "release_baselines": {
                        "schema_version": 1,
                        "entries": {"ant-cli/stable": malformed},
                    },
                }
                with self.assertRaisesRegex(
                    validator.ValidationError,
                    r"github_release\.published_at",
                ):
                    self.validate(manifest)

    def test_duplicate_yaml_keys_are_rejected_by_the_real_loader(self) -> None:
        path = self.root / "duplicate.yml"
        path.write_text("scope: {}\nsources: {}\nrelease_baselines:\n  schema_version: 1\n  schema_version: 1\n  entries: {}\n", encoding="utf-8")
        with self.assertRaisesRegex(validator.ValidationError, "duplicate YAML key"):
            validator.load_yaml_strict(path)

    def test_unknown_keys_are_rejected_at_each_release_map_level(self) -> None:
        base = valid_entry(self.root)
        locations = [
            (), ("source",), ("github_release",), ("github_release", "checksum_asset"),
            ("github_release", "platforms", "aarch64-apple-darwin"),
            ("github_release", "platforms", "aarch64-apple-darwin", "archive"),
            ("npm",), ("npm", "platforms", "aarch64-apple-darwin"),
            ("installers", 0), ("shipped_dependencies", "ant-core"), ("promotion",),
        ]
        for location in locations:
            with self.subTest(location=location):
                broken = copy.deepcopy(base)
                target = broken
                for key in location:
                    target = target[key]
                target["unknown"] = "value"
                manifest = {"scope": {}, "sources": {}, "release_baselines": {"schema_version": 1, "entries": {"ant-cli/stable": broken}}}
                with self.assertRaisesRegex(validator.ValidationError, "unknown keys"):
                    self.validate(manifest)

    def test_placeholders_malformed_values_duplicates_and_relationships_fail(self) -> None:
        mutations = []
        placeholder = valid_entry(self.root); placeholder["source"]["tag"] = "<tag>"; mutations.append(placeholder)
        bad_version = valid_entry(self.root); bad_version["version"] = "0.3.12-beta.1"; mutations.append(bad_version)
        wrong_repo = valid_entry(self.root); wrong_repo["source"]["repo"] = "missing"; mutations.append(wrong_repo)
        wrong_page = valid_entry(self.root); wrong_page["scoped_pages"] = ["docs/index.md"]; mutations.append(wrong_page)
        duplicate_page = valid_entry(self.root); duplicate_page["scoped_pages"] = ["docs/cli/use-the-cli.md", "docs/cli/use-the-cli.md"]; mutations.append(duplicate_page)
        missing_file = valid_entry(self.root); missing_file["promotion"]["record"] = "planning/sweeps/2026-10-27.md"; mutations.append(missing_file)
        duplicate_asset = valid_entry(self.root); duplicate_asset["github_release"]["platforms"]["aarch64-apple-darwin"]["archive"]["id"] = 1; mutations.append(duplicate_asset)
        wrong_pair = valid_entry(self.root); del wrong_pair["npm"]["platforms"]["aarch64-apple-darwin"]; mutations.append(wrong_pair)
        wrong_installer = valid_entry(self.root); wrong_installer["installers"].reverse(); mutations.append(wrong_installer)
        bad_hash = valid_entry(self.root); bad_hash["source"]["commit"] = "A" * 40; mutations.append(bad_hash)
        for index, broken in enumerate(mutations):
            with self.subTest(case=index):
                manifest = {"scope": {}, "sources": {}, "release_baselines": {"schema_version": 1, "entries": {"ant-cli/stable": broken}}}
                with self.assertRaises(validator.ValidationError):
                    self.validate(manifest)

    def test_npm_integrity_requires_canonical_sha512_bytes(self) -> None:
        invalid_values = (
            "sha512-YWJjZA==",
            "sha512-" + base64.b64encode(b"x" * 64).decode("ascii").rstrip("="),
            "sha512-" + base64.b64encode(b"x" * 64).decode("ascii")[:-2] + "!!",
            "sha256-" + base64.b64encode(b"x" * 64).decode("ascii"),
        )
        for location in (("npm", "integrity"), ("npm", "platforms", "aarch64-apple-darwin", "integrity")):
            for integrity in invalid_values:
                with self.subTest(location=location, integrity=integrity):
                    broken = valid_entry(self.root)
                    target = broken
                    for key in location[:-1]:
                        target = target[key]
                    target[location[-1]] = integrity
                    manifest = {
                        "scope": {},
                        "sources": {},
                        "release_baselines": {
                            "schema_version": 1,
                            "entries": {"ant-cli/stable": broken},
                        },
                    }
                    with self.assertRaises(validator.ValidationError):
                        self.validate(manifest)

    def authenticity_fixture(self):
        downloads = self.root / f"downloads-{len(list(self.root.glob('downloads-*')))}"
        downloads.mkdir()
        key = downloads / "release.pub"
        key.write_bytes(b"fixture public key")
        selected = valid_entry(self.root)["github_release"]
        archive_lines = []
        for target in sorted(TARGETS):
            archive = selected["platforms"][target]["archive"]
            signature = selected["platforms"][target]["signature"]
            archive_bytes = f"archive:{target}".encode()
            signature_bytes = f"signature:{target}".encode()
            (downloads / archive["name"]).write_bytes(archive_bytes)
            (downloads / signature["name"]).write_bytes(signature_bytes)
            archive["digest"] = "sha256:" + hashlib.sha256(archive_bytes).hexdigest()
            signature["digest"] = "sha256:" + hashlib.sha256(signature_bytes).hexdigest()
            archive_lines.append(
                f"{hashlib.sha256(archive_bytes).hexdigest()}  {archive['name']}"
            )
        checksum_bytes = ("\n".join(archive_lines) + "\n").encode()
        checksum = selected["checksum_asset"]
        (downloads / checksum["name"]).write_bytes(checksum_bytes)
        checksum["digest"] = "sha256:" + hashlib.sha256(checksum_bytes).hexdigest()
        canonical = {
            "key_file": key.name,
            "key_source": f"https://github.com/WithAutonomi/ant-client/blob/{COMMIT}/release.pub",
            "key_fingerprint": "fixture-key-fingerprint-001",
            "tool": "fixture-signature-tool",
            "tool_version": "1.0.0",
            "context": "ant-cli-release",
        }

        def verify(archive_path, signature_path, key_path, evidence):
            return {
                "command": [
                    evidence["tool"],
                    "verify",
                    str(key_path),
                    str(signature_path),
                    str(archive_path),
                ],
                "exit_code": 0,
                "verified": True,
            }

        return downloads, selected, canonical, verify

    def test_local_authenticity_fixture_checks_every_asset_checksum_and_signature(self) -> None:
        downloads, selected, canonical, verify = self.authenticity_fixture()
        with patch.object(
            validator.urllib.parse,
            "urlparse",
            wraps=validator.urllib.parse.urlparse,
        ):
            results = validator.validate_authenticity_fixture(
                selected, downloads, canonical, verify
            )
        self.assertEqual(len(results), 5)
        self.assertEqual(
            {result["archive"] for result in results},
            {
                selected["platforms"][target]["archive"]["name"]
                for target in TARGETS
            },
        )

    def test_local_authenticity_fixture_fails_closed_on_each_evidence_class(self) -> None:
        mutations = []

        downloads, selected, canonical, verify = self.authenticity_fixture()
        selected["platforms"][next(iter(TARGETS))]["archive"]["digest"] = "sha256:" + "0" * 64
        mutations.append((downloads, selected, canonical, verify, "provider digest mismatch"))

        downloads, selected, canonical, verify = self.authenticity_fixture()
        missing_archive = selected["platforms"][next(iter(TARGETS))]["archive"]["name"]
        (downloads / missing_archive).unlink()
        mutations.append((downloads, selected, canonical, verify, "downloaded file is missing"))

        downloads, selected, canonical, verify = self.authenticity_fixture()
        checksum_path = downloads / selected["checksum_asset"]["name"]
        checksum_path.write_text(checksum_path.read_text() + checksum_path.read_text().splitlines()[0] + "\n")
        selected["checksum_asset"]["digest"] = "sha256:" + hashlib.sha256(checksum_path.read_bytes()).hexdigest()
        mutations.append((downloads, selected, canonical, verify, "duplicate checksum entry"))

        downloads, selected, canonical, verify = self.authenticity_fixture()
        checksum_path = downloads / selected["checksum_asset"]["name"]
        checksum_lines = checksum_path.read_text().splitlines()
        checksum_lines[0] = "0" * 64 + checksum_lines[0][64:]
        checksum_path.write_text("\n".join(checksum_lines) + "\n")
        selected["checksum_asset"]["digest"] = "sha256:" + hashlib.sha256(checksum_path.read_bytes()).hexdigest()
        mutations.append((downloads, selected, canonical, verify, "checksum mismatch"))

        downloads, selected, canonical, verify = self.authenticity_fixture()
        bad_canonical = dict(canonical)
        bad_canonical["context"] = "<context>"
        mutations.append((downloads, selected, bad_canonical, verify, "placeholder"))

        downloads, selected, canonical, verify = self.authenticity_fixture()
        missing_key = dict(canonical)
        missing_key["key_file"] = "missing.pub"
        mutations.append((downloads, selected, missing_key, verify, "missing local canonical key"))

        downloads, selected, canonical, _verify = self.authenticity_fixture()
        def failed_verify(archive_path, signature_path, key_path, evidence):
            return {
                "command": [
                    evidence["tool"], str(key_path), str(signature_path), str(archive_path)
                ],
                "exit_code": 1,
                "verified": False,
            }
        mutations.append((downloads, selected, canonical, failed_verify, "signature verification failed"))

        downloads, selected, canonical, _verify = self.authenticity_fixture()
        def ambient_verify(archive_path, signature_path, key_path, evidence):
            return {
                "command": [evidence["tool"], str(signature_path), str(archive_path)],
                "exit_code": 0,
                "verified": True,
            }
        mutations.append((downloads, selected, canonical, ambient_verify, "explicit archive, signature, and key paths"))

        for downloads, selected, canonical, verifier, diagnostic in mutations:
            with self.subTest(diagnostic=diagnostic), self.assertRaisesRegex(
                validator.ValidationError, diagnostic
            ):
                validator.validate_authenticity_fixture(
                    selected, downloads, canonical, verifier
                )


class ReleaseDiscoveryTest(FixtureRepo):
    def setUp(self) -> None:
        super().setUp()
        self.components = components()
        self.registry = repos()
        self.patches = patch.multiple(scanner, REPO_ROOT=self.root, DOCS_DIR=self.root / "docs")
        self.patches.start()
        self.addCleanup(self.patches.stop)

    def discover(self, baseline=None, *, gh=None, npm=None):
        notices = []
        baselines = {"ant-cli/stable": baseline} if baseline is not None else {}
        with (
            patch.object(scanner, "github_request", side_effect=gh or github_router()) as github_mock,
            patch.object(scanner, "npm_request", side_effect=npm or npm_router()) as npm_mock,
            patch.object(scanner.urllib.request, "urlopen", side_effect=AssertionError("network access forbidden")),
        ):
            records, candidates = scanner.discover_releases(self.components, self.registry, baselines, "token", notices)
        return records, candidates, notices, github_mock.call_args_list, npm_mock.call_args_list

    def promote_pages(self, entry):
        for page in entry["scoped_pages"]:
            (self.root / page).write_text(
                verification_block(entry["source"]["commit"], entry["source"]["tag"], "target-manifest"),
                encoding="utf-8",
            )

    def test_github_paginates_sorts_semver_and_peels_annotated_tag(self) -> None:
        page_one = [release("0.3.9", release_id=309)]
        page_one.extend(
            release("99.0.0", release_id=1000 + index, draft=True)
            for index in range(97)
        )
        page_one.extend((release("1.0.0", release_id=1998, prerelease=True), release("0.3.11", release_id=311)))
        self.assertEqual(len(page_one), 100)
        router = github_router({1: page_one, 2: [release("0.3.12")], 3: []})
        with patch.object(scanner, "github_request", side_effect=router) as mocked:
            observed = scanner.observe_github_release("WithAutonomi", "ant-client", discovery_config()["github"], "token")
        self.assertTrue(observed["complete"])
        self.assertEqual((observed["version"], observed["commit"]), ("0.3.12", COMMIT))
        self.assertEqual(list(observed["release"]["platforms"]), sorted(TARGETS))
        self.assertIn("page=2", mocked.call_args_list[1].args[0])
        self.assertTrue(any("/git/tags/" in item.args[0] for item in mocked.call_args_list))

        def lightweight(path, token=None):
            if "/releases?" in path:
                return [release()]
            if "/git/ref/tags/" in path:
                return {"object": {"type": "commit", "sha": COMMIT}}
            raise AssertionError(path)
        with patch.object(scanner, "github_request", side_effect=lightweight) as mocked:
            self.assertEqual(
                scanner.observe_github_release("WithAutonomi", "ant-client", discovery_config()["github"], None)["commit"],
                COMMIT,
            )
        self.assertFalse(any("/git/tags/" in item.args[0] for item in mocked.call_args_list))

    def test_github_published_at_requires_complete_rfc3339_utc_datetime(self) -> None:
        valid = release()
        valid["published_at"] = "2026-10-23T00:17:25Z"
        with patch.object(
            scanner,
            "github_request",
            side_effect=github_router({1: [valid]}),
        ):
            observed = scanner.observe_github_release(
                "WithAutonomi", "ant-client", discovery_config()["github"], None
            )
        self.assertEqual(
            observed["release"]["published_at"], "2026-10-23T00:17:25Z"
        )

        for published_at in (
            "2026-10-25Z",
            "2026-10-23 00:17:25Z",
            "20261023T001725Z",
            "2026-10-23T00:17Z",
        ):
            with self.subTest(published_at=published_at):
                malformed = release()
                malformed["published_at"] = published_at
                with (
                    patch.object(
                        scanner,
                        "github_request",
                        side_effect=github_router({1: [malformed]}),
                    ),
                    self.assertRaises(scanner.FailClosed) as raised,
                ):
                    scanner.observe_github_release(
                        "WithAutonomi",
                        "ant-client",
                        discovery_config()["github"],
                        None,
                    )
                self.assertEqual(
                    raised.exception.diagnostic["kind"],
                    "github_release_shape_error",
                )

    def test_github_rejects_suffixes_flags_and_reports_asset_incompleteness(self) -> None:
        configured = discovery_config()["github"]
        invalid = release("0.3.99", draft=True)
        suffix = release(); suffix["tag_name"] = "ant-cli-v0.4.0-beta.1"
        selected = release(); selected["assets"].pop(); selected["assets"].append(copy.deepcopy(selected["assets"][1]))
        with patch.object(scanner, "github_request", side_effect=github_router({1: [invalid, suffix, selected]})):
            observed = scanner.observe_github_release("WithAutonomi", "ant-client", configured, None)
        self.assertFalse(observed["complete"])
        self.assertTrue(any("occurs" in problem for problem in observed["problems"]))

    def test_github_rejects_duplicate_required_asset_ids(self) -> None:
        selected = release()
        selected["assets"][2]["id"] = selected["assets"][1]["id"]
        with patch.object(
            scanner,
            "github_request",
            side_effect=github_router({1: [selected]}),
        ):
            observed = scanner.observe_github_release(
                "WithAutonomi", "ant-client", discovery_config()["github"], None
            )
        self.assertFalse(observed["complete"])
        self.assertTrue(
            any("asset id" in problem for problem in observed["problems"])
        )

    def test_npm_requires_latest_meta_and_all_five_exact_platforms(self) -> None:
        with patch.object(scanner, "npm_request", side_effect=npm_router()):
            observed = scanner.observe_npm_release(discovery_config()["npm"])
        self.assertTrue(observed["complete"])
        self.assertEqual(list(observed["npm"]["platforms"]), sorted(TARGETS))

        cases = []
        prerelease = npm_router(version="0.3.13-beta.1"); cases.append(prerelease)
        no_integrity = npm_meta(); del no_integrity["dist"]["integrity"]; cases.append(npm_router(meta=no_integrity))
        no_head = npm_meta(); del no_head["gitHead"]; cases.append(npm_router(meta=no_head))
        wrong_optional = npm_meta(); wrong_optional["optionalDependencies"][next(iter(PACKAGES.values()))] = "0.3.11"; cases.append(npm_router(meta=wrong_optional))
        package = next(iter(PACKAGES.values()))
        cases.append(npm_router(platform_overrides={package: npm_platform("0.3.11")}))
        cases.append(npm_router(platform_overrides={package: npm_platform(commit="6" * 40)}))
        for index, router in enumerate(cases):
            with self.subTest(case=index), patch.object(scanner, "npm_request", side_effect=router):
                self.assertFalse(scanner.observe_npm_release(discovery_config()["npm"])["complete"])

    def test_candidate_requires_identical_complete_five_platform_sets(self) -> None:
        removed = "x86_64-pc-windows-msvc"
        for reduce_github in (False, True):
            with self.subTest(
                case="both reduced" if reduce_github else "five versus four"
            ):
                self.components = components()
                stable = self.components["ant-cli"]["release_discovery"]["stable"]
                del stable["npm"]["platform_packages"][removed]
                if reduce_github:
                    del stable["github"]["platforms"][removed]

                _, candidates, notices, _, _ = self.discover()

                self.assertEqual(candidates, [])
                manual = next(
                    notice
                    for notice in notices
                    if notice["kind"] == "release_manual_review"
                )
                self.assertIn(
                    "same five required CLI platform targets", manual["reason"]
                )

    def test_npm_discovery_rejects_noncanonical_or_wrong_length_integrity(self) -> None:
        invalid_values = (
            "sha512-YWJjZA==",
            "sha512-" + base64.b64encode(b"x" * 64).decode("ascii").rstrip("="),
            "sha512-" + base64.b64encode(b"x" * 64).decode("ascii")[:-2] + "!!",
            "sha256-" + base64.b64encode(b"x" * 64).decode("ascii"),
        )
        package = next(iter(PACKAGES.values()))
        for integrity in invalid_values:
            with self.subTest(kind="meta", integrity=integrity):
                meta = npm_meta()
                meta["dist"]["integrity"] = integrity
                with patch.object(scanner, "npm_request", side_effect=npm_router(meta=meta)):
                    self.assertFalse(
                        scanner.observe_npm_release(discovery_config()["npm"])["complete"]
                    )
            with self.subTest(kind="platform", integrity=integrity):
                platform = npm_platform()
                platform["dist"]["integrity"] = integrity
                router = npm_router(platform_overrides={package: platform})
                with patch.object(scanner, "npm_request", side_effect=router):
                    self.assertFalse(
                        scanner.observe_npm_release(discovery_config()["npm"])["complete"]
                    )

    def test_initial_candidate_maps_two_cli_and_seven_shared_pages_deterministically(self) -> None:
        before = {path: (self.root / "docs" / path).read_bytes() for path in MAPPED}
        records, candidates, notices, github_calls, npm_calls = self.discover()
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual((candidate["version"], candidate["source"]["commit"]), ("0.3.12", COMMIT))
        self.assertEqual([page["path"] for page in candidate["pages"]], sorted(f"docs/{page}" for page in MAPPED))
        self.assertEqual(sum(page["components"] == ["ant-cli"] for page in candidate["pages"]), 2)
        self.assertEqual(sum(page["components"] == ["ant-cli", "ant-core"] for page in candidate["pages"]), 7)
        self.assertEqual(candidate["records"], records)
        self.assertTrue(all(set(record) == {"location", "scope", "repo", "ref", "recorded_sha", "head_sha", "drifted"} for record in records))
        self.assertTrue(all(record["drifted"] for record in records))
        self.assertEqual([notice["kind"] for notice in notices], ["installer_observation"])
        self.assertEqual(len(notices[0]["installers"]), 2)
        self.assertEqual(len(npm_calls), 7)
        self.assertTrue(any("install.sh" in item.args[0] for item in github_calls))
        self.assertEqual(before, {path: (self.root / "docs" / path).read_bytes() for path in MAPPED})

    def test_disagreement_and_incomplete_evidence_use_manual_review_without_candidate(self) -> None:
        records, candidates, notices, _, _ = self.discover(npm=npm_router(version="0.3.11"))
        self.assertEqual(candidates, [])
        self.assertEqual(len(records), 9)
        manual = [notice for notice in notices if notice["kind"] == "release_manual_review"]
        self.assertEqual(len(manual), 1)
        self.assertIn("versions disagree", manual[0]["reason"])

        incomplete = release(); incomplete["assets"].pop()
        records, candidates, notices, _, _ = self.discover(gh=github_router({1: [incomplete]}))
        self.assertEqual(candidates, [])
        self.assertEqual(len(records), 9)
        self.assertTrue(any(notice["kind"] == "release_manual_review" for notice in notices))

    def test_missing_github_signature_retains_other_valid_release_assets(self) -> None:
        selected = release()
        target = sorted(TARGETS)[0]
        archive_name = f"ant-0.3.12-{target}.{TARGETS[target]}"
        signature_name = f"{archive_name}.sig"
        selected["assets"] = [
            item for item in selected["assets"] if item["name"] != signature_name
        ]

        _, candidates, notices, _, _ = self.discover(
            gh=github_router({1: [selected]})
        )

        self.assertEqual(candidates, [])
        manual = next(
            notice for notice in notices if notice["kind"] == "release_manual_review"
        )
        self.assertIn(
            f"required asset {signature_name!r} occurs 0 times", manual["reason"]
        )
        observed = manual["current"]["github"]["release"]
        self.assertEqual(observed["checksum_asset"]["name"], "SHA256SUMS.txt")
        self.assertEqual(
            observed["platforms"][target],
            {"archive": baseline_asset(next(
                item for item in selected["assets"] if item["name"] == archive_name
            ))},
        )
        self.assertTrue(
            all(
                set(assets) == {"archive", "signature"}
                for other_target, assets in observed["platforms"].items()
                if other_target != target
            )
        )

    def test_invalid_npm_integrity_retains_other_valid_package_evidence(self) -> None:
        target = sorted(PACKAGES)[0]
        package = PACKAGES[target]
        invalid = npm_platform()
        invalid["dist"]["integrity"] = "sha512-invalid"

        _, candidates, notices, _, _ = self.discover(
            npm=npm_router(platform_overrides={package: invalid})
        )

        self.assertEqual(candidates, [])
        manual = next(
            notice for notice in notices if notice["kind"] == "release_manual_review"
        )
        self.assertIn(
            f"npm platform package {package!r} integrity is missing or invalid",
            manual["reason"],
        )
        observed = manual["current"]["npm"]["npm"]
        self.assertEqual(observed["version"], "0.3.12")
        self.assertEqual(observed["integrity"], META_INTEGRITY)
        self.assertEqual(
            observed["platforms"][target],
            {
                "package": package,
                "version": "0.3.12",
                "metadata_url": (
                    f"https://registry.npmjs.org/{package.replace('/', '%2F')}/0.3.12"
                ),
                "git_head": COMMIT,
            },
        )
        self.assertTrue(
            all(
                (
                    package_observation["version"],
                    package_observation["integrity"],
                    package_observation["git_head"],
                )
                == ("0.3.12", PLATFORM_INTEGRITY, COMMIT)
                for other_target, package_observation in observed["platforms"].items()
                if other_target != target
            )
        )

    def test_initial_incomplete_evidence_uses_each_pages_own_final_fallbacks(self) -> None:
        self.components["ant-cli"]["feeds_pages"] = [
            "cli/command-reference.md",
            "cli/use-the-cli.md",
        ]
        page_fields = {
            "docs/cli/command-reference.md": ("release/page-a", COMMIT),
            "docs/cli/use-the-cli.md": ("release/page-b", OLD_COMMIT),
        }
        for page, (ref, commit) in page_fields.items():
            (self.root / page).write_text(
                verification_block(commit=commit, ref=ref), encoding="utf-8"
            )

        no_github_release = github_router({1: []})
        records, candidates, notices, _, _ = self.discover(gh=no_github_release)
        self.assertEqual(candidates, [])
        by_page = {record["location"].split(":", 1)[0]: record for record in records}
        self.assertEqual(
            {
                page: (record["ref"], record["recorded_sha"], record["head_sha"], record["drifted"])
                for page, record in by_page.items()
            },
            {
                "docs/cli/command-reference.md": (
                    "release/page-a",
                    COMMIT,
                    COMMIT,
                    False,
                ),
                "docs/cli/use-the-cli.md": (
                    "release/page-b",
                    OLD_COMMIT,
                    COMMIT,
                    True,
                ),
            },
        )
        self.assertTrue(
            any(notice["kind"] == "release_manual_review" for notice in notices)
        )

        npm_without_head = npm_meta()
        del npm_without_head["gitHead"]
        records, candidates, notices, _, _ = self.discover(
            gh=no_github_release,
            npm=npm_router(meta=npm_without_head),
        )
        self.assertEqual(candidates, [])
        by_page = {record["location"].split(":", 1)[0]: record for record in records}
        self.assertEqual(
            {
                page: (record["ref"], record["head_sha"], record["drifted"])
                for page, record in by_page.items()
            },
            {
                "docs/cli/command-reference.md": (
                    "release/page-a",
                    COMMIT,
                    False,
                ),
                "docs/cli/use-the-cli.md": (
                    "release/page-b",
                    OLD_COMMIT,
                    False,
                ),
            },
        )
        self.assertTrue(
            any(notice["kind"] == "release_manual_review" for notice in notices)
        )

    def test_baseline_equal_newer_mutated_lower_and_installer_drift(self) -> None:
        base = valid_entry(self.root)
        self.promote_pages(base)
        records, candidates, notices, _, _ = self.discover(base)
        self.assertEqual(candidates, [])
        self.assertEqual(len(records), 2)
        self.assertTrue(all(not record["drifted"] for record in records))
        self.assertFalse(any(notice["kind"] == "release_manual_review" for notice in notices))

        older = valid_entry(self.root, version="0.3.11", commit=OLD_COMMIT)
        self.promote_pages(older)
        records, candidates, notices, _, _ = self.discover(older)
        self.assertEqual(len(candidates), 1)
        self.assertTrue(all(record["drifted"] for record in records))

        self.promote_pages(base)
        mutated = copy.deepcopy(base); mutated["github_release"]["id"] = 999
        records, candidates, notices, _, _ = self.discover(mutated)
        self.assertEqual(candidates, [])
        self.assertTrue(any(notice["kind"] == "release_manual_review" for notice in notices))

        newer = valid_entry(self.root, version="0.3.13", commit=OLD_COMMIT)
        self.promote_pages(newer)
        records, candidates, notices, _, _ = self.discover(newer)
        self.assertEqual(candidates, [])
        self.assertTrue(any("lower" in notice.get("reason", "") for notice in notices))

        self.promote_pages(base)
        drifted_installers = copy.deepcopy(base); drifted_installers["installers"][0]["blob_sha"] = "7" * 40
        records, candidates, notices, _, _ = self.discover(drifted_installers)
        self.assertEqual(candidates, [])
        self.assertTrue(all(not record["drifted"] for record in records))
        self.assertTrue(any("installer evidence" in notice.get("reason", "") for notice in notices))

    def test_manual_review_notice_carries_exact_baseline_and_current_evidence(self) -> None:
        baseline = valid_entry(self.root)
        self.promote_pages(baseline)
        baseline["github_release"]["id"] = 999
        _, candidates, notices, _, _ = self.discover(baseline)
        self.assertEqual(candidates, [])
        manual = next(
            notice for notice in notices if notice["kind"] == "release_manual_review"
        )
        self.assertEqual(
            manual["baseline"],
            {
                "source": baseline["source"],
                "github_release": baseline["github_release"],
                "npm": baseline["npm"],
                "installers": baseline["installers"],
            },
        )
        current = valid_entry(self.root)
        self.assertEqual(manual["current"]["github"]["release"], current["github_release"])
        self.assertEqual(manual["current"]["npm"]["npm"], current["npm"])
        self.assertEqual(
            manual["current"]["installers"],
            [
                {key: value for key, value in installer.items() if key != "selected_version"}
                | {"repo": "WithAutonomi/ant-client", "ref": "main", "path": path}
                for installer, path in zip(current["installers"], ("install.sh", "install.ps1"))
            ],
        )

    def test_url_timestamp_order_and_download_count_do_not_change_projection(self) -> None:
        base = valid_entry(self.root)
        changed = copy.deepcopy(base)
        changed["github_release"]["release_url"] = "https://example.invalid/ignored"
        changed["github_release"]["published_at"] = "2030-01-01T00:00:00Z"
        changed["npm"]["metadata_url"] = "https://example.invalid/ignored"
        self.assertEqual(
            scanner._release_projection("ant-cli", "stable", base),
            scanner._release_projection("ant-cli", "stable", changed),
        )

    def test_installer_provider_and_blob_linkage_fail_closed(self) -> None:
        def failing(path, token=None):
            if "/commits?" in path:
                raise scanner.FailClosed({"kind": "github_api_http_error", "message": "fixture failure"})
            return github_router()(path, token)
        with self.assertRaises(scanner.FailClosed):
            self.discover(gh=failing)

        broken = github_router(installer_blobs=("not-a-sha", INSTALL_BLOBS[1]))
        with self.assertRaises(scanner.FailClosed) as raised:
            self.discover(gh=broken)
        self.assertEqual(raised.exception.diagnostic["kind"], "installer_blob_linkage_error")

    def test_provider_transport_parse_and_shape_failures_are_fail_closed(self) -> None:
        with patch.object(scanner.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")):
            with self.assertRaises(scanner.FailClosed) as raised:
                scanner._provider_json("https://registry.npmjs.org/example", "npm")
        self.assertEqual(raised.exception.diagnostic["kind"], "npm_network_error")
        with patch.object(scanner, "github_request", return_value={}):
            with self.assertRaises(scanner.FailClosed) as raised:
                scanner.observe_github_release("WithAutonomi", "ant-client", discovery_config()["github"], None)
        self.assertEqual(raised.exception.diagnostic["kind"], "github_release_shape_error")

    def test_main_provider_failure_has_existing_top_level_error_shape(self) -> None:
        (self.root / "component-registry.yml").write_text(
            yaml.safe_dump({"components": self.components}), encoding="utf-8"
        )
        (self.root / "repo-registry.yml").write_text(
            yaml.safe_dump({"repos": self.registry}), encoding="utf-8"
        )
        (self.root / "target-manifest.yml").write_text(
            "scope: {}\nsources: {}\n", encoding="utf-8"
        )
        output = io.StringIO()
        paths = {
            "REPO_ROOT": self.root,
            "DOCS_DIR": self.root / "docs",
            "REGISTRY_PATH": self.root / "repo-registry.yml",
            "COMPONENT_REGISTRY_PATH": self.root / "component-registry.yml",
            "TARGET_MANIFEST_PATH": self.root / "target-manifest.yml",
        }
        failure = scanner.FailClosed({"kind": "release_provider_fixture", "message": "fixture failure"})
        with (
            patch.multiple(scanner, **paths),
            patch.object(scanner, "discover_releases", side_effect=failure),
            patch.dict("os.environ", {"GITHUB_TOKEN": "fixture"}),
            contextlib.redirect_stdout(output),
        ):
            code = scanner.main()
        report = json.loads(output.getvalue())
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "error")
        self.assertEqual(report["records"], [])
        self.assertEqual(report["migration_backlog"], [])
        self.assertEqual(report["release_candidates"], [])

    def test_main_malformed_github_published_at_fails_closed(self) -> None:
        (self.root / "component-registry.yml").write_text(
            yaml.safe_dump({"components": self.components}), encoding="utf-8"
        )
        (self.root / "repo-registry.yml").write_text(
            yaml.safe_dump({"repos": self.registry}), encoding="utf-8"
        )
        (self.root / "target-manifest.yml").write_text(
            "scope: {}\nsources: {}\n", encoding="utf-8"
        )
        paths = {
            "REPO_ROOT": self.root,
            "DOCS_DIR": self.root / "docs",
            "REGISTRY_PATH": self.root / "repo-registry.yml",
            "COMPONENT_REGISTRY_PATH": self.root / "component-registry.yml",
            "TARGET_MANIFEST_PATH": self.root / "target-manifest.yml",
        }
        for published_at in (123, "not-a-timestampZ"):
            with self.subTest(published_at=published_at):
                malformed = release()
                malformed["published_at"] = published_at
                output = io.StringIO()
                with (
                    patch.multiple(scanner, **paths),
                    patch.object(
                        scanner,
                        "github_request",
                        side_effect=github_router({1: [malformed]}),
                    ),
                    patch.object(
                        scanner.urllib.request,
                        "urlopen",
                        side_effect=AssertionError("network access forbidden"),
                    ),
                    patch.dict("os.environ", {"GITHUB_TOKEN": "fixture"}),
                    contextlib.redirect_stdout(output),
                ):
                    code = scanner.main()
                report = json.loads(output.getvalue())
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "error")
                self.assertEqual(report["records"], [])
                self.assertEqual(report["migration_backlog"], [])
                self.assertEqual(report["release_candidates"], [])
                self.assertEqual(
                    report["errors"][0]["kind"], "github_release_shape_error"
                )

    def test_main_output_includes_installer_observation_notice(self) -> None:
        (self.root / "component-registry.yml").write_text(
            yaml.safe_dump({"components": self.components}), encoding="utf-8"
        )
        (self.root / "repo-registry.yml").write_text(
            yaml.safe_dump({"repos": self.registry}), encoding="utf-8"
        )
        (self.root / "target-manifest.yml").write_text(
            "scope: {}\nsources: {}\n", encoding="utf-8"
        )
        output = io.StringIO()
        paths = {
            "REPO_ROOT": self.root,
            "DOCS_DIR": self.root / "docs",
            "REGISTRY_PATH": self.root / "repo-registry.yml",
            "COMPONENT_REGISTRY_PATH": self.root / "component-registry.yml",
            "TARGET_MANIFEST_PATH": self.root / "target-manifest.yml",
        }
        with (
            patch.multiple(scanner, **paths),
            patch.object(scanner, "github_request", side_effect=github_router()),
            patch.object(scanner, "npm_request", side_effect=npm_router()),
            patch.object(
                scanner.urllib.request,
                "urlopen",
                side_effect=AssertionError("network access forbidden"),
            ),
            patch.dict("os.environ", {"GITHUB_TOKEN": "fixture"}),
            contextlib.redirect_stdout(output),
        ):
            code = scanner.main()
        report = json.loads(output.getvalue())
        observations = [
            notice
            for notice in report["notices"]
            if notice["kind"] == "installer_observation"
        ]
        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(len(report["migration_backlog"]), len(MAPPED))
        self.assertEqual(
            {
                entry["location"]
                for entry in report["migration_backlog"]
                if entry["location"].startswith("docs/cli/")
            },
            {
                "docs/cli/command-reference.md:1",
                "docs/cli/use-the-cli.md:1",
            },
        )
        self.assertEqual(len(observations), 1)
        self.assertEqual(len(observations[0]["installers"]), 2)

    def test_missing_multiple_and_mismatched_page_blocks_fail_closed(self) -> None:
        base = valid_entry(self.root)
        self.promote_pages(base)
        page = self.root / "docs/cli/use-the-cli.md"
        for content in (
            "# missing\n",
            verification_block(COMMIT, base["source"]["tag"], "target-manifest") * 2,
            verification_block(COMMIT, "wrong-tag", "target-manifest"),
        ):
            with self.subTest(content=content):
                page.write_text(content, encoding="utf-8")
                with self.assertRaises(scanner.FailClosed):
                    self.discover(base)
                page.write_text(verification_block(COMMIT, base["source"]["tag"], "target-manifest"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
