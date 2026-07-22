# System Overview

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 71c84b9054ceab0d98656805c654d395d592a2db
  verified_date: 2026-07-22
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9a4d8c4d02def2ffae20b56a04220048c1c69bf7
  verified_date: 2026-07-21
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: eb74b5640055986e41ea408053a72e6249cb0d82
  verified_date: 2026-07-22
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-protocol
  source_ref: main
  source_commit: 83d588e34633c812c329ffb9a2666f5c7387dd7b
  verified_date: 2026-07-13
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-core
  source_ref: main
  source_commit: b0ee4877d9fbdb0b0c76713d86f54847be5a03fb
  verified_date: 2026-07-21
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: d9e1687c28430c96d4325265ee901f5c9d42d595
  verified_date: 2026-07-21
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
