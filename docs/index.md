# Introduction

Autonomi is a decentralized peer-to-peer network for permanent, immutable data storage. Data is encrypted before upload, stored using content-addressing, and paid for once at upload.\
\
These guides will help you get started building with the Autonomi Network!

## How to build on Autonomi

You can build on Autonomi in four main ways: with the SDKs, through MCP-compatible AI tools, through the CLI, or directly in Rust.

### SDK

Use the SDKs if you want the simplest integration model for application development in Python, Node.js / TypeScript, Go, Rust, Java, C#, Kotlin, Swift, Ruby, PHP, Dart, Zig, and other supported languages.

`antd` runs on your machine and exposes REST and gRPC endpoints so your application can use a stable local interface to the network.

Start with [Build with the SDKs](getting-started/install.md), then [Start the Local Daemon](getting-started/using-the-autonomi-daemon.md), then [Retrieve Data from the Network](getting-started/retrieve-data-from-the-network.md), then [Store Data on the Network](getting-started/hello-world.md).

### MCP

Use MCP when you want AI tools such as Claude Desktop, Claude Code, or another MCP-compatible client to call Autonomi through structured tools. This path still uses `antd` under the hood, but the MCP server handles the bridge between your AI client and the daemon.

Start with [Use MCP with AI Tools](getting-started/use-mcp-with-ai-tools.md), then continue to [Use the Autonomi MCP Server](how-to-guides/use-the-mcp-server.md).

### CLI

[Use the CLI](getting-started/using-ant-client.md) when you want direct shell access for uploads, downloads, wallet checks, chunk operations, or node-management workflows.

### Direct Rust

Build in Rust without the daemon when you want direct programmatic control over networking, uploads, and payments in your application.

Start with [Build Directly in Rust](getting-started/build-directly-in-rust.md).

## Core Concepts

* [Data Types](core-concepts/data-types.md)
* [Keys, Addresses, and DataMaps](core-concepts/keys-addresses-and-datamaps.md)
* [Self-Encryption](core-concepts/self-encryption.md)
* [Payment Model](core-concepts/payment-model.md)
* [Post-Quantum Cryptography](core-concepts/post-quantum-cryptography.md)

## Reference

* [REST API](sdk-reference/rest-api.md)
* [SDK Overview](sdk-reference/overview.md)
* [MCP Server Reference](sdk-reference/mcp-server.md)
* [CLI Command Reference](cli-reference/command-reference.md)
* [Rust Library Reference](cli-reference/ant-core-library.md)

## Go Deeper

* [System Overview](architecture/system-overview.md)
* [GitHub](github.md)
