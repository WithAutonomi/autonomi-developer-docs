# Payment Model

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
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: fbf879b1f7068b5b072a936589721272c62f2ca0
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-protocol
  source_ref: main
  source_commit: 2bd604a88aaee8cf9a8bf60bf4e61268ed0d0581
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->

Autonomi uses a pay-once storage model. You pay in Autonomi Network Token (ANT) when you upload data, then retrieve it later without ongoing storage charges or download fees.

## Why it matters

You cannot treat uploads as fire-and-forget writes. [`antd`](../sdk/use-antd.md), the [CLI](../cli/use-the-cli.md), and [Direct Rust](../rust/README.md) all require wallet context for paid storage operations, and they differ in where they expose cost estimation, wallet approval, and payment-mode control.

## How it works

### Pay once on upload

Autonomi is designed around immutable storage rather than renewable storage leases. In practice, that means the payment event happens when you upload data. There are no recurring storage fees or separate retrieval payments.

### Wallet-backed writes

The tools use different wallet inputs:

- `antd` uses `AUTONOMI_WALLET_KEY` for direct-wallet uploads
- `ant` and `ant-core` use `SECRET_KEY` or an attached `Wallet`

Without wallet configuration, direct-wallet write endpoints fail. External-signer preparation endpoints can collect quotes without giving `antd` custody of the wallet key.

The OpenAPI description and `antd` runtime behavior are not fully aligned for public external-signer preparation. Follow [Use External Signers for Upload Payments](../sdk/how-to-guides/use-external-signers-for-upload-payments.md) for supported operations and known limitations before integrating this flow.

When you use the CLI or Direct Rust with `ant-core`, the client asks close peers for signed storage quotes, validates them, and uses them to construct the on-chain payment.

### Ethereum Virtual Machine network choices

The `ant` CLI exposes these Ethereum Virtual Machine (EVM) network values:

- `arbitrum-one`
- `arbitrum-sepolia`
- `local`

The `antd` external-signer flow also exposes the Remote Procedure Call (RPC) URL and payment contract addresses the signer needs to submit the transaction for the selected EVM network.

### Cost estimation

The `antd` surface exposes cost estimation explicitly:

- `POST /v1/data/cost`
- `POST /v1/files/cost`

Those endpoints return a structured estimate with cost, file size, chunk count, estimated gas, and the payment mode that would be used.

### Payment modes

The supported payment modes are:

| Mode | Behavior |
|------|------------------|
| `auto` | Choose Merkle batch payment for larger batches and single payments otherwise |
| `merkle` | Force Merkle batch payment |
| `single` | Force per-chunk payment |

In `ant-core`, the Merkle batch payment threshold is `64` chunks.

Nodes verify the payment proof that arrives with each write. That includes signature checks, on-chain payment verification, and record-level validation before content is accepted into the chunk store.

Node-side storage pricing follows `BASELINE + (n * n * K) / (D * D)`, where `n` is the `key_count` in the node's signed storage commitment, `K` is a fixed coefficient, and `D` is a fixed divisor. If no commitment is available, the node uses the non-zero baseline price. The client recomputes the expected price from the same committed key count before paying.

### What happens on retrieval

Downloads do not require a separate payment step. Payments are tied to storage writes such as storing data, chunks, or files.

## Practical example

Two payment patterns show up across `antd` and the CLI:

1. Estimate and upload through `antd`

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/cost \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"

curl -X POST http://localhost:8082/v1/data/public \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\",\"payment_mode\":\"merkle\"}"
```

2. Upload directly with `ant`

```bash
SECRET_KEY=0x... ant \
  --devnet-manifest /tmp/devnet.json \
  --allow-loopback \
  --evm-network local \
  file upload my_data.bin --public --merkle
```

In both examples, payment happens as part of the upload flow, but the `antd` example exposes explicit cost-estimation endpoints while the CLI example emphasizes direct upload flags and wallet setup.

## Related pages

- [Keys, Addresses, and DataMaps](keys-addresses-and-datamaps.md)
- [Prepare a Wallet for Uploads](../guides/prepare-a-wallet-for-uploads.md)
- [Estimate Costs and Handle Upload Payments](../guides/estimate-costs-and-handle-upload-payments.md)
- [Use External Signers for Upload Payments](../sdk/how-to-guides/use-external-signers-for-upload-payments.md)
- [Build Read-Only Features](../guides/build-read-only-features.md)
- [Data Types](data-types.md)
