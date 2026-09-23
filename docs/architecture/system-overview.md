# System Overview

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

When your application stores or retrieves data, a client connects it to the Autonomi Network. This page shows where that client runs and how it communicates with storage nodes.

## High-level architecture

```text
Application
  |
  +-- REST or gRPC --> antd --> ant-core 0.8.0 --> client saorsa-core
  |                                                + saorsa-transport --+
  |                                                                      |
  +-- Native library --> bundled ant-core 0.8.1 --> client saorsa-core    |
  |                                                + saorsa-transport --+
  |                                                                      |
  +-- Direct Rust --> ant-core 0.8.1 --> client saorsa-core              | QUIC
  |                                      + saorsa-transport -------------+
  |                                                                      |
  +-- CLI --> ant --> ant-core 0.8.1 --> client saorsa-core              |
                                         + saorsa-transport -------------+
                                                                         |
                                                                         v
                                                                 remote ant-node
                                                                         |
                                                               node saorsa-core
                                                                 + saorsa-transport
                                                                         |
                                                                         v
                                                         chunk storage, payment checks,
                                                                and replication
```

## Developer interfaces

The developer interfaces covered by these guides are:

- the local `antd` service, called through a [client library](../sdk/reference/language-bindings/overview.md) or directly over [REST](../sdk/reference/rest-api.md) or [gRPC](../sdk/reference/grpc-services.md)
- [native libraries](../sdk/native/README.md) for Python, Node.js, or .NET applications
- [Direct Rust](../rust/README.md) using `ant-core` and [the CLI](../cli/use-the-cli.md) using `ant`

Both the `antd` client libraries and the native libraries run inside your application. An `antd` client library sends requests to a separate background service that handles the network connection; a native library handles that connection within your application. You can also call `antd` without a client library, for example by sending HTTP requests to its REST API.

These interfaces target the same Autonomi Network. Native libraries, Direct Rust, and the CLI connect without `antd`; choose according to your application's requirements. `antd 0.13.0` ships `ant-core 0.8.0`; native SDK packages `0.0.9`, `ant-cli 0.3.6`, and the published Direct Rust package use `ant-core 0.8.1`.

The native libraries, `antd`, the CLI, and Direct Rust use `ant-core` on the client side. For normal data operations, `ant-core` runs a client-mode `saorsa-core` peer and connects to remote storage nodes over `saorsa-transport`; it does not route requests through a local `ant-node`. The optional `ant-core` devnet feature links `ant-node` only to run a local test network.

## Network and node layer

The `ant-node` crate builds on `saorsa-core::P2PNode`. It adds configuration, chunk storage, payment verification, replication, upgrade handling, and node runtime management on top of the core peer-to-peer layer.

`ant-core` and `ant-node` also share wire-message types, payment-proof types, and devnet manifest types through `ant-protocol`.

`ant-node` accepts chunks as its storage data type.

With its default settings, `ant-node 0.18.1` records but does not penalize a peer for failing to hold a chunk for which it belongs to the close group. This does not disable storage auditing: failed audits of a peer's signed storage commitment still incur penalties, as do replication fetch responses reporting storage-read faults. A missing chunk and a failed storage read are different outcomes. The `ANT_SUSPEND_UNHELD_CHUNK_PENALTY` environment override can change the missing-chunk penalty policy.

## Routing and transport

`saorsa-core` provides the peer-to-peer node, Kademlia DHT, bootstrap handling, trust system, and routing-table logic around typed addresses and peer identity. It is also responsible for publishing dialable self-addresses and coordinator hints into DHT records. `saorsa-transport` provides QUIC transport, NAT traversal, address discovery, and relay fallback where direct hole punching is not enough.

When the routing table falls below its recovery threshold, automatic recovery can re-dial configured bootstrap peers after losing every connection. A client with too few routing entries can also dial peers learned from connected peers. Recovery still depends on reachable peers and routing-table admission; it is not a guarantee that a write will succeed.

The transport story includes:

- observed-address discovery and address propagation across the Autonomi Network
- reachability tracking by scope: loopback, local-network, or global
- best-effort UPnP port mapping as an extra public candidate on compatible routers
- peer-ID-based hole-punch coordination, with coordinator hints and coordinator rotation when one path cannot help
- relay fallback for some CGNAT cases
- QUIC-based post-quantum transport security centered on ML-KEM-768 and ML-DSA-65

That post-quantum framing applies to transport identity and session establishment. Content self-encryption remains a separate client-side layer built around BLAKE3 and ChaCha20-Poly1305.

## Data path

For data and file uploads, client-side self-encryption turns content into a `DataMap` plus encrypted chunks. Raw chunk calls bypass that step and send caller-supplied bytes. Client-side `ant-core`, `saorsa-core`, and `saorsa-transport` connect to remote `ant-node` processes. Each node receives chunk requests through its networking layer, verifies payments, stores and serves chunks, and coordinates replication across the Autonomi Network.

## Upstream sources

- [ant-sdk](https://github.com/WithAutonomi/ant-sdk)
- [ant-client](https://github.com/WithAutonomi/ant-client)
- [ant-node](https://github.com/WithAutonomi/ant-node)
- [ant-protocol](https://github.com/WithAutonomi/ant-protocol)
- [self_encryption](https://github.com/WithAutonomi/self_encryption)

Client and node releases have separate dependency graphs. They share `saorsa-core 0.27.3` and `saorsa-transport 0.36.3`, but `antd 0.13.0` uses an older `ant-core` and `ant-protocol` than the CLI. See [Source Repositories](../reference/source-repositories.md) for exact package identities and source-identity limitations.

## Related pages

- [Core Concepts Overview](../core-concepts/overview.md)
- [SDK Overview](../sdk/reference/overview.md)
- [Use the CLI](../cli/use-the-cli.md)
- [Direct Rust](../rust/README.md)
