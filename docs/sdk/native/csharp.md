# .NET SDK

Use `Autonomi.Ffi` to connect directly to the Autonomi Network from your .NET application. Your application loads the compiled network library through the `AntFfi` namespace; no separate daemon is required. This page is an installation and API reference for connection, retrieval, types, and errors, rather than a download walkthrough.

To manage networking outside your application instead, [start the local daemon](../start-the-local-daemon.md) and use its service-backed clients.

## Install

Use .NET development tools capable of targeting .NET 8. Create a console project and add the package:

```bash
dotnet new console --framework net8.0 --output NativeRead
dotnet add NativeRead/NativeRead.csproj package Autonomi.Ffi
```

The package contains the libraries your application loads, including the compiled network client. You do not need a Rust source build or a separate network service.

## Connection and retrieval API

Use `Client` from the `AntFfi` namespace. Asynchronous methods return `Task` or `Task<T>` without an `Async` suffix. Await connection before calling retrieval methods on the returned client.

| Method | Return type | Purpose |
|--------|-------------|---------|
| `Client.ConnectDefault(dataDir)` | `Task<Client>` | Connect using built-in public peers, with no payment wallet attached. |
| `client.DataGetPublic(addressHex)` | `Task<byte[]>` | Retrieve public content by its address. |
| `client.DataGetPrivate(dataMapHex)` | `Task<byte[]>` | Retrieve private content using its serialized DataMap. |
| `client.Dispose()` | `void` | Release the native client handle. |

Public retrieval does not require a wallet or payment. Dispose the client with `using`. Passing a directory string as `dataDir` changes the process-wide `HOME` environment variable; isolate the client in a separate process if your application needs a different home directory. The connection and retrieval methods listed here take no `CancellationToken`; see [client lifetime](../reference/native-sdks.md#client-lifetime).

## Type mappings

| Value | C# type | Format |
|-------|---------|--------|
| Public address (`addressHex`) | `string` | 64 hexadecimal characters, without `0x`. |
| Private DataMap (`dataMapHex`) | `string` | Hex-encoded serialized DataMap, not a public address or raw file bytes. |
| Retrieved content | `byte[]` | File content, not text decoded by the SDK. |

Keep a private DataMap secret and backed up: anyone who has it can retrieve the content.

## Errors

Catch `ClientException` around awaited client calls. Handle file-system exceptions separately if your application writes the returned bytes to disk.

- **Native library cannot load:** match your application's architecture to the [bundled platforms](../reference/native-sdks.md). No Linux musl-specific library is bundled.
- **Invalid address:** pass the full 64-character hexadecimal public address without `0x`, not a URL or a private DataMap.
- **Connection or retrieval fails:** check UDP connectivity and public peer availability. A network failure does not mean the file is missing.

## Full API reference

See the [Native SDK Reference](../reference/native-sdks.md) for file-download methods, storage methods, upload result fields, payment configuration, and external signing. The default read-only client is not configured for paid uploads.

## Related pages

- Other SDK languages include [Node.js](nodejs.md) and [Python](python.md).
- [Build with the SDKs](../install.md): compare direct libraries and service-backed clients.
