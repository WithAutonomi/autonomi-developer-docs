# Autonomi Developer Documentation

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 6c4df9b745f3adcb022ac82b6bbc485727297e3e
  verified_date: 2026-04-02
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 796d0df75d748419a004aec6f5e288b41d8b496e
  verified_date: 2026-04-04
  verification_mode: current-merged-truth
-->

{% hint style="warning" %}
This is preview documentation for Autonomi 2.0 ahead of the planned network launch on 7 April 2026. Content is under active review and may change before launch.
{% endhint %}

These guides help you build on the Autonomi Network.

Autonomi is a decentralized peer-to-peer network for permanent, immutable data storage. Data is encrypted before upload, stored using content-addressing, and paid for once at write time.

## How to build on Autonomi

You can build on Autonomi in several ways, from SDKs in more than 15 languages through a local daemon that exposes REST and gRPC, to direct CLI access, to native Rust with `ant-core`.

### Build an app with the SDKs

Use the SDKs if you want the easiest starting point for application development in Python, Node.js / TypeScript, Go, Rust, Java, C#, Kotlin, Swift, Ruby, PHP, Dart, Zig, and other supported languages.

`antd` runs on your machine as a local daemon and gives your application a stable REST and gRPC interface to the network.

Start with [Build with the SDKs](getting-started/install.md), then [Your First Upload with the SDKs](getting-started/hello-world.md).

### Use the ant CLI

Use the CLI when you want direct shell access for uploads, downloads, wallet checks, chunk operations, or node-management workflows.

Start with [Use the ant CLI](getting-started/using-ant-client.md).

### Build in Rust with ant-core

Build in Rust without the daemon when you want direct programmatic control over networking, uploads, and payments in your application.

Start with [Build in Rust with ant-core](getting-started/build-directly-in-rust.md).

## Core Concepts

- [Data Types](core-concepts/data-types.md)
- [Self-Encryption](core-concepts/self-encryption.md)
- [Payment Model](core-concepts/payment-model.md)
- [Post-Quantum Cryptography](core-concepts/post-quantum-cryptography.md)
- [Key Derivation](core-concepts/key-derivation.md)

## Reference

- [REST API](sdk-reference/rest-api.md)
- [SDK Overview](sdk-reference/overview.md)
- [CLI Command Reference](cli-reference/command-reference.md)
- [Rust Library Reference](cli-reference/ant-core-library.md)
- [MCP Server Reference](sdk-reference/mcp-server.md)

## Go Deeper

- [System Overview](architecture/system-overview.md)
- [GitHub](github.md)
