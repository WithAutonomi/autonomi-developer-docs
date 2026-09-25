# Prepare a Wallet for Uploads

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

Configure wallet access for `antd`, understand what the direct CLI can inspect, and avoid payment settings that mainnet storage nodes reject.

This guide covers wallet inputs shared across SDK, CLI, and Direct Rust work. Treat a wallet as upload-ready only after a paid write/read test succeeds in an approved environment. A direct-wallet upload can grant an unlimited allowance automatically when the existing allowance is too low.

If you want to understand public addresses and `DataMap` handling rather than upload wallets, see [Keys, Addresses, and DataMaps](../core-concepts/keys-addresses-and-datamaps.md).

## Start with your environment

The practical difference between environments is:

| Environment | Wallet state |
|------|--------------|
| Local devnet | `ant-dev 0.1.0` provisions a wallet and local balances; test the workflow in an isolated environment |
| Arbitrum Sepolia | Use a test wallet funded with test ANT and test gas |
| Arbitrum One | Use a production wallet funded with real ANT and gas |

If you are only building read-only features, you do not need any of this wallet setup.

## Prerequisites

- The `antd v0.14.0` binary or [ant installed through npm or an operating-system installer](../cli/use-the-cli.md#install-the-cli)
- A hex-encoded private key you control when you are not using a local devnet
- A low-value wallet suitable for the environment you selected
- `curl` for the `antd` wallet checks
- An understanding that approval and uploads make on-chain transactions and spend gas

For the local daemon commands, set its executable path from the directory where you installed it:

```bash
export ANTD_BIN="$(pwd)/antd"
"$ANTD_BIN" --version
```

Expect `antd 0.14.0 (build dbf6a7d3d951)`. Keep that variable in the shell or process environment used for the startup scripts below.

## Steps

### 1. Choose the wallet interface

The tools accept these wallet inputs:

- `antd` -> `AUTONOMI_WALLET_KEY`
- `ant` -> `SECRET_KEY`
- Direct Rust with `ant-core` -> an attached `Wallet`

The interfaces do not provide the same checks:

- `antd` reports the wallet address, ANT balance, and gas balance, and exposes an unlimited token-approval operation.
- The direct CLI reports the wallet address and ANT balance only. It does not report gas balance or expose token approval.
- Direct Rust exposes wallet and approval primitives. Validate its complete paid write/read flow against the production Autonomi Network before production use.

Use the external-signer flow when `antd` should not hold the private key.

### 2. Start antd with a built-in EVM preset

Set `AUTONOMI_WALLET_KEY` outside your shell history, then select the built-in preset. `arbitrum-one` is also the `antd v0.14.0` default, but setting it explicitly makes the intended payment environment visible.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${AUTONOMI_WALLET_KEY:?Set AUTONOMI_WALLET_KEY without writing it into this script}"
export AUTONOMI_WALLET_KEY

export EVM_NETWORK=arbitrum-one
unset EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS

: "${ANTD_BIN:?Set ANTD_BIN to the absolute path of the installed antd executable}"
exec "$ANTD_BIN" --rest-addr 127.0.0.1:8082 --grpc-addr 127.0.0.1:50051
```

Expected startup output identifies REST port `8082`, gRPC port `50051`, and network mode `default`.

For testnet, replace `arbitrum-one` with `arbitrum-sepolia` and use a testnet-funded key.

Do not set `EVM_RPC_URL`, `EVM_PAYMENT_TOKEN_ADDRESS`, `EVM_PAYMENT_VAULT_ADDRESS`, or `EVM_DATA_PAYMENTS_ADDRESS` for a public-network write with `antd v0.14.0`. Any one of those variables switches `antd` to custom payment encoding. Mainnet storage nodes can reject that encoding after ANT has been spent. `antd v0.14.0` therefore has no safe documented interface for combining a custom RPC URL with public writes.

### 3. Inspect the antd wallet

Run these commands in another terminal after `antd` starts:

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

The values are decimal strings. `balance` is measured in atto tokens and `gas_balance` is measured in wei.

These checks establish which wallet `antd` holds and what balances its RPC provider reports. They do not prove that the wallet has approved the correct vault or that a storage write will succeed.

### 4. Pre-approve the payment vault when you intend to upload

`antd` offers an optional pre-approval operation. Direct-wallet payments also check the allowance and automatically grant an unlimited allowance when it is too low. Use this endpoint only when you want approval to be a separate transaction:

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

This transaction spends gas and grants the built-in payment vault an unlimited ANT allowance. Confirm the wallet address, `EVM_NETWORK` preset, and low-value balance before running it. The command is not a readiness check: a successful approval does not prove that payment, storage, or retrieval will succeed.

### 5. Inspect a direct CLI wallet

The direct CLI uses `SECRET_KEY` and a built-in EVM preset.

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${SECRET_KEY:?Set SECRET_KEY without writing it into this script}"
export SECRET_KEY

ant --evm-network arbitrum-one wallet address
ant --evm-network arbitrum-one wallet balance
```

Expected output is an EVM address followed by the ANT balance as an integer. The CLI does not print gas balance.

The CLI has no separate wallet-approval command. Its direct-wallet payment path can approve an unlimited allowance automatically when the existing allowance is too low, which means the first upload may spend gas on both approval and payment. Address and ANT balance checks do not show whether you have enough gas or an existing allowance; the CLI does not expose either as a separate preflight check.

### 6. Keep signing outside antd when needed

Run `antd` without `AUTONOMI_WALLET_KEY` and select a built-in EVM preset:

```bash
#!/usr/bin/env bash
set -euo pipefail

unset AUTONOMI_WALLET_KEY EVM_RPC_URL EVM_PAYMENT_TOKEN_ADDRESS EVM_PAYMENT_VAULT_ADDRESS EVM_DATA_PAYMENTS_ADDRESS
export EVM_NETWORK=arbitrum-one

: "${ANTD_BIN:?Set ANTD_BIN to the absolute path of the installed antd executable}"
exec "$ANTD_BIN" --rest-addr 127.0.0.1:8082 --grpc-addr 127.0.0.1:50051
```

Expected startup output identifies REST port `8082`, gRPC port `50051`, and network mode `default`.

`antd` returns the preset RPC URL and contract addresses during prepare operations. Your external wallet or signer submits the transaction. Wallet address and balance endpoints return 503 in this mode because no wallet is attached to `antd`.

Use the external-signer flow only in an approved test environment until prepare, payment, finalize, and read-back all succeed against the production Autonomi Network. Do not treat `antd` startup as proof that the complete flow works.

## Verify it worked

For `antd`, verify that the wallet address and both balances match the wallet you intended to use. If you approve token spend, record the approval transaction and confirm it targets the vault from the selected built-in preset.

For the direct CLI, an address and ANT balance check is not enough to establish upload readiness because gas balance and allowance are not exposed.

A complete upload-readiness test requires an approved paid write followed by retrieval and byte comparison. Treat the wallet as not upload-ready until that test succeeds.

## Common errors

**503 Service Unavailable**: A wallet endpoint or direct-wallet write was called without `AUTONOMI_WALLET_KEY`. External-signer mode intentionally leaves `antd` without a wallet.

**Custom EVM configuration on a public network**: Remove every individual `EVM_*` override and use `EVM_NETWORK=arbitrum-one` or `EVM_NETWORK=arbitrum-sepolia`. Do not retry a paid operation after a custom-payment verification failure without checking whether funds were already spent.

**Unsupported local CLI wallet command**: `ant wallet` with `--evm-network local` requires a devnet manifest containing EVM settings.

**Invalid key format**: Check for whitespace or truncated hex. The direct CLI accepts the `0x` prefix; `ant-dev` strips that prefix before passing its generated local key to `antd`.

## Next steps

- [Start the Local Daemon](../sdk/start-the-local-daemon.md)
- [Estimate Costs and Handle Upload Payments](estimate-costs-and-handle-upload-payments.md)
- [Use External Signers for Upload Payments](../sdk/how-to-guides/use-external-signers-for-upload-payments.md)
- [Build Read-Only Features](build-read-only-features.md)
- [Keys, Addresses, and DataMaps](../core-concepts/keys-addresses-and-datamaps.md)
