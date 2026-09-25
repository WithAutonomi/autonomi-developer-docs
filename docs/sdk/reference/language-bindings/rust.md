# Rust SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Rust binding to store and retrieve data through a local daemon, a background service called antd. The asynchronous client supports REST and gRPC.

## Install

The `antd-client` crate is not published on crates.io for ant-sdk v0.12.1. Use the exact release source as a local Cargo dependency.

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee"
```

Add the binding and Tokio runtime to your application's `Cargo.toml`:

```toml
[package]
name = "autonomi-example"
version = "0.1.0"
edition = "2021"

[dependencies]
antd-client = { path = "../ant-sdk/antd-rust" }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

Adjust the relative path if your application and the cloned source have a different parent directory.

## Connect to antd

Follow [Start the Local Daemon](../../start-the-local-daemon.md) to run antd before connecting.

```rust
use antd_client::{discover_daemon_url, Client, DEFAULT_BASE_URL};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let base_url = discover_daemon_url().unwrap_or_else(|| DEFAULT_BASE_URL.to_string());
    let client = Client::new(&base_url);
    let health = client.health().await?;
    println!("antd version: {}", health.version);
    Ok(())
}
```

Expected output:

```text
antd version: <version>
```

For gRPC, the crate also exports `GrpcClient` and `DEFAULT_GRPC_ENDPOINT`.

Both transports expose `write_ready`, `connected_peers`, `routing_table_size`, `rebootstrap_threshold`, and `last_store_ok_secs_ago` on `HealthStatus`. `write_ready` is a best-effort connectivity signal, not proof that a wallet is configured or an upload will succeed. See [REST health diagnostics](../rest-api.md) for their meanings.

These diagnostics require `antd 0.12.1`. With older versions, including the [local-development setup](../../../guides/set-up-a-local-network.md), the binding substitutes false or zero for missing readiness fields. Those defaults do not measure connectivity.

## Store and retrieve data

For upload examples in this section, start **antd** in a write-enabled mode first. The public Autonomi Network requires [wallet and Ethereum Virtual Machine (EVM) payment configuration](../../../guides/prepare-a-wallet-for-uploads.md). A local development network created with [`ant dev start`](../../../guides/set-up-a-local-network.md) includes that configuration.

```rust
use antd_client::{Client, DEFAULT_BASE_URL, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);

    let health = client.health().await?;
    assert!(health.ok);

    let result = client
        .data_put_public(b"Hello from Rust!", PaymentMode::Auto)
        .await?;
    println!("Stored at: {}", result.address);

    let data = client.data_get_public(&result.address).await?;
    assert_eq!(data, b"Hello from Rust!");
    println!("Retrieved: {}", String::from_utf8_lossy(&data));
    Ok(())
}
```

Expected output:

```text
Stored at: <64-character hexadecimal address>
Retrieved: Hello from Rust!
```

## Type mappings

| Autonomi type | Rust type |
|------|------|
| `HealthStatus` | `antd_client::HealthStatus` |
| `PutResult` | `antd_client::PutResult` for chunk writes |
| `DataPutPublicResult` | `antd_client::DataPutPublicResult` |
| `DataPutResult` | `antd_client::DataPutResult` |
| `FilePutPublicResult` | `antd_client::FilePutPublicResult` |
| `FilePutResult` | `antd_client::FilePutResult` |
| `PaymentMode` | `antd_client::PaymentMode` |
| `UploadCostEstimate` | `antd_client::UploadCostEstimate` |
| `WalletAddress` | `antd_client::WalletAddress` |
| `WalletBalance` | `antd_client::WalletBalance` |
| `PrepareUploadResult` | `antd_client::PrepareUploadResult` |
| `FinalizeUploadResult` | `antd_client::FinalizeUploadResult` |
| Raw data | `Vec<u8>` or `&[u8]` |

## Error handling

`antd v0.13.0` reports a missing DataMap as an internal error instead of not found. Handle `AntdError::Internal` for this behavior. The client source is pinned independently to `v0.12.1`.

```rust
use antd_client::{AntdError, Client, DEFAULT_BASE_URL};

#[tokio::main]
async fn main() {
    let client = Client::new(DEFAULT_BASE_URL);

    let missing_address = "0000000000000000000000000000000000000000000000000000000000000000";

    match client.data_get_public(missing_address).await {
        Ok(data) => println!("{}", data.len()),
        Err(AntdError::Internal(_)) => println!("Missing data returned an internal error"),
        Err(error) => println!("{error}"),
    }
}
```

Output when the valid address is not stored:

```text
Missing data returned an internal error
```

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md). To connect without a local service using `ant-core`, see [Developing in Rust](../../../rust/README.md).
