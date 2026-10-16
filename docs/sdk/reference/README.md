# SDK Reference

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

<!-- verification:
  source_repo: ant-browser-sdk
  source_ref: v0.1.2
  source_commit: a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0
  verified_date: 2026-10-16
  verification_mode: target-manifest
-->

Find the methods, parameters, return values, and errors for the library or API you are using.

For native libraries that connect directly to the Autonomi Network, use the [native SDK reference](native-sdks.md). For web applications, [Browser SDK](../build-in-browser.md) introduces the separate experimental package and links to its API documentation. For client libraries that send requests to a local daemon, a separate background service called [antd](../use-antd.md), use [Language Bindings](language-bindings/README.md). The REST and gRPC references cover that service's APIs.

The APIs are not interchangeable. Each reference describes its own constructors, supported operations, and limits.

## Connection model

- [SDK Overview](overview.md): connection arrangements, service behavior, and API coverage.

## Direct-connection libraries

- [Native SDKs](../native/README.md): package choices and how the libraries connect.
- [Python SDK](../native/python.md): installation, a public-read example, types, and errors.
- [Node.js SDK](../native/nodejs.md): installation, a public-read example, types, and errors.
- [.NET SDK](../native/csharp.md): installation, methods, types, and errors.
- [Native SDK Reference](native-sdks.md): data, file, wallet, and external-signer APIs.

## Local service and clients

- [Local-Daemon Clients](../use-antd.md): service setup and client package choices.
- [REST API](rest-api.md)
- [gRPC Services](grpc-services.md)
- [Daemon Command Reference](daemon-command-reference.md)
- [Language Bindings](language-bindings/README.md)

## Next steps

- [Build with the SDKs](../install.md)
- [SDK How-To Guides](../how-to-guides/README.md)
