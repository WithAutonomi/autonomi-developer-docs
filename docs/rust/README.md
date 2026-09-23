# Developing in Rust

<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

To store and retrieve data in Rust, use a client library that calls the local `antd` service or the `ant-core` library that connects directly to the Autonomi Network. Both libraries run in your application; the difference is which process handles the network connection.

## Choose how you'll work in Rust

### Rust client library for antd

Use `antd-client` when you want a separate background service, `antd`, to handle network access. Your application calls the Rust library, which sends requests to `antd` over REST or gRPC.

The Rust client library is included in the `ant-sdk v0.12.1` release source but is not published on crates.io. Use it only from a checkout pinned to the `ant-sdk v0.12.1` release commit. If you need an obtainable crates.io dependency, choose Direct Rust with `ant-core 0.8.1`.

Choose `antd-client` if you want:

- to keep the network connection in a separate local service
- to use the same REST or gRPC service as the other [antd client libraries](../sdk/reference/language-bindings/overview.md)

Not every SDK library uses `antd`: the [native libraries for Python, Node.js, and .NET](../sdk/native/README.md) connect directly from your application.

See [Rust client library](../sdk/reference/language-bindings/rust.md).

### Direct Rust with ant-core

Use `ant-core` to handle networking, uploads, and payment flows within your Rust application, without a separate `antd` service.

Choose Direct Rust with `ant-core` if you want:

- direct control over the Autonomi Network client in Rust
- no `antd` process between your code and the Autonomi Network
- access to Rust types, local devnet helpers, and client tuning such as loopback and timeout control

See [Build with Direct Rust](build-directly-in-rust.md) and [Rust Library Reference](library-reference.md).

## How the two Rust paths differ

| | `antd-client` | `ant-core` |
|---|---|---|
| Runs in | your application | your application |
| Network access | through `antd` | direct |
| Good fit | network access managed by a separate service | network access managed within your application |
| Installation | Pinned `ant-sdk v0.12.1` source checkout | `ant-core 0.8.1` from crates.io |

The local-development examples use `ant-core 0.8.0`, separately from the direct-network dependency. Keep the versions shown in those examples together rather than substituting `0.8.1`.

## Upstream sources

- [ant-sdk](https://github.com/WithAutonomi/ant-sdk)
- [ant-client](https://github.com/WithAutonomi/ant-client)

## Related pages

- [Build with Direct Rust](build-directly-in-rust.md)
- [Rust client library](../sdk/reference/language-bindings/rust.md)
- [Rust Library Reference](library-reference.md)
