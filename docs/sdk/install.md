# Build with the SDKs

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Build applications that store and retrieve data on the Autonomi Network. The software development kits (SDKs) provide language libraries and supporting tools; your application calls the library for your language.

## Choose how your application connects

Both kinds of library run inside your application. Choose whether the library manages the network connection there or calls a separately running service.

| Connection | Choose it when | Installation and usage |
|------------|----------------|------------------------|
| Direct from your application | You want a language library with no separate network service to start | [Direct-connection libraries](native/README.md) |
| Through a local daemon | Several applications should share one service, or you prefer a local REST or gRPC API | [Local-daemon clients](use-antd.md) |

The packages and APIs differ. Use the package for the connection arrangement you choose; a Python or Node.js library for one is not interchangeable with the other.

## Libraries that connect directly

The package manager installs the language library and its compiled network client together. Import the library into your application; there is no separate executable to start.

| Language reference | Package |
|--------------------|---------|
| [Python SDK](native/python.md) | `ant-sdk` on PyPI; import `ant_ffi` |
| [Node.js SDK](native/nodejs.md), including TypeScript declarations | `@withautonomi/ant-sdk` on npm |
| [.NET SDK](native/csharp.md) | `Autonomi.Ffi` on NuGet; namespace `AntFfi` |

Each language reference covers installation and its API. Python and Node.js also include a complete public-file download example. For storage methods and payment setup, use the [Native SDK Reference](reference/native-sdks.md).

## Clients for a local daemon

A local daemon is a background service running separately on your computer. Autonomi's daemon, [antd](use-antd.md), manages the network connection and provides a local REST or gRPC API. Installing a client library does not install or start this service.

| Client | Package or setup |
|--------|------------------|
| cURL | Call the [REST API](reference/rest-api.md) without a language library |
| [Python](reference/language-bindings/python.md) | `antd[rest]` on PyPI |
| [JavaScript](reference/language-bindings/javascript.md) / [TypeScript](reference/language-bindings/typescript.md) | `@withautonomi/antd` on npm |
| [Rust](reference/language-bindings/rust.md) | `antd-client` from the source checkout in its installation instructions |
| Other languages | See [Language Bindings](reference/language-bindings/README.md) for package and source-install instructions |

The walkthroughs include client installation in matching language tabs:

- [Start the Local Daemon](start-the-local-daemon.md): install and run the service for your operating system.
- [Retrieve Data from the Network](retrieve-data-from-the-network.md): download a supplied public image without a wallet or payment.
- [Store Data on the Network](store-data-on-the-network.md): configure upload payments, store a public payload, and read it back.

## Public and private storage

Uploads require a wallet and storage payment. Choose public storage when you want to share a file by its address, or private storage when you want to keep its access information secret. See [Keys, Addresses, and DataMaps](../core-concepts/keys-addresses-and-datamaps.md) for how you retain access to each.

## Related pages

- [SDK How-To Guides](how-to-guides/README.md)
- [SDK Reference](reference/README.md)
- [Use the CLI](../cli/use-the-cli.md) for command-line access
- [Build Directly in Rust](../rust/build-directly-in-rust.md)
- [Build with AI Tools](../mcp/use-mcp-with-ai-tools.md)
