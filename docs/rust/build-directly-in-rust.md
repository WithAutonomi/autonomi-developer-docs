# Build with Direct Rust

<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Choose Direct Rust when you want your application to talk to the Autonomi Network without using `antd`. This interface gives your application direct access to networking, uploads, and downloads through `ant-core`.

This guide uses `ant-core 0.8.0` for local development. Keep that version for this example: `ant-core 0.8.1` uses a different node dependency. See the [Rust Library Reference](library-reference.md) for the direct-network dependency.

## Prerequisites

- Rust toolchain
- [Foundry](https://book.getfoundry.sh/getting-started/installation) with `anvil` available on `PATH`
- A new or existing Rust application

To connect through a local background service instead, see [Use a Local Daemon](../sdk/use-antd.md) and [Start the Local Daemon](../sdk/start-the-local-daemon.md). For shell access instead of writing Rust code, see [Use the CLI](../cli/use-the-cli.md).

## Steps

### 1. Create a Rust app and add ant-core

```bash
cargo new autonomi-rust-app
cd autonomi-rust-app
anvil --version
```

The final command must print an Anvil version before you continue. `LocalDevnet` starts an Anvil process for local Ethereum Virtual Machine (EVM) payments.

Update `Cargo.toml`:

```toml
[dependencies]
ant-core = { version = "=0.8.0", features = ["devnet"] }
bytes = "1"
tokio = { version = "1", features = ["full"] }
```

### 2. Start a local devnet and upload data from Rust

Replace `src/main.rs` with:

```rust
use ant_core::data::LocalDevnet;
use bytes::Bytes;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut devnet = LocalDevnet::start_small().await?;
    let client = devnet.create_funded_client().await?;

    let original = Bytes::from("Hello from Rust!");
    let result = client.data_upload(original.clone()).await?;
    let downloaded = client.data_download(&result.data_map).await?;

    assert_eq!(downloaded, original);
    println!("Stored {} chunks", result.chunks_stored);

    devnet.shutdown().await?;
    Ok(())
}
```

### 3. Run the app

```bash
cargo run
```

On success, the final output includes `Stored <number> chunks`. The exact number depends on self-encryption, but it is greater than zero.

This example starts a local development network for Autonomi, creates a funded Rust client with local payment approval already in place, uploads a payload, downloads it again, and shuts the devnet down.

## What happened

Your Rust application used Direct Rust through `ant-core`, without `antd` or a CLI wrapper. `ant-core` started a local devnet, created a client funded by the local Anvil chain, handled self-encryption and local payment, and gave you direct access to the upload and download results in Rust.

## Next steps

- [Developing in Rust](README.md)
- [Rust Library Reference](library-reference.md)
- [Rust SDK](../sdk/reference/language-bindings/rust.md)
