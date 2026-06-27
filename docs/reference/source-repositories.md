# Source Repositories

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: e56292325d04f1cf398c7e6bc77619ff2ab44447
  verified_date: 2026-06-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 3ab50c44a6ba62b34e879b86c97eae469b56cb3c
  verified_date: 2026-06-25
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: e53928ac8eeb33cb07576dae06dbac5f1cf94f18
  verified_date: 2026-06-27
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-protocol
  source_ref: main
  source_commit: 7caae7701a52f7ec557dea394abf60c33670521e
  verified_date: 2026-06-27
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-core
  source_ref: main
  source_commit: ead67187b912118fc7d43ca1e8d01938761d5682
  verified_date: 2026-06-27
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: a24065b83c188a2b74cd8a0ad2c518f076016756
  verified_date: 2026-06-27
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-pqc
  source_ref: main
  source_commit: bb2aa1981afe94340160b70f65bd633098da6e5b
  verified_date: 2026-06-15
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: self_encryption
  source_ref: master
  source_commit: 0deb040084f94bea2ebb53bda20fa23464bbcfe0
  verified_date: 2026-05-16
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: 225acbb1af613193bcc8264b6ede4d7e4a7ac607
  verified_date: 2026-05-16
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-merkle
  source_ref: master
  source_commit: 80af80a5df1e26e3b6fb386d041178889c4ed993
  verified_date: 2026-05-16
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-keygen
  source_ref: main
  source_commit: 3a2953f384a3b16391968de451b703843b98ed86
  verified_date: 2026-05-16
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
