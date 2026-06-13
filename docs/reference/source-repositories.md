# Source Repositories

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: e102df9b3ea1a17fba7cf731081f515d89552b82
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 84332e2d752499df5402da797e5d8bba547bc58b
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: fb7494e84dd02f664fce83cebd210a4c73ddcfe2
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-protocol
  source_ref: main
  source_commit: 34c11cb9f626290b18263ebe8e10e172e5523424
  verified_date: 2026-06-13
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-core
  source_ref: main
  source_commit: 180454671b87debcb2afbd83f2d8126c41b0dd02
  verified_date: 2026-06-13
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: e24ecaced902f668d64cda2269deef0babd5d9ab
  verified_date: 2026-06-13
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-pqc
  source_ref: main
  source_commit: 56e7b435de76f868f285b93cc470000fc6f5eec4
  verified_date: 2026-06-10
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
