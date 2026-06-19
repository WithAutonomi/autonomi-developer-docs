# Use External Signers for Upload Payments

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: e56292325d04f1cf398c7e6bc77619ff2ab44447
  verified_date: 2026-06-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 4d0448458ec302af68a5504c533d105b0991c93c
  verified_date: 2026-06-19
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: 225acbb1af613193bcc8264b6ede4d7e4a7ac607
  verified_date: 2026-05-02
  verification_mode: current-merged-truth
-->

Use the two-phase upload flow when your application needs a wallet outside `antd` to sign and submit upload payments.

This is the right approach when:

- your users pay for their own uploads
- your app should not custody a wallet key for them
- you need to integrate with an external signer or wallet stack

## Prerequisites

- `antd` running without `AUTONOMI_WALLET_KEY` (see [Start the Local Daemon](../start-the-local-daemon.md))
- EVM configuration available to the daemon for the target network
- An external signer or wallet stack that can submit the required payment transactions

## Steps

### 1. Start antd without a wallet key

The daemon does not have an `--external-signer` flag. External-signer mode is the absence of `AUTONOMI_WALLET_KEY` plus the use of the prepare/finalize endpoints.

From the `ant-sdk/antd` build directory, run:

```bash
EVM_RPC_URL=https://your-rpc-endpoint \
EVM_PAYMENT_TOKEN_ADDRESS=0x... \
EVM_PAYMENT_VAULT_ADDRESS=0x... \
./target/release/antd
```

If `antd` is already on your `PATH`, replace `./target/release/antd` with `antd`.

Use `EVM_PAYMENT_VAULT_ADDRESS` for both wave-batch and Merkle uploads in the external-signer flow.

### 2. Prepare the upload

For a single chunk (up to 4 MiB of raw bytes), call `POST /v1/chunks/prepare`. This is the simplest external-signer flow — one chunk, one payment:

```bash
CHUNK_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/chunks/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$CHUNK_B64\"}"
```

When the chunk is already stored on the Autonomi Network, the response returns `already_stored: true` with the existing address and no `upload_id`. There is nothing more to do: no payment to make and no finalize call to issue. Otherwise the response returns the wave-batch payment shape:

```json
{
  "address": "<64_hex_chunk_address>",
  "already_stored": false,
  "upload_id": "<hex_id>",
  "payment_type": "wave_batch",
  "payments": [
    { "quote_hash": "0x...", "rewards_address": "0x...", "amount": "<atto_tokens>" }
  ],
  "total_amount": "<atto_tokens>",
  "payment_vault_address": "0x...",
  "payment_token_address": "0x...",
  "rpc_url": "https://your-rpc-endpoint"
}
```

After the external signer calls `payForQuotes()` with the returned `payments`, finalize with `POST /v1/chunks/finalize`:

```bash
curl -X POST http://localhost:8082/v1/chunks/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote_hash":"0xtx_hash"}}'
```

The finalize response returns the network address of the stored chunk. Requires antd 0.7.0 or later.

For multi-chunk uploads (arbitrary files or in-memory data larger than one chunk), use the data or file prepare/finalize endpoints described below.

For in-memory data, call `POST /v1/data/prepare`.

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

The in-memory data prepare endpoint accepts `"private"` (default) or `"public"` for `visibility`. When `"public"`, the serialized DataMap is bundled into the same external-signer payment batch and published on-network on finalize; the finalize response then includes a `data_map_address` field with its network address.

The prepare endpoints return a `payment_type` discriminator. Use that value to decide which on-chain call to make and which finalize payload to send back.

The daemon returns `wave_batch` for uploads under 64 chunks and `merkle` for uploads with 64 or more chunks.

Wave-batch prepare response:

```json
{
  "upload_id": "<hex_id>",
  "payment_type": "wave_batch",
  "payments": [
    {
      "quote_hash": "0x...",
      "rewards_address": "0x...",
      "amount": "<atto_token_amount>"
    }
  ],
  "total_amount": "<atto_token_amount>",
  "payment_vault_address": "0x...",
  "payment_token_address": "0x...",
  "rpc_url": "https://your-rpc-endpoint",
  "total_chunks": 12,
  "already_stored_count": 4
}
```

Merkle prepare response:

```json
{
  "upload_id": "<hex_id>",
  "payment_type": "merkle",
  "depth": 6,
  "pool_commitments": [
    {
      "pool_hash": "0x...",
      "candidates": [
        {
          "rewards_address": "0x...",
          "amount": "<atto_token_amount>"
        }
      ]
    }
  ],
  "merkle_payment_timestamp": 1744041600,
  "payment_vault_address": "0x...",
  "total_amount": "0",
  "payment_token_address": "0x...",
  "rpc_url": "https://your-rpc-endpoint",
  "total_chunks": 128,
  "already_stored_count": 0
}
```

Each `pool_commitments` entry contains exactly 16 candidate payments. The sample above shows one candidate for brevity.

Both prepare shapes also return `total_chunks` and `already_stored_count`. `total_chunks` is the full chunk count for the upload, including chunks already on the network; `already_stored_count` is how many were already stored and so excluded from payment and the PUT. Pay for `total_chunks - already_stored_count` chunks, and reconcile against the full file size when a prepare comes back cheaper than expected.

For file uploads, the equivalent is `POST /v1/upload/prepare` with a local `path` field instead of `data`. To make the upload publicly retrievable by address, add `"visibility":"public"` to the prepare request. `antd` bundles the serialized DataMap chunk into the same payment batch, and the finalize response includes a `data_map_address` field with its Autonomi Network address.

### 3. Submit the payment externally

Use your signer stack to submit the EVM payment transaction described by the prepare response.

`antd` does not sign or broadcast those transactions in this flow.

- For `wave_batch`, call `payForQuotes()` with the returned `payments` and keep the resulting transaction hashes keyed by `quote_hash`.
- For `merkle`, call `payForMerkleTree2()` with `depth`, `pool_commitments`, and `merkle_payment_timestamp`, then keep the `winner_pool_hash` from the `MerklePaymentMade` event.

Both calls use the `payment_vault_address` returned by the prepare step.

### 4. Finalize the upload

After the external payment is on-chain, call `POST /v1/upload/finalize` with the matching fields for the prepared upload.

Wave-batch finalize request:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

Merkle finalize request:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hash":"0x..."}'
```

Expected response shape:

```json
{
  "data_map": "<hex_encoded_datamap>",
  "address": "<64_hex_address_if_store_data_map_true>",
  "data_map_address": "<64_hex_address_if_visibility_public>",
  "chunks_stored": <chunk_count>
}
```

`address` is only present when `store_data_map` is `true`; that path stores the DataMap through `antd`'s configured wallet. Use it only when `antd` has a wallet key. `data_map_address` is only present when the upload was prepared with `visibility:"public"`; it is the Autonomi Network address of the DataMap chunk whose payment was included in the same external-signer batch.

### 5. Use SDK helpers when available

The language bindings for `antd` follow the same prepare/finalize split across both REST and gRPC transports. Merkle-capable bindings expose `payment_type` on prepare results and a `finalize_merkle_upload` helper for the Merkle path. For file and in-memory data uploads, gRPC `UploadService` exposes the full finalize surface, including `data_map`, `data_map_address`, and `store_data_map`. For single-chunk uploads, gRPC `ChunkService` exposes `PrepareChunk` and `FinalizeChunk`; `FinalizeChunk` returns the stored chunk address.

If you are building in Rust with ant-core instead of `antd`, the library exposes native external-payment helpers such as `data_prepare_upload`, `data_prepare_upload_with_visibility`, `file_prepare_upload`, `prepare_merkle_batch_external`, and `finalize_merkle_batch`. Use `data_prepare_upload_with_visibility(content, Visibility::Public)` to bundle the DataMap chunk into the payment batch for a public in-memory upload. Progress-aware variants such as `file_prepare_upload_with_progress`, `finalize_upload_with_progress`, and `finalize_upload_merkle_with_progress` are also available when you need UI feedback during long-running uploads.

## Verify it worked

Finalize succeeds when `antd` accepts the `upload_id` plus either the `tx_hashes` map or the `winner_pool_hash`, then returns upload metadata. Use the returned `data_map` for private retrieval. If you prepared with `visibility:"public"`, use the returned `data_map_address` for public retrieval.

## Common errors

**404 Not Found**: The `upload_id` is missing, expired, or already finalized.

**400 Bad Request**: Check whether the prepared upload expects `tx_hashes` or `winner_pool_hash`, and validate the hex formatting of those values.

**503 Service Unavailable**: You started `antd` in direct-wallet mode or without the required network configuration.

## Next steps

- [Prepare a Wallet for Uploads](../../guides/prepare-a-wallet-for-uploads.md)
- [Estimate Costs and Handle Upload Payments](../../guides/estimate-costs-and-handle-upload-payments.md)
- [REST API](../reference/rest-api.md)
- [Use the Daemon as a Local Service](use-the-daemon-as-a-local-service.md)
