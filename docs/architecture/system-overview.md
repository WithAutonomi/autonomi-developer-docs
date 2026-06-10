# System Overview

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
  source_commit: ffaf12d41c1f129ed92051e04aaf5d6f8e94eec7
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-core
  source_ref: main
  source_commit: a681772c042b8215f36a9a860510d1fdb54b7540
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: 2ee8e944ae32c3667ca8b588365a65a41f4b0f14
  verified_date: 2026-06-10
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

This page gives a high-level view of how the main developer-facing and network-facing repos fit together.

## High-level architecture

```text
Application
  |                         Rust / CLI
  | REST or gRPC                |
  v                             v
 antd                      ant-core / ant
  |                             |
  +-------------+---------------+
                |
                v
             ant-node
                |
                v
            saorsa-core
                |
                v
         saorsa-transport
                |
                v
            Autonomi peers
```

## Developer interfaces

The main developer entry points are:

- `ant-sdk`, centered on the `antd` daemon plus language SDKs
- `ant-client`, centered on `ant-core` and the `ant` CLI

These interfaces target the same network, but one uses a local daemon and the other connects directly from Rust or CLI code.

## Network and node layer

The `ant-node` crate builds on `saorsa-core::P2PNode`. It adds configuration, chunk storage, payment verification, replication, upgrade handling, and node runtime management on top of the core P2P layer.

`ant-core` and `ant-node` also share wire-message types, payment-proof types, and devnet manifest types through `ant-protocol`.

In the repos used for this page, `ant-node` documents chunk storage as its active network data type.

## Routing and transport

`saorsa-core` provides the P2P node, DHT, bootstrap handling, trust system, and routing-table logic around typed addresses and peer identity. It is also responsible for publishing dialable self-addresses and coordinator hints into DHT records. `saorsa-transport` provides QUIC transport, NAT traversal, address discovery, and relay fallback where direct hole punching is not enough.

The transport story includes:

- observed-address discovery and address propagation across the network
- reachability tracking by scope: loopback, local-network, or global
- best-effort UPnP port mapping as an extra public candidate on compatible routers
- peer-ID-based hole-punch coordination, with coordinator hints and coordinator rotation when one path cannot help
- relay fallback for some CGNAT cases
- QUIC-based post-quantum transport security centered on ML-KEM-768 and ML-DSA-65

That post-quantum framing applies to transport identity and session establishment. Content self-encryption remains a separate client-side layer built around BLAKE3 and ChaCha20-Poly1305.

## Data path

On the client side, `self_encryption` turns uploaded content into a `DataMap` plus encrypted chunks. Developer-facing clients such as `antd` and `ant-core` prepare and retrieve that content, while `ant-node` stores and serves chunk data across the network.

## Upstream sources

- [ant-sdk](https://github.com/WithAutonomi/ant-sdk)
- [ant-client](https://github.com/WithAutonomi/ant-client)
- [ant-node](https://github.com/WithAutonomi/ant-node)
- [ant-protocol](https://github.com/WithAutonomi/ant-protocol)
- [self_encryption](https://github.com/WithAutonomi/self_encryption)
- [saorsa-core](https://github.com/saorsa-labs/saorsa-core)
- [saorsa-transport](https://github.com/saorsa-labs/saorsa-transport)
- [saorsa-pqc](https://github.com/saorsa-labs/saorsa-pqc)

## Related pages

- [Core Concepts Overview](../core-concepts/overview.md)
- [SDK Overview](../sdk/reference/overview.md)
- [Using the Autonomi CLI](../cli/use-the-cli.md)
- [Developing in Rust](../rust/README.md)
