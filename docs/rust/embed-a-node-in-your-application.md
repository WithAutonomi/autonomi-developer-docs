# How to Embed a Node in Your Application

<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Use the `ant-node` API when your Rust application needs to own a node runtime directly.

## Prerequisites

- Rust 1.91 or later
- A Rust application that can own an async node task for the life of the process
- A rewards address for production node operation

## Steps

### 1. Add ant-node

Use the published `ant-node` crate from crates.io:

```toml
[dependencies]
ant-node = "=0.20.0"
tokio = { version = "1", features = ["full"] }
```

The crate enables its `logging` and `webrtc-direct` features by default. With `webrtc-direct`, the node also starts a WebRTC Direct listener for browser clients on a UDP port chosen by the operating system; set `config.webrtc_direct.enabled = false` if your application does not serve browsers. If you opt into `default-features = false`, add `features = ["logging"]` explicitly when you still want tracing output from the node runtime.

Test startup, events, and shutdown in an isolated environment before embedding the node in your application.

### 2. Build a node with the API

For local or development embedding, start from the development preset. This lifecycle example disables storage, so it does not need a rewards address or accept paid chunk writes.

```rust
use ant_node::{NodeBuilder, NodeConfig};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut config = NodeConfig::development();
    config.root_dir = "./embedded-node".into();
    config.storage.enabled = false;

    let mut node = NodeBuilder::new(config).build().await?;
    println!("Embedded node starting; press Ctrl+C to stop");
    node.run().await?;
    Ok(())
}
```

Expected output includes `Embedded node starting; press Ctrl+C to stop`. The process continues until it receives a shutdown signal.

### 3. Subscribe to node events

`RunningNode` exposes event subscriptions. This complete example keeps the event task alive while the node runs:

```rust
use ant_node::{NodeBuilder, NodeConfig, NodeEvent};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut config = NodeConfig::development();
    config.root_dir = "./embedded-node-events".into();
    config.storage.enabled = false;

    let mut node = NodeBuilder::new(config).build().await?;
    let mut events = node.subscribe_events();
    let event_task = tokio::spawn(async move {
        while let Ok(event) = events.recv().await {
            let is_shutting_down = matches!(&event, NodeEvent::ShuttingDown);
            println!("{event:?}");
            if is_shutting_down {
                break;
            }
        }
    });

    node.run().await?;
    event_task.await?;
    Ok(())
}
```

Expected output includes `Started` after the node begins running and `ShuttingDown` when it receives a shutdown signal.

### 4. Configure production settings explicitly

`NodeConfig::default()` is production-oriented and expects real rewards configuration. The config includes fields such as:

- `root_dir`
- `port`
- `ipv4_only`
- `bootstrap`
- `network_mode`
- `testnet`
- `upgrade`
- `payment.rewards_address`
- `payment.evm_network`
- `storage`
- `webrtc_direct`
- `close_group_cache_dir`
- `max_message_size`
- `log_level`

`payment.evm_network` can target `ArbitrumOne`, `ArbitrumSepolia`, or a private Ethereum Virtual Machine (EVM) with `Custom { rpc_url, payment_token_address, payment_vault_address }`.

Storage is enabled by default in both production and development configurations. Before building a storing node, set `payment.rewards_address` to a valid EVM address and configure `payment.evm_network` for the deployment the node joins. Set `storage.enabled = false` only for a non-storing embedded node such as the lifecycle examples above.

Treat that list as a practical overview rather than a complete contract. For the full config surface, see the [ant-node API](https://github.com/WithAutonomi/ant-node).

## Verify it worked

The node is running when `node.run().await?` starts successfully, the runtime binds to a port, and your event subscriber begins receiving node events.

## Common errors

**Missing rewards configuration in production mode**: The builder rejects production nodes without `payment.rewards_address`.

**Missing rewards configuration with storage enabled in development mode**: Development mode relaxes network restrictions, but storage initialization still needs `payment.rewards_address`. Configure it or disable storage for a non-storing node.

**Multiple identities under the default root**: Use an explicit `root_dir` if you do not want identity auto-discovery under the default node directory.

**Failed to create dual-stack network nodes**: The host has no working IPv6. Set `config.ipv4_only = true` before building the node.

**Node task blocks the rest of the app**: Put your application orchestration around the async node task instead of expecting `run()` to return immediately.

## Next steps

- [System Overview](../architecture/system-overview.md)
- [Deploy to Mainnet](../guides/deploy-to-mainnet.md)
- [Core Concepts Overview](../core-concepts/overview.md)
