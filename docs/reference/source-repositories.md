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
  source_commit: 50b4370bc08acf57c93f1c763063d3582ecf3aef
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 661e68aa0f6edfd5884003025c34647389256872
  verified_date: 2026-08-19
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
  source_commit: a08750c7d13b10d4469bea4dcee95fea15d34571
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: ace6d07a227b1530f3d63e4e02e9c5606aa96887
  verified_date: 2026-08-19
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

This docs set is assembled from the active source repositories below. If you want to inspect the implementation directly, start with these repos.

## WithAutonomi

- [`WithAutonomi`](https://github.com/WithAutonomi) — Main GitHub organization for the current Autonomi developer-facing repos
- [`ant-sdk`](https://github.com/WithAutonomi/ant-sdk) — `antd`, language SDKs, local dev tooling, and `antd-mcp`
- [`ant-client`](https://github.com/WithAutonomi/ant-client) — Direct CLI and native Rust path: `ant`, `ant-core`, and local devnet tooling
- [`ant-node`](https://github.com/WithAutonomi/ant-node) — Node runtime, chunk storage, payment verification, and replication behavior
- [`ant-protocol`](https://github.com/WithAutonomi/ant-protocol) — Shared wire protocol crate for chunk messages, payment proofs, and devnet manifests
- [`self_encryption`](https://github.com/WithAutonomi/self_encryption) — Client-side self-encryption crate used for content processing before network storage
- [`evmlib`](https://github.com/WithAutonomi/evmlib) — EVM payment helpers used by the daemon, CLI, and direct Rust flows
- [`ant-merkle`](https://github.com/WithAutonomi/ant-merkle) — Merkle batch payment contracts and proof structures used by larger upload batches
- [`ant-keygen`](https://github.com/WithAutonomi/ant-keygen) — ML-DSA-65 release-signing utility

## saorsa-labs

- [`saorsa-labs`](https://github.com/saorsa-labs) — Supporting transport, networking, and cryptography repos used by the current Autonomi stack
- [`saorsa-core`](https://github.com/saorsa-labs/saorsa-core) — Core peer-to-peer node, DHT, routing, and trust system
- [`saorsa-transport`](https://github.com/saorsa-labs/saorsa-transport) — QUIC transport, NAT traversal, relay-assisted connectivity, and post-quantum transport layer
- [`saorsa-pqc`](https://github.com/saorsa-labs/saorsa-pqc) — Post-quantum cryptography library used by the broader stack

## How to use these links

Use these repos when you want to:

- inspect the implementation behind a documented interface
- follow a tool or crate in more detail
- review upstream changes alongside the docs
- understand how the different parts of the Autonomi stack fit together

For a docs-first view of how the stack fits together, start with [System Overview](../architecture/system-overview.md).
