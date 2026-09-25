# Retrieve Data from the Network

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Download a public image from the Autonomi Network without a wallet, a payment, or an address of your own. This walkthrough uses a local daemon, a background service called `antd`, so your application can request data without managing its own network connection.

For libraries that connect directly without this service, use the [Python SDK](native/python.md) or [Node SDK](native/nodejs.md). The steps here use cURL or a client for antd; [Language Bindings](reference/language-bindings/overview.md) covers other supported client languages.

## Steps

{% stepper %}
{% step %}
### Start the local service

Follow [Start the Local Daemon](start-the-local-daemon.md) through its installation, wallet-free startup, and connection check, choosing the instructions for your operating system. Return here once the first terminal shows `REST server listening on 127.0.0.1:8082` and the health response contains `"status": "ok"`.

Keep antd running in that same first terminal. If you already completed that guide, reuse the running service; do not start a second copy. The health response confirms the local API responds, while the download below tests retrieval from the Autonomi Network.
{% endstep %}
{% step %}
### Install your chosen client

In a second terminal, create a project directory. These two commands work in macOS/Linux shells and Windows PowerShell:

```sh
mkdir autonomi-read
cd autonomi-read
```

If you already have a project from another SDK guide, open its directory instead. Keep using that directory for installation, the example file, and the run command. Choose the same language tab in this step and the download step. These installations add application clients, not the antd executable.

{% tabs %}
{% tab title="cURL" %}
Use cURL to make HTTP requests without a language library. Check that it is available on macOS or Linux:

```bash
curl --version
```

On Windows, use PowerShell and the executable name `curl.exe`, not the `curl` alias:

```powershell
curl.exe --version
```

Expect a cURL version line. If the command is missing, [install cURL](https://curl.se/download.html) before continuing.
{% endtab %}
{% tab title="Python" %}
Use [Python 3.10 or later](https://www.python.org/downloads/). Create and activate a virtual environment so the client is installed only for this project.

On macOS or Linux:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'antd[rest]'
```

On Windows PowerShell:

```powershell
py -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
.\.venv\Scripts\Activate.ps1
if (-not $?) { throw 'Activation failed; use the virtual environment executable directly as described below.' }
python -m pip install 'antd[rest]'
```

If PowerShell blocks activation, do not change your system policy: use `.\.venv\Scripts\python.exe -m pip install 'antd[rest]'`, then `.\.venv\Scripts\python.exe download.py` for the run command. If you reopen a terminal, activate the environment again or use its Python executable directly.
{% endtab %}
{% tab title="Node.js / TypeScript" %}
Use [Node.js](https://nodejs.org/en/download) 18 or later with npm. Install the client and the tools to run the TypeScript file:

```bash
npm install @withautonomi/antd
npm install --save-dev @types/node tsx typescript
```

These commands also work in Windows PowerShell. npm creates the local package files for a new project; an existing project keeps its package settings.
{% endtab %}
{% tab title="Rust" %}
Install [Rust and Cargo](https://www.rust-lang.org/tools/install), [Git](https://git-scm.com/downloads), and [protoc](https://protobuf.dev/installation/) (the Protocol Buffers compiler). The client build needs protoc even when your application uses REST. Your Rust toolchain also needs your platform's linker and C/C++ build tools.

The `antd-client` crate is not published on crates.io. Use the exact `v0.12.1` source below; this client source pin is separate from the antd executable version. These setup commands use Bash or zsh on macOS/Linux:

```bash
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git ant-sdk
test "$(git -C ant-sdk rev-parse HEAD)" = "f9cd5c5fc08133847909e47e04af186593ccbaee" || exit 1
cargo init --bin --name autonomi-read .
```

In Windows PowerShell, use:

```powershell
git clone --branch v0.12.1 --depth 1 https://github.com/WithAutonomi/ant-sdk.git ant-sdk
if ($LASTEXITCODE -ne 0) { throw 'Source download failed.' }
if ((git -C ant-sdk rev-parse HEAD) -ne 'f9cd5c5fc08133847909e47e04af186593ccbaee') {
    throw 'Unexpected client source version.'
}
cargo init --bin --name autonomi-read .
if ($LASTEXITCODE -ne 0) { throw 'Project creation failed.' }
```

For a new project, replace `Cargo.toml` with the following complete file. For an existing Rust project, skip `cargo init` and add only these dependency entries, adjusting the source path if necessary. Keep the full cloned source tree: its `antd/proto` directory is required during compilation.

```toml
[package]
name = "autonomi-read"
version = "0.1.0"
edition = "2021"

[dependencies]
antd-client = { path = "ant-sdk/antd-rust" }
tokio = { version = "1", features = ["macros", "rt-multi-thread"] }
```
{% endtab %}
{% endtabs %}
{% endstep %}
{% step %}
### Download the example image

Use the supplied public address to save `autonomi-example.jpg` in your project directory. You do not need to upload anything first. The examples refuse to replace an existing file with that name; choose another output filename if needed.

{% tabs %}
{% tab title="cURL" %}
On macOS or Linux, run this in Bash or zsh. The `/stream` endpoint returns the image bytes directly:

```bash
ADDRESS="711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a"
if [ -e autonomi-example.jpg ] || [ -L autonomi-example.jpg ]; then
  printf 'autonomi-example.jpg already exists; choose another output name.\n' >&2
else
  curl --fail --show-error \
    "http://localhost:8082/v1/data/public/$ADDRESS/stream" \
    --output autonomi-example.jpg &&
    printf 'Saved autonomi-example.jpg\n'
fi
```

On Windows PowerShell:

```powershell
$address = '711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a'
if (Test-Path -LiteralPath autonomi-example.jpg) {
    throw 'autonomi-example.jpg already exists; choose another output name.'
}
curl.exe --fail --show-error "http://localhost:8082/v1/data/public/$address/stream" --output autonomi-example.jpg
if ($LASTEXITCODE -ne 0) { throw 'Download failed.' }
Write-Output 'Saved autonomi-example.jpg'
```
{% endtab %}
{% tab title="Python" %}
Create `download.py` in your project directory:

```python
from pathlib import Path

from antd import AntdClient

address = "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a"
output = Path("autonomi-example.jpg")

try:
    with AntdClient() as client:
        data = client.data_get_public(address)
    with output.open("xb") as image:
        image.write(data)
except Exception as error:
    raise SystemExit(f"Download failed: {error}") from error

print(f"Saved {len(data)} bytes to {output}")
```

Run it with the virtual environment active:

```bash
python download.py
```
{% endtab %}
{% tab title="Node.js / TypeScript" %}
Create `download.ts` in your project directory:

```typescript
import { writeFile } from "node:fs/promises";
import { createClient } from "@withautonomi/antd";

async function main() {
  const address = "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a";
  const output = "autonomi-example.jpg";
  const client = createClient();
  const data = await client.dataGetPublic(address);
  await writeFile(output, data, { flag: "wx" });
  console.log(`Saved ${data.length} bytes to ${output}`);
}

main().catch((error) => {
  console.error("Download failed:", error);
  process.exit(1);
});
```

Run it on macOS, Linux, or Windows PowerShell:

```bash
npx tsx download.ts
```
{% endtab %}
{% tab title="Rust" %}
Replace the new project's `src/main.rs` with this complete program:

```rust
use std::fs::OpenOptions;
use std::io::Write;

use antd_client::{Client, DEFAULT_BASE_URL};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let address = "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a";
    let output = "autonomi-example.jpg";
    let client = Client::new(DEFAULT_BASE_URL);
    let data = client.data_get_public(address).await?;

    let mut image = OpenOptions::new().write(true).create_new(true).open(output)?;
    image.write_all(&data)?;
    println!("Saved {} bytes to {}", data.len(), output);
    Ok(())
}
```

From the directory containing `Cargo.toml`, run:

```bash
cargo run
```
{% endtab %}
{% endtabs %}
{% endstep %}
{% step %}
### Open the image

Open `autonomi-example.jpg` from your project directory in an image viewer. You have downloaded a 138,931-byte JPEG from the Autonomi Network without configuring a wallet.

The Python, Node.js / TypeScript, and Rust programs print:

```text
Saved 138931 bytes to autonomi-example.jpg
```

cURL prints `Saved autonomi-example.jpg` after a successful download. If a download reports an error, do not treat any partial output file as complete; choose a new filename before retrying.
{% endstep %}
{% step %}
### Retrieve data at your own address

Replace the example's `address` value (`ADDRESS` in Bash) with a public data address supplied by a publisher or returned by an earlier upload. Choose an output filename and extension that match that content, then run the same command again. A public data address is 64 hexadecimal characters; it is not a wallet address or a raw chunk address.

For private content, you need the caller-held `DataMap` instead of a public address. Continue to [Build Read-Only Features](../guides/build-read-only-features.md) for that workflow.
{% endstep %}
{% endstepper %}

## What happened

Your application requested existing public content from the local service. `antd` fetched it from the Autonomi Network and returned the bytes; the storage payment was handled when the content was uploaded. Keep the first terminal running for more requests, or press Ctrl+C there to stop antd.

## Common errors

| Symptom | What to do |
|---|---|
| Connection refused or failed to connect | Check the first terminal: antd must still be running on `http://localhost:8082`. Wait for its API-listening message before retrying. A healthy local API does not guarantee that every public address is retrievable. |
| File already exists, `EEXIST`, or an output-name warning | Choose a new output filename in the example. The programs preserve your existing file. |
| `500 INTERNAL_ERROR` during retrieval | A missing public DataMap can return this error rather than not-found (or `INTERNAL` over gRPC). Inspect the error message and confirm the public data address with its publisher; not every internal error means missing data. See [REST API errors](reference/rest-api.md) for more detail. |

## Next steps

- [Build Read-Only Features](../guides/build-read-only-features.md)
- [Store Data on the Network](store-data-on-the-network.md)
- [Store and Retrieve Data with the SDKs](how-to-guides/store-and-retrieve-data.md)
- [REST API](reference/rest-api.md)
- [Python SDK](native/python.md) or [Node SDK](native/nodejs.md) for direct-library usage
- [Use the CLI](../cli/use-the-cli.md) for shell commands
- [Build Directly in Rust](../rust/build-directly-in-rust.md) for Rust access without a local service
