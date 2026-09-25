# Deploy to Mainnet

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

Configure a mainnet-facing `antd` or direct CLI process without replacing the built-in Arbitrum One payment preset.

This guide covers read-only startup, wallet inspection, cost preflight, and optional pre-approval. Keep paid writes inside a controlled release test that records the amount spent and confirms retrieval of the uploaded bytes.

## Prerequisites

- The `antd v0.14.0` binary or [ant installed through npm or an operating-system installer](../cli/use-the-cli.md#install-the-cli)
- `curl`, Python 3, and a base64 command-line utility
- A process supervisor that keeps `antd` bound to loopback or another protected interface
- For wallet-backed `antd`: a low-value production wallet funded with ANT and gas

The `antd` examples below use REST directly. If you use a [language client](../sdk/reference/language-bindings/overview.md), follow its setup instructions and check compatibility with `antd v0.14.0`.

For the local daemon commands, set its executable path from the directory where you installed it:

```bash
export ANTD_BIN="$(pwd)/antd"
"$ANTD_BIN" --version
```

Expect `antd 0.14.0 (build dbf6a7d3d951)`. Set the same absolute path as `ANTD_BIN` in your process supervisor's environment. The scripts below use it rather than selecting a possibly different executable from `PATH`.

## Steps

### 1. Use the built-in Arbitrum One preset

Remove individual EVM overrides and select the built-in preset:

```bash
#!/usr/bin/env bash
set -euo pipefail

export EVM_NETWORK=arbitrum-one
unset EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS

printf 'Using EVM preset: %s\n' "$EVM_NETWORK"
```

Expected output:

```text
Using EVM preset: arbitrum-one
```

Do not set any individual `EVM_*` override for public writes with `antd v0.14.0`. Any one of those variables creates a custom EVM network. Mainnet storage nodes can reject that payment encoding after the wallet has spent ANT. `antd v0.14.0` has no safe documented public-write interface using a custom RPC URL.

### 2. Start a read-only mainnet-facing daemon

Keep the REST and gRPC listeners on loopback. `antd` has no built-in authentication.

```bash
#!/usr/bin/env bash
set -euo pipefail

unset AUTONOMI_WALLET_KEY EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS
export EVM_NETWORK=arbitrum-one

: "${ANTD_BIN:?Set ANTD_BIN to the absolute path of the installed antd executable}"
exec "$ANTD_BIN" \
  --rest-addr 127.0.0.1:8082 \
  --grpc-addr 127.0.0.1:50051 \
  --log-level info
```

Expected startup output identifies REST port `8082`, gRPC port `50051`, and network mode `default`. `antd v0.14.0` loads public bootstrap peers from installed configuration, or from the bootstrap list bundled into the release, when no explicit peers are supplied.

This process can serve reads without a wallet. Run it under your process supervisor rather than exposing its unauthenticated ports directly.

### 3. Verify the complete health response

```bash
#!/usr/bin/env bash
set -euo pipefail

HEALTH=$(curl --fail --show-error http://127.0.0.1:8082/health)

python3 -c '
import json
import sys

health = json.loads(sys.argv[1])
required = {
    "status",
    "network",
    "version",
    "evm_network",
    "uptime_seconds",
    "build_commit",
    "payment_token_address",
    "payment_vault_address",
    "write_ready",
    "connected_peers",
    "routing_table_size",
    "rebootstrap_threshold",
    "last_store_ok_secs_ago",
}
missing = required.difference(health)
if missing:
    raise SystemExit(f"Missing fields: {sorted(missing)}")
if (
    health["status"] != "ok"
    or health["network"] != "default"
    or health["version"] != "0.14.0"
):
    raise SystemExit(f"Unexpected health response: {health}")
if health["evm_network"] != "arbitrum-one":
    evm_network = health["evm_network"]
    raise SystemExit(f"Unexpected EVM preset: {evm_network}")
if not health["payment_token_address"] or not health["payment_vault_address"]:
    raise SystemExit("Mainnet payment contract addresses are missing")
print("Mainnet-facing antd health check passed")
' "$HEALTH"
```

Expected output:

```text
Mainnet-facing antd health check passed
```

This proves that the local process selected the intended configuration. `status: ok` means the process is alive, not that storage is available. Inspect `write_ready`, `connected_peers`, `routing_table_size`, and `rebootstrap_threshold` before attempting uploads. `last_store_ok_secs_ago` is `null` until this process observes a successful store. Even `write_ready: true` does not prove that payment, storage, or retrieval works against the deployed Autonomi Network.

### 4. Add a wallet only if the service must upload

Stop the read-only process through your process supervisor. Set the wallet key through its secret store, then start a replacement process with the same built-in preset:

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${AUTONOMI_WALLET_KEY:?Set AUTONOMI_WALLET_KEY through the process supervisor secret store}"
export AUTONOMI_WALLET_KEY

export EVM_NETWORK=arbitrum-one
unset EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS

: "${ANTD_BIN:?Set ANTD_BIN to the absolute path of the installed antd executable}"
exec "$ANTD_BIN" \
  --rest-addr 127.0.0.1:8082 \
  --grpc-addr 127.0.0.1:50051 \
  --log-level info
```

Expected startup output identifies REST port `8082`, gRPC port `50051`, and network mode `default`.

In another terminal, inspect the wallet:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl --fail --show-error http://127.0.0.1:8082/v1/wallet/address
curl --fail --show-error http://127.0.0.1:8082/v1/wallet/balance
```

The balance response contains ANT in `balance` and gas in `gas_balance`. Both are decimal strings in their smallest units.

### 5. Decide whether to pre-approve token spend

`POST /v1/wallet/approve` lets you approve token spend before an upload. It spends gas and grants the configured payment vault an unlimited ANT allowance. Direct-wallet payments also check the allowance and automatically grant the same unlimited allowance when it is too low.

Use pre-approval only when you want approval to be a separate, deliberate transaction. Do not automate it until you have independently checked the wallet address, `arbitrum-one` preset, payment token address, and payment vault address returned by `/health`.

The command is:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data '{}' \
  http://127.0.0.1:8082/v1/wallet/approve
```

The success response is `{"approved":true}`. It does not prove that a later payment, upload, or retrieval will succeed.

### 6. Run a no-spend cost preflight

Cost estimation queries storage prices but does not make a payment:

```bash
#!/usr/bin/env bash
set -euo pipefail

DATA_B64=$(printf 'mainnet deployment preflight' | base64 | tr -d '\n')

curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data "{\"data\":\"${DATA_B64}\",\"payment_mode\":\"auto\"}" \
  http://127.0.0.1:8082/v1/data/cost
```

Expected output contains `cost`, `file_size`, `chunk_count`, `estimated_gas_cost_wei`, and `payment_mode`.

The storage estimate samples at most five chunk addresses, the gas figure is heuristic, and this data endpoint omits the additional paid `DataMap` storage required by a public upload. Do not treat it as an exact or maximum charge.

### 7. Check the direct CLI separately

The CLI includes built-in bootstrap peers. You do not need a separate connection file for the npm installation; if you override the defaults, use real network contacts rather than example IP addresses.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${SECRET_KEY:?Set SECRET_KEY without writing it into this script}"
export SECRET_KEY

ant --evm-network arbitrum-one wallet address
ant --evm-network arbitrum-one wallet balance
```

Expected output is the wallet address followed by its ANT balance. The CLI does not report gas balance or expose approval as a separate command. Its upload path can approve an unlimited allowance automatically, so these checks do not establish the total gas needed for a first upload.

### 8. Gate the production write with a release test

Run the paid upload through a controlled release test before adding it to a production deployment. The test must record:

- the exact client and shipped dependency versions
- the selected built-in EVM preset and contract addresses
- token approval result
- estimated and actual ANT and gas spend
- returned 64-character public address
- successful retrieval and byte comparison
- any partial-upload error and funds already spent

### 9. Monitor the local service

Use the `antd` health and wallet endpoints directly:

```bash
#!/usr/bin/env bash
set -euo pipefail

curl -sf http://127.0.0.1:8082/health

if curl -sf http://127.0.0.1:8082/v1/wallet/address >/dev/null; then
  curl -sf http://127.0.0.1:8082/v1/wallet/balance
else
  printf 'antd is running without a configured wallet\n'
fi
```

Expected output is the health JSON followed by either wallet balance JSON or `antd is running without a configured wallet`.

## Verify it worked

The setup portion is complete when `/health` reports `status: ok`, `network: default`, and `evm_network: arbitrum-one`, and when the listeners remain protected from untrusted access.

Before production uploads, confirm the wallet address and balances, the built-in EVM preset and contract addresses, token approval, actual payment, successful storage, and retrieval of identical bytes through the controlled release test above. Record every item in its checklist, including any partial-upload error and funds already spent.

## Common errors

**503 on wallet or direct-write endpoints**: `antd` is running without `AUTONOMI_WALLET_KEY`. This is expected for read-only and external-signer processes.

**Direct CLI wallet check succeeds but upload fails**: The CLI does not report gas balance or expose approval as a separate command. A first upload can spend gas on automatic approval as well as payment, so do not infer upload readiness from address and ANT balance output.

**Median quote payment verification failed**: Stop retrying. Check whether ANT was already spent, remove every individual `EVM_*` override, and return to the built-in `arbitrum-one` preset.

**Unexpected local behavior**: Remove `--network local`, `--allow-loopback`, and devnet manifest flags from production commands.

## Next steps

- [Use the Daemon as a Local Service](../sdk/how-to-guides/use-the-daemon-as-a-local-service.md)
- [Estimate Costs and Handle Upload Payments](estimate-costs-and-handle-upload-payments.md)
- [Use External Signers for Upload Payments](../sdk/how-to-guides/use-external-signers-for-upload-payments.md)
