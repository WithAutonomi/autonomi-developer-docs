#!/usr/bin/env python3
"""Validate the optional released-software baseline manifest extension."""

from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "target-manifest.yml"
COMPONENT_REGISTRY_PATH = REPO_ROOT / "component-registry.yml"
REPO_REGISTRY_PATH = REPO_ROOT / "repo-registry.yml"

SEMVER_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
DIGEST_HEX_RE = re.compile(r"[0-9a-f]{64}\Z")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
PROMOTION_RE = re.compile(r"planning/sweeps/[0-9]{4}-[0-9]{2}-[0-9]{2}\.md\Z")
PROMOTION_BRANCH_RE = re.compile(
    r"claude/(sweep|prose)-([0-9]{4}-[0-9]{2}-[0-9]{2})(?:-[a-z0-9][a-z0-9-]*)?\Z"
)
PLACEHOLDER_RE = re.compile(r"(?:<[^>]+>|\b(?:TBD|TODO|PLACEHOLDER)\b)", re.IGNORECASE)
GITHUB_RELEASE_TIMESTAMP_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z\Z"
)
VERIFICATION_BLOCK_RE = re.compile(rb"<!--\s*verification:(.*?)-->", re.DOTALL)
BLOCK_KEY_VALUE_RE = re.compile(rb"^\s*([a-z_]+)\s*:\s*(\S.*?)\s*$")
TOP_LEVEL_KEY_RE = re.compile(rb"^[A-Za-z_][A-Za-z0-9_-]*\s*:")


class ValidationError(ValueError):
    """A deterministic validation failure suitable for command output."""


class UniqueKeyLoader(yaml.SafeLoader):
    """PyYAML safe loader that rejects mapping keys before construction."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ValidationError(
                f"line {key_node.start_mark.line + 1}: mapping key must be scalar"
            ) from exc
        if duplicate:
            raise ValidationError(
                f"line {key_node.start_mark.line + 1}: duplicate YAML key {key!r}"
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def load_yaml_strict(path: Path) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except OSError as exc:
        raise ValidationError(f"{path}: cannot read file: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValidationError(f"{path}: invalid YAML: {exc}") from exc


def load_yaml_strict_text(text: bytes, where: str) -> Any:
    try:
        return yaml.load(text.decode("utf-8"), Loader=UniqueKeyLoader)
    except UnicodeDecodeError as exc:
        raise ValidationError(f"{where}: expected UTF-8 YAML") from exc
    except yaml.YAMLError as exc:
        raise ValidationError(f"{where}: invalid YAML: {exc}") from exc


def _map(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{where}: expected map")
    if any(not isinstance(key, str) for key in value):
        raise ValidationError(f"{where}: keys must be strings")
    return value


def _exact_keys(
    value: Any, where: str, required: set[str], optional: set[str] | None = None
) -> dict[str, Any]:
    mapping = _map(value, where)
    optional = optional or set()
    missing = sorted(required - mapping.keys())
    unknown = sorted(mapping.keys() - required - optional)
    if missing:
        raise ValidationError(f"{where}: missing keys: {', '.join(missing)}")
    if unknown:
        raise ValidationError(f"{where}: unknown keys: {', '.join(unknown)}")
    return mapping


def _string(value: Any, where: str, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValidationError(f"{where}: expected non-empty string without outer whitespace")
    if PLACEHOLDER_RE.search(value):
        raise ValidationError(f"{where}: placeholder values are forbidden")
    if pattern is not None and pattern.fullmatch(value) is None:
        raise ValidationError(f"{where}: invalid format")
    return value


def _positive_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValidationError(f"{where}: expected positive integer")
    return value


def _literal(value: Any, expected: Any, where: str) -> None:
    if type(value) is not type(expected) or value != expected:
        raise ValidationError(f"{where}: expected {expected!r}")


def _url(value: Any, where: str, expected: str | None = None) -> str:
    text = _string(value, where)
    parsed = urllib.parse.urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.fragment:
        raise ValidationError(f"{where}: expected public HTTPS URL")
    if expected is not None and text != expected:
        raise ValidationError(f"{where}: URL does not match configured immutable evidence")
    return text


def _timestamp(value: Any, where: str) -> str:
    text = _string(value, where)
    if GITHUB_RELEASE_TIMESTAMP_RE.fullmatch(text) is None:
        raise ValidationError(f"{where}: expected RFC 3339 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise ValidationError(f"{where}: expected RFC 3339 UTC timestamp") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{where}: expected timezone")
    return text


def _integrity(value: Any, where: str) -> str:
    text = _string(value, where)
    if not text.startswith("sha512-"):
        raise ValidationError(f"{where}: expected sha512 Subresource Integrity value")
    encoded = text[len("sha512-") :]
    try:
        encoded_bytes = encoded.encode("ascii")
        decoded = base64.b64decode(encoded_bytes, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError) as exc:
        raise ValidationError(f"{where}: invalid canonical Base64") from exc
    if len(decoded) != 64 or base64.b64encode(decoded) != encoded_bytes:
        raise ValidationError(
            f"{where}: expected canonical Base64 encoding of exactly 64 bytes"
        )
    return text


def _repo_coordinates(repo_config: dict[str, Any], where: str) -> tuple[str, str]:
    url = _string(repo_config.get("url"), f"{where}.url")
    parsed = urllib.parse.urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if parsed.netloc != "github.com" or len(parts) != 2:
        raise ValidationError(f"{where}.url: expected GitHub repository URL")
    return parts[0], parts[1].removesuffix(".git")


def _immutable_github_source_url(
    value: Any, where: str, owner: str, repo: str, commit: str
) -> str:
    text = _url(value, where)
    parsed = urllib.parse.urlparse(text)
    parts = parsed.path.strip("/").split("/")
    expected = [owner, repo, "blob", commit]
    if (
        parsed.netloc != "github.com"
        or parsed.params
        or parsed.query
        or len(parts) < 5
        or parts[:4] != expected
        or any(not part for part in parts[4:])
        or any(
            decoded in {".", ".."} or any(char in decoded for char in "/\\")
            for decoded in (urllib.parse.unquote(part) for part in parts[4:])
        )
    ):
        raise ValidationError(
            f"{where}: must identify the immutable source commit"
        )
    return text


def _validate_asset(
    value: Any,
    where: str,
    expected_name: str,
    owner: str,
    repo: str,
    tag: str,
    seen_names: set[str],
    seen_ids: set[int],
) -> None:
    asset = _exact_keys(value, where, {"name", "id", "url", "digest"})
    name = _string(asset["name"], f"{where}.name")
    if name != expected_name:
        raise ValidationError(f"{where}.name: expected {expected_name!r}")
    asset_id = _positive_int(asset["id"], f"{where}.id")
    if name in seen_names:
        raise ValidationError(f"{where}.name: duplicate asset name {name!r}")
    if asset_id in seen_ids:
        raise ValidationError(f"{where}.id: duplicate asset id {asset_id}")
    seen_names.add(name)
    seen_ids.add(asset_id)
    expected_url = f"https://github.com/{owner}/{repo}/releases/download/{tag}/{name}"
    _url(asset["url"], f"{where}.url", expected_url)
    _string(asset["digest"], f"{where}.digest", DIGEST_RE)


def _validate_npm_package(
    value: Any,
    where: str,
    package: str,
    version: str,
    commit: str,
    platform: bool,
) -> None:
    required = {"package", "version", "metadata_url", "integrity", "git_head"}
    if not platform:
        required.add("dist_tag")
    package_data = _exact_keys(value, where, required, {"platforms"} if not platform else set())
    if _string(package_data["package"], f"{where}.package") != package:
        raise ValidationError(f"{where}.package: does not match discovery configuration")
    if _string(package_data["version"], f"{where}.version", SEMVER_RE) != version:
        raise ValidationError(f"{where}.version: does not match baseline version")
    if not platform:
        _literal(package_data["dist_tag"], "latest", f"{where}.dist_tag")
    encoded = urllib.parse.quote(package, safe="@")
    _url(
        package_data["metadata_url"],
        f"{where}.metadata_url",
        f"https://registry.npmjs.org/{encoded}/{version}",
    )
    _integrity(package_data["integrity"], f"{where}.integrity")
    if _string(package_data["git_head"], f"{where}.git_head", COMMIT_RE) != commit:
        raise ValidationError(f"{where}.git_head: does not match source commit")


def _browser_source(
    manifest: Any,
    components: dict[str, Any],
    repos: dict[str, Any],
    where: str = "target-manifest.yml",
) -> tuple[dict[str, Any], list[str]] | None:
    """Validate the fixed manual Browser SDK source profile, when present."""
    top = _map(manifest, where)
    sources = _map(top.get("sources"), f"{where}.sources")
    if "ant-browser-sdk" not in sources:
        return None

    component = _map(
        components.get("ant-browser-sdk"), "components.ant-browser-sdk"
    )
    if component.get("repo") != "ant-browser-sdk":
        raise ValidationError(
            "components.ant-browser-sdk.repo: expected 'ant-browser-sdk'"
        )
    mapped = component.get("feeds_pages")
    if not isinstance(mapped, list) or len(mapped) != 6:
        raise ValidationError(
            "components.ant-browser-sdk.feeds_pages: expected exactly six pages"
        )
    expected_pages = [
        f"docs/{_string(page, 'components.ant-browser-sdk.feeds_pages')}"
        for page in mapped
    ]
    if len(set(expected_pages)) != 6:
        raise ValidationError(
            "components.ant-browser-sdk.feeds_pages: expected six unique pages"
        )

    scope = _exact_keys(top.get("scope"), f"{where}.scope", {"pages"})
    pages = scope["pages"]
    if pages != expected_pages:
        raise ValidationError(
            f"{where}.scope.pages: must name exactly the six mapped Browser SDK pages"
        )

    source_where = f"{where}.sources.ant-browser-sdk"
    source = _exact_keys(
        sources["ant-browser-sdk"],
        source_where,
        {
            "source_ref",
            "source_commit",
            "release_url",
            "support_status",
            "package",
            "shipped_wasm",
        },
    )
    version = _string(
        _map(source["package"], f"{source_where}.package").get("version"),
        f"{source_where}.package.version",
        SEMVER_RE,
    )
    tag = _string(source["source_ref"], f"{source_where}.source_ref")
    if tag != f"v{version}":
        raise ValidationError(
            f"{source_where}.source_ref: must be v followed by the package version"
        )
    commit = _string(
        source["source_commit"], f"{source_where}.source_commit", COMMIT_RE
    )

    repo_config = _map(repos.get("ant-browser-sdk"), "repos.ant-browser-sdk")
    owner, repo = _repo_coordinates(repo_config, "repos.ant-browser-sdk")
    _url(
        source["release_url"],
        f"{source_where}.release_url",
        f"https://github.com/{owner}/{repo}/releases/tag/{tag}",
    )
    _literal(
        source["support_status"], "experimental", f"{source_where}.support_status"
    )

    package_where = f"{source_where}.package"
    package = _exact_keys(
        source["package"],
        package_where,
        {"name", "version", "metadata_url", "integrity"},
    )
    _literal(
        package["name"],
        "@withautonomi/ant-browser-sdk",
        f"{package_where}.name",
    )
    if package["version"] != version:
        raise ValidationError(f"{package_where}.version: does not match release tag")
    _url(
        package["metadata_url"],
        f"{package_where}.metadata_url",
        f"https://registry.npmjs.org/@withautonomi/ant-browser-sdk/{version}",
    )
    _integrity(package["integrity"], f"{package_where}.integrity")

    wasm_where = f"{source_where}.shipped_wasm"
    wasm = _exact_keys(
        source["shipped_wasm"],
        wasm_where,
        {"source_repo", "source_commit", "sha256", "evidence_url"},
    )
    _literal(wasm["source_repo"], "ant-client", f"{wasm_where}.source_repo")
    _string(wasm["source_commit"], f"{wasm_where}.source_commit", COMMIT_RE)
    _string(wasm["sha256"], f"{wasm_where}.sha256", DIGEST_HEX_RE)
    _url(
        wasm["evidence_url"],
        f"{wasm_where}.evidence_url",
        f"https://github.com/{owner}/{repo}/blob/{commit}/src/wasm/source.json",
    )
    return source, expected_pages


def validate_manifest_data(
    manifest: Any,
    components_data: Any,
    repos_data: Any,
    repo_root: Path,
) -> None:
    top = _exact_keys(manifest, "target-manifest.yml", {"scope", "sources"}, {"release_baselines"})
    components = _map(_map(components_data, "component-registry.yml").get("components"), "components")
    repos = _map(_map(repos_data, "repo-registry.yml").get("repos"), "repos")
    _browser_source(top, components, repos)
    if "release_baselines" not in top:
        return

    release = _exact_keys(top["release_baselines"], "release_baselines", {"schema_version", "entries"})
    _literal(release["schema_version"], 1, "release_baselines.schema_version")
    entries = _map(release["entries"], "release_baselines.entries")
    identities: set[tuple[str, str]] = set()

    for entry_key in sorted(entries):
        where = f"release_baselines.entries.{entry_key}"
        entry = _exact_keys(
            entries[entry_key],
            where,
            {
                "component", "context", "version", "source", "github_release",
                "npm", "installers", "scoped_pages", "promotion",
            },
            {"shipped_dependencies"},
        )
        component_name = _string(entry["component"], f"{where}.component")
        context = _string(entry["context"], f"{where}.context")
        if context != "stable":
            raise ValidationError(f"{where}.context: version 1 permits only 'stable'")
        identity = (component_name, context)
        if identity in identities:
            raise ValidationError(f"{where}: duplicate component/context identity")
        identities.add(identity)
        if entry_key != f"{component_name}/{context}":
            raise ValidationError(f"{where}: key does not match component/context")
        if component_name not in components:
            raise ValidationError(f"{where}.component: unknown component")
        component = _map(components[component_name], f"components.{component_name}")
        discovery_all = _map(component.get("release_discovery"), f"components.{component_name}.release_discovery")
        if context not in discovery_all:
            raise ValidationError(f"{where}.context: no matching discovery configuration")
        discovery = _map(discovery_all[context], f"components.{component_name}.release_discovery.{context}")
        github_config = _map(discovery.get("github"), f"{where}.discovery.github")
        npm_config = _map(discovery.get("npm"), f"{where}.discovery.npm")
        installer_config = discovery.get("installers")
        if not isinstance(installer_config, list):
            raise ValidationError(f"{where}.discovery.installers: expected list")

        version = _string(entry["version"], f"{where}.version", SEMVER_RE)
        source = _exact_keys(entry["source"], f"{where}.source", {"repo", "tag", "commit"})
        source_repo = _string(source["repo"], f"{where}.source.repo")
        if source_repo != component.get("repo") or source_repo not in repos:
            raise ValidationError(f"{where}.source.repo: component/repository mismatch")
        repo_config = _map(repos[source_repo], f"repos.{source_repo}")
        if repo_config.get("class") == "excluded":
            raise ValidationError(f"{where}.source.repo: excluded repository")
        owner, repo = _repo_coordinates(repo_config, f"repos.{source_repo}")
        tag = _string(source["tag"], f"{where}.source.tag")
        tag_pattern_value = github_config.get("tag_pattern")
        if not isinstance(tag_pattern_value, str) or not tag_pattern_value:
            raise ValidationError(f"{where}.discovery.github.tag_pattern: expected non-empty string")
        tag_pattern = tag_pattern_value
        match = re.fullmatch(tag_pattern, tag)
        if match is None or match.groupdict().get("version") != version:
            raise ValidationError(f"{where}.source.tag: does not match configured version pattern")
        commit = _string(source["commit"], f"{where}.source.commit", COMMIT_RE)

        gh_where = f"{where}.github_release"
        gh = _exact_keys(
            entry["github_release"], gh_where,
            {"id", "api_url", "release_url", "published_at", "draft", "prerelease", "checksum_asset", "platforms"},
        )
        release_id = _positive_int(gh["id"], f"{gh_where}.id")
        _url(gh["api_url"], f"{gh_where}.api_url", f"https://api.github.com/repos/{owner}/{repo}/releases/{release_id}")
        _url(gh["release_url"], f"{gh_where}.release_url", f"https://github.com/{owner}/{repo}/releases/tag/{tag}")
        _timestamp(gh["published_at"], f"{gh_where}.published_at")
        _literal(gh["draft"], False, f"{gh_where}.draft")
        _literal(gh["prerelease"], False, f"{gh_where}.prerelease")
        configured_targets = _map(github_config.get("platforms"), f"{where}.discovery.github.platforms")
        gh_platforms = _map(gh["platforms"], f"{gh_where}.platforms")
        if set(gh_platforms) != set(configured_targets):
            raise ValidationError(f"{gh_where}.platforms: target set mismatch")
        seen_names: set[str] = set()
        seen_ids: set[int] = set()
        checksum_name = _string(github_config.get("checksum_asset"), f"{where}.discovery.github.checksum_asset")
        _validate_asset(gh["checksum_asset"], f"{gh_where}.checksum_asset", checksum_name, owner, repo, tag, seen_names, seen_ids)
        for target in sorted(configured_targets):
            platform_where = f"{gh_where}.platforms.{target}"
            platform = _exact_keys(gh_platforms[target], platform_where, {"archive", "signature"})
            extension = _string(configured_targets[target], f"{where}.discovery.github.platforms.{target}")
            archive_name = f"ant-{version}-{target}.{extension}"
            _validate_asset(platform["archive"], f"{platform_where}.archive", archive_name, owner, repo, tag, seen_names, seen_ids)
            _validate_asset(platform["signature"], f"{platform_where}.signature", f"{archive_name}.sig", owner, repo, tag, seen_names, seen_ids)

        npm_where = f"{where}.npm"
        npm = _exact_keys(entry["npm"], npm_where, {"package", "dist_tag", "version", "metadata_url", "integrity", "git_head", "platforms"})
        meta_package = _string(npm_config.get("package"), f"{where}.discovery.npm.package")
        _validate_npm_package(npm, npm_where, meta_package, version, commit, False)
        _literal(npm_config.get("dist_tag"), "latest", f"{where}.discovery.npm.dist_tag")
        npm_targets = _map(npm_config.get("platform_packages"), f"{where}.discovery.npm.platform_packages")
        npm_platforms = _map(npm["platforms"], f"{npm_where}.platforms")
        if set(npm_targets) != set(configured_targets) or set(npm_platforms) != set(configured_targets):
            raise ValidationError(f"{npm_where}.platforms: GitHub/npm target pairing mismatch")
        for target in sorted(configured_targets):
            _validate_npm_package(
                npm_platforms[target], f"{npm_where}.platforms.{target}",
                _string(npm_targets[target], f"{where}.discovery.npm.platform_packages.{target}"),
                version, commit, True,
            )

        installers = entry["installers"]
        if not isinstance(installers, list) or len(installers) != 2 or len(installer_config) != 2:
            raise ValidationError(f"{where}.installers: expected exactly two configured installers")
        seen_installer_platforms: set[str] = set()
        for index, (actual_value, configured_value) in enumerate(zip(installers, installer_config)):
            installer_where = f"{where}.installers[{index}]"
            actual = _exact_keys(actual_value, installer_where, {"platform", "url", "source_commit", "blob_sha", "evidence_url", "selected_version"})
            configured = _exact_keys(configured_value, f"{where}.discovery.installers[{index}]", {"platform", "ref", "path", "url"})
            platform = _string(actual["platform"], f"{installer_where}.platform")
            if platform not in {"linux-macos", "windows"} or platform != configured["platform"] or platform in seen_installer_platforms:
                raise ValidationError(f"{installer_where}.platform: invalid, duplicate, or out of order")
            seen_installer_platforms.add(platform)
            configured_url = _string(configured["url"], f"{where}.discovery.installers[{index}].url")
            _url(actual["url"], f"{installer_where}.url", configured_url)
            source_commit = _string(actual["source_commit"], f"{installer_where}.source_commit", COMMIT_RE)
            _string(actual["blob_sha"], f"{installer_where}.blob_sha", COMMIT_RE)
            path = _string(configured["path"], f"{where}.discovery.installers[{index}].path")
            _url(actual["evidence_url"], f"{installer_where}.evidence_url", f"https://github.com/{owner}/{repo}/blob/{source_commit}/{path}")
            if _string(actual["selected_version"], f"{installer_where}.selected_version", SEMVER_RE) != version:
                raise ValidationError(f"{installer_where}.selected_version: does not match baseline version")

        if entry_key == "ant-cli/stable":
            if "shipped_dependencies" not in entry:
                raise ValidationError(
                    f"{where}: missing keys: shipped_dependencies"
                )
            dependencies = _map(
                entry["shipped_dependencies"], f"{where}.shipped_dependencies"
            )
            if "ant-core" not in dependencies:
                raise ValidationError(
                    f"{where}.shipped_dependencies: missing keys: ant-core"
                )
        elif "shipped_dependencies" in entry:
            dependencies = _map(
                entry["shipped_dependencies"], f"{where}.shipped_dependencies"
            )
        else:
            dependencies = None
        if dependencies is not None:
            if not dependencies:
                raise ValidationError(f"{where}.shipped_dependencies: empty map must be omitted")
            for dependency_name in sorted(dependencies):
                dep_where = f"{where}.shipped_dependencies.{dependency_name}"
                dep = _exact_keys(dependencies[dependency_name], dep_where, {"version", "source_repo", "source_commit", "evidence_url"})
                if dependency_name not in components:
                    raise ValidationError(f"{dep_where}: unknown component dependency")
                dependency_component = _map(components[dependency_name], f"components.{dependency_name}")
                dependency_repo = _string(dep["source_repo"], f"{dep_where}.source_repo")
                if dependency_repo != dependency_component.get("repo") or dependency_repo not in repos:
                    raise ValidationError(f"{dep_where}.source_repo: component/repository mismatch")
                _string(dep["version"], f"{dep_where}.version", SEMVER_RE)
                dependency_commit = _string(dep["source_commit"], f"{dep_where}.source_commit", COMMIT_RE)
                dep_owner, dep_repo = _repo_coordinates(_map(repos[dependency_repo], f"repos.{dependency_repo}"), f"repos.{dependency_repo}")
                _immutable_github_source_url(
                    dep["evidence_url"],
                    f"{dep_where}.evidence_url",
                    dep_owner,
                    dep_repo,
                    dependency_commit,
                )

        scoped_pages = entry["scoped_pages"]
        if not isinstance(scoped_pages, list) or not scoped_pages:
            raise ValidationError(f"{where}.scoped_pages: expected non-empty list")
        if scoped_pages != sorted(scoped_pages) or len(scoped_pages) != len(set(scoped_pages)):
            raise ValidationError(f"{where}.scoped_pages: must be unique and lexicographically sorted")
        allowed_pages = {f"docs/{page}" for page in component.get("feeds_pages", [])}
        for index, page_value in enumerate(scoped_pages):
            page = _string(page_value, f"{where}.scoped_pages[{index}]")
            if page not in allowed_pages:
                raise ValidationError(f"{where}.scoped_pages[{index}]: page is not mapped to component")
            path = (repo_root / page).resolve()
            try:
                path.relative_to(repo_root.resolve())
            except ValueError as exc:
                raise ValidationError(f"{where}.scoped_pages[{index}]: path escapes repository") from exc
            if not path.is_file():
                raise ValidationError(f"{where}.scoped_pages[{index}]: file does not exist")
        if component_name == "ant-cli" and not set(scoped_pages).issubset({"docs/cli/command-reference.md", "docs/cli/use-the-cli.md"}):
            raise ValidationError(f"{where}.scoped_pages: first CLI promotion permits only the two CLI pages")

        promotion = _exact_keys(entry["promotion"], f"{where}.promotion", {"record"})
        record = _string(promotion["record"], f"{where}.promotion.record", PROMOTION_RE)
        record_path = (repo_root / record).resolve()
        try:
            record_path.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValidationError(f"{where}.promotion.record: path escapes repository") from exc
        if not record_path.is_file():
            raise ValidationError(f"{where}.promotion.record: file does not exist")


def _verification_fields(body: bytes, where: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in body.splitlines():
        match = BLOCK_KEY_VALUE_RE.fullmatch(line.strip())
        if match is None:
            continue
        key = match.group(1).decode("ascii")
        try:
            value = match.group(2).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(f"{where}: verification block is not UTF-8") from exc
        if key in fields:
            raise ValidationError(f"{where}: duplicate verification field {key!r}")
        fields[key] = value
    return fields


def _verification_blocks(text: bytes, where: str) -> list[tuple[bytes, dict[str, str]]]:
    blocks: list[tuple[bytes, dict[str, str]]] = []
    for match in VERIFICATION_BLOCK_RE.finditer(text):
        line = text.count(b"\n", 0, match.start()) + 1
        blocks.append(
            (match.group(0), _verification_fields(match.group(1), f"{where}:{line}"))
        )
    return blocks


def validate_manifest_page_blocks(manifest: Any, repo_root: Path) -> None:
    """Require every release entry to have one exact block on each scoped page."""
    top = _map(manifest, "target-manifest.yml")
    sources = _map(top.get("sources"), "sources")
    browser = sources.get("ant-browser-sdk")
    if browser is not None:
        browser_map = _map(browser, "sources.ant-browser-sdk")
        scope = _map(top.get("scope"), "scope")
        for page in scope.get("pages", []):
            page_path = repo_root / page
            try:
                text = page_path.read_bytes()
            except OSError as exc:
                raise ValidationError(
                    f"{page}: cannot read scoped page: {exc}"
                ) from exc
            matches = [
                fields
                for _raw, fields in _verification_blocks(text, page)
                if fields.get("source_repo") == "ant-browser-sdk"
            ]
            if len(matches) != 1:
                raise ValidationError(
                    f"{page}: expected exactly one 'ant-browser-sdk' verification block"
                )
            fields = matches[0]
            required_fields = {
                "source_repo",
                "source_ref",
                "source_commit",
                "verified_date",
                "verification_mode",
            }
            missing = sorted(required_fields - fields.keys())
            unknown = sorted(fields.keys() - required_fields)
            if missing:
                raise ValidationError(
                    f"{page}: target-manifest verification block missing fields: "
                    + ", ".join(missing)
                )
            if unknown:
                raise ValidationError(
                    f"{page}: target-manifest verification block has unknown fields: "
                    + ", ".join(unknown)
                )
            expected = {
                "source_repo": "ant-browser-sdk",
                "source_ref": browser_map.get("source_ref"),
                "source_commit": browser_map.get("source_commit"),
                "verification_mode": "target-manifest",
            }
            for key, value in expected.items():
                if fields.get(key) != value:
                    raise ValidationError(
                        f"{page}: {key} does not match manual Browser SDK source"
                    )

    release = top.get("release_baselines")
    if release is None:
        return
    release_map = _map(release, "release_baselines")
    entries = _map(release_map.get("entries"), "release_baselines.entries")
    for entry_key in sorted(entries):
        where = f"release_baselines.entries.{entry_key}"
        entry = _map(entries[entry_key], where)
        source = _map(entry.get("source"), f"{where}.source")
        repo = source.get("repo")
        tag = source.get("tag")
        commit = source.get("commit")
        for page in entry.get("scoped_pages", []):
            page_path = repo_root / page
            try:
                text = page_path.read_bytes()
            except OSError as exc:
                raise ValidationError(f"{page}: cannot read scoped page: {exc}") from exc
            matches = [
                fields
                for _raw, fields in _verification_blocks(text, page)
                if fields.get("source_repo") == repo
            ]
            if len(matches) != 1:
                raise ValidationError(
                    f"{page}: expected exactly one {repo!r} verification block for {entry_key}"
                )
            fields = matches[0]
            required_fields = {
                "source_repo",
                "source_ref",
                "source_commit",
                "verified_date",
                "verification_mode",
            }
            missing = sorted(required_fields - fields.keys())
            unknown = sorted(fields.keys() - required_fields)
            if missing:
                raise ValidationError(
                    f"{page}: target-manifest verification block missing fields: "
                    + ", ".join(missing)
                )
            if unknown:
                raise ValidationError(
                    f"{page}: target-manifest verification block has unknown fields: "
                    + ", ".join(unknown)
                )
            expected = {
                "source_repo": repo,
                "source_ref": tag,
                "source_commit": commit,
                "verification_mode": "target-manifest",
            }
            for key, value in expected.items():
                if fields.get(key) != value:
                    raise ValidationError(
                        f"{page}: {key} does not match release baseline {entry_key}"
                    )


def _git_bytes(ref: str, path: str) -> bytes | None:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _git_changes(base_ref: str, head_ref: str) -> dict[str, str]:
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--name-status", "-z", f"{base_ref}..{head_ref}"]
        )
    except subprocess.CalledProcessError as exc:
        raise ValidationError("cannot inspect promotion diff") from exc
    tokens = [token.decode("utf-8") for token in raw.split(b"\0") if token]
    changes: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        status = tokens[index]
        if status.startswith(("R", "C")):
            if index + 2 >= len(tokens):
                raise ValidationError("unexpected truncated git name-status output")
            changes[tokens[index + 1]] = status[0]
            changes[tokens[index + 2]] = status[0]
            index += 3
        else:
            if index + 1 >= len(tokens):
                raise ValidationError("unexpected truncated git name-status output")
            changes[tokens[index + 1]] = status
            index += 2
    return changes


def _top_level_section(text: bytes, key: str) -> bytes:
    lines = text.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"{key}:".encode("ascii")):
            start = index
            break
    if start is None:
        raise ValidationError(f"target-manifest.yml: missing top-level {key!r}")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if TOP_LEVEL_KEY_RE.match(lines[index]):
            end = index
            break
    while end > start + 1 and not lines[end - 1].strip():
        end -= 1
    return b"".join(lines[start:end])


def _optional_top_level_section(text: bytes, key: str) -> bytes | None:
    try:
        return _top_level_section(text, key)
    except ValidationError:
        return None


def _without_mapping_child(text: bytes, parent: str, child: str) -> bytes:
    """Replace one two-space-indented YAML child while preserving all other bytes."""
    lines = text.splitlines(keepends=True)
    parent_start = None
    for index, line in enumerate(lines):
        if line.startswith(f"{parent}:".encode("ascii")):
            parent_start = index
            break
    if parent_start is None:
        raise ValidationError(f"target-manifest.yml: missing top-level {parent!r}")
    child_start = None
    for index in range(parent_start + 1, len(lines)):
        line = lines[index]
        if TOP_LEVEL_KEY_RE.match(line):
            break
        if line.startswith(f"  {child}:".encode("utf-8")):
            child_start = index
            break
    if child_start is None:
        raise ValidationError(f"target-manifest.yml.{parent}: missing {child!r}")
    child_end = len(lines)
    for index in range(child_start + 1, len(lines)):
        line = lines[index]
        if line.strip() and (
            TOP_LEVEL_KEY_RE.match(line)
            or (line.startswith(b"  ") and not line.startswith(b"    "))
            or not line.startswith((b" ", b"\t"))
        ):
            child_end = index
            break
    while child_end > child_start + 1 and not lines[child_end - 1].strip():
        child_end -= 1
    return (
        b"".join(lines[:child_start])
        + b"  __MANUAL_BROWSER_SOURCE__: true\n"
        + b"".join(lines[child_end:])
    )


def _semver_tuple(value: str) -> tuple[int, int, int]:
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def _rendered_body(text: bytes | None) -> bytes:
    return VERIFICATION_BLOCK_RE.sub(b"", text or b"")


def _release_entries(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        return {}
    release = manifest.get("release_baselines")
    if release is None:
        return {}
    if not isinstance(release, dict) or not isinstance(release.get("entries"), dict):
        raise ValidationError("release_baselines: expected entries map")
    return release["entries"]


def _target_blocks(text: bytes | None, where: str) -> list[tuple[bytes, dict[str, str]]]:
    if text is None:
        return []
    return [
        (raw, fields)
        for raw, fields in _verification_blocks(text, where)
        if fields.get("verification_mode") == "target-manifest"
    ]


def _validate_browser_git_promotion(
    *,
    base_ref: str,
    head_ref: str,
    base_manifest_text: bytes,
    head_manifest_text: bytes,
    base_manifest: Any,
    head_manifest: Any,
    changes: dict[str, str],
    changed_target_paths: set[str],
    branch: str,
    repo_root: Path,
) -> dict[str, Any]:
    branch_match = PROMOTION_BRANCH_RE.fullmatch(branch)
    if branch_match is None:
        raise ValidationError(
            "manual Browser SDK promotion requires claude/sweep-YYYY-MM-DD-* "
            "or claude/prose-YYYY-MM-DD-*"
        )
    family, branch_date = branch_match.groups()
    try:
        datetime.strptime(branch_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValidationError(
            "manual Browser SDK promotion branch has an invalid date"
        ) from exc

    components_data = load_yaml_strict(repo_root / "component-registry.yml")
    repos_data = load_yaml_strict(repo_root / "repo-registry.yml")
    components = _map(
        _map(components_data, "component-registry.yml").get("components"),
        "components",
    )
    repos = _map(_map(repos_data, "repo-registry.yml").get("repos"), "repos")
    base_profile = _browser_source(
        base_manifest, components, repos, "base target-manifest.yml"
    )
    head_profile = _browser_source(
        head_manifest, components, repos, "head target-manifest.yml"
    )
    if base_profile is None or head_profile is None:
        raise ValidationError(
            "manual Browser SDK promotion requires the existing ant-browser-sdk source"
        )
    base_source, base_pages = base_profile
    head_source, expected_pages_list = head_profile
    if base_pages != expected_pages_list:
        raise ValidationError("manual Browser SDK promotion cannot change scoped pages")
    expected_pages = set(expected_pages_list)

    if _top_level_section(base_manifest_text, "scope") != _top_level_section(
        head_manifest_text, "scope"
    ):
        raise ValidationError(
            "target-manifest.yml scope must remain byte-identical during a "
            "manual Browser SDK promotion"
        )
    if _optional_top_level_section(
        base_manifest_text, "release_baselines"
    ) != _optional_top_level_section(head_manifest_text, "release_baselines"):
        raise ValidationError(
            "release_baselines must remain byte-identical during a manual Browser SDK promotion"
        )
    if _without_mapping_child(
        base_manifest_text, "sources", "ant-browser-sdk"
    ) != _without_mapping_child(head_manifest_text, "sources", "ant-browser-sdk"):
        raise ValidationError(
            "only sources.ant-browser-sdk may change during a manual Browser SDK promotion"
        )

    base_version = _string(
        _map(base_source["package"], "base sources.ant-browser-sdk.package")["version"],
        "base sources.ant-browser-sdk.package.version",
        SEMVER_RE,
    )
    head_version = _string(
        _map(head_source["package"], "head sources.ant-browser-sdk.package")["version"],
        "head sources.ant-browser-sdk.package.version",
        SEMVER_RE,
    )
    if _semver_tuple(head_version) <= _semver_tuple(base_version):
        raise ValidationError(
            "manual Browser SDK promotion version must be greater than the reviewed source"
        )

    if changed_target_paths != expected_pages:
        raise ValidationError(
            "changed Browser SDK target-manifest block paths must exactly equal the six scoped pages"
        )
    expected_record = f"planning/sweeps/{branch_date}.md"
    changed_records = {
        path for path in changes if path.startswith("planning/sweeps/")
    }
    if changed_records != {expected_record}:
        raise ValidationError(
            "manual Browser SDK promotion must add exactly one dated promotion record matching the branch"
        )
    if changes.get(expected_record) != "A":
        raise ValidationError(f"{expected_record}: promotion record must be newly added")

    rendered_changed = False
    for path in changes:
        if not (path.startswith("docs/") and path.endswith(".md")):
            continue
        base_text = _git_bytes(base_ref, path)
        head_text = _git_bytes(head_ref, path)
        if _rendered_body(base_text) != _rendered_body(head_text):
            rendered_changed = True
        base_blocks = _verification_blocks(base_text or b"", path)
        head_blocks = _verification_blocks(head_text or b"", path)
        if path not in expected_pages and sorted(
            raw for raw, _ in base_blocks
        ) != sorted(raw for raw, _ in head_blocks):
            raise ValidationError(f"{path}: unrelated verification block changed")

    if rendered_changed and family != "prose":
        raise ValidationError(
            "rendered documentation changes require a claude/prose-YYYY-MM-DD-* branch"
        )
    if not rendered_changed and family != "sweep":
        raise ValidationError(
            "metadata-only Browser SDK promotions require a claude/sweep-YYYY-MM-DD-* branch"
        )

    for page in sorted(expected_pages):
        base_all = _verification_blocks(
            _git_bytes(base_ref, page) or b"", page
        )
        head_all = _verification_blocks(
            _git_bytes(head_ref, page) or b"", page
        )
        base_own = [
            (raw, fields)
            for raw, fields in base_all
            if fields.get("source_repo") == "ant-browser-sdk"
        ]
        head_own = [
            (raw, fields)
            for raw, fields in head_all
            if fields.get("source_repo") == "ant-browser-sdk"
        ]
        if (
            len(base_own) != 1
            or len(head_own) != 1
            or base_own[0][0] == head_own[0][0]
        ):
            raise ValidationError(
                f"{page}: Browser SDK source block must advance exactly once"
            )
        expected_fields = {
            "source_repo": "ant-browser-sdk",
            "source_ref": head_source["source_ref"],
            "source_commit": head_source["source_commit"],
            "verified_date": branch_date,
            "verification_mode": "target-manifest",
        }
        if head_own[0][1] != expected_fields:
            raise ValidationError(
                f"{page}: Browser SDK block must match the promoted tag, commit, date, and exact schema"
            )
        if base_own[0][1].get("verified_date") == branch_date:
            raise ValidationError(f"{page}: Browser SDK verified_date did not advance")
        # Freeze non-Browser blocks until their separate migration debt is resolved.
        base_other = sorted(
            raw for raw, fields in base_all if fields.get("source_repo") != "ant-browser-sdk"
        )
        head_other = sorted(
            raw for raw, fields in head_all if fields.get("source_repo") != "ant-browser-sdk"
        )
        if base_other != head_other:
            raise ValidationError(f"{page}: unrelated verification block changed")

    validate_manifest_data(head_manifest, components_data, repos_data, repo_root)
    validate_manifest_page_blocks(head_manifest, repo_root)
    return {
        "promoted": True,
        "route": "manual-browser-source",
        "entries": ["sources.ant-browser-sdk"],
        "pages": sorted(expected_pages),
        "records": [expected_record],
    }


def validate_git_promotion(
    base_ref: str,
    head_ref: str,
    branch: str,
    repo_root: Path = REPO_ROOT,
) -> dict[str, Any]:
    """Validate one atomic release promotion from two Git revisions.

    Ordinary updater changes return ``promoted: False``. Protected changes on
    any other branch fail with routing guidance rather than becoming a green
    scope skip.
    """
    changes = _git_changes(base_ref, head_ref)
    base_manifest_text = _git_bytes(base_ref, "target-manifest.yml")
    head_manifest_text = _git_bytes(head_ref, "target-manifest.yml")
    if base_manifest_text is None or head_manifest_text is None:
        raise ValidationError("target-manifest.yml must exist on both sides of a promotion")
    base_manifest = load_yaml_strict_text(base_manifest_text, "base target-manifest.yml")
    head_manifest = load_yaml_strict_text(head_manifest_text, "head target-manifest.yml")
    base_entries = _release_entries(base_manifest)
    head_entries = _release_entries(head_manifest)
    base_sources = _map(
        _map(base_manifest, "base target-manifest.yml").get("sources"),
        "base sources",
    )
    head_sources = _map(
        _map(head_manifest, "head target-manifest.yml").get("sources"),
        "head sources",
    )
    browser_source_changed = base_sources.get("ant-browser-sdk") != head_sources.get(
        "ant-browser-sdk"
    )
    record_paths = {
        entry.get("promotion", {}).get("record")
        for entry in [*base_entries.values(), *head_entries.values()]
        if isinstance(entry, dict) and isinstance(entry.get("promotion"), dict)
    }
    record_paths.discard(None)

    changed_target_paths: set[str] = set()
    for path in changes:
        if not (path.startswith("docs/") and path.endswith(".md")):
            continue
        base_blocks = sorted(raw for raw, _fields in _target_blocks(_git_bytes(base_ref, path), path))
        head_blocks = sorted(raw for raw, _fields in _target_blocks(_git_bytes(head_ref, path), path))
        if base_blocks != head_blocks:
            changed_target_paths.add(path)
    changed_records = {
        path
        for path in changes
        if path in record_paths or path.startswith("planning/sweeps/")
    }
    manifest_changed = base_manifest_text != head_manifest_text
    protected = manifest_changed or bool(changed_target_paths) or bool(changed_records)
    if not protected:
        return {"promoted": False, "entries": [], "pages": [], "records": []}

    if not (branch.startswith("claude/sweep-") or branch.startswith("claude/prose-")):
        raise ValidationError(
            "release-sensitive change is not permitted on this branch; use "
            "claude/sweep-* for a metadata-only promotion or claude/prose-* "
            "when rendered documentation changes"
        )
    if not manifest_changed:
        raise ValidationError(
            "target-manifest blocks and promotion records must change atomically with target-manifest.yml"
        )

    if browser_source_changed:
        return _validate_browser_git_promotion(
            base_ref=base_ref,
            head_ref=head_ref,
            base_manifest_text=base_manifest_text,
            head_manifest_text=head_manifest_text,
            base_manifest=base_manifest,
            head_manifest=head_manifest,
            changes=changes,
            changed_target_paths=changed_target_paths,
            branch=branch,
            repo_root=repo_root,
        )

    if _top_level_section(base_manifest_text, "scope") != _top_level_section(
        head_manifest_text, "scope"
    ):
        raise ValidationError("target-manifest.yml scope subtree changed; browser pins must remain byte-identical")
    if _top_level_section(base_manifest_text, "sources") != _top_level_section(
        head_manifest_text, "sources"
    ):
        raise ValidationError("target-manifest.yml sources subtree changed; browser pins must remain byte-identical")

    validate_manifest_data(
        head_manifest,
        load_yaml_strict(repo_root / "component-registry.yml"),
        load_yaml_strict(repo_root / "repo-registry.yml"),
        repo_root,
    )
    validate_manifest_page_blocks(head_manifest, repo_root)

    removed = sorted(set(base_entries) - set(head_entries))
    if removed:
        raise ValidationError(f"release baseline entries cannot be removed: {', '.join(removed)}")
    changed_entries = sorted(
        key for key in head_entries if base_entries.get(key) != head_entries[key]
    )
    if not changed_entries:
        raise ValidationError("target-manifest.yml changed without adding or advancing a release baseline")

    expected_pages: set[str] = set()
    expected_records: set[str] = set()
    for key in changed_entries:
        entry = head_entries[key]
        previous = base_entries.get(key)
        if key == "ant-cli/stable" and previous is None and set(
            entry.get("scoped_pages", [])
        ) != {"docs/cli/command-reference.md", "docs/cli/use-the-cli.md"}:
            raise ValidationError(
                "ant-cli/stable: the first promotion must atomically scope both CLI pages"
            )
        if previous is not None:
            if entry.get("scoped_pages") != previous.get("scoped_pages"):
                raise ValidationError(f"{key}: scoped_pages cannot change while advancing a baseline")
            before = tuple(int(part) for part in previous["version"].split("."))
            after = tuple(int(part) for part in entry["version"].split("."))
            if after <= before:
                raise ValidationError(f"{key}: promotion version must be greater than the reviewed baseline")
        expected_pages.update(entry["scoped_pages"])
        expected_records.add(entry["promotion"]["record"])

    if changed_target_paths != expected_pages:
        raise ValidationError(
            "changed target-manifest block paths must exactly equal the changed entries' scoped_pages"
        )
    if changed_records != expected_records:
        raise ValidationError(
            "changed promotion records must exactly equal the changed entries' promotion.record values"
        )
    for record in sorted(expected_records):
        if changes.get(record) != "A":
            raise ValidationError(f"{record}: promotion record must be newly added")

    for page in sorted(expected_pages):
        base_all = _verification_blocks(_git_bytes(base_ref, page) or b"", page)
        head_all = _verification_blocks(_git_bytes(head_ref, page) or b"", page)
        matching_entries = [
            head_entries[key]
            for key in changed_entries
            if page in head_entries[key]["scoped_pages"]
        ]
        if len(matching_entries) != 1:
            raise ValidationError(f"{page}: expected one changed release entry")
        source_repo = matching_entries[0]["source"]["repo"]
        base_own = [raw for raw, fields in base_all if fields.get("source_repo") == source_repo]
        head_own = [raw for raw, fields in head_all if fields.get("source_repo") == source_repo]
        if len(base_own) != 1 or len(head_own) != 1 or base_own == head_own:
            raise ValidationError(f"{page}: promoted source block must change exactly once")
        base_other_target = sorted(
            raw
            for raw, fields in base_all
            if fields.get("verification_mode") == "target-manifest"
            and fields.get("source_repo") != source_repo
        )
        head_other_target = sorted(
            raw
            for raw, fields in head_all
            if fields.get("verification_mode") == "target-manifest"
            and fields.get("source_repo") != source_repo
        )
        if base_other_target != head_other_target:
            raise ValidationError(f"{page}: unrelated target-manifest block changed")

    return {
        "promoted": True,
        "entries": changed_entries,
        "pages": sorted(expected_pages),
        "records": sorted(expected_records),
    }


SignatureVerifier = Callable[[Path, Path, Path, dict[str, str]], dict[str, Any]]


def validate_authenticity_fixture(
    github_release: dict[str, Any],
    download_dir: Path,
    canonical: Any,
    verify_signature: SignatureVerifier,
) -> list[dict[str, Any]]:
    """Validate already-downloaded local release assets without network access."""
    canonical_map = _exact_keys(
        canonical,
        "canonical_signature_evidence",
        {"key_file", "key_source", "key_fingerprint", "tool", "tool_version", "context"},
    )
    normalized = {
        key: _string(canonical_map[key], f"canonical_signature_evidence.{key}")
        for key in canonical_map
    }
    _url(normalized["key_source"], "canonical_signature_evidence.key_source")
    key_file = download_dir / normalized["key_file"]
    if key_file.parent.resolve() != download_dir.resolve() or not key_file.is_file():
        raise ValidationError("canonical_signature_evidence.key_file: missing local canonical key")

    checksum = _map(github_release.get("checksum_asset"), "github_release.checksum_asset")
    platforms = _map(github_release.get("platforms"), "github_release.platforms")
    assets = [checksum]
    archive_names: set[str] = set()
    pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for target in sorted(platforms):
        platform = _exact_keys(platforms[target], f"github_release.platforms.{target}", {"archive", "signature"})
        archive = _map(platform["archive"], f"github_release.platforms.{target}.archive")
        signature = _map(platform["signature"], f"github_release.platforms.{target}.signature")
        assets.extend((archive, signature))
        archive_names.add(_string(archive.get("name"), f"github_release.platforms.{target}.archive.name"))
        pairs.append((archive, signature))

    computed: dict[str, str] = {}
    for asset_data in assets:
        name = _string(asset_data.get("name"), "release asset name")
        if Path(name).name != name:
            raise ValidationError(f"release asset {name!r}: name must not contain a path")
        path = download_dir / name
        if not path.is_file():
            raise ValidationError(f"release asset {name!r}: downloaded file is missing")
        digest = f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        if digest != asset_data.get("digest"):
            raise ValidationError(f"release asset {name!r}: provider digest mismatch")
        computed[name] = digest.removeprefix("sha256:")

    checksum_name = _string(checksum.get("name"), "github_release.checksum_asset.name")
    checksum_text = (download_dir / checksum_name).read_text(encoding="utf-8")
    checksum_entries: dict[str, str] = {}
    for line_number, raw_line in enumerate(checksum_text.splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64}) [ *]([^/\\]+)", raw_line)
        if match is None:
            raise ValidationError(f"{checksum_name}:{line_number}: malformed checksum entry")
        digest, name = match.groups()
        if name in checksum_entries:
            raise ValidationError(f"{checksum_name}:{line_number}: duplicate checksum entry {name!r}")
        checksum_entries[name] = digest
    if set(checksum_entries) != archive_names:
        raise ValidationError(f"{checksum_name}: entries must exactly match required archives")
    for name in sorted(archive_names):
        if checksum_entries[name] != computed[name]:
            raise ValidationError(f"{checksum_name}: checksum mismatch for {name}")

    results: list[dict[str, Any]] = []
    for archive, signature in pairs:
        archive_path = download_dir / archive["name"]
        signature_path = download_dir / signature["name"]
        result = _exact_keys(
            verify_signature(archive_path, signature_path, key_file, normalized),
            f"signature result for {archive['name']}",
            {"command", "exit_code", "verified"},
        )
        command = result["command"]
        if not isinstance(command, list) or not command or any(
            not isinstance(item, str) or not item for item in command
        ):
            raise ValidationError(f"signature result for {archive['name']}: command must be a string list")
        required_paths = {str(archive_path), str(signature_path), str(key_file)}
        if not required_paths.issubset(command):
            raise ValidationError(
                f"signature result for {archive['name']}: command must use explicit archive, signature, and key paths"
            )
        if isinstance(result["exit_code"], bool) or result["exit_code"] != 0 or result["verified"] is not True:
            raise ValidationError(f"signature verification failed for {archive['name']}")
        results.append({"archive": archive["name"], "signature": signature["name"], **result})
    return results


def validate_paths(
    manifest_path: Path = MANIFEST_PATH,
    component_registry_path: Path = COMPONENT_REGISTRY_PATH,
    repo_registry_path: Path = REPO_REGISTRY_PATH,
    repo_root: Path = REPO_ROOT,
) -> None:
    manifest = load_yaml_strict(manifest_path)
    validate_manifest_data(
        manifest,
        load_yaml_strict(component_registry_path),
        load_yaml_strict(repo_registry_path),
        repo_root,
    )
    validate_manifest_page_blocks(manifest, repo_root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-ref")
    parser.add_argument("--head-ref")
    parser.add_argument("--branch")
    args = parser.parse_args()
    diff_args = (args.base_ref, args.head_ref, args.branch)
    if any(diff_args) and not all(diff_args):
        parser.error("--base-ref, --head-ref, and --branch must be supplied together")
    try:
        validate_paths()
        promotion = None
        if all(diff_args):
            promotion = validate_git_promotion(
                args.base_ref, args.head_ref, args.branch, REPO_ROOT
            )
    except ValidationError as exc:
        print(f"release baseline validation failed: {exc}", file=sys.stderr)
        return 1
    if promotion and promotion["promoted"]:
        route = (
            " (manual Browser SDK source)"
            if promotion.get("route") == "manual-browser-source"
            else ""
        )
        print(
            f"release baseline validation passed: atomic promotion{route} for "
            + ", ".join(promotion["entries"])
        )
    else:
        print("release baseline validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
