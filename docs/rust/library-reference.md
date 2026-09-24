# Rust Library Reference

<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: a954ec83bd1988a3a8e12c2a748db0d959922461
  verified_date: 2026-08-25
  verification_mode: current-merged-truth
-->

`ant-core` is the Direct Rust library for building on Autonomi without `antd`.

## Install

`ant-core 0.10.0` requires Rust 1.91 or later. For direct access to the Autonomi Network, use the released crate without local-development dependencies:

```toml
[dependencies]
ant-core = "=0.10.0"
tokio = { version = "1", features = ["full"] }
```

Retain your application's `Cargo.lock`: an exact `ant-core` version does not pin every dependency it uses.

The local examples below also enable the `devnet` feature, which provides `LocalDevnet` and adds `ant-node 0.20.0` as a dependency:

```toml
[dependencies]
ant-core = { version = "=0.10.0", features = ["devnet"] }
bytes = "1"
tempfile = "3"
tokio = { version = "1", features = ["full"] }
```

Install [Foundry](https://book.getfoundry.sh/getting-started/installation) and make `anvil` available on `PATH` before running a `LocalDevnet` example. `LocalDevnet` starts Anvil for local Ethereum Virtual Machine (EVM) payments.

For same-machine devnets or local testnets created outside `LocalDevnet`, set `ClientConfig { allow_loopback: true, ..ClientConfig::default() }` before `Client::connect`. Keep the default `false` when connecting to the Autonomi Network.

## Connect to the Autonomi Network

```rust
use ant_core::data::{Client, ClientConfig};
use std::net::SocketAddr;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let bootstrap_peer: SocketAddr = std::env::var("ANT_BOOTSTRAP_PEER")?.parse()?;
    let client = Client::connect(&[bootstrap_peer], ClientConfig::default()).await?;
    let _ = client;
    println!("Connected through {bootstrap_peer}");
    Ok(())
}
```

Set `ANT_BOOTSTRAP_PEER` to the address and port of one `quic` entry from the [bootstrap list shipped with `ant-core 0.10.0`](https://github.com/WithAutonomi/ant-client/blob/9112d683d8dbecffd8ad437546453f9f52310964/ant-core/resources/bootstrap_peers.toml), in `IP:PORT` form. An entry written as `/ip4/<IP>/udp/<PORT>/quic` becomes `<IP>:<PORT>`. Expected output:

```text
Connected through <IP:PORT>
```

To enable paid operations, attach a wallet:

```rust
use ant_core::data::{Client, ClientConfig, EvmNetwork, Wallet};
use std::net::SocketAddr;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let bootstrap_peer: SocketAddr = std::env::var("ANT_BOOTSTRAP_PEER")?.parse()?;
    let private_key = std::env::var("SECRET_KEY")?;
    let client = Client::connect(&[bootstrap_peer], ClientConfig::default()).await?;
    let wallet = Wallet::new_from_private_key(EvmNetwork::ArbitrumOne, &private_key)?;
    let address = wallet.address();
    let client = client.with_wallet(wallet);
    client.approve_token_spend().await?;
    println!("Wallet {address:?} is ready for paid operations");
    Ok(())
}
```

This sends a transaction on Arbitrum and grants the payment vault an unlimited token allowance. The approval needs ETH for Arbitrum gas; later storage payments need Autonomi Network Token (ANT). Use a funded wallet only when you intend to make that approval. Expected output after confirmation:

```text
Wallet <ADDRESS> is ready for paid operations
```

## Store and retrieve data

```rust
use ant_core::data::LocalDevnet;
use bytes::Bytes;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut devnet = LocalDevnet::start_small().await?;
    let client = devnet.create_funded_client().await?;

    let original = Bytes::from("hello Autonomi");
    let result = client.data_upload(original.clone()).await?;
    let private_copy = client.data_download(&result.data_map).await?;
    assert_eq!(private_copy, original);

    let public_address = client.data_map_store(&result.data_map).await?;
    let public_data_map = client.data_map_fetch(&public_address).await?;
    let public_copy = client.data_download(&public_data_map).await?;
    assert_eq!(public_copy, original);

    println!(
        "Stored {} chunks and retrieved the public DataMap at {public_address:?}",
        result.chunks_stored
    );
    devnet.shutdown().await?;
    Ok(())
}
```

Expected final output:

```text
Stored <number> chunks and retrieved the public DataMap at <ADDRESS>
```

## File operations

```rust
use ant_core::data::{LocalDevnet, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let temp = tempfile::tempdir()?;
    let input = temp.path().join("message.txt");
    let output = temp.path().join("message-copy.txt");
    tokio::fs::write(&input, b"hello from Direct Rust").await?;

    let mut devnet = LocalDevnet::start_small().await?;
    let client = devnet.create_funded_client().await?;

    let result = client
        .file_upload_public_with_mode(&input, PaymentMode::Auto)
        .await?;
    let address = result.data_map_address.ok_or_else(|| {
        std::io::Error::other("public upload did not return a DataMap address")
    })?;
    let data_map = client.data_map_fetch(&address).await?;
    client.file_download(&data_map, &output).await?;

    assert_eq!(tokio::fs::read(&output).await?, b"hello from Direct Rust");
    println!("Uploaded and retrieved {} chunks", result.chunks_stored);
    devnet.shutdown().await?;
    Ok(())
}
```

Expected final output:

```text
Uploaded and retrieved <number> chunks
```

## External signer flows

The Direct Rust library exposes both wave-batch and Merkle batch external payment helpers.

For in-memory wave-batch uploads, `data_prepare_upload` and `data_prepare_upload_with_visibility` prepare the upload and collect quotes, while `finalize_upload` stores the chunks after an external signer returns transaction hashes. Use `data_prepare_upload_with_visibility(content, Visibility::Public)` to bundle the DataMap chunk into the same payment batch and receive its Autonomi Network address in the `FileUploadResult` after finalize.

For files, `file_prepare_upload` and `file_prepare_upload_with_visibility` use `PaymentMode::Auto`. The returned `ExternalPaymentInfo` identifies whether the upload needs wave-batch or Merkle payment and therefore which finalize method to call. Use `file_prepare_upload_with_mode` when you need to select the payment mode explicitly.

For Merkle batches, `prepare_merkle_batch_external` and `finalize_merkle_batch` expose the low-level single-batch helpers, while `finalize_upload_merkle` completes a prepared upload from one winning pool hash. An upload larger than a single Merkle tree (256 fresh chunks, roughly 1 GiB) spans several batches: `prepare_merkle_batches_external` returns the batches to pay, and `finalize_upload_merkle_multi` completes the upload from a `Vec` of per-batch winner-hash entries aligned to those batches — one entry per batch, in order, with `None` marking a batch the signer did not pay. At least one batch must be paid, or the call returns a payment error; the chunks of an unpaid batch surface through the partial-upload error once the paid batches store. Progress-aware variants such as `file_prepare_upload_with_progress`, `finalize_upload_with_progress`, `finalize_upload_merkle_with_progress`, and `finalize_upload_merkle_multi_with_progress` are also available when you need UI feedback during long-running uploads.

When an external-signer upload pays successfully but some chunks miss quorum, the resumable finalize variants let you store the remainder against the same payment. `finalize_upload_resumable` for wave-batch payments and `finalize_upload_merkle_multi_resumable` for Merkle batch payments return a `FinalizeOutcome`: `Complete(FileUploadResult)` once every chunk is stored, or `Partial { result, resume }` when chunks remain. Pass the opaque `FinalizeResume` value from `Partial` to `finalize_resume` to retry only the unstored chunks without re-quoting, signing again, or paying again.

Bound calls to `finalize_resume`. A persistent storage failure returns `Partial` on every call instead of returning an error. The Merkle resumable method also requires every sub-batch to be paid. Use the non-resumable `finalize_upload_merkle_multi` when some sub-batches were not paid; it reports their chunks through `Error::PartialUpload`. Each resumable method also has a `_with_progress` variant that emits `UploadEvent::ChunkStored` events.

## Key types

| Type | Description |
|------|-------------|
| `ant_core::data::Client` | Main Autonomi Network client |
| `ant_core::data::ClientConfig` | Quote, Merkle batch store (`merkle_store_timeout_secs`, 270 s default), and chunk retrieve (`chunk_get_timeout_secs`) timeouts; concurrency limits; loopback policy. Non-Merkle chunk PUT response timeout is set by an internal `STORE_RESPONSE_TIMEOUT` constant, not via this struct. |
| `ant_core::data::PaymentMode` | `Auto`, `Merkle`, or `Single` |
| `ant_core::data::DataMap` | Private retrieval map for uploaded data |
| `ant_core::data::LocalDevnet` | Local development helper |
| `ant_core::data::Wallet` | EVM wallet used for paid operations |
| `ant_core::data::PreparedUpload` | Two-phase upload state used by external-signer flows |
| `ant_core::data::ExternalPaymentInfo` | External payment details for prepared uploads |
| `ant_core::data::PreparedMerkleBatch` | Prepared Merkle batch data for external signing |
| `ant_core::data::FinalizeOutcome` | Resumable finalize result: `Complete(FileUploadResult)` or `Partial { result, resume }` |
| `ant_core::data::FinalizeResume` | Opaque paid-material handle passed to `finalize_resume` after a partial finalize |
| `ant_core::data::Visibility` | Upload visibility: `Private` (DataMap returned to caller) or `Public` (DataMap bundled into the payment batch and stored on the Autonomi Network) |

## Prepare an external-signing request

This local example prepares and inspects a payment request. It stops before the external wallet signs or submits a transaction, so it does not pretend that an empty transaction map can finalize an upload.

```rust
use ant_core::data::{Client, ClientConfig, ExternalPaymentInfo, LocalDevnet};
use bytes::Bytes;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut devnet = LocalDevnet::start_small().await?;
    let config = ClientConfig {
        allow_loopback: true,
        ..ClientConfig::default()
    };
    let client = Client::connect(&devnet.bootstrap_addrs(), config)
        .await?
        .with_evm_network(devnet.evm_network().clone());
    let prepared = client.data_prepare_upload(Bytes::from("hello Autonomi")).await?;

    match &prepared.payment_info {
        ExternalPaymentInfo::WaveBatch { payment_intent, .. } => {
            println!("Need to pay {} atto", payment_intent.total_amount);
        }
        ExternalPaymentInfo::Merkle { prepared_batches, .. } => {
            println!("Merkle batches: {}", prepared_batches.len());
        }
    }

    devnet.shutdown().await?;
    Ok(())
}
```

The in-memory data preparation path uses wave-batch payment, so the expected output is:

```text
Need to pay <amount> atto
```

## Error handling

```rust
use ant_core::data::{Error, LocalDevnet};
use bytes::Bytes;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut devnet = LocalDevnet::start_small().await?;
    let client = devnet.create_funded_client().await?;

    match client.data_upload(Bytes::from("hello")).await {
        Ok(result) => println!("{}", result.chunks_stored),
        Err(Error::Payment(message)) => println!("{message}"),
        Err(Error::InsufficientPeers(message)) => println!("{message}"),
        Err(error) => println!("{error}"),
    }

    devnet.shutdown().await?;
    Ok(())
}
```

On success, this prints the positive number of stored chunks. The other branches show how to separate payment and peer-availability failures from other errors.

## Local development

The library also exports `LocalDevnet` for local development flows:

Enable the `ant-core` `devnet` feature before you use this section:

```toml
[dependencies]
ant-core = { version = "=0.10.0", features = ["devnet"] }
```

Confirm that `anvil --version` succeeds before running the example.

```rust
use ant_core::data::LocalDevnet;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut devnet = LocalDevnet::start_minimal().await?;
    let client = devnet.create_funded_client().await?;
    let _ = client;
    println!("LocalDevnet client is ready");
    devnet.shutdown().await?;
    Ok(())
}
```

Expected output includes `LocalDevnet client is ready`.

## Related pages

- [Developing in Rust](README.md)
- [Build with Direct Rust](build-directly-in-rust.md)
- [Rust SDK](../sdk/reference/language-bindings/rust.md)
