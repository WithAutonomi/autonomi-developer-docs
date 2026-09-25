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

Use .NET 8 and reference the SDK project from the exact ant-sdk v0.12.1 release source. A separate [Autonomi.Antd 0.1.0 package](https://www.nuget.org/packages/Autonomi.Antd/0.1.0) is available on NuGet; the project-reference workflow below does not use that package.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
dotnet new console --framework net8.0 --name AutonomiExample
dotnet add AutonomiExample/AutonomiExample.csproj reference ant-sdk/antd-csharp/Antd.Sdk/Antd.Sdk.csproj
```

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

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `InternalException` for this behavior. The client source is pinned independently to `v0.12.1`.

```csharp
using System;
using Antd.Sdk;

try
{
    using var client = AntdClient.CreateRest();
    var missingAddress = new string('0', 64);
    await client.DataGetPublicAsync(missingAddress);
}
catch (InternalException)
{
    Console.WriteLine("Missing data returned an internal error");
}
catch (AntdException ex)
{
    Console.WriteLine(ex.Message);
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).

## Related pages

For access without a local service, see the [native C# SDK](../../native/csharp.md). Its [Autonomi.Ffi package](https://www.nuget.org/packages/Autonomi.Ffi/0.0.9) does not provide the `Antd.Sdk` client API used here.
