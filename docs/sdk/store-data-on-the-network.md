# Store Data on the Network

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Store a small public payload on the Autonomi Network, keep its address, and retrieve the same bytes. These examples use a local daemon, a background service called antd, to handle network access and upload payments separately from your application. For libraries that connect without a local service, use the [native SDK API reference](reference/native-sdks.md); their APIs differ from the clients in these tabs.

This is a **paid upload**, including when you use the sample text unchanged. To try a free read without configuring a wallet, use [Retrieve Data from the Network](retrieve-data-from-the-network.md).

## Prerequisites

- A low-value wallet you control, with Autonomi Network Token (ANT) and ETH for transaction gas on Arbitrum One.
- Your selected language runtime: Python 3.10+, Node.js 18+, or Rust with Cargo. The cURL tab lists its own command-line tools.

The shell setup commands on this page use **Bash on macOS or Linux**, not PowerShell. For OS-specific executable installation, including Windows, use [Start the Local Daemon](start-the-local-daemon.md). Assess your application's upload flow in the [local-development setup](../guides/set-up-a-local-network.md) before committing real funds.

## Steps

### 1. Install your client

Choose one tab. If you followed [Retrieve Data from the Network](retrieve-data-from-the-network.md), reuse that project and its installed client; do not create another project or reinstall it. Otherwise, open a working directory for your application and follow the selected setup.

These commands install a **client library**, not the antd executable. Other supported languages have [language-specific references](reference/language-bindings/overview.md). The Python and Node.js examples use `antd` client 0.2 with `antd` 0.14; the Rust example uses the `v0.12.1` client source.

{% tabs %}
{% tab title="cURL" %}

No SDK library is needed. Use cURL 7.76+ (`--fail-with-body` support), Python 3 for JSON/base64 conversion, and the standard `base64`, `tr`, and `cmp` utilities. Check that they are available:

```bash
curl --version
python3 --version
command -v base64 tr cmp
```

{% endtab %}
{% tab title="Python" %}

Create and activate a project-local environment, then install the REST client:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'antd[rest]'
```

Keep this environment active when you run `store.py`.

{% endtab %}
{% tab title="Node.js / TypeScript" %}

Install the client and the local tools that run TypeScript:

```bash
npm install @withautonomi/antd
npm install --save-dev @types/node tsx typescript
```

Use `@withautonomi/antd`, not the unrelated `antd` npm package. The example runs with `npx tsx store.ts` and does not require a module-setting change in an existing project.

{% endtab %}
{% tab title="Rust" %}

Install [Rust and Cargo](https://www.rust-lang.org/tools/install), Git, and [protoc](https://protobuf.dev/installation/), the Protocol Buffers compiler, with each on your `PATH`. Your Rust toolchain also needs your platform's linker and C/C++ build tools. The Rust client is source-only, not a crates.io dependency. Keep the full checkout: its build reads protocol files from the neighboring `antd/proto` directory.

From an empty application directory:

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee" || exit 1
cargo init --bin --name autonomi-example .
```

Use this `Cargo.toml` in your application directory:

```toml
[package]
name = "autonomi-example"
version = "0.1.0"
edition = "2021"

[dependencies]
antd-client = { path = "ant-sdk/antd-rust" }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```

For an existing project, add these dependencies rather than replacing its manifest, and adjust the relative source path. The client pin is independent of the antd executable version.

{% endtab %}
{% endtabs %}

### 2. Start antd with a payment wallet

Install the executable using [Start the Local Daemon](start-the-local-daemon.md). If you already have a read-only instance running, stop that instance with Ctrl+C in its terminal: setting a wallet variable in another terminal does not update a running service.

In a Bash terminal, open the directory containing your installed `antd` executable. Enter your wallet's hex-encoded private key at the hidden prompt, not in a command, source file, or shell history. The script selects the built-in Arbitrum One payment preset and starts antd on loopback ports:

```bash
set -euo pipefail
read -r -s -p 'Wallet private key (input hidden): ' AUTONOMI_WALLET_KEY
printf '\n'
: "${AUTONOMI_WALLET_KEY:?A wallet key is required for this paid example}"
export AUTONOMI_WALLET_KEY
export EVM_NETWORK=arbitrum-one
unset EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS
exec ./antd --rest-addr 127.0.0.1:8082 --grpc-addr 127.0.0.1:50051
```

Leave that terminal running and return to your application directory in another terminal. Startup identifies REST port `8082`, gRPC port `50051`, and network mode `default`. Keep the service local: antd has no built-in API authentication.

Do not add individual Ethereum Virtual Machine (EVM) overrides to this public-network setup. In antd 0.14.0, any of `EVM_RPC_URL`, `EVM_PAYMENT_TOKEN_ADDRESS`, `EVM_PAYMENT_VAULT_ADDRESS`, or `EVM_DATA_PAYMENTS_ADDRESS` selects custom payment encoding that mainnet storage nodes can reject **after funds have been spent**. Even a custom RPC URL is not a safe substitute for the built-in preset.

Follow [Prepare a Wallet for Uploads](../guides/prepare-a-wallet-for-uploads.md) to inspect the configured wallet address, ANT balance, and gas balance before uploading. A successful `/health` response means the API responds; `write_ready` measures connectivity, not funds or guaranteed storage. If you want to keep the signing key outside antd, use [external signers](how-to-guides/use-external-signers-for-upload-payments.md) instead of the paid examples below.

### 3. Review the cost before writing

Use [Estimate Costs and Handle Upload Payments](../guides/estimate-costs-and-handle-upload-payments.md#2-estimate-storage-cost-without-spending-funds) with the same `Hello, Autonomi!` payload before continuing. The released `/v1/data/cost` endpoint does not spend funds, but its sampled estimate is **not a spending limit**: it omits the additional public DataMap storage, and its gas estimate is advisory. Do not treat it as the exact final charge.

### 4. Upload once, retain the address, and read back

Each tab performs one public upload, records its address in `public-address.txt` before retrieval, then compares the retrieved bytes with the original payload. Run it in a directory where `public-address.txt` and the cURL output files do not already contain work you need to keep.

**Before running:** anyone with the returned public address can read this payload; do not replace it with secrets or personal data. The upload spends ANT and transaction gas, and can automatically grant the payment vault an **unlimited ANT allowance** if its allowance is too low. There is no separate confirmation prompt in the client call. Use only the intended low-value wallet, and do not assume unchanged sample text bypasses billing.

{% tabs %}
{% tab title="cURL" %}

Run this as `bash store.sh` in your application directory:

```bash
#!/usr/bin/env bash
set -euo pipefail

printf 'Hello, Autonomi!' > original.bin
DATA_B64=$(base64 < original.bin | tr -d '\n')

# Paid public write; may automatically approve unlimited ANT spend.
STORE_RESPONSE=$(curl --fail-with-body --silent --show-error \
  -X POST http://localhost:8082/v1/data/public \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}")
ADDRESS=$(printf '%s' "$STORE_RESPONSE" \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["address"])')
printf '%s\n' "$ADDRESS" > public-address.txt
printf 'Stored at: %s\n' "$ADDRESS"

curl --fail-with-body --silent --show-error \
  "http://localhost:8082/v1/data/public/$ADDRESS" \
  | python3 -c 'import base64, json, sys; sys.stdout.buffer.write(base64.b64decode(json.load(sys.stdin)["data"], validate=True))' \
  > retrieved.bin
cmp original.bin retrieved.bin
printf 'Round-trip verified: 16 bytes match\n'
```

{% endtab %}
{% tab title="Python" %}

Create `store.py` in your project and run `python store.py` with its environment active:

```python
from pathlib import Path

from antd import AntdClient

try:
    with AntdClient() as client:
        original = b"Hello, Autonomi!"
        # Paid public write; may automatically approve unlimited ANT spend.
        result = client.data_put_public(original)
        Path("public-address.txt").write_text(result.address + "\n", encoding="utf-8")
        print(f"Stored at: {result.address}")
        retrieved = client.data_get_public(result.address)
        if retrieved != original:
            raise ValueError("Retrieved bytes differ from the original")
        print(f"Round-trip verified: {len(retrieved)} bytes match")
except Exception as error:
    raise SystemExit(f"Round-trip failed: {error}") from error
```

{% endtab %}
{% tab title="Node.js / TypeScript" %}

Create `store.ts` in your project and run `npx tsx store.ts`:

```typescript
import assert from "node:assert/strict";
import { writeFile } from "node:fs/promises";
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const original = Buffer.from("Hello, Autonomi!");
  // Paid public write; may automatically approve unlimited ANT spend.
  const result = await client.dataPutPublic(original);
  await writeFile("public-address.txt", `${result.address}\n`);
  console.log(`Stored at: ${result.address}`);
  const retrieved = await client.dataGetPublic(result.address);
  assert.deepEqual(retrieved, original);
  console.log(`Round-trip verified: ${retrieved.length} bytes match`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

{% endtab %}
{% tab title="Rust" %}

Put this program in your application's `src/main.rs`, then run `cargo run` from the directory containing `Cargo.toml`:

```rust
use antd_client::{Client, DEFAULT_BASE_URL, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let original = b"Hello, Autonomi!";
    // Paid public write; may automatically approve unlimited ANT spend.
    let result = client.data_put_public(original, PaymentMode::Auto).await?;
    std::fs::write("public-address.txt", format!("{}\n", result.address))?;
    println!("Stored at: {}", result.address);
    let retrieved = client.data_get_public(&result.address).await?;
    assert_eq!(retrieved, original);
    println!("Round-trip verified: {} bytes match", retrieved.len());
    Ok(())
}
```

{% endtab %}
{% endtabs %}

Expected output:

```text
Stored at: <64-character hexadecimal address>
Round-trip verified: 16 bytes match
```

Keep `public-address.txt` to retrieve the payload in later sessions. If retrieval fails after the address is recorded, retry the read using that address, not the whole upload program. A failed write can also have spent funds: inspect its error and payment history before attempting another write.

## What happened

antd self-encrypted your payload, stored its chunks and public DataMap on the Autonomi Network, and returned the address needed to read it. Your application retained that address and checked the returned bytes against the original, rather than treating an address or a healthy API as proof of a successful round trip. REST carries binary data as base64 inside JSON; the language clients handle that conversion for you.

## Next steps

- [Store and Retrieve Data with the SDKs](how-to-guides/store-and-retrieve-data.md) for independent public, private, and file recipes
- [Retrieve Data from the Network](retrieve-data-from-the-network.md) for later reads without another upload
- [Prepare a Wallet for Uploads](../guides/prepare-a-wallet-for-uploads.md)
- [REST API](reference/rest-api.md)
- [SDK Overview](reference/overview.md)
- [Native SDK API reference](reference/native-sdks.md) for libraries without a local service
- [Use the CLI](../cli/use-the-cli.md) for shell commands
- [Build Directly in Rust](../rust/build-directly-in-rust.md) for Rust access without a local service
