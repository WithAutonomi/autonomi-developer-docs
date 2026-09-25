# Store and Retrieve Data with the SDKs

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Store and retrieve your own public data, private data, and files using clients for a local daemon, a background service called antd. Use this arrangement to keep network access and upload payments outside your application process. For libraries that connect without that service, use the [native SDK API reference](../reference/native-sdks.md); do not substitute native calls into these client examples.

These are **independent recipes**, not a sequence to run from top to bottom. Choose the operation you need and replace sample payloads, addresses, DataMaps, and absolute file paths with your own values. For a guided first upload with one retained address and byte-for-byte read-back, use [Store Data on the Network](../store-data-on-the-network.md).

Featured examples on this page use cURL, Python, Node.js / TypeScript, and Rust. The [Language Bindings](../reference/language-bindings/overview.md) section lists API details and installation options for other languages.

## Prerequisites

- Your payload or an existing public address or private DataMap for a read.
- For file operations, a source file and an existing destination directory on the machine running antd.
- For paid writes, a low-value wallet with Autonomi Network Token (ANT) and ETH for transaction gas on the selected Arbitrum environment.

## Set up once

### 1. Open your client project

Reuse the project from the [read walkthrough](../retrieve-data-from-the-network.md) or [write walkthrough](../store-data-on-the-network.md) if you have one. Otherwise, follow [Install your client](../store-data-on-the-network.md#1-install-your-client): choose cURL, Python, Node.js / TypeScript, or the source-pinned Rust client. That setup includes the complete Cargo manifest and `protoc` requirement for Rust; `antd-client` is not installed from crates.io. Client installation does not install the antd executable.

Run your selected recipe as a complete program. Python recipes are complete `app.py` programs run with `python app.py` in the activated environment. TypeScript recipes are complete `app.ts` programs run with `npx tsx app.ts`. Rust recipes replace the example application's `src/main.rs` and run with `cargo run`. The cURL recipes are Bash scripts for macOS or Linux, not PowerShell; run each as `bash recipe.sh`.

### 2. Start the local service for your operation

Install and start antd using the OS-specific instructions in [Start the Local Daemon](../start-the-local-daemon.md). The clients here use `http://localhost:8082`. Reads need no wallet. For writes, stop a read-only instance and follow [Start antd with a payment wallet](../store-data-on-the-network.md#2-start-antd-with-a-payment-wallet), then inspect its configured wallet and balances with [Prepare a Wallet for Uploads](../../guides/prepare-a-wallet-for-uploads.md).

Use the built-in `EVM_NETWORK=arbitrum-one` or `arbitrum-sepolia` preset for the matching public environment. With antd 0.14.0, any individual override (`EVM_RPC_URL`, `EVM_PAYMENT_TOKEN_ADDRESS`, `EVM_PAYMENT_VAULT_ADDRESS`, or `EVM_DATA_PAYMENTS_ADDRESS`) selects custom payment encoding that mainnet storage nodes can reject after funds are spent. Remove all four; a custom RPC URL alone is not safe for public writes. Keep the unauthenticated service bound to loopback, not a public interface.

Assess your application's upload flow in the [local-development setup](../../guides/set-up-a-local-network.md) before committing funds on the public Autonomi Network. That setup supplies its own local payment configuration; do not replace it with the public-network settings.

Check `/health` before writing. `write_ready: false` signals degraded connectivity; `true` is a best-effort peer-count signal, not a wallet check or a guarantee of storage. `status: "ok"` alone only confirms that the API responds.

The readiness fields require `antd 0.12.1`. The [local-development setup](../../guides/set-up-a-local-network.md) uses `antd 0.12.0`, which omits them; a binding's default false or zero value is not a connectivity measurement.

### 3. Review cost and signing before a write

Use [Estimate Costs and Handle Upload Payments](../../guides/estimate-costs-and-handle-upload-payments.md) for your actual payload or file before running an upload recipe. Estimates are sampled, gas is advisory, and `/v1/data/cost` excludes the additional public DataMap storage. An estimate is not a maximum charge. A failed write can still spend funds; inspect its error and transaction history before retrying.

For signing outside antd, follow [Use External Signers for Upload Payments](use-external-signers-for-upload-payments.md), not these direct-wallet recipes. That guide covers client limitations and payment reconciliation before retrying a failed finalization.

## Recipes

### Store public data

Replace `Hello, Autonomi!` with the bytes your application intends to publish. A successful result contains a public address; persist it before doing anything else, then use the public-read recipe to retrieve those bytes. The sample payload still uses a paid upload API, not a free-write bypass.

**Before running:** anyone with the address can read the payload. Do not upload secrets. This call spends ANT and gas and can automatically grant the payment vault an unlimited ANT allowance when the existing allowance is too low.

{% tabs %}
{% tab title="cURL" %}

Use cURL 7.76+, `base64`, and `tr` in Bash:

```bash
set -euo pipefail
DATA_B64=$(printf 'Hello, Autonomi!' | base64 | tr -d '\n')

curl --fail-with-body -X POST http://localhost:8082/v1/data/public \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```
{% endtab %}
{% tab title="Python" %}
```python
from antd import AntdClient

try:
    client = AntdClient()
    result = client.data_put_public(b"Hello, Autonomi!")
except Exception as error:
    raise SystemExit(f"Upload failed: {error}") from error

print(result.address)
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
```typescript
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const result = await client.dataPutPublic(Buffer.from("Hello, Autonomi!"));
  console.log(result.address);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```
{% endtab %}
{% tab title="Rust" %}
```rust
use antd_client::{Client, DEFAULT_BASE_URL, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let result = client
        .data_put_public(b"Hello, Autonomi!", PaymentMode::Auto)
        .await?;

    println!("{}", result.address);
    Ok(())
}
```
{% endtab %}
{% endtabs %}

### Retrieve public data

Replace the address placeholder with your retained public address. This recipe reads existing data and makes no storage payment; it does not require the public-write recipe to run in the same session. The text output examples assume the original bytes are UTF-8; use a byte-oriented file write for binary content.

{% tabs %}
{% tab title="cURL" %}
```bash
set -euo pipefail
ADDRESS="<64_hex_address>"
curl --fail-with-body "http://localhost:8082/v1/data/public/$ADDRESS"
```
{% endtab %}
{% tab title="Python" %}
```python
from antd import AntdClient

try:
    client = AntdClient()
    data = client.data_get_public("<address>")
except Exception as error:
    raise SystemExit(f"Download failed: {error}") from error

print(data.decode())
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
```typescript
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const data = await client.dataGetPublic("<address>");
  console.log(data.toString());
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```
{% endtab %}
{% tab title="Rust" %}
```rust
use antd_client::{Client, DEFAULT_BASE_URL};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let data = client.data_get_public("<address>").await?;

    println!("{}", String::from_utf8_lossy(&data));
    Ok(())
}
```
{% endtab %}
{% endtabs %}

The REST response uses base64 in the `data` field. The Python, Node.js / TypeScript, and Rust SDKs decode it back into bytes.

### Store private data

Private uploads return a serialized DataMap, the secret retrieval information for your data. Keep it in protected application storage: anyone with the DataMap can retrieve the content, and losing it can mean losing access. The private operation returns it to you rather than publishing it as a public address. The examples display it so you can retain it; do not run them in a recorded terminal or send their output to shared logs.

**Before running:** private storage is still paid. This call spends ANT and gas and can automatically grant the payment vault an unlimited ANT allowance when the existing allowance is too low. Keep both the original private payload and returned DataMap out of source control and shared logs.

{% tabs %}
{% tab title="cURL" %}

Use cURL 7.76+, `base64`, and `tr` in Bash:

```bash
set -euo pipefail
DATA_B64=$(printf 'Secret message' | base64 | tr -d '\n')

curl --fail-with-body -X POST http://localhost:8082/v1/data \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```
Expected response shape:

```json
{
  "data_map": "<hex_encoded_datamap>",
  "chunks_stored": 3,
  "payment_mode_used": "single"
}
```
{% endtab %}
{% tab title="Python" %}
```python
from antd import AntdClient

try:
    client = AntdClient()
    result = client.data_put(b"Secret message")
except Exception as error:
    raise SystemExit(f"Upload failed: {error}") from error

data_map = result.data_map
print(data_map)
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
```typescript
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const result = await client.dataPut(Buffer.from("Secret message"));
  const dataMap = result.dataMap;
  console.log(dataMap);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```
{% endtab %}
{% tab title="Rust" %}
```rust
use antd_client::{Client, DEFAULT_BASE_URL, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let result = client.data_put(b"Secret message", PaymentMode::Auto).await?;

    let data_map = result.data_map;
    println!("{}", data_map);
    Ok(())
}
```
{% endtab %}
{% endtabs %}

The Python and Rust SDKs surface the DataMap through `DataPutResult.data_map`; the Node.js / TypeScript SDK uses `DataPutResult.dataMap`.

### Retrieve private data

Replace the placeholder with your retained DataMap in a protected local script, not a committed source file. This read does not spend funds. The examples display the recovered text; avoid shared logs and recorded terminals. For binary data, write bytes to a protected file rather than decoding as text.

{% tabs %}
{% tab title="cURL" %}
```bash
set -euo pipefail
DATA_MAP="<hex_encoded_datamap>"

curl --fail-with-body -X POST http://localhost:8082/v1/data/get \
  -H "Content-Type: application/json" \
  -d "{\"data_map\":\"$DATA_MAP\"}"
```
{% endtab %}
{% tab title="Python" %}
```python
from antd import AntdClient

try:
    client = AntdClient()
    data = client.data_get("<hex_encoded_datamap>")
except Exception as error:
    raise SystemExit(f"Download failed: {error}") from error

print(data.decode())
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
```typescript
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const data = await client.dataGet("<hex_encoded_datamap>");
  console.log(data.toString());
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```
{% endtab %}
{% tab title="Rust" %}
```rust
use antd_client::{Client, DEFAULT_BASE_URL};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let data = client.data_get("<hex_encoded_datamap>").await?;

    println!("{}", String::from_utf8_lossy(&data));
    Ok(())
}
```
{% endtab %}
{% endtabs %}

### Upload and download a file

These endpoints work on paths visible to the machine running antd. Replace both absolute paths with your source file and a new destination filename in an existing directory; do not choose a destination containing data you need to keep. Keep the source unchanged during this recipe. The comparison runs on the same machine as antd and checks the downloaded bytes against the original.

**Before running:** this recipe publishes the file, spends ANT and gas, and can automatically grant the payment vault an unlimited ANT allowance. Anyone with its public address can retrieve the file. Do not use a private document as the upload candidate.

{% tabs %}
{% tab title="cURL" %}

Use cURL 7.76+, Python 3 for JSON parsing, and `cmp` in Bash:

```bash
set -euo pipefail
FILE_RESPONSE=$(curl --fail-with-body --silent --show-error \
  -X POST http://localhost:8082/v1/files/public \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf"}')

printf '%s\n' "$FILE_RESPONSE"
FILE_ADDRESS=$(printf '%s' "$FILE_RESPONSE" \
  | python3 -c 'import json, sys; print(json.load(sys.stdin)["address"])')

curl --fail-with-body -X POST http://localhost:8082/v1/files/public/get \
  -H "Content-Type: application/json" \
  -d "{\"address\":\"$FILE_ADDRESS\",\"dest_path\":\"/absolute/path/to/downloaded-document.pdf\"}"
cmp /absolute/path/to/document.pdf /absolute/path/to/downloaded-document.pdf
printf 'File round-trip verified\n'
```
{% endtab %}
{% tab title="Python" %}
```python
from pathlib import Path

from antd import AntdClient

try:
    client = AntdClient()
    original = Path("/absolute/path/to/document.pdf").read_bytes()
    result = client.file_put_public("/absolute/path/to/document.pdf")
    print(result.address)
    client.file_get_public(result.address, "/absolute/path/to/downloaded-document.pdf")
    if Path("/absolute/path/to/downloaded-document.pdf").read_bytes() != original:
        raise ValueError("Downloaded file differs from the original")
except Exception as error:
    raise SystemExit(f"File round-trip failed: {error}") from error

print("File round-trip verified")
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
```typescript
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const original = await readFile("/absolute/path/to/document.pdf");
  const result = await client.filePutPublic("/absolute/path/to/document.pdf");
  console.log(result.address);
  await client.fileGetPublic(result.address, "/absolute/path/to/downloaded-document.pdf");
  assert.deepEqual(await readFile("/absolute/path/to/downloaded-document.pdf"), original);
  console.log("File round-trip verified");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```
{% endtab %}
{% tab title="Rust" %}
```rust
use antd_client::{Client, DEFAULT_BASE_URL, PaymentMode};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new(DEFAULT_BASE_URL);
    let original = std::fs::read("/absolute/path/to/document.pdf")?;
    let result = client
        .file_put_public("/absolute/path/to/document.pdf", PaymentMode::Auto)
        .await?;
    println!("{}", result.address);
    client
        .file_get_public(&result.address, "/absolute/path/to/downloaded-document.pdf")
        .await?;

    assert_eq!(std::fs::read("/absolute/path/to/downloaded-document.pdf")?, original);
    println!("File round-trip verified");
    Ok(())
}
```
{% endtab %}
{% endtabs %}

## Verify it worked

Public writes return a 64-character hexadecimal address. Private writes return a hex-encoded DataMap, not a public address. Neither result alone proves a complete round trip: retrieve and compare your original bytes, as demonstrated in [the first-upload walkthrough](../store-data-on-the-network.md#4-upload-once-retain-the-address-and-read-back). The file recipe performs that comparison and prints `File round-trip verified` only when it matches.

If a file download fails after upload, retain its printed address and retry only the download. Do not rerun the entire paid recipe to troubleshoot a read.

## Common errors

**400 Bad Request**: Check base64 encoding, address length, and local path values.

**402 Payment Required**: Inspect the payment error, selected EVM preset, ANT balance, gas balance, and allowance before retrying. A failed storage attempt can already have spent funds.

**503 Service Unavailable**: `antd` does not have a wallet key for a direct write. Restart it with `AUTONOMI_WALLET_KEY` or let `ant dev start` provision a local environment.

**404 Not Found during retrieval**: No data was found for the address or DataMap. Confirm it, and check `/health` for connected peers: without them, a lookup can also report not found.

## Next steps

- [Store Data on the Network](../store-data-on-the-network.md)
- [Prepare a Wallet for Uploads](../../guides/prepare-a-wallet-for-uploads.md)
- [REST API](../reference/rest-api.md)
- [SDK Overview](../reference/overview.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Native SDK API reference](../reference/native-sdks.md) for libraries without a local service
- [Use the CLI](../../cli/use-the-cli.md) for shell commands
- [Build Directly in Rust](../../rust/build-directly-in-rust.md) for Rust access without a local service
