#!/usr/bin/env python3
"""Deterministic release scanner for the daily sweep routine.

Walks every <!-- verification: ... --> block in docs/**/*.md. Released profiles
emit candidate records; legacy moving-source blocks emit migration backlog
entries without resolving their refs.

Read-only. Never modifies files. Exits 0 on success, 2 on fail-closed errors.
See planning/routines/upstream-sweep.md for the policy this implements.
"""

from __future__ import annotations

import base64
import binascii
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "repo-registry.yml"
COMPONENT_REGISTRY_PATH = REPO_ROOT / "component-registry.yml"
TARGET_MANIFEST_PATH = REPO_ROOT / "target-manifest.yml"
DOCS_DIR = REPO_ROOT / "docs"

SEMVER_RE = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z"
)
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
VERIFIED_DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
GITHUB_RELEASE_TIMESTAMP_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z\Z"
)
FIRST_CLI_PLATFORM_TARGETS = {
    "aarch64-apple-darwin",
    "aarch64-unknown-linux-musl",
    "x86_64-apple-darwin",
    "x86_64-pc-windows-msvc",
    "x86_64-unknown-linux-musl",
}

VERIFICATION_BLOCK_RE = re.compile(
    r"<!--\s*verification:(.*?)-->",
    re.DOTALL,
)
KEY_VALUE_RE = re.compile(r"^\s*([a-z_]+)\s*:\s*(\S.*?)\s*$")
ALLOWED_MODES = {"current-merged-truth", "target-manifest"}
REQUIRED_DOC_KEYS = (
    "source_repo",
    "source_ref",
    "source_commit",
    "verified_date",
    "verification_mode",
)


class FailClosed(Exception):
    """Raised whenever the scanner cannot make a confident drift judgment.

    Carries one diagnostic dict to embed in the JSON output's `errors` array.
    """

    def __init__(self, diagnostic: dict[str, Any]):
        super().__init__(diagnostic.get("message", "fail-closed"))
        self.diagnostic = diagnostic


def _github_get(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "autonomi-developer-docs-sweep-poll",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_error_context(exc: urllib.error.HTTPError) -> dict[str, Any]:
    # Drain headers and body once so a bare 403 in a status comment carries
    # enough signal (rate-limit state, GitHub's own error message, the
    # request id) to distinguish org-policy refusal from anonymous quota
    # exhaustion from a transient outage.
    raw_headers = exc.headers if exc.headers is not None else {}
    body_text = ""
    try:
        raw = exc.read()
        if raw:
            body_text = raw.decode("utf-8", errors="replace")
    except Exception:
        body_text = ""
    body_message: str | None = body_text.strip()[:500] if body_text else None
    try:
        parsed = json.loads(body_text)
        if isinstance(parsed, dict) and isinstance(parsed.get("message"), str):
            body_message = parsed["message"][:500]
    except (ValueError, TypeError):
        pass

    def _h(name: str) -> str | None:
        value = raw_headers.get(name)
        return str(value) if value is not None else None

    return {
        "status": exc.code,
        "body_message": body_message,
        "request_id": _h("x-github-request-id"),
        "ratelimit_limit": _h("x-ratelimit-limit"),
        "ratelimit_remaining": _h("x-ratelimit-remaining"),
        "ratelimit_used": _h("x-ratelimit-used"),
        "ratelimit_reset": _h("x-ratelimit-reset"),
        "ratelimit_resource": _h("x-ratelimit-resource"),
        "retry_after": _h("retry-after"),
    }


def github_request(path: str, token: str | None = None) -> Any:
    # An authenticated 403 means the org refuses the token, not that the repo
    # is unreachable. Retry once without auth so public repos in orgs that
    # restrict fine-grained PATs still resolve.
    url = f"https://api.github.com{path}"
    try:
        return _github_get(url, token)
    except urllib.error.HTTPError as auth_exc:
        if auth_exc.code == 403 and token:
            auth_context = _http_error_context(auth_exc)
            try:
                return _github_get(url, None)
            except urllib.error.HTTPError as anon_exc:
                anon_context = _http_error_context(anon_exc)
                raise FailClosed(
                    {
                        "kind": "github_api_http_error",
                        "url": url,
                        "status": anon_context["status"],
                        "auth_status": auth_context["status"],
                        "auth": auth_context,
                        "anon": anon_context,
                        "message": (
                            f"GitHub API returned {auth_context['status']} "
                            f"authenticated and {anon_context['status']} "
                            f"anonymous for {path}"
                        ),
                    }
                ) from anon_exc
            except urllib.error.URLError as anon_exc:
                raise FailClosed(
                    {
                        "kind": "github_api_network_error",
                        "url": url,
                        "auth_status": auth_context["status"],
                        "auth": auth_context,
                        "anon_network_error": str(anon_exc.reason),
                        "message": (
                            f"GitHub API network error on anonymous retry "
                            f"for {path}: {anon_exc.reason}"
                        ),
                    }
                ) from anon_exc
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as anon_exc:
                raise FailClosed(
                    {
                        "kind": "github_api_parse_error",
                        "url": url,
                        "auth_status": auth_context["status"],
                        "auth": auth_context,
                        "anon_parse_error": str(anon_exc),
                        "message": (
                            f"GitHub API returned invalid JSON on anonymous "
                            f"retry for {path}: {anon_exc}"
                        ),
                    }
                ) from anon_exc
        context = _http_error_context(auth_exc)
        raise FailClosed(
            {
                "kind": "github_api_http_error",
                "url": url,
                **context,
                "message": f"GitHub API returned {context['status']} for {path}",
            }
        ) from auth_exc
    except urllib.error.URLError as exc:
        raise FailClosed(
            {
                "kind": "github_api_network_error",
                "url": url,
                "message": f"GitHub API network error for {path}: {exc.reason}",
            }
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise FailClosed(
            {
                "kind": "github_api_parse_error",
                "url": url,
                "message": f"GitHub API returned invalid JSON for {path}: {exc}",
            }
        ) from exc


def parse_owner_repo(url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(url)
    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if parsed.netloc != "github.com" or len(parts) < 2:
        raise FailClosed(
            {
                "kind": "registry_url_unparseable",
                "url": url,
                "message": f"cannot derive <owner>/<repo> from registry url: {url}",
            }
        )
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[: -len(".git")]
    return owner, repo


def load_registry() -> dict[str, dict[str, Any]]:
    try:
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FailClosed(
            {
                "kind": "registry_yaml_parse_error",
                "path": str(REGISTRY_PATH.relative_to(REPO_ROOT)),
                "message": f"YAML parse error in repo-registry.yml: {exc}",
            }
        ) from exc
    repos = (data or {}).get("repos") or {}
    if not isinstance(repos, dict):
        raise FailClosed(
            {
                "kind": "registry_shape_error",
                "path": str(REGISTRY_PATH.relative_to(REPO_ROOT)),
                "message": "repo-registry.yml: expected top-level 'repos' map",
            }
        )
    return repos


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise FailClosed(
                {
                    "kind": "yaml_shape_error",
                    "message": "YAML mapping keys must be scalar",
                }
            ) from exc
        if duplicate:
            raise FailClosed(
                {
                    "kind": "yaml_duplicate_key",
                    "key": str(key),
                    "line": key_node.start_mark.line + 1,
                    "message": f"duplicate YAML key {key!r}",
                }
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load_yaml(path: Path, label: str) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except OSError as exc:
        raise FailClosed(
            {
                "kind": "configuration_read_error",
                "path": str(path),
                "message": f"cannot read {label}: {exc}",
            }
        ) from exc
    except yaml.YAMLError as exc:
        raise FailClosed(
            {
                "kind": "configuration_yaml_parse_error",
                "path": str(path),
                "message": f"YAML parse error in {label}: {exc}",
            }
        ) from exc


def load_release_configuration() -> tuple[dict[str, Any], dict[str, Any]]:
    if not COMPONENT_REGISTRY_PATH.exists():
        raise FailClosed(
            {
                "kind": "component_registry_missing",
                "path": str(COMPONENT_REGISTRY_PATH),
                "message": "component-registry.yml is required for release-aware scanning",
            }
        )
    component_data = _load_yaml(COMPONENT_REGISTRY_PATH, "component-registry.yml")
    if not isinstance(component_data, dict) or not isinstance(
        component_data.get("components"), dict
    ):
        raise FailClosed(
            {
                "kind": "component_registry_shape_error",
                "message": "component-registry.yml: expected top-level components map",
            }
        )
    components = component_data["components"]
    manifest: dict[str, Any] = {}
    if TARGET_MANIFEST_PATH.exists():
        manifest_data = _load_yaml(TARGET_MANIFEST_PATH, "target-manifest.yml")
        if not isinstance(manifest_data, dict):
            raise FailClosed(
                {
                    "kind": "target_manifest_shape_error",
                    "message": "target-manifest.yml: expected top-level map",
                }
            )
        manifest = manifest_data
    return components, manifest


def validate_release_manifest(
    manifest: dict[str, Any], components: dict[str, Any], registry: dict[str, Any]
) -> None:
    if not manifest and not components:
        return
    validator_path = Path(__file__).resolve().parent / "validate_release_baselines.py"
    spec = importlib.util.spec_from_file_location("release_baseline_validator", validator_path)
    if spec is None or spec.loader is None:
        raise FailClosed(
            {
                "kind": "release_baseline_validator_unavailable",
                "message": "cannot load release baseline validator",
            }
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.validate_manifest_data(
            manifest,
            {"components": components},
            {"repos": registry},
            REPO_ROOT,
        )
    except module.ValidationError as exc:
        raise FailClosed(
            {
                "kind": "release_baseline_validation_error",
                "message": str(exc),
            }
        ) from exc


def _release_enrolments(components: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    enrolments: list[tuple[str, str, dict[str, Any]]] = []
    for component_name in sorted(components):
        component = components[component_name]
        if not isinstance(component, dict):
            raise FailClosed(
                {
                    "kind": "component_registry_shape_error",
                    "component": component_name,
                    "message": f"component {component_name!r} must be a map",
                }
            )
        discovery = component.get("release_discovery")
        if discovery is None:
            continue
        if not isinstance(discovery, dict):
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "component": component_name,
                    "message": "release_discovery must be a map",
                }
            )
        for context in sorted(discovery):
            config = discovery[context]
            if not isinstance(config, dict):
                raise FailClosed(
                    {
                        "kind": "release_discovery_configuration_error",
                        "component": component_name,
                        "context": context,
                        "message": "release discovery context must be a map",
                    }
                )
            enrolments.append((component_name, context, config))
    return enrolments


def _release_baselines(manifest: dict[str, Any]) -> dict[str, Any]:
    release = manifest.get("release_baselines")
    if release is None:
        return {}
    if not isinstance(release, dict) or release.get("schema_version") != 1 or not isinstance(
        release.get("entries"), dict
    ):
        raise FailClosed(
            {
                "kind": "release_baseline_shape_error",
                "message": "release_baselines must be schema version 1 with an entries map",
            }
        )
    return release["entries"]


def parse_verification_block(body: str, location: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = KEY_VALUE_RE.match(line)
        if match is None:
            raise FailClosed(
                {
                    "kind": "doc_block_unparseable_line",
                    "location": location,
                    "line": line[:200],
                    "message": (
                        f"verification block at {location} has an "
                        f"unparseable line: {line[:200]!r}"
                    ),
                }
            )
        key = match.group(1)
        if key in fields:
            raise FailClosed(
                {
                    "kind": "doc_block_duplicate_key",
                    "location": location,
                    "key": key,
                    "message": f"verification block at {location} repeats key: {key}",
                }
            )
        fields[key] = match.group(2)
    unknown = sorted(set(fields) - set(REQUIRED_DOC_KEYS))
    if unknown:
        raise FailClosed(
            {
                "kind": "doc_block_unknown_keys",
                "location": location,
                "unknown": unknown,
                "message": (
                    f"verification block at {location} has unknown keys: "
                    f"{', '.join(unknown)}"
                ),
            }
        )
    return fields


def line_of_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def walk_docs(
    registry: dict[str, dict[str, Any]],
    migration_backlog: list[dict[str, Any]],
    target_manifest_skipped: list[dict[str, Any]],
) -> None:
    if not DOCS_DIR.exists():
        return
    for path in sorted(DOCS_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(REPO_ROOT))
        for match in VERIFICATION_BLOCK_RE.finditer(text):
            block_line = line_of_offset(text, match.start())
            location = f"{rel}:{block_line}"
            fields = parse_verification_block(match.group(1), location)
            missing = [k for k in REQUIRED_DOC_KEYS if k not in fields]
            if missing:
                raise FailClosed(
                    {
                        "kind": "doc_block_missing_required_keys",
                        "location": f"{rel}:{block_line}",
                        "missing": missing,
                        "message": (
                            f"verification block at {rel}:{block_line} "
                            f"missing required keys: {', '.join(missing)}"
                        ),
                    }
                )
            mode = fields["verification_mode"]
            if mode not in ALLOWED_MODES:
                raise FailClosed(
                    {
                        "kind": "doc_block_unknown_verification_mode",
                        "location": f"{rel}:{block_line}",
                        "verification_mode": mode,
                        "message": (
                            f"verification block at {rel}:{block_line} has "
                            f"unknown verification_mode: {mode!r}"
                        ),
                    }
                )
            repo_key = fields["source_repo"]
            if repo_key not in registry:
                raise FailClosed(
                    {
                        "kind": "doc_block_unknown_source_repo",
                        "location": f"{rel}:{block_line}",
                        "source_repo": repo_key,
                        "message": (
                            f"verification block at {rel}:{block_line} "
                            f"references repo not in repo-registry.yml: {repo_key}"
                        ),
                    }
                )
            ref = fields["source_ref"]
            recorded = fields["source_commit"]
            if SHA_RE.fullmatch(recorded) is None:
                raise FailClosed(
                    {
                        "kind": "doc_block_invalid_source_commit",
                        "location": location,
                        "source_commit": recorded,
                        "message": (
                            f"verification block at {location} must record a "
                            "lowercase 40-hex source_commit"
                        ),
                    }
                )
            verified_date = fields["verified_date"]
            try:
                valid_date = (
                    VERIFIED_DATE_RE.fullmatch(verified_date) is not None
                    and datetime.strptime(verified_date, "%Y-%m-%d").strftime(
                        "%Y-%m-%d"
                    )
                    == verified_date
                )
            except ValueError:
                valid_date = False
            if not valid_date:
                raise FailClosed(
                    {
                        "kind": "doc_block_invalid_verified_date",
                        "location": location,
                        "verified_date": verified_date,
                        "message": (
                            f"verification block at {location} must record a "
                            "real YYYY-MM-DD verified_date"
                        ),
                    }
                )
            if mode == "target-manifest":
                target_manifest_skipped.append(
                    {
                        "location": location,
                        "repo": repo_key,
                        "ref": ref,
                        "recorded_sha": recorded,
                    }
                )
                continue
            migration_backlog.append(
                {
                    "location": location,
                    "repo": repo_key,
                    "ref": ref,
                    "recorded_sha": recorded,
                }
            )


def _provider_json(url: str, provider: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/json",
        "User-Agent": "autonomi-developer-docs-sweep-poll",
    }
    if token and provider == "github":
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        context = _http_error_context(exc)
        raise FailClosed(
            {
                "kind": f"{provider}_http_error",
                "url": url,
                **context,
                "message": f"{provider} returned HTTP {context['status']} for {url}",
            }
        ) from exc
    except urllib.error.URLError as exc:
        raise FailClosed(
            {
                "kind": f"{provider}_network_error",
                "url": url,
                "message": f"{provider} network error for {url}: {exc.reason}",
            }
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise FailClosed(
            {
                "kind": f"{provider}_parse_error",
                "url": url,
                "message": f"{provider} returned invalid JSON for {url}: {exc}",
            }
        ) from exc


def npm_request(package: str, version: str | None = None) -> Any:
    encoded = urllib.parse.quote(package, safe="@")
    suffix = f"/{urllib.parse.quote(version, safe='')}" if version is not None else ""
    return _provider_json(f"https://registry.npmjs.org/{encoded}{suffix}", "npm")


def _semver(value: Any) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or SEMVER_RE.fullmatch(value) is None:
        return None
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def _github_coordinates(repo_config: dict[str, Any]) -> tuple[str, str]:
    url = repo_config.get("url")
    if not isinstance(url, str):
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "message": "release source repository has no URL",
            }
        )
    return parse_owner_repo(url)


def _github_releases(owner: str, repo: str, token: str | None) -> list[dict[str, Any]]:
    releases: list[dict[str, Any]] = []
    page = 1
    while True:
        response = github_request(
            f"/repos/{owner}/{repo}/releases?per_page=100&page={page}", token
        )
        if not isinstance(response, list) or any(not isinstance(item, dict) for item in response):
            raise FailClosed(
                {
                    "kind": "github_release_shape_error",
                    "repo": f"{owner}/{repo}",
                    "page": page,
                    "message": "GitHub releases response must be an array of objects",
                }
            )
        releases.extend(response)
        if len(response) < 100:
            return releases
        page += 1


def _peel_tag(owner: str, repo: str, tag: str, token: str | None) -> str:
    encoded_tag = urllib.parse.quote(tag, safe="")
    response = github_request(
        f"/repos/{owner}/{repo}/git/ref/tags/{encoded_tag}", token
    )
    if not isinstance(response, dict) or not isinstance(response.get("object"), dict):
        raise FailClosed(
            {
                "kind": "github_tag_shape_error",
                "tag": tag,
                "message": "GitHub tag reference has no object",
            }
        )
    target = response["object"]
    seen: set[str] = set()
    while True:
        target_type = target.get("type")
        sha = target.get("sha")
        if not isinstance(target_type, str) or not isinstance(sha, str) or SHA_RE.fullmatch(sha) is None:
            raise FailClosed(
                {
                    "kind": "github_tag_shape_error",
                    "tag": tag,
                    "message": "GitHub tag target must have a type and lowercase 40-hex SHA",
                }
            )
        if target_type == "commit":
            return sha
        if target_type != "tag" or sha in seen:
            raise FailClosed(
                {
                    "kind": "github_tag_shape_error",
                    "tag": tag,
                    "message": "GitHub tag does not peel to a commit",
                }
            )
        seen.add(sha)
        tag_object = github_request(f"/repos/{owner}/{repo}/git/tags/{sha}", token)
        if not isinstance(tag_object, dict) or not isinstance(tag_object.get("object"), dict):
            raise FailClosed(
                {
                    "kind": "github_tag_shape_error",
                    "tag": tag,
                    "message": "GitHub annotated tag object has no target",
                }
            )
        target = tag_object["object"]


def _asset_projection(
    asset: dict[str, Any], expected_name: str, owner: str, repo: str, tag: str
) -> tuple[dict[str, Any] | None, str | None]:
    required = ("name", "id", "browser_download_url", "digest")
    if any(key not in asset for key in required):
        return None, f"asset {expected_name!r} lacks required provider metadata"
    name, asset_id, url, digest = (asset[key] for key in required)
    if name != expected_name or isinstance(asset_id, bool) or not isinstance(asset_id, int) or asset_id <= 0:
        return None, f"asset {expected_name!r} has invalid name or id"
    expected_url = f"https://github.com/{owner}/{repo}/releases/download/{tag}/{expected_name}"
    if url != expected_url or not isinstance(digest, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", digest) is None:
        return None, f"asset {expected_name!r} has invalid URL or digest"
    return {"name": name, "id": asset_id, "url": url, "digest": digest}, None


def observe_github_release(
    owner: str,
    repo: str,
    config: dict[str, Any],
    token: str | None,
) -> dict[str, Any]:
    pattern_text = config.get("tag_pattern")
    platforms = config.get("platforms")
    checksum_name = config.get("checksum_asset")
    if (
        not isinstance(pattern_text, str)
        or not isinstance(platforms, dict)
        or not platforms
        or not isinstance(checksum_name, str)
        or config.get("reject_drafts") is not True
        or config.get("reject_prereleases") is not True
    ):
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "message": "GitHub release discovery configuration is malformed",
            }
        )
    try:
        pattern = re.compile(pattern_text)
    except re.error as exc:
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "message": f"invalid release tag pattern: {exc}",
            }
        ) from exc
    eligible: list[tuple[tuple[int, int, int], dict[str, Any], str]] = []
    for release in _github_releases(owner, repo, token):
        tag = release.get("tag_name")
        draft = release.get("draft")
        prerelease = release.get("prerelease")
        if not isinstance(tag, str) or not isinstance(draft, bool) or not isinstance(prerelease, bool):
            raise FailClosed(
                {
                    "kind": "github_release_shape_error",
                    "message": "GitHub release lacks tag_name, draft, or prerelease",
                }
            )
        match = pattern.fullmatch(tag)
        if match is None or draft or prerelease:
            continue
        version = match.groupdict().get("version")
        parsed = _semver(version)
        if parsed is not None:
            eligible.append((parsed, release, version))
    if not eligible:
        return {
            "complete": False,
            "problems": ["GitHub has no eligible stable release"],
            "version": None,
            "tag": None,
            "commit": None,
            "release": None,
        }
    _, selected, version = max(eligible, key=lambda item: item[0])
    tag = selected["tag_name"]
    commit = _peel_tag(owner, repo, tag, token)
    base_required = ("id", "url", "html_url", "published_at", "assets")
    if any(key not in selected for key in base_required):
        raise FailClosed(
            {
                "kind": "github_release_shape_error",
                "tag": tag,
                "message": "selected GitHub release lacks provider metadata",
            }
        )
    expected_api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/{selected['id']}"
    expected_release_url = f"https://github.com/{owner}/{repo}/releases/tag/{tag}"
    published_at = selected["published_at"]
    published = None
    if (
        isinstance(published_at, str)
        and GITHUB_RELEASE_TIMESTAMP_RE.fullmatch(published_at) is not None
    ):
        try:
            published = datetime.fromisoformat(
                published_at.removesuffix("Z") + "+00:00"
            )
        except ValueError:
            pass
    if (
        isinstance(selected["id"], bool)
        or not isinstance(selected["id"], int)
        or selected["id"] <= 0
        or not all(isinstance(selected[key], str) and selected[key] for key in ("url", "html_url", "published_at"))
        or not isinstance(selected["assets"], list)
        or any(not isinstance(asset, dict) for asset in selected["assets"])
        or selected["url"] != expected_api_url
        or selected["html_url"] != expected_release_url
        or published is None
    ):
        raise FailClosed(
            {
                "kind": "github_release_shape_error",
                "tag": tag,
                "message": "selected GitHub release metadata has invalid types",
            }
        )
    by_name: dict[str, list[dict[str, Any]]] = {}
    for asset in selected["assets"]:
        name = asset.get("name")
        if isinstance(name, str):
            by_name.setdefault(name, []).append(asset)
    problems: list[str] = []
    required_asset_ids: set[int] = set()

    def required_asset(name: str) -> dict[str, Any] | None:
        matches = by_name.get(name, [])
        if len(matches) != 1:
            problems.append(f"required asset {name!r} occurs {len(matches)} times")
            return None
        projected, problem = _asset_projection(matches[0], name, owner, repo, tag)
        if problem:
            problems.append(problem)
            return projected
        if projected["id"] in required_asset_ids:
            problems.append(f"required asset id {projected['id']} occurs more than once")
            return None
        required_asset_ids.add(projected["id"])
        return projected

    checksum = required_asset(checksum_name)
    normalized_platforms: dict[str, Any] = {}
    for target in sorted(platforms):
        extension = platforms[target]
        if not isinstance(target, str) or not isinstance(extension, str):
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "message": "GitHub platform target and extension must be strings",
                }
            )
        archive_name = f"ant-{version}-{target}.{extension}"
        archive = required_asset(archive_name)
        signature = required_asset(f"{archive_name}.sig")
        observed_assets: dict[str, Any] = {}
        if archive is not None:
            observed_assets["archive"] = archive
        if signature is not None:
            observed_assets["signature"] = signature
        if observed_assets:
            normalized_platforms[target] = observed_assets
    normalized = {
        "id": selected["id"],
        "api_url": selected["url"],
        "release_url": selected["html_url"],
        "published_at": selected["published_at"],
        "draft": False,
        "prerelease": False,
    }
    if checksum is not None:
        normalized["checksum_asset"] = checksum
    normalized["platforms"] = normalized_platforms
    return {
        "complete": not problems,
        "problems": problems,
        "version": version,
        "tag": tag,
        "commit": commit,
        "release": normalized,
    }


def _npm_facts(data: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    version = data.get("version") if isinstance(data.get("version"), str) else None
    git_head = data.get("gitHead") if isinstance(data.get("gitHead"), str) else None
    dist = data.get("dist")
    integrity = dist.get("integrity") if isinstance(dist, dict) and isinstance(dist.get("integrity"), str) else None
    return version, git_head, integrity


def _valid_sha512_integrity(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha512-"):
        return False
    encoded = value[len("sha512-") :]
    try:
        encoded_bytes = encoded.encode("ascii")
        decoded = base64.b64decode(encoded_bytes, validate=True)
    except (UnicodeEncodeError, binascii.Error, ValueError):
        return False
    return len(decoded) == 64 and base64.b64encode(decoded) == encoded_bytes


def observe_npm_release(config: dict[str, Any]) -> dict[str, Any]:
    package = config.get("package")
    dist_tag = config.get("dist_tag")
    platform_packages = config.get("platform_packages")
    if not isinstance(package, str) or dist_tag != "latest" or not isinstance(platform_packages, dict) or not platform_packages:
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "message": "npm release discovery configuration is malformed",
            }
        )
    root = npm_request(package)
    if not isinstance(root, dict):
        raise FailClosed(
            {
                "kind": "npm_shape_error",
                "package": package,
                "message": "npm package metadata must be an object",
            }
        )
    dist_tags = root.get("dist-tags")
    latest = dist_tags.get("latest") if isinstance(dist_tags, dict) else None
    if not isinstance(latest, str):
        return {"complete": False, "problems": ["npm latest distribution tag is missing"], "version": None, "commit": None, "npm": None, "git_heads": []}
    if _semver(latest) is None:
        return {"complete": False, "problems": ["npm latest is not a stable Semantic Versioning value"], "version": latest, "commit": None, "npm": None, "git_heads": []}
    meta = npm_request(package, latest)
    if not isinstance(meta, dict):
        raise FailClosed(
            {
                "kind": "npm_shape_error",
                "package": package,
                "version": latest,
                "message": "npm version metadata must be an object",
            }
        )
    version, git_head, integrity = _npm_facts(meta)
    optional = meta.get("optionalDependencies")
    problems: list[str] = []
    if version != latest:
        problems.append("npm meta-package version does not equal latest")
    if not _valid_sha512_integrity(integrity):
        problems.append("npm meta-package integrity is missing or invalid")
    if not isinstance(git_head, str) or SHA_RE.fullmatch(git_head) is None:
        problems.append("npm meta-package gitHead is missing or invalid")
    if not isinstance(optional, dict):
        problems.append("npm meta-package optionalDependencies is missing")
        optional = {}
    normalized_platforms: dict[str, Any] = {}
    git_heads: list[str] = [git_head] if isinstance(git_head, str) and SHA_RE.fullmatch(git_head) else []
    for target in sorted(platform_packages):
        platform_package = platform_packages[target]
        if not isinstance(target, str) or not isinstance(platform_package, str):
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "message": "npm target and package names must be strings",
                }
            )
        if optional.get(platform_package) != latest:
            problems.append(f"npm optional dependency {platform_package!r} does not equal {latest}")
        platform_data = npm_request(platform_package, latest)
        if not isinstance(platform_data, dict):
            raise FailClosed(
                {
                    "kind": "npm_shape_error",
                    "package": platform_package,
                    "version": latest,
                    "message": "npm platform metadata must be an object",
                }
            )
        platform_version, platform_head, platform_integrity = _npm_facts(platform_data)
        if platform_version != latest:
            problems.append(f"npm platform package {platform_package!r} has wrong version")
        if not _valid_sha512_integrity(platform_integrity):
            problems.append(
                f"npm platform package {platform_package!r} integrity is missing or invalid"
            )
        if not isinstance(platform_head, str) or SHA_RE.fullmatch(platform_head) is None:
            problems.append(f"npm platform package {platform_package!r} lacks gitHead")
        else:
            git_heads.append(platform_head)
            if isinstance(git_head, str) and platform_head != git_head:
                problems.append(
                    f"npm platform package {platform_package!r} gitHead differs from meta-package"
                )
        platform_observation = {"package": platform_package}
        if isinstance(platform_version, str):
            platform_observation["version"] = platform_version
        platform_observation["metadata_url"] = (
            f"https://registry.npmjs.org/"
            f"{urllib.parse.quote(platform_package, safe='@')}/{latest}"
        )
        if _valid_sha512_integrity(platform_integrity):
            platform_observation["integrity"] = platform_integrity
        if isinstance(platform_head, str) and SHA_RE.fullmatch(platform_head):
            platform_observation["git_head"] = platform_head
        normalized_platforms[target] = platform_observation
    normalized = {"package": package, "dist_tag": "latest"}
    if isinstance(version, str):
        normalized["version"] = version
    normalized["metadata_url"] = (
        f"https://registry.npmjs.org/{urllib.parse.quote(package, safe='@')}/{latest}"
    )
    if _valid_sha512_integrity(integrity):
        normalized["integrity"] = integrity
    if isinstance(git_head, str) and SHA_RE.fullmatch(git_head):
        normalized["git_head"] = git_head
    normalized["platforms"] = normalized_platforms
    return {
        "complete": not problems,
        "problems": problems,
        "version": latest,
        "commit": git_head if isinstance(git_head, str) and SHA_RE.fullmatch(git_head) else None,
        "npm": normalized,
        "git_heads": sorted(git_heads),
    }


def observe_installers(
    owner: str,
    repo: str,
    configs: Any,
    token: str | None,
) -> list[dict[str, Any]]:
    if not isinstance(configs, list) or not configs:
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "message": "installer discovery configuration must be a non-empty list",
            }
        )
    observations: list[dict[str, Any]] = []
    for config in configs:
        if not isinstance(config, dict) or set(config) != {"platform", "ref", "path", "url"}:
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "message": "installer configuration has invalid fields",
                }
            )
        platform, ref, path, raw_url = (config[key] for key in ("platform", "ref", "path", "url"))
        if not all(isinstance(value, str) and value for value in (platform, ref, path, raw_url)):
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "message": "installer configuration values must be non-empty strings",
                }
            )
        expected_raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
        if raw_url != expected_raw or path.startswith("/") or ".." in Path(path).parts:
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "platform": platform,
                    "message": "installer URL, repository, ref, and path do not match",
                }
            )
        query = urllib.parse.urlencode({"path": path, "sha": ref, "per_page": 1})
        history = github_request(f"/repos/{owner}/{repo}/commits?{query}", token)
        if not isinstance(history, list) or len(history) != 1 or not isinstance(history[0], dict):
            raise FailClosed(
                {
                    "kind": "installer_history_shape_error",
                    "platform": platform,
                    "message": "installer path history must contain one latest commit",
                }
            )
        source_commit = history[0].get("sha")
        if not isinstance(source_commit, str) or SHA_RE.fullmatch(source_commit) is None:
            raise FailClosed(
                {
                    "kind": "installer_history_shape_error",
                    "platform": platform,
                    "message": "installer path history lacks a lowercase 40-hex commit",
                }
            )
        encoded_path = urllib.parse.quote(path, safe="/")
        content = github_request(
            f"/repos/{owner}/{repo}/contents/{encoded_path}?ref={source_commit}", token
        )
        expected_evidence = f"https://github.com/{owner}/{repo}/blob/{source_commit}/{path}"
        if (
            not isinstance(content, dict)
            or not isinstance(content.get("sha"), str)
            or SHA_RE.fullmatch(content["sha"]) is None
            or content.get("html_url") != expected_evidence
        ):
            raise FailClosed(
                {
                    "kind": "installer_blob_linkage_error",
                    "platform": platform,
                    "message": "installer blob metadata does not link path and exact source commit",
                }
            )
        observations.append(
            {
                "platform": platform,
                "url": raw_url,
                "repo": f"{owner}/{repo}",
                "ref": ref,
                "path": path,
                "source_commit": source_commit,
                "blob_sha": content["sha"],
                "evidence_url": expected_evidence,
            }
        )
    return observations


def _mapped_pages(components: dict[str, Any], component_name: str) -> tuple[list[str], dict[str, list[str]]]:
    component = components[component_name]
    feeds_pages = component.get("feeds_pages")
    if not isinstance(feeds_pages, list) or any(not isinstance(page, str) for page in feeds_pages):
        raise FailClosed(
            {
                "kind": "release_discovery_configuration_error",
                "component": component_name,
                "message": "release component feeds_pages must be a string array",
            }
        )
    reverse: dict[str, list[str]] = {}
    for name, candidate in components.items():
        if not isinstance(candidate, dict):
            continue
        pages = candidate.get("feeds_pages", [])
        if not isinstance(pages, list):
            raise FailClosed(
                {
                    "kind": "component_registry_shape_error",
                    "component": name,
                    "message": "feeds_pages must be an array",
                }
            )
        for page in pages:
            if isinstance(page, str):
                reverse.setdefault(f"docs/{page}", []).append(name)
    mapped = sorted({f"docs/{page}" for page in feeds_pages})
    return mapped, {page: sorted(reverse.get(page, [])) for page in mapped}


def _match_page_block(
    page: str,
    repo_key: str,
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    path = REPO_ROOT / page
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise FailClosed(
            {
                "kind": "release_page_missing",
                "path": page,
                "message": f"cannot read release-scoped page {page}: {exc}",
            }
        ) from exc
    matches: list[dict[str, Any]] = []
    for match in VERIFICATION_BLOCK_RE.finditer(text):
        location = f"{page}:{line_of_offset(text, match.start())}"
        fields = parse_verification_block(match.group(1), location)
        if fields.get("source_repo") == repo_key:
            matches.append(
                {
                    "fields": fields,
                    "location": location,
                }
            )
    if len(matches) != 1:
        raise FailClosed(
            {
                "kind": "release_page_block_ambiguous",
                "path": page,
                "repo": repo_key,
                "count": len(matches),
                "message": f"{page} must contain exactly one {repo_key} verification block",
            }
        )
    selected = matches[0]
    fields = selected["fields"]
    if baseline is not None:
        source = baseline["source"]
        if (
            fields.get("verification_mode") != "target-manifest"
            or fields.get("source_ref") != source["tag"]
            or fields.get("source_commit") != source["commit"]
        ):
            raise FailClosed(
                {
                    "kind": "release_page_block_mismatch",
                    "path": page,
                    "message": f"{page} verification block does not match release baseline",
                }
            )
    elif any(key not in fields for key in REQUIRED_DOC_KEYS):
        raise FailClosed(
            {
                "kind": "release_page_block_mismatch",
                "path": page,
                "message": f"{page} component verification block is malformed",
            }
        )
    return selected


def _release_projection(component: str, context: str, evidence: dict[str, Any]) -> tuple[Any, ...]:
    source = evidence["source"]
    github = evidence["github_release"]
    npm = evidence["npm"]
    assets: list[tuple[Any, ...]] = []
    checksum = github["checksum_asset"]
    assets.append(("", "checksum", checksum["name"], checksum["id"], checksum["digest"]))
    for target in sorted(github["platforms"]):
        for role in ("archive", "signature"):
            asset = github["platforms"][target][role]
            assets.append((target, role, asset["name"], asset["id"], asset["digest"]))
    packages = tuple(
        (
            target,
            npm["platforms"][target]["package"],
            npm["platforms"][target]["version"],
            npm["platforms"][target]["integrity"],
            npm["platforms"][target]["git_head"],
        )
        for target in sorted(npm["platforms"])
    )
    return (
        component,
        context,
        evidence["version"],
        source["repo"],
        source["tag"],
        source["commit"],
        github["id"],
        tuple(sorted(assets)),
        npm["package"],
        npm["dist_tag"],
        npm["version"],
        npm["integrity"],
        npm["git_head"],
        packages,
    )


def _installer_projection(installer: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(installer[key] for key in ("platform", "url", "source_commit", "blob_sha", "evidence_url"))


def _synthesize_records(
    pages: list[str],
    repo_key: str,
    baseline: dict[str, Any] | None,
    ref: str | None,
    head_sha: str | None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for page in sorted(pages):
        matched = _match_page_block(page, repo_key, baseline)
        recorded = matched["fields"]["source_commit"]
        final_ref = ref or matched["fields"]["source_ref"]
        final_head = head_sha or recorded
        records.append(
            {
                "location": matched["location"],
                "scope": "docs",
                "repo": repo_key,
                "ref": final_ref,
                "recorded_sha": recorded,
                "head_sha": final_head,
                "drifted": recorded != final_head,
            }
        )
    return records


def discover_releases(
    components: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    baselines: dict[str, Any],
    token: str | None,
    notices: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for component_name, context, config in _release_enrolments(components):
        component = components[component_name]
        repo_key = component.get("repo")
        if not isinstance(repo_key, str) or repo_key not in registry:
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "component": component_name,
                    "message": "release component repository is unknown",
                }
            )
        owner, repo = _github_coordinates(registry[repo_key])
        github_config = config.get("github")
        npm_config = config.get("npm")
        if not isinstance(github_config, dict) or not isinstance(npm_config, dict):
            raise FailClosed(
                {
                    "kind": "release_discovery_configuration_error",
                    "component": component_name,
                    "message": "release discovery requires GitHub and npm maps",
                }
            )
        github = observe_github_release(owner, repo, github_config, token)
        npm = observe_npm_release(npm_config)
        installers = observe_installers(owner, repo, config.get("installers"), token)
        notices.append(
            {
                "kind": "installer_observation",
                "severity": "info",
                "component": component_name,
                "context": context,
                "message": "Observed installer path commits and immutable blobs; installers were not downloaded or executed.",
                "installers": installers,
            }
        )

        baseline_key = f"{component_name}/{context}"
        baseline = baselines.get(baseline_key)
        if baseline is not None and not isinstance(baseline, dict):
            raise FailClosed(
                {
                    "kind": "release_baseline_shape_error",
                    "entry": baseline_key,
                    "message": "release baseline entry must be a map",
                }
            )
        mapped_pages, reverse = _mapped_pages(components, component_name)
        scoped_pages = baseline["scoped_pages"] if baseline is not None else mapped_pages
        problems = list(github["problems"]) + list(npm["problems"])
        commits = [npm["commit"], *npm["git_heads"]]
        commits = [value for value in commits if value is not None]
        platform_sets_agree = True
        if component_name == "ant-cli" and context == "stable":
            github_platforms = (
                github["release"].get("platforms", {})
                if isinstance(github["release"], dict)
                else {}
            )
            npm_platforms = (
                npm["npm"].get("platforms", {})
                if isinstance(npm["npm"], dict)
                else {}
            )
            platform_sets_agree = (
                set(github_platforms)
                == set(npm_platforms)
                == FIRST_CLI_PLATFORM_TARGETS
            )
        agrees = (
            github["complete"]
            and npm["complete"]
            and platform_sets_agree
            and github["version"] == npm["version"]
            and github["commit"] is not None
            and commits
            and all(value == github["commit"] for value in commits)
        )
        if github["complete"] and npm["complete"] and github["version"] != npm["version"]:
            problems.append("GitHub and npm stable versions disagree")
        if github["complete"] and npm["complete"] and commits and not all(value == github["commit"] for value in commits):
            problems.append("GitHub and npm source commits disagree")
        if github["complete"] and npm["complete"] and not platform_sets_agree:
            problems.append(
                "GitHub and npm must expose the same five required CLI platform targets"
            )

        observed: dict[str, Any] | None = None
        candidate = False
        manual_reasons: list[str] = []
        if agrees:
            observed = {
                "component": component_name,
                "context": context,
                "version": github["version"],
                "source": {"repo": repo_key, "tag": github["tag"], "commit": github["commit"]},
                "github_release": github["release"],
                "npm": npm["npm"],
            }
            if baseline is None:
                candidate = True
            else:
                current_projection = _release_projection(component_name, context, observed)
                baseline_projection = _release_projection(component_name, context, baseline)
                if current_projection != baseline_projection:
                    if _semver(observed["version"]) > _semver(baseline["version"]):
                        candidate = True
                    else:
                        manual_reasons.append("same or lower release version has changed immutable evidence")
        else:
            manual_reasons.extend(problems or ["release evidence is incomplete or conflicting"])

        if baseline is not None:
            baseline_installers = baseline.get("installers", [])
            if (
                not isinstance(baseline_installers, list)
                or sorted(_installer_projection(item) for item in baseline_installers)
                != sorted(_installer_projection(item) for item in installers)
            ):
                manual_reasons.append("installer evidence differs from the reviewed baseline")

        fallback_ref = (
            github["tag"]
            or (baseline["source"]["tag"] if baseline is not None else None)
        )
        valid_npm_head = npm["commit"] if isinstance(npm["commit"], str) and SHA_RE.fullmatch(npm["commit"]) else None
        fallback_head = (
            github["commit"]
            or valid_npm_head
            or (baseline["source"]["commit"] if baseline is not None else None)
        )
        release_records = _synthesize_records(
            scoped_pages,
            repo_key,
            baseline,
            observed["source"]["tag"] if observed is not None else fallback_ref,
            observed["source"]["commit"] if observed is not None else fallback_head,
        )
        records.extend(release_records)

        if manual_reasons:
            notices.append(
                {
                    "kind": "release_manual_review",
                    "severity": "warning",
                    "component": component_name,
                    "context": context,
                    "locations": [record["location"] for record in release_records],
                    "reason": "; ".join(sorted(set(manual_reasons))),
                    "baseline": (
                        {
                            "source": baseline["source"],
                            "github_release": baseline["github_release"],
                            "npm": baseline["npm"],
                            "installers": baseline.get("installers", []),
                        }
                        if baseline is not None
                        else None
                    ),
                    "current": {
                        "github": github,
                        "npm": npm,
                        "installers": installers,
                    },
                }
            )
        if candidate and observed is not None:
            candidates.append(
                {
                    **observed,
                    "pages": [
                        {"path": page, "components": reverse[page]}
                        for page in mapped_pages
                    ],
                    "records": release_records,
                }
            )
    records.sort(key=lambda record: tuple(record["location"].rsplit(":", 1)))
    candidates.sort(key=lambda item: (item["component"], item["context"]))
    return records, candidates


def main() -> int:
    token_raw = os.environ.get("GITHUB_TOKEN", "").strip()
    token: str | None = token_raw or None
    notices: list[dict[str, Any]] = []
    if token is None:
        notices.append(
            {
                "kind": "unauthenticated_mode",
                "severity": "info",
                "message": (
                    "GITHUB_TOKEN not set; using anonymous GitHub API "
                    "requests (60 req/hour limit)."
                ),
            }
        )

    try:
        registry = load_registry()
        components, manifest = load_release_configuration()
        validate_release_manifest(manifest, components, registry)
        baselines = _release_baselines(manifest)
        migration_backlog: list[dict[str, Any]] = []
        target_manifest_skipped: list[dict[str, Any]] = []
        walk_docs(registry, migration_backlog, target_manifest_skipped)
        migration_backlog.sort(
            key=lambda record: (
                record["location"].rsplit(":", 1)[0],
                int(record["location"].rsplit(":", 1)[1]),
            )
        )
        records, release_candidates = discover_releases(
            components, registry, baselines, token, notices
        )

    except FailClosed as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "records": [],
                    "release_candidates": [],
                    "target_manifest_skipped": [],
                    "migration_backlog": [],
                    "notices": notices,
                    "errors": [exc.diagnostic],
                },
                indent=2,
            )
        )
        return 2

    output = {
        "status": "ok",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "release_candidates": release_candidates,
        "target_manifest_skipped": target_manifest_skipped,
        "migration_backlog": migration_backlog,
        "notices": notices,
        "errors": [],
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
