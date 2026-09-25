# C# SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the C# SDK to store and retrieve data through a local daemon, a background service called antd. The asynchronous client supports REST and gRPC.

## Install

Use .NET 8. Create a console project and add the [Autonomi.Antd package](https://www.nuget.org/packages/Autonomi.Antd) from NuGet:

```bash
dotnet new console --framework net8.0 --name AutonomiExample
cd AutonomiExample
dotnet add package Autonomi.Antd
```

The package provides the `Antd.Sdk` namespace used below. Replace the contents of `Program.cs` with an example and run it with `dotnet run`. Examples on this page use `Autonomi.Antd` 0.2 with antd 0.14.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```csharp
using System;
using Antd.Sdk;

try
{
    using var client = AntdClient.CreateRest(baseUrl: "http://localhost:8082");
    var health = await client.HealthAsync();
    Console.WriteLine($"antd version: {health.Version}");
}
catch (AntdException exception)
{
    Console.Error.WriteLine($"antd request failed: {exception.Message}");
    Environment.ExitCode = 1;
}
```

Expected output:

```text
antd version: <version>
```

## Store and retrieve data

Start **antd** in a write-enabled mode before you upload. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```csharp
using System;
using System.Linq;
using System.Text;
using Antd.Sdk;

try
{
    using var client = AntdClient.CreateRest();
    var payload = Encoding.UTF8.GetBytes("Hello, Autonomi!");
    var result = await client.DataPutPublicAsync(payload);
    Console.WriteLine($"Stored at: {result.Address}");

    var data = await client.DataGetPublicAsync(result.Address);
    if (!data.SequenceEqual(payload))
    {
        throw new InvalidOperationException("downloaded data did not match the upload");
    }
    Console.WriteLine($"Retrieved: {Encoding.UTF8.GetString(data)}");
}
catch (AntdException exception)
{
    Console.Error.WriteLine($"antd request failed: {exception.Message}");
    Environment.ExitCode = 1;
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello, Autonomi!
```

## Type mappings

| Autonomi type | C# type |
|------|------|
| `HealthStatus` | `HealthStatus` |
| `PutResult` | `PutResult` |
| Raw data | `byte[]` |

## Error handling

An address with no stored data throws `NotFoundException`, a subclass of `AntdException`.

```csharp
using System;
using Antd.Sdk;

try
{
    using var client = AntdClient.CreateRest();
    var missingAddress = new string('0', 64);
    await client.DataGetPublicAsync(missingAddress);
}
catch (NotFoundException)
{
    Console.WriteLine("No data is stored at that address");
}
catch (AntdException ex)
{
    Console.WriteLine(ex.Message);
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

External-signer finalize methods throw `PartialUploadException`, a subclass of `NetworkException`, when some chunks remain unstored; it carries `ChunksStored`, `ChunksFailed`, `TotalChunks`, `Retryable`, and `RetentionKnown`. When `Retryable` is `true`, repeating the same finalize call with the same upload ID stores the remainder without paying again; see the [external-signer guide](../../how-to-guides/use-external-signers-for-upload-payments.md) for the other cases.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).

## Related pages

For access without a local service, see the [native C# SDK](../../native/csharp.md). Its [Autonomi.Ffi package](https://www.nuget.org/packages/Autonomi.Ffi/0.0.9) does not provide the `Antd.Sdk` client API used here.
