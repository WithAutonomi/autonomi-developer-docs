# How Language Bindings Work

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

These language bindings are client libraries that your application imports and calls. They send requests to a local daemon, a separately running background service called [antd](../../use-antd.md), which handles the network connection, encryption, and configured payments.

## Package availability

The Python and JavaScript clients install from PyPI and npm. Other languages have their own package or source-install instructions, listed below. Follow the guide for your language: package versions and supported operations can differ.

| Language | Installation used in this guide | Transport |
|----------|---------------------|-----------|
| [Go](go.md) | Public Go module pinned to `v0.12.1` | REST, gRPC |
| [Rust](rust.md) | Local Cargo path dependency | REST, gRPC |
| [Python](python.md) | PyPI `antd[rest]`; gRPC extra available separately | REST, gRPC |
| [JavaScript](javascript.md) | npm `@withautonomi/antd` | REST |
| [TypeScript](typescript.md) | npm `@withautonomi/antd` with type declarations | REST |
| [Java](java.md) | Local Maven publication built from source | REST, gRPC |
| [C#](csharp.md) | Local .NET project reference | REST, gRPC |
| [Kotlin](kotlin.md) | Unavailable for supported consumer installation | REST, gRPC source implementation |
| [Swift](swift.md) | Local Swift package path | REST, gRPC |
| [Ruby](ruby.md) | Locally built gem | REST, gRPC |
| [PHP](php.md) | Release-source Composer project | REST |
| [C++](cpp.md) | Local CMake subdirectory | REST, optional gRPC |
| [Dart](dart.md) | Local Dart path dependency | REST, gRPC |
| [Zig](zig.md) | Local Zig path dependency | REST |

## How it connects

```text
Your application
       |
       v
Client library in your application
       |
       v
antd: separate background service
       |
       v
Autonomi Network
```

REST clients connect to `http://localhost:8082` by default. gRPC clients connect to `localhost:50051`. You can override these addresses when you create a client.

## Common operations

Each implementation includes operations for these tasks:

| Task | Typical operation |
|------|-------------------|
| Check connectivity | `health` |
| Store public data | `dataPutPublic` or `data_put_public` |
| Retrieve public data | `dataGetPublic` or `data_get_public` |
| Store private data | `dataPut` or `data_put` |
| Retrieve private data | `dataGet` or `data_get` |
| Upload and download public files | `filePutPublic` / `fileGetPublic`, or snake_case equivalents |
| Estimate storage cost | `dataCost`, `fileCost`, or language-specific equivalents |
| Read the wallet balance | `walletBalance` or `wallet_balance` |

Names follow each language's conventions, so exact capitalization varies by binding.

## Error handling

The bindings map service failures to language-specific error types:

| Status | Meaning |
|--------|---------|
| 400 | Invalid request parameters |
| 402 | Payment required or insufficient funds |
| 404 | Prepared upload or in-memory chunk not found |
| 409 | Data already exists or version conflict |
| 413 | Upload too large |
| 500 | Internal service error; `antd v0.13.0` also reports a missing DataMap this way |
| 502 | Network communication failure |
| 503 | Service unavailable, such as an unconfigured wallet |

A malformed address is an invalid request and returns status 400. `antd v0.13.0` has a known error-mapping defect: retrieving a valid DataMap address that is not stored returns status 500 over REST or `INTERNAL` over gRPC instead of a not-found response. Do not interpret every internal error as missing data; inspect the message and confirm the address.

## Related pages

- [Choose a language binding](README.md)
- [REST API Reference](../rest-api.md)
- [Connect from Your Application](../../native/README.md) for SDKs that do not need a local daemon
