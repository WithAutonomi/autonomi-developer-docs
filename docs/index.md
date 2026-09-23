# What is Autonomi?

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
  source_repo: self_encryption
  source_ref: master
  source_commit: 4021f663612c5b963bef935b277eb65416b7d958
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-transport
  source_ref: main
  source_commit: 75a1e11e49872fa4ebe768d85f20ae3a8db9e91d
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Autonomi is a decentralized peer-to-peer network for encrypted, immutable storage. File uploads use self-encryption before the data leaves your device, and content addressing identifies the stored data. You pay once for storage, and downloads are free.

## What makes Autonomi different

At a high level, Autonomi gives you:

- Immutable storage, where changing the content produces a new address instead of mutating the old one.
- Client-side encryption through self-encryption for file uploads.
- Public and private retrieval through addresses and DataMaps.
- Pay-once storage, where you pay in Autonomi Network Token (ANT) when you upload and downloads are free.
- Post-quantum cryptography in the transport and security model.

## How you can build on Autonomi

Whether you want to retrieve data for free, upload files for immutable storage, or build a decentralized application, Autonomi provides several ways to get started.

### CLI

Use the command-line interface (CLI) to upload and download files, check your wallet, or manage nodes from a terminal.

Start with [Use the CLI](cli/use-the-cli.md).

### SDK

Store and retrieve data from your application using a language library. Autonomi's software development kits (SDKs) provide these libraries and supporting tools. The language references cover installation and usage, while the walkthroughs take you through retrieval and storage.

Some libraries connect directly to the Autonomi Network; others send requests to a local daemon, a separately running background service called [antd](sdk/use-antd.md).

Start with [Build with the SDKs](sdk/install.md).

### Direct Rust

Build directly in Rust when you want to manage networking, uploads, and downloads through the Rust library in your application.

Start with [Direct Rust](rust/README.md).

## Agent tools

Use Autonomi through an AI assistant. MCP provides tools the assistant can call; a skill provides instructions and workflows it can follow. You do not need both to get started.

Start with [Build with AI Tools](mcp/use-mcp-with-ai-tools.md) for prompt-led setup, skill installation, and help choosing your tools.

### MCP

Use the Model Context Protocol (MCP) server when you want an AI tool such as Claude Desktop, Claude Code, or another MCP-compatible client to interact with Autonomi through structured tools.

The MCP server uses a local daemon, a background service called [antd](sdk/use-antd.md), to connect to the Autonomi Network.

Follow [How to Use the MCP Server](mcp/use-the-autonomi-mcp-server.md).

### Autonomi skill

Give your AI assistant guidance on using the Autonomi Network, building applications, and running nodes. The Autonomi skill provides instructions for these tasks and does not require an MCP connection.

Install it from [Build with AI Tools](mcp/use-mcp-with-ai-tools.md#add-the-autonomi-skill), or explore the [skill repository](https://github.com/WithAutonomi/skills).

## Core concepts

- [Data Types](core-concepts/data-types.md)
- [Keys, Addresses, and DataMaps](core-concepts/keys-addresses-and-datamaps.md)
- [Self-encryption](core-concepts/self-encryption.md)
- [Payment Model](core-concepts/payment-model.md)
- [Post-Quantum Cryptography](core-concepts/post-quantum-cryptography.md)

## Go deeper

- [System Overview](architecture/system-overview.md)
- [Source Repositories](reference/source-repositories.md)
