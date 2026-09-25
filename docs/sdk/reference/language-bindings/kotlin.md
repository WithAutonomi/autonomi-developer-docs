# Kotlin SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

The Kotlin SDK source targets a local daemon, a background service called antd, over REST and gRPC. The `v0.12.1` release has no published Kotlin client package or supported application installation workflow.

## Install

The source requires JDK 17 or later. Do not add `com.autonomi:antd-kotlin:0.1.0`: that artifact is not available from Maven Central.

You cannot install this binding as a supported application dependency in ant-sdk v0.12.1. You can inspect or build the exact release source without treating it as an installable package:

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
cd ant-sdk/antd-kotlin
./gradlew :lib:build
```

## Connect to antd

No supported consumer setup is available for a runnable connection example in this release.

## Store and retrieve data

No supported consumer setup is available for a runnable upload and download example in this release. Use the public [Go SDK](go.md), another release-source workflow listed in the [language bindings overview](overview.md), or the [REST API](../rest-api.md).

## Type mappings

| Autonomi type | Kotlin type |
|------|------|
| `HealthStatus` | Kotlin data class |
| `PutResult` | Kotlin data class |
| Raw data | `ByteArray` |

## Error handling

Kotlin error examples also depend on an installable consumer package, which is unavailable in the pinned `v0.12.1` source release. `antd` returns status 400 for malformed addresses. `antd 0.14.0` returns status 404 over REST, or `NOT_FOUND` over gRPC, for a valid address with no stored data; the binding raises `NotFoundException` for it.

## Full API reference

For all available `antd` endpoints, see the [REST API](../rest-api.md).
