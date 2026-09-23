# Glossary

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
  source_repo: ant-keygen
  source_ref: main
  source_commit: 902442f123e16f57de0aeb0f1bfbacf385aa2e87
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->

Canonical terms used throughout this docs set.

## A

**ant-client** — Direct Rust and CLI interface to the Autonomi Network via `ant-core` and the `ant` binary.

**ant-core** — Headless Rust library powering `antd`, the Direct Rust interface, and the `ant` CLI.

**ant-keygen** — ML-DSA-65 release-signing utility.

**ant-protocol** — Shared wire protocol crate used by `ant-core` and `ant-node` for chunk messages, payment proofs, and devnet manifests.

**ant-sdk** — Software development kit for building on Autonomi, including libraries that connect directly, client libraries for `antd`, and tools such as `antd`.

**antd** — Separate background service that handles Autonomi Network access for your application, exposing REST on `http://localhost:8082` and gRPC on `localhost:50051` by default.

**Autonomi Network Token (ANT)** — ERC-20 token on Arbitrum used for storage payments.

**Arbitrum** — Layer 2 Ethereum network used by Autonomi payment tooling.

**Autonomi** — Decentralized data storage network for storing and retrieving content.

**Autonomi Network** — The peer-to-peer network reached through `antd`, `ant-core`, `ant`, and `ant-node`.

## B

**BLAKE3** — Cryptographic hash used for content addresses and for self-encryption chunk hashing.

## C

**ChaCha20-Poly1305** — Authenticated encryption primitive used in self-encryption.

**chunk** — Immutable, content-addressed storage unit of up to 4 MB; data and file operations store encrypted chunks, while raw chunk operations store caller-supplied bytes.

**close group** — The set of nodes closest to a target address in XOR space.

**content addressing** — Deriving an address from content rather than from a mutable location.

## D

**daemon** — A program that runs as a background service, separate from the application that calls it.

**DataMap** — Retrieval metadata that ties uploaded content back to its encrypted chunks.

## E

**external signer** — Wallet or signing flow that submits upload-payment transactions without giving `antd` or `ant-core` direct custody of the private key.

## H

**HKDF** — Key-derivation primitive exposed by `saorsa-pqc`.

## K

**Kademlia DHT** — Peer-routing system that locates nodes by XOR distance.

## L

**library** — Reusable code that your application imports or links and runs as part of its own process.

**local trust scoring** — Per-node reputation based on direct peer observations combined through an exponential moving average.

## M

**Merkle batch payment** — Batch-payment mode used for larger chunk sets.

**ML-DSA-65** — NIST FIPS 204 digital signature algorithm used for transport authentication and release-signing tools.

**ML-KEM-768** — NIST FIPS 203 key encapsulation mechanism used during transport session establishment.

## N

**NAT traversal** — Peer-observed address discovery, coordinator hints, hole punching, and optional UPnP-assisted address mapping used to keep peers reachable across NAT boundaries. Relay-assisted fallback handles cases where direct traversal still fails.

## P

**pay-once** — Storage payment model where you pay when you upload and do not pay ongoing storage fees.

**post-quantum cryptography** — Cryptographic algorithms designed to resist quantum attacks. Autonomi uses them for transport key exchange, transport identity, and release signing; content self-encryption remains a separate BLAKE3 plus ChaCha20-Poly1305 layer.

## Q

**QUIC** — UDP-based transport protocol used for peer connections, NAT traversal coordination, and relay-assisted fallback.

## S

**SDK (software development kit)** — A collection of libraries, tools, and documentation for building applications, not a single running program.

**self-encryption** — Client-side content processing that returns a `DataMap` plus encrypted chunks.

## X

**XOR distance** — Distance metric used for peer and data proximity in Kademlia-style routing.
