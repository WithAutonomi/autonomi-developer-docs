# C# SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: e102df9b3ea1a17fba7cf731081f515d89552b82
  verified_date: 2026-06-10
  verification_mode: current-merged-truth
-->

The C# SDK is an async .NET 8 client for `antd` with both REST and gRPC transports.

## Install

```bash
cd antd-csharp
dotnet build Antd.sln
```

## Connect to the daemon

```csharp
using Antd.Sdk;

using var client = AntdClient.CreateRest(baseUrl: "http://localhost:8082");
var health = await client.HealthAsync();
Console.WriteLine(health.Network);
```

## Store and retrieve data

```csharp
using System.Text;
using Antd.Sdk;

using var client = AntdClient.CreateRest();
var result = await client.DataPutPublicAsync(Encoding.UTF8.GetBytes("Hello, Autonomi!"));
Console.WriteLine(result.Address);

var data = await client.DataGetPublicAsync(result.Address);
Console.WriteLine(Encoding.UTF8.GetString(data));
```

## Type mappings

| Autonomi type | C# type |
|------|------|
| `HealthStatus` | `HealthStatus` |
| `PutResult` | `PutResult` |
| Raw data | `byte[]` |

## Error handling

```csharp
try
{
    var data = await client.DataGetPublicAsync("nonexistent");
}
catch (NotFoundException)
{
    Console.WriteLine("Data not found");
}
catch (PaymentException)
{
    Console.WriteLine("Insufficient funds");
}
catch (AntdException ex)
{
    Console.WriteLine(ex.Message);
}
```

## Full API reference

For all available daemon endpoints, see the [REST API](../rest-api.md).
