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
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
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

Keep your wallet key outside the service that handles uploads. This two-phase flow uses a local daemon, a background service called antd, to prepare and finalize uploads while your external wallet signs and submits the payments.

This is the right approach when:

- your users pay for their own uploads
- your app should not custody a wallet key for them
- you need to integrate with an external signer or wallet stack

## Prerequisites

- `antd` running without `AUTONOMI_WALLET_KEY` (see [Start the Local Daemon](../start-the-local-daemon.md))
- An external signer or wallet stack that can submit the required payment transactions

The cURL flow below uses the REST API. Transport differences for gRPC are called out where the two interfaces behave differently.

Payments on the public Autonomi Network spend real funds. Assess your signer integration in the [local-development setup](../../guides/set-up-a-local-network.md) first; a successful health check or retrieval does not establish payment readiness.

## Steps

### 1. Start antd without a wallet key

`antd` does not have an `--external-signer` flag. External signing uses the prepare/finalize endpoints while `AUTONOMI_WALLET_KEY` is unset.

From the directory containing the executable installed by [Start the Local Daemon](../start-the-local-daemon.md), run:

```bash
./antd
```

From another directory, use the absolute path to that executable. A bare `antd` command is appropriate only if you deliberately installed the intended version on your `PATH`.

On the default network, `antd v0.14.0` selects the Arbitrum One preset and returns its canonical RPC and payment contracts from the prepare endpoints. Do not set individual `EVM_RPC_URL`, `EVM_PAYMENT_TOKEN_ADDRESS`, or `EVM_PAYMENT_VAULT_ADDRESS` overrides; those activate custom payment handling that default-network storage nodes reject.

### 2. Prepare the upload

For a single chunk (up to 4 MiB of raw bytes), call `POST /v1/chunks/prepare`. This is the simplest external-signer flow — one chunk, one payment:

```bash
CHUNK_B64=$(printf 'Hello, Autonomi!' | base64)

curl --fail-with-body -X POST http://localhost:8082/v1/chunks/prepare \
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
  "rpc_url": "<arbitrum_one_rpc_url>"
}
```

After the external signer calls `payForQuotes()` with the returned `payments`, finalize with `POST /v1/chunks/finalize`:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/chunks/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote_hash":"0xtx_hash"}}'
```

The finalize response returns the Autonomi Network address of the stored chunk. This endpoint requires `antd` 0.7.0 or later.

For multi-chunk uploads (arbitrary files or in-memory data larger than one chunk), use the data or file prepare/finalize endpoints described below.

For in-memory data, call `POST /v1/data/prepare`.

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl --fail-with-body -X POST http://localhost:8082/v1/data/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

The in-memory data prepare endpoint accepts `"private"` (default) or `"public"` for `visibility`. When `"public"`, the serialized DataMap is bundled into the same external-signer payment batch and published on-network on finalize; the finalize response then includes a `data_map_address` field with its network address.

The prepare endpoints return a `payment_type` discriminator. Use that value to decide which on-chain call to make and which finalize payload to send back.

File prepares start uploads of 64 or more chunks on the Merkle path and smaller file uploads on the wave-batch path, but that initial selection is not final. A large file can still come back as `wave_batch`: the already-stored preflight can leave fewer than 64 chunks to pay for, and too few reachable Merkle-capable peers also switches the preparation to wave-batch. In-memory data prepares always use wave-batch. Branch on the returned `payment_type`, not on the submitted chunk count.

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
  "rpc_url": "<arbitrum_one_rpc_url>",
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
  "rpc_url": "<arbitrum_one_rpc_url>",
  "total_chunks": 128,
  "already_stored_count": 0
}
```

Each `pool_commitments` entry contains exactly 16 candidate payments. The sample above shows one candidate for brevity.

`merkle_batches` lists one entry per on-chain payment. A single Merkle tree covers up to 256 fresh chunks (roughly 1 GiB), so an upload larger than that splits across several batches, and the external signer submits one `payForMerkleTree2()` transaction per entry. The top-level `depth`, `pool_commitments`, and `merkle_payment_timestamp` are legacy single-batch fields: `antd` populates them only when `merkle_batches` has exactly one entry, mirroring that entry. A multi-batch response omits them, so read the payment details from `merkle_batches` and treat the singular fields as a convenience for the single-batch case.

Both prepare shapes also return `total_chunks` and `already_stored_count`. `total_chunks` is the full chunk count for the upload, including chunks already on-network; `already_stored_count` is how many were already stored and so excluded from payment and the PUT. Use the two counts to reconcile cost — the difference explains why a prepare can come back cheaper than the raw file size implies. Construct the payment itself from the returned `payments` or `merkle_batches` entries, never from the chunk counts. The gRPC `PrepareUploadResponse` carries the same two counts.

For file uploads, the equivalent is `POST /v1/upload/prepare` with a local `path` field instead of `data`. To make the upload publicly retrievable by address, add `"visibility":"public"` to the prepare request. `antd` bundles the serialized DataMap chunk into the same payment batch, and the finalize response includes a `data_map_address` field with its Autonomi Network address.

### 3. Submit the payment externally

Use your signer stack to submit the EVM payment transaction described by the prepare response.

`antd` does not sign or broadcast those transactions in this flow.

- For `wave_batch`, call `payForQuotes()` with the returned `payments` and keep the resulting transaction hashes keyed by `quote_hash`. When the prepare response carried no `payments` because every chunk is already stored on the Autonomi Network, there is nothing to submit and you can go straight to finalize through REST or gRPC.
- For `merkle`, call `payForMerkleTree2()` once per entry in `merkle_batches`, passing that entry's `depth`, `pool_commitments`, and `merkle_payment_timestamp`. Keep the `winner_pool_hash` from each transaction's `MerklePaymentMade` event, in the same order as the batches.

Both calls use the `payment_vault_address` returned by the prepare step.

### 4. Finalize the upload

After the external payment is on-chain, call `POST /v1/upload/finalize` with the matching fields for the prepared upload.

Wave-batch finalize request:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

With REST, when the prepare response carried no `payments` because every chunk is already stored on the Autonomi Network, finalize with an empty `tx_hashes` object. No on-chain payment is needed, and `antd` returns the DataMap directly:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{}}'
```

The gRPC `FinalizeUpload` method also accepts an empty wave-batch `tx_hashes` map for this all-already-stored case. Both transports validate that every payment reported by prepare has a transaction hash before consuming the prepared state. Missing receipts return REST `400 BAD_REQUEST` or gRPC `INVALID_ARGUMENT`; correct the request and retry the same ID. After validation succeeds, a storage shortfall can be resumed under the same ID (see step 5). Any other later failure requires a new prepare call and payment reconciliation.

Merkle finalize request. Pass `winner_pool_hashes` as an array holding one winner hash per entry in the prepare response's `merkle_batches`, in the same order:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hashes":["0x...","0x..."]}'
```

When the prepared upload has exactly one batch, you can pass the single `winner_pool_hash` field instead. Do not combine the two fields in one request.

Keep one slot per prepared batch, in the prepare response's order — do not compact or reorder the list. With REST, send an empty string or `null` when the signer skipped a batch. With gRPC, use an empty string because repeated string fields cannot carry `null`. The chunks that batch would have paid for surface as a partial upload with `retryable: false` rather than a stored result, because only a fully paid batch list can be resumed under the same ID. If no batch was paid at all, finalize rejects the request with a `402` payment error instead — a partial upload is reported only when at least one batch was paid.

Single-batch uploads may still use the legacy field:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hash":"0x..."}'
```

Expected response shape:

```json
{
  "data_map": "<hex_encoded_datamap>",
  "address": "<64_hex_address_if_store_data_map_true>",
  "data_map_address": "<64_hex_address_if_visibility_public>",
  "chunks_stored": 128
}
```

In REST responses, `address` is omitted unless `store_data_map` is `true`; that path stores the DataMap through `antd`'s configured wallet. Use it only when `antd` has a wallet key. `data_map_address` is omitted unless the upload was prepared with `visibility:"public"`; it is the Autonomi Network address of the DataMap chunk whose payment was included in the same external-signer batch. The gRPC response uses empty strings instead of omitted fields.

### 5. Recover from a partial store

If the payment landed but some chunks are still unstored after retries, REST finalize returns HTTP `502` with `code: "PARTIAL_UPLOAD"`. Branch on `code` rather than the status, because a network error also returns `502`:

```json
{
  "error": "Partial upload: 200/256 chunks stored, 56 failed after retries: ...",
  "code": "PARTIAL_UPLOAD",
  "chunks_stored": 200,
  "chunks_failed": 56,
  "total_chunks": 256,
  "retryable": true
}
```

The stored chunks persist. What you do next depends on `retryable`:

- `retryable: true`: `antd` kept the payment proofs and the unstored chunks under the same `upload_id`. Repeat the same finalize request with that `upload_id` to store the remainder against the same payment. Do not prepare again, sign again, or pay again; `antd` ignores the payment fields on this resume. Cap the number of retries, because a persistent failure returns `PARTIAL_UPLOAD` on every call. The retained attempt lives only in the running `antd` process and becomes eligible for cleanup one hour after the partial upload is reported.
- `retryable: false`: nothing was retained. This happens for a Merkle finalize that left one or more batches unpaid. Prepare the same content again, pay for the new prepare response, and finalize to store only the remainder; chunks that are already stored are excluded from the new payment.

For example, repeat a wave-batch finalize with the same request body:

```bash
curl --fail-with-body -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

With gRPC, `FinalizeUpload` returns `ABORTED` with a message that starts with `Partial upload:` and carries the counts. The message includes `paid attempt retained` when you can repeat the same call, and `re-prepare the same content` when nothing was retained.

### 6. Use SDK helpers when available

The REST endpoints shown above expose the complete multi-batch surface in `antd v0.14.0`. The Go convenience client also exposes `MerkleBatches` and `FinalizeMerkleUploadMulti` through REST and gRPC.

For Python, use `pip install 'antd[rest]'` (see [Python installation](../reference/language-bindings/python.md#install)). For Node.js / TypeScript, use `npm install @withautonomi/antd` and import from `"@withautonomi/antd"` (see [TypeScript installation](../reference/language-bindings/typescript.md#install)). These clients are separate from the [native SDKs](../native/README.md), whose APIs do not use this REST workflow.

The Python `antd` 0.2.0, Node.js / TypeScript `@withautonomi/antd` 0.2.0, and Rust `v0.12.1` convenience clients accept one winner-pool hash and therefore handle single-batch Merkle uploads at most. The Python REST parser also checks for `payment_type: "merkle_batch"` while `antd` returns `payment_type: "merkle"`. Do not use the Python convenience client for Merkle preparation with this release. For multi-batch uploads in these languages, use the REST requests shown above. The `upload.proto` file defines `merkle_batches` and `winner_pool_hashes`, but generated binding files do not all expose them.

The OpenAPI schema also omits multi-batch Merkle fields and incorrectly rejects public in-memory preparation. Do not generate an external-signer client from that schema alone; use the [REST API](../reference/rest-api.md) fields for these operations.

For file and in-memory data uploads, gRPC `UploadService` exposes `data_map`, `data_map_address`, and `store_data_map`. For single-chunk uploads, gRPC `ChunkService` exposes `PrepareChunk` and `FinalizeChunk`; `FinalizeChunk` returns the stored chunk address.

If you are building in Rust with ant-core instead of `antd`, the library exposes native external-payment helpers such as `data_prepare_upload`, `data_prepare_upload_with_visibility`, `file_prepare_upload`, `prepare_merkle_batch_external`, and `finalize_merkle_batch`. Use `data_prepare_upload_with_visibility(content, Visibility::Public)` to bundle the DataMap chunk into the payment batch for a public in-memory upload. For uploads that span more than one Merkle tree, `prepare_merkle_batches_external` returns the batches to pay and `finalize_upload_merkle_multi` completes the upload from a `Vec` of winner hashes aligned to those batches. Progress-aware variants such as `file_prepare_upload_with_progress`, `finalize_upload_with_progress`, `finalize_upload_merkle_with_progress`, and `finalize_upload_merkle_multi_with_progress` are also available when you need UI feedback during long-running uploads.

## Verify it worked

Finalize succeeds when `antd` accepts the `upload_id` plus either the `tx_hashes` map (wave-batch) or the Merkle winner hashes (`winner_pool_hashes`, or `winner_pool_hash` for a single batch), then returns upload metadata. Use the returned `data_map` for private retrieval. If you prepared with `visibility:"public"`, use the returned `data_map_address` for public retrieval.

## Common errors

**404 Not Found**: The `upload_id` is missing, expired, or already finalized, or a retained partial upload expired or was lost when `antd` restarted.

**400 Bad Request**: Check whether the prepared upload expects `tx_hashes`, `winner_pool_hash`, or `winner_pool_hashes`, validate the hex formatting of those values, and confirm the number of winner hashes matches the number of `merkle_batches`.

**402 Payment Required**: No Merkle batch was paid — every `winner_pool_hashes` slot was empty. Pay at least one batch before finalizing.

**502 Partial Upload**: The payment landed and some chunks stored, but others are still unstored after retries (or belonged to a batch the signer never paid). The response body carries the `PARTIAL_UPLOAD` code with `chunks_stored`, `chunks_failed`, `total_chunks`, and `retryable`. The stored chunks persist. With `retryable: true`, repeat the same finalize call with the same `upload_id`; with `retryable: false`, re-prepare the same content and finalize again to pay for and store only the remainder.

**503 Service Unavailable**: `antd` does not have an EVM network configured. On the default network, remove individual EVM overrides and restart `antd` so it selects the Arbitrum One preset. For a local network, use `ant dev start` to supply the matching local configuration.

## Next steps

- [Prepare a Wallet for Uploads](../../guides/prepare-a-wallet-for-uploads.md)
- [Estimate Costs and Handle Upload Payments](../../guides/estimate-costs-and-handle-upload-payments.md)
- [REST API](../reference/rest-api.md)
- [Use the Daemon as a Local Service](use-the-daemon-as-a-local-service.md)
