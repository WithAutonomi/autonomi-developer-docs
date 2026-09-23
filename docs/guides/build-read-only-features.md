# Build Read-Only Features

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Retrieve existing public or private data without configuring a wallet or an upload payment flow.

This guide covers read-only retrieval through the `antd` REST API and CLI. For application code, see [SDK retrieval](../sdk/retrieve-data-from-the-network.md) or [Direct Rust](../rust/build-directly-in-rust.md). SDK client package versions are independent of antd; follow the [language-specific installation instructions](../sdk/reference/language-bindings/overview.md).

## Why this matters

Read-only features have fewer security and operational requirements than upload-enabled features.

If your application only reads data that has already been written to the Autonomi Network:

- you do not need ANT
- you do not need gas
- you do not need a wallet
- you do not need upload permissions

This keeps retrieval-only tools, dashboards, and content browsers separate from wallet keys and token approvals.

## Prerequisites

- A 64-character public address, or a hex-encoded `DataMap` for private data
- For REST: the `antd v0.13.0` binary running on `http://127.0.0.1:8082`
- For CLI: `ant-cli v0.3.6` with a valid bootstrap configuration
- A known copy of the expected content if you want to verify its bytes

You do not need `AUTONOMI_WALLET_KEY`, `SECRET_KEY`, ANT, gas, or token approval for these retrieval operations.

## Steps

### 1. Retrieve public data through antd

The streaming endpoint writes the decrypted bytes directly instead of returning a base64 field inside JSON.

Set `ADDRESS` to a real public address, then run:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${ADDRESS:?Set ADDRESS to a 64-character public address}"

curl --fail --show-error \
  "http://127.0.0.1:8082/v1/data/public/${ADDRESS}/stream" \
  --output downloaded.bin

test -s downloaded.bin
printf 'Downloaded %s bytes\n' "$(wc -c < downloaded.bin)"
```

Expected output:

```text
Downloaded <non-zero number> bytes
```

### 2. Retrieve private data through antd

Keep the `DataMap` private. It contains the material needed to locate and decrypt the content.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${DATA_MAP:?Set DATA_MAP to the hex-encoded DataMap}"

curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data "{\"data_map\":\"${DATA_MAP}\"}" \
  http://127.0.0.1:8082/v1/data/stream \
  --output downloaded-private.bin

test -s downloaded-private.bin
printf 'Downloaded %s bytes\n' "$(wc -c < downloaded-private.bin)"
```

Expected output:

```text
Downloaded <non-zero number> bytes
```

The buffered endpoints, `GET /v1/data/public/{address}` and `POST /v1/data/get`, instead return JSON with the content encoded as base64 in the `data` field.

### 3. Retrieve a file with the CLI

The `ant-cli v0.3.6` installer writes `bootstrap_peers.toml` to the standard `ant` configuration directory. If you built the CLI from source, configure real bootstrap peers before using this command. Do not replace that configuration with example IP addresses.

Public retrieval:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${ADDRESS:?Set ADDRESS to a 64-character public address}"

ant file download "$ADDRESS" --output downloaded.bin
test -s downloaded.bin
```

Private retrieval:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${DATA_MAP_FILE:?Set DATA_MAP_FILE to a local .datamap file}"

ant file download --datamap "$DATA_MAP_FILE" --output downloaded-private.bin
test -s downloaded-private.bin
```

Expected output includes `Download complete!`, the output filename, its size, and elapsed time.

### 4. Keep wallet setup out of read-only applications

If your application only reads data that has already been stored, omit:

- `AUTONOMI_WALLET_KEY`
- `SECRET_KEY`
- token approvals
- upload payment flows

Add wallet configuration only when the application also uploads.

## Verify it worked

Compare the downloaded bytes with a known copy:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${EXPECTED_FILE:?Set EXPECTED_FILE to the known original file}"

cmp "$EXPECTED_FILE" downloaded.bin
printf 'Downloaded content matches the expected file\n'
```

Expected output:

```text
Downloaded content matches the expected file
```

## Common errors

**400 Bad Request**: A public address must be exactly 64 hexadecimal characters, and a private `DataMap` must be valid hex-encoded serialized data.

**500 Internal Server Error for missing data**: `antd v0.13.0` reports an absent public `DataMap` as `INTERNAL_ERROR` instead of not found. Check that the address identifies stored public data before treating other 500 responses as retryable service failures.

**No bootstrap peers**: Restore the `ant-cli v0.3.6` installer's `bootstrap_peers.toml` or provide real bootstrap peers from an approved source.

**Private retrieval without a DataMap**: Private content requires the caller-held `DataMap`, even though the storage payment has already happened.

## Next steps

- [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
- [Payment Model](../core-concepts/payment-model.md)
- [Use the CLI](../cli/use-the-cli.md)
