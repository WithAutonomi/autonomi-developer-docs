# Estimate Costs and Handle Upload Payments

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: fbf879b1f7068b5b072a936589721272c62f2ca0
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->

Use the `antd v0.14.0` REST API to inspect a wallet, request a sampled upload estimate, and understand the approval and payment-mode choices before an upload.

The examples use cURL to keep payment requests independent of binding-specific behavior. If you use a daemon-backed [SDK binding](../sdk/reference/language-bindings/overview.md), follow its installation instructions and test it against your target environment.

## Prerequisites

- The `antd v0.14.0` binary running on `http://127.0.0.1:8082`
- `curl` and Python 3 for the response checks below
- For wallet endpoints: `AUTONOMI_WALLET_KEY` configured when starting `antd`
- For public EVM environments: a funded wallet and the built-in `arbitrum-one` or `arbitrum-sepolia` preset

Cost estimation does not require a wallet or spend funds. Approval and upload operations make on-chain transactions and spend gas; uploads also spend ANT. Run them only in a controlled environment.

## Steps

### 1. Check the configured wallet

```bash
#!/usr/bin/env bash
set -euo pipefail

curl --fail --show-error http://127.0.0.1:8082/v1/wallet/address
curl --fail --show-error http://127.0.0.1:8082/v1/wallet/balance
```

Expected response shapes:

```json
{"address":"0x0123456789abcdef0123456789abcdef01234567"}
{"balance":"1000000000000000000","gas_balance":"1000000000000000"}
```

The wallet balance response returns token balance as atto tokens and gas balance as wei.

On public EVM networks, both values matter:

- ANT covers storage payment
- gas covers the transaction itself

### 2. Estimate storage cost without spending funds

The response contains a storage-cost estimate, file size, data-chunk count, heuristic gas estimate, and selected payment mode.

```bash
#!/usr/bin/env bash
set -euo pipefail

DATA_B64=$(printf 'Hello, Autonomi!' | base64 | tr -d '\n')

RESPONSE=$(curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data "{\"data\":\"${DATA_B64}\",\"payment_mode\":\"auto\"}" \
  http://127.0.0.1:8082/v1/data/cost)

python3 -c '
import json
import sys

response = json.loads(sys.argv[1])
required = {"cost", "file_size", "chunk_count", "estimated_gas_cost_wei", "payment_mode"}
missing = required.difference(response)
if missing:
    raise SystemExit(f"Missing fields: {sorted(missing)}")
print(json.dumps(response, indent=2))
' "$RESPONSE"
```

Expected output is a JSON object containing all five checked fields. Numeric payment values are decimal strings.

The estimate is not a quote for the complete public operation:

- storage pricing is extrapolated from at most five sampled chunk addresses
- `estimated_gas_cost_wei` is an advisory heuristic, not a live gas-oracle result
- `/v1/data/cost` counts the encrypted data chunks but not the additional paid `DataMap` storage performed by `POST /v1/data/public`, whose `chunks_stored` includes that DataMap chunk
- the final payment can differ because stored-chunk availability and prices can change

Do not use this response as a maximum charge or an exact balance requirement.

### 3. Estimate a public file

For a file on the same machine as `antd`, `/v1/files/cost` accepts `is_public`. `antd v0.14.0` approximates one additional `DataMap` chunk in this estimate. `POST /v1/files/public` pays for the data chunks and the DataMap chunk in one batch, so its `chunks_stored`, `storage_cost_atto`, and `gas_cost_wei` also include the DataMap chunk.

```bash
#!/usr/bin/env bash
set -euo pipefail

FILE_PATH=$(pwd)/upload-candidate.bin
printf 'Autonomi cost estimate\n' > "$FILE_PATH"
REQUEST=$(python3 -c '
import json
import sys

print(json.dumps({"path": sys.argv[1], "is_public": True, "payment_mode": "auto"}))
' "$FILE_PATH")

curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data "$REQUEST" \
  http://127.0.0.1:8082/v1/files/cost
```

Expected output contains the same five fields as the data-cost response. This remains a sampled estimate rather than the final amount paid.

### 4. Pre-approve token spend only when you intend to upload

`antd` exposes an endpoint for approving token spend before an upload. It sends an on-chain transaction, spends gas, and grants the configured payment vault an unlimited token allowance. Review the wallet address, EVM preset, token address, and vault address before running it.

This pre-approval is optional. Direct-wallet payments check the allowance and automatically grant the same unlimited allowance when it is too low. Use the endpoint only when you want approval to be a separate, deliberate transaction:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{}' \
  http://127.0.0.1:8082/v1/wallet/approve
```

The success response is:

```json
{"approved":true}
```

Do not interpret this response as proof that a later storage payment or upload will succeed.

### 5. Choose a payment mode

`antd` accepts three payment modes: `auto`, `merkle`, and `single`.

- `auto` is the default
- `merkle` forces Merkle batch payments
- `single` forces per-chunk payments

`merkle` batches payments to reduce transaction count for multi-chunk uploads. Forced Merkle payment requires at least two chunks. The mode reported by an estimate or upload response is the mode selected for that operation.

### 6. Validate paid uploads separately

Before enabling paid uploads, run a controlled test. Record the on-chain transactions, amount spent, selected payment mode, and returned address, then retrieve the data and compare its bytes with the original.

## Verify it worked

For the no-spend portion of this guide, confirm that the cost response contains all required fields. The cost endpoint does not submit a payment; do not use an unchanged wallet balance as the only check because unrelated on-chain activity can also change it.

## Common errors

**402 Payment Required**: The payment operation failed. Check the selected EVM preset, token balance, gas balance, allowance, and returned error before retrying. A failed storage attempt can still have spent funds.

**503 Service Unavailable**: A wallet endpoint or direct-wallet write was called without `AUTONOMI_WALLET_KEY`.

**400 Bad Request**: Check the base64 payload and use `auto`, `merkle`, or `single` for `payment_mode`.

**Binding import resolves to the wrong package**: Do not install `antd` from npm; that name belongs to Ant Design. The pub.dev package named `antd` is also unrelated; the Dart client is `antd_client`. Rust `antd-client` is absent from crates.io. Follow the [language-specific installation instructions](../sdk/reference/language-bindings/overview.md) instead of assuming a package name or version, or use cURL.

## Next steps

- [Start the Local Daemon](../sdk/start-the-local-daemon.md)
- [Prepare a Wallet for Uploads](prepare-a-wallet-for-uploads.md)
- [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
- [Use External Signers for Upload Payments](../sdk/how-to-guides/use-external-signers-for-upload-payments.md)
- [Build Read-Only Features](build-read-only-features.md)
- [REST API](../sdk/reference/rest-api.md)
