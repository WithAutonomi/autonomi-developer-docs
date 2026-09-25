# SDK Overview

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

A software development kit (SDK) brings together libraries, tools, and examples for building applications. To store or retrieve data, your application usually imports a language library and calls its methods. Supporting tools, such as a local daemon, are separate programs you start when your integration needs them.

## What your application calls

Autonomi provides libraries for two connection arrangements. Both kinds of library run inside your application; the difference is where the connection to the Autonomi Network is managed.

| Library | How it works | Reference |
|---------|--------------|-----------|
| Direct-connection library | Includes a compiled network client that your application loads | [Native SDK Reference](native-sdks.md) |
| Client library for a local daemon | Sends requests to a separately running background service called `antd` | [Language Bindings](language-bindings/README.md) |

The packages and APIs differ. Use the installation instructions for the library you choose; installing a client library does not start a daemon.

## Connecting directly

```text
Your application
       |
       v
Language library and bundled network client
       |
       v
Autonomi Network
```

The compiled library is loaded by your application, not run as a separate command. Use the [Python SDK](../native/python.md), [Node.js SDK](../native/nodejs.md), or [.NET SDK](../native/csharp.md) reference for installation and language-specific usage.

## Connecting through a local daemon

```text
Your application
    |
    |  Client library or direct REST/gRPC calls
    v
+-----------------------------+
|            antd             |
| REST 127.0.0.1:8082         |
| gRPC 127.0.0.1:50051        |
+-----------------------------+
              |
              v
        Autonomi Network
```

Your application makes local API calls; the background service handles the connection to the Autonomi Network. Start it before making requests from a language client.

## Connection model

`antd` has no built-in authentication and listens only on the local machine by default:

- REST: `http://127.0.0.1:8082`
- gRPC: `127.0.0.1:50051`

Any process that can connect can call write, wallet, and local-filesystem endpoints. Keep both listeners on loopback unless you place access controls in front of them. Enabling Cross-Origin Resource Sharing (CORS) does not add authentication.

Some clients can discover antd automatically. See your [language reference](language-bindings/README.md) for connection options.

## API coverage

Use the [REST API](rest-api.md) to store and retrieve data and files, estimate costs, and manage upload payments.

The gRPC definitions cover health, data, chunks, files, uploads, wallet operations, signed quote verification, and events. The Event Service method completes immediately without events, so it is not a usable event subscription.

Health responses separate API liveness from network connectivity. `status: "ok"` means the API responds; `write_ready` reports a best-effort peer-count threshold, not wallet readiness or guaranteed storage. REST and gRPC expose the counts and the age of the last successful store-type operation. See [REST API](rest-api.md#health) for field meanings.

## Local-daemon client libraries

Choose a client in [Language Bindings](language-bindings/README.md). The Python and JavaScript clients install from PyPI and npm. Other languages have their own package or source-install instructions.

Do not assume feature parity. Bindings have language-specific constructors and expose different transport subsets. For example:

- JavaScript examples use `createClient()` from `@withautonomi/antd`
- Python examples use `AntdClient()` from `antd`
- some bindings implement both REST and gRPC, while others implement REST only
- gRPC prepare responses omit `total_chunks` and `already_stored_count`, which REST returns

Chunk writes return `PutResult`-style shapes with `cost` plus an address, but `cost` is an empty string because the write path does not return its prepaid cost. REST data writes return an address or `data_map` plus `chunks_stored` and the resolved `payment_mode_used`, which is `single` or `merkle`, not the requested `auto`. File uploads also return `storage_cost_atto` and `gas_cost_wei`.

For public direct writes, `antd` stores the DataMap in a separate operation after uploading the data chunks. Reported cost, gas, chunk count, and payment mode cover the data-chunk upload only; they exclude that separate DataMap store.

Cost endpoints such as `POST /v1/data/cost` and `POST /v1/files/cost` are advisory. They sample up to five chunk addresses, use the first live sampled price to extrapolate storage cost, and estimate gas without a live gas-price query. The write reconciles the amount actually due.

Use the binding-specific page when you need package names, constructors, or transport details.

## Upstream sources

- [ant-sdk](https://github.com/WithAutonomi/ant-sdk)

## Related pages

- [Build with the SDKs](../install.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Store Data on the Network](../store-data-on-the-network.md)
- [Use the Autonomi MCP Server](../../mcp/use-the-autonomi-mcp-server.md)
- [MCP Server Reference](../../mcp/mcp-server-reference.md)
- [REST API](rest-api.md)
- [gRPC Services](grpc-services.md)
- [Daemon Command Reference](daemon-command-reference.md)
