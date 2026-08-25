# Use External Signers for Upload Payments

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
  source_commit: a954ec83bd1988a3a8e12c2a748db0d959922461
  verified_date: 2026-08-25
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: evmlib
  source_ref: main
  source_commit: fbf879b1f7068b5b072a936589721272c62f2ca0
  verified_date: 2026-08-19
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

The daemon starts uploads of 64 or more chunks on the Merkle path and smaller uploads on the wave-batch path, but that initial selection is not final. A large upload can still come back as `wave_batch`: the already-stored preflight can leave fewer than 64 chunks to pay for, and too few reachable Merkle-capable peers also switches the preparation to wave-batch. Branch on the returned `payment_type`, not on the chunk count you submitted.

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
  "merkle_batches": [
    {
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
      "merkle_payment_timestamp": 1744041600
    }
  ],
  "payment_vault_address": "0x...",
  "total_amount": "0",
  "payment_token_address": "0x...",
  "rpc_url": "https://your-rpc-endpoint",
  "total_chunks": 128,
  "already_stored_count": 0
}
```

Each `pool_commitments` entry contains exactly 16 candidate payments. The sample above shows one candidate for brevity.

`merkle_batches` lists one entry per on-chain payment. A single Merkle tree covers up to 256 fresh chunks (roughly 1 GiB), so an upload larger than that splits across several batches, and the external signer submits one `payForMerkleTree2()` transaction per entry. The top-level `depth`, `pool_commitments`, and `merkle_payment_timestamp` are legacy single-batch fields: the daemon populates them only when `merkle_batches` has exactly one entry, mirroring that entry. A multi-batch response omits them, so read the payment details from `merkle_batches` and treat the singular fields as a convenience for the single-batch case.

Both prepare shapes also return `total_chunks` and `already_stored_count`. `total_chunks` is the full chunk count for the upload, including chunks already on-network; `already_stored_count` is how many were already stored and so excluded from payment and the PUT. Use the two counts to reconcile cost — the difference explains why a prepare can come back cheaper than the raw file size implies. Construct the payment itself from the returned `payments` or `merkle_batches` entries, never from the chunk counts.

For file uploads, the equivalent is `POST /v1/upload/prepare` with a local `path` field instead of `data`. To make the upload publicly retrievable by address, add `"visibility":"public"` to the prepare request. `antd` bundles the serialized DataMap chunk into the same payment batch, and the finalize response includes a `data_map_address` field with its Autonomi Network address.

### 3. Submit the payment externally

Use your signer stack to submit the EVM payment transaction described by the prepare response.

`antd` does not sign or broadcast those transactions in this flow.

- For `wave_batch`, call `payForQuotes()` with the returned `payments` and keep the resulting transaction hashes keyed by `quote_hash`. When the prepare response carried no `payments` because every chunk is already stored on the Autonomi Network, there is nothing to submit — go straight to finalize.
- For `merkle`, call `payForMerkleTree2()` once per entry in `merkle_batches`, passing that entry's `depth`, `pool_commitments`, and `merkle_payment_timestamp`. Keep the `winner_pool_hash` from each transaction's `MerklePaymentMade` event, in the same order as the batches.

Both calls use the `payment_vault_address` returned by the prepare step.

### 4. Finalize the upload

After the external payment is on-chain, call `POST /v1/upload/finalize` with the matching fields for the prepared upload.

Wave-batch finalize request:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

When the prepare response carried no `payments` because every chunk is already stored on the Autonomi Network — for example on a repeated upload — finalize with an empty `tx_hashes` object. No on-chain payment is needed, and `antd` returns the DataMap directly:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{}}'
```

Merkle finalize request. Pass `winner_pool_hashes` as an array holding one winner hash per entry in the prepare response's `merkle_batches`, in the same order:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hashes":["0x...","0x..."]}'
```

When the prepared upload has exactly one batch, you can pass the single `winner_pool_hash` field instead. Do not combine the two fields in one request.

Keep one slot per prepared batch, in the prepare response's order — do not compact or reorder the list. If the signer skipped a batch, send an empty string (or `null`) in that slot; the chunks that batch would have paid for surface as a partial upload rather than a stored result. If no batch was paid at all, finalize rejects the request with a `402` payment error instead — a partial upload is reported only when at least one batch was paid.

Single-batch uploads may still use the legacy field:

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

The language bindings for `antd` follow the same prepare/finalize split across both REST and gRPC transports, but their Merkle support is narrower than the raw API. The `finalize_merkle_upload`-style helpers accept a single `winner_pool_hash`, which serves single-batch uploads at most, and not every binding surfaces the Merkle payment fields on its prepare result. For Merkle uploads, the dependable interfaces are direct REST calls and the generated gRPC request and response types, which carry `merkle_batches` and `winner_pool_hashes` in full. Among the convenience clients, the Go binding exposes multi-batch natively, with `MerkleBatches` on the prepare result and a `FinalizeMerkleUploadMulti` helper; in other languages, drive a multi-batch upload through the REST endpoints shown in the steps above. For file and in-memory data uploads, gRPC `UploadService` exposes the full finalize surface, including `data_map`, `data_map_address`, and `store_data_map`. For single-chunk uploads, gRPC `ChunkService` exposes `PrepareChunk` and `FinalizeChunk`; `FinalizeChunk` returns the stored chunk address.

If you are building in Rust with ant-core instead of `antd`, the library exposes native external-payment helpers such as `data_prepare_upload`, `data_prepare_upload_with_visibility`, `file_prepare_upload`, `prepare_merkle_batch_external`, and `finalize_merkle_batch`. Use `data_prepare_upload_with_visibility(content, Visibility::Public)` to bundle the DataMap chunk into the payment batch for a public in-memory upload. For uploads that span more than one Merkle tree, `prepare_merkle_batches_external` returns the batches to pay and `finalize_upload_merkle_multi` completes the upload from a `Vec` of winner hashes aligned to those batches. Progress-aware variants such as `file_prepare_upload_with_progress`, `finalize_upload_with_progress`, `finalize_upload_merkle_with_progress`, and `finalize_upload_merkle_multi_with_progress` are also available when you need UI feedback during long-running uploads.

## Verify it worked

Finalize succeeds when `antd` accepts the `upload_id` plus either the `tx_hashes` map (wave-batch) or the Merkle winner hashes (`winner_pool_hashes`, or `winner_pool_hash` for a single batch), then returns upload metadata. Use the returned `data_map` for private retrieval. If you prepared with `visibility:"public"`, use the returned `data_map_address` for public retrieval.

## Common errors

**404 Not Found**: The `upload_id` is missing, expired, or already finalized.

**400 Bad Request**: Check whether the prepared upload expects `tx_hashes`, `winner_pool_hash`, or `winner_pool_hashes`, validate the hex formatting of those values, and confirm the number of winner hashes matches the number of `merkle_batches`.

**402 Payment Required**: No Merkle batch was paid — every `winner_pool_hashes` slot was empty. Pay at least one batch before finalizing.

**502 Partial Upload**: The payment landed and some chunks stored, but others missed quorum after retries (or belonged to a batch the signer never paid). The response body carries the `PARTIAL_UPLOAD` code with `chunks_stored`, `chunks_failed`, and `total_chunks`. The stored chunks persist, so re-prepare the same content and finalize again to pay for and store only the remainder.

**503 Service Unavailable**: You started `antd` in direct-wallet mode or without the required network configuration.

## Next steps

- [Prepare a Wallet for Uploads](../../guides/prepare-a-wallet-for-uploads.md)
- [Estimate Costs and Handle Upload Payments](../../guides/estimate-costs-and-handle-upload-payments.md)
- [REST API](../reference/rest-api.md)
- [Use the Daemon as a Local Service](use-the-daemon-as-a-local-service.md)
