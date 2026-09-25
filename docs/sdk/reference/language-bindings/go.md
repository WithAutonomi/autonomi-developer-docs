# Go SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Go SDK to store and retrieve data through a local daemon, a background service called antd. The client supports REST and gRPC and is available as a public Go module.

## Install

Use Go 1.25 or later. Create a module and add the client to it:

```bash
mkdir antd-go-example
cd antd-go-example
go mod init example.com/antd-quickstart
go get github.com/WithAutonomi/ant-sdk/antd-go
```

Examples on this page use module v0.14.0 with antd 0.14.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```go
package main

import (
    "context"
    "fmt"
    "log"

    antd "github.com/WithAutonomi/ant-sdk/antd-go"
)

func main() {
    client := antd.NewClient(antd.DefaultBaseURL)
    ctx := context.Background()

    health, err := client.Health(ctx)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println(health.OK)

    discoveredClient, url := antd.NewClientAutoDiscover()
    _ = discoveredClient
    fmt.Println(url)
}
```

Expected output:

```text
true
http://127.0.0.1:<port>
```

The SDK also includes a `GrpcClient` for the **antd** gRPC endpoint.

## Store and retrieve data

For upload examples in this section, start **antd** in a write-enabled mode first. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```go
package main

import (
    "context"
    "fmt"
    "log"

    antd "github.com/WithAutonomi/ant-sdk/antd-go"
)

func main() {
    client := antd.NewClient(antd.DefaultBaseURL)
    ctx := context.Background()

    result, err := client.DataPutPublic(
        ctx,
        []byte("Hello from Go!"),
        antd.PaymentModeAuto,
    )
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Stored at: %s\n", result.Address)

    data, err := client.DataGetPublic(ctx, result.Address)
    if err != nil {
        log.Fatal(err)
    }
    if string(data) != "Hello from Go!" {
        log.Fatal("downloaded data did not match the upload")
    }
    fmt.Printf("Retrieved: %s\n", data)
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello from Go!
```

## Type mappings

| Autonomi type | Go type |
|------|------|
| `HealthStatus` | `antd.HealthStatus` |
| `PutResult` | `antd.PutResult` for chunk writes |
| `DataPutPublicResult` | `antd.DataPutPublicResult` |
| `DataPutResult` | `antd.DataPutResult` |
| `FilePutPublicResult` | `antd.FilePutPublicResult` |
| `FilePutResult` | `antd.FilePutResult` |
| `PaymentMode` | `antd.PaymentMode` |
| `UploadCostEstimate` | `antd.UploadCostEstimate` |
| `WalletAddress` | `antd.WalletAddress` |
| `WalletBalance` | `antd.WalletBalance` |
| `PrepareUploadResult` | `antd.PrepareUploadResult` |
| `FinalizeUploadResult` | `antd.FinalizeUploadResult` |
| `PrepareChunkResult` | `antd.PrepareChunkResult` |
| Raw data | `[]byte` |

`PrepareChunkResult` is returned by `PrepareChunkUpload`. When `AlreadyStored` is `true`, only `Address` and `AlreadyStored` are populated and there is no payment to make or finalize call to issue. Otherwise, `UploadID`, `Payments`, and `TotalAmount` describe the external-signer payment required before calling `FinalizeChunkUpload`.

## Error handling

An address with no stored data returns `*antd.NotFoundError`. Match typed errors with `errors.As`.

```go
package main

import (
    "context"
    "errors"
    "fmt"

    antd "github.com/WithAutonomi/ant-sdk/antd-go"
)

func main() {
    client := antd.NewClient(antd.DefaultBaseURL)
    missingAddress := "0000000000000000000000000000000000000000000000000000000000000000"
    _, err := client.DataGetPublic(context.Background(), missingAddress)
    if err != nil {
        var notFound *antd.NotFoundError
        if errors.As(err, &notFound) {
            fmt.Println("No data is stored at that address")
            return
        }
        fmt.Println(err)
    }
}
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

External-signer finalize methods return `*antd.PartialUploadError` when some chunks remain unstored; it carries `ChunksStored`, `ChunksFailed`, `TotalChunks`, `Retryable`, and `RetentionKnown`. When `Retryable` is `true`, repeating the same finalize call with the same upload ID stores the remainder without paying again; see the [external-signer guide](../../how-to-guides/use-external-signers-for-upload-payments.md) for the other cases.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).
