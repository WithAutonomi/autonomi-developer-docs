# Source Repositories

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-protocol
  source_ref: main
  source_commit: 2bd604a88aaee8cf9a8bf60bf4e61268ed0d0581
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-core
  source_ref: main
  source_commit: 74eb48289381c019d6bc6d35174a22591cb32150
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: 75a1e11e49872fa4ebe768d85f20ae3a8db9e91d
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-pqc
  source_ref: main
  source_commit: 4fbb31d3d29f710726edd32e12ce7b1f64a2aae1
  verified_date: 2026-08-04
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: self_encryption
  source_ref: master
  source_commit: 4021f663612c5b963bef935b277eb65416b7d958
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: fbf879b1f7068b5b072a936589721272c62f2ca0
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-merkle
  source_ref: master
  source_commit: 176ab0a1cafaeee712b3442d9d5af09769149d31
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-keygen
  source_ref: main
  source_commit: 902442f123e16f57de0aeb0f1bfbacf385aa2e87
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->

This page maps publicly obtainable releases for the Autonomi components covered here. Some components exist only inside a release source tree. Repository links follow the ownership declared in this site's source registry.

## Developer products covered here

- [`ant-sdk`](https://github.com/WithAutonomi/ant-sdk) - [`v0.14.0`](https://github.com/WithAutonomi/ant-sdk/releases/tag/v0.14.0), source commit [`dbf6a7d3d9511da6518ed369a2d1e4dba2c9ae51`](https://github.com/WithAutonomi/ant-sdk/commit/dbf6a7d3d9511da6518ed369a2d1e4dba2c9ae51), publishes `antd` binaries, installers, and the `ghcr.io/withautonomi/antd` container image. The source tree also includes native SDKs, language clients, `ant-dev`, and `antd-mcp`. The [antd clients](../sdk/reference/language-bindings/overview.md) for Python, JavaScript and TypeScript, C#, Ruby, PHP, and Dart are published as `0.2.0` packages on PyPI (`antd`), npm (`@withautonomi/antd`), NuGet (`Autonomi.Antd`), RubyGems (`antd`), Packagist (`autonomi/antd`), and pub.dev (`antd_client`), built from the `v0.14.0` source with a version bump at commit [`8481c6f82ef551089971fa712b8f76d0e3581eeb`](https://github.com/WithAutonomi/ant-sdk/commit/8481c6f82ef551089971fa712b8f76d0e3581eeb). The Go client is the module `github.com/WithAutonomi/ant-sdk/antd-go` at `v0.14.0`. [Native SDKs](../sdk/native/README.md) have independently published package versions.
- [`ant-client`](https://github.com/WithAutonomi/ant-client) - [`ant-cli-v0.3.8`](https://github.com/WithAutonomi/ant-client/releases/tag/ant-cli-v0.3.8), source commit [`9112d683d8dbecffd8ad437546453f9f52310964`](https://github.com/WithAutonomi/ant-client/commit/9112d683d8dbecffd8ad437546453f9f52310964), publishes the `ant` CLI as release archives and [`@withautonomi/ant` on npm](https://www.npmjs.com/package/@withautonomi/ant). The npm package selects the platform binary and requires Node.js 18 or later. [`ant-core 0.10.0`](https://crates.io/crates/ant-core/0.10.0) comes from the same source commit and is used by the [Direct Rust examples](../rust/library-reference.md).
- [`ant-node`](https://github.com/WithAutonomi/ant-node) - [`v0.20.0`](https://github.com/WithAutonomi/ant-node/releases/tag/v0.20.0), source commit [`2b4ab3c5c13617ca1fc01f9ab18457bcba369d85`](https://github.com/WithAutonomi/ant-node/commit/2b4ab3c5c13617ca1fc01f9ab18457bcba369d85), publishes `ant-node` archives and the [`ant-node 0.20.0`](https://crates.io/crates/ant-node/0.20.0) crate.
- [`ant-keygen`](https://github.com/WithAutonomi/ant-keygen) — [`v0.1.0`](https://github.com/WithAutonomi/ant-keygen/releases/tag/v0.1.0), source commit [`3a2953f384a3b16391968de451b703843b98ed86`](https://github.com/WithAutonomi/ant-keygen/commit/3a2953f384a3b16391968de451b703843b98ed86), publishes the ML-DSA-65 release-signing utility.

## Shipped dependencies

### CLI, daemon, and node

The npm package and release archives for `ant-cli 0.3.8` contain the same platform executables. `antd 0.14.0` ships the same versions of these components. `ant-node 0.20.0` ships the same versions except `ant-core`, which the node does not use. Their dependencies include:

| Component | Version and source |
|-----------|--------------------|
| ant-core | [0.10.0](https://github.com/WithAutonomi/ant-client/tree/9112d683d8dbecffd8ad437546453f9f52310964/ant-core) |
| ant-protocol | [3.0.0](https://github.com/WithAutonomi/ant-protocol/tree/007d4a0fd3d97ca479ec890fcfb6c24a423432af) |
| evmlib | [0.10.0](https://github.com/WithAutonomi/evmlib/tree/cec38987be0e844b08efbb1e0c7a6e29c8d908cd) |
| saorsa-core | [0.28.0](https://github.com/saorsa-labs/saorsa-core/tree/46243b37a9ae20aee48b9cad21a522e485d496ca) |
| saorsa-transport | [0.37.0](https://github.com/saorsa-labs/saorsa-transport/tree/a10509aca872aba6e5257b3c24e2f79a11f8412b) |
| saorsa-pqc | [0.5.2](https://github.com/saorsa-labs/saorsa-pqc/tree/b90282e5dc87a5643d0dcdb039559ea32cd6896f) |
| self_encryption | [0.36.0](https://github.com/WithAutonomi/self_encryption/tree/0deb040084f94bea2ebb53bda20fa23464bbcfe0) |
| ant-merkle | [1.5.1](https://github.com/WithAutonomi/ant-merkle/tree/80af80a5df1e26e3b6fb386d041178889c4ed993) |

### Native SDKs

- `ant-core` - Native SDK packages `0.0.9` ship `ant-core 0.8.1` from [the CLI 0.3.6 source commit](https://github.com/WithAutonomi/ant-client/commit/dbc01ce8fdbdfe9ac4d064d35f36b4684bf6a616).
- [`self_encryption`](https://github.com/WithAutonomi/self_encryption) — Client-side self-encryption used by data and file uploads. The native SDKs ship [`0.36.0`](https://crates.io/crates/self_encryption/0.36.0) from commit [`0deb040084f94bea2ebb53bda20fa23464bbcfe0`](https://github.com/WithAutonomi/self_encryption/commit/0deb040084f94bea2ebb53bda20fa23464bbcfe0).
- [`evmlib`](https://github.com/WithAutonomi/evmlib) — Ethereum Virtual Machine (EVM) payment helpers. The native SDKs ship [`0.9.1`](https://crates.io/crates/evmlib/0.9.1) from commit [`fbf879b1f7068b5b072a936589721272c62f2ca0`](https://github.com/WithAutonomi/evmlib/commit/fbf879b1f7068b5b072a936589721272c62f2ca0).
- [`ant-merkle`](https://github.com/WithAutonomi/ant-merkle) — Merkle batch payment contracts and proof structures. The released products ship [`1.5.1`](https://crates.io/crates/ant-merkle/1.5.1) from commit [`80af80a5df1e26e3b6fb386d041178889c4ed993`](https://github.com/WithAutonomi/ant-merkle/commit/80af80a5df1e26e3b6fb386d041178889c4ed993). The package has no matching source tag and contains older repository metadata.

These are the dependencies of the named product releases, not the newest standalone packages. Adding a library to your own Cargo project resolves dependencies separately; retain and review your application's `Cargo.lock` rather than assuming it reproduces a released binary's dependency graph.

## Source-only components

- The daemon's Rust binding requires a pinned source checkout. Follow [Rust SDK](../sdk/reference/language-bindings/rust.md) rather than substituting the separate `ant-core` crate.
- `ant-dev` and `antd-mcp` are source components. [Set Up a Local Network](../guides/set-up-a-local-network.md) pins `ant-sdk v0.12.0`; [How to Use the MCP Server](../mcp/use-the-autonomi-mcp-server.md) installs the MCP server and its Python client from `v0.14.0` with `antd 0.14.0`. These source installations are not automatically advanced with the antd executable; keep the versions specified in each guide together.
- `ant-devnet` has no independent release. It is parent-bound to `ant-node 0.20.0` as a second binary in the crates.io source package and is not included in the `ant-node v0.20.0` binary archives. The local-network guide uses a separate, older pairing; keep its pinned versions together rather than substituting independently released components.

## Source identity limitations

The source registry identifies the `saorsa-labs` repositories above as canonical. Some published package metadata points to older locations; use the registry links rather than those stale locations.

The `ant-node v0.20.0` archive signatures do not validate against `sign/release-signing-key.pub` at the release tag. Do not treat manual verification with that repository key as a valid installation route. A matching SHA-256 checksum alone does not resolve the signing-key mismatch.

## How to use these links

Use these links when you want to:

- inspect the implementation behind a documented interface
- follow a tool or crate in more detail
- compare repository changes with versioned package contents where source identity is established
- understand how the different parts of the Autonomi stack fit together

For a docs-first view of how the stack fits together, start with [System Overview](../architecture/system-overview.md).
