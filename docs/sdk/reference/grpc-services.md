# gRPC Services

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

This page describes the gRPC surface exposed by `antd` on `localhost:50051` by default.

Unlike the REST API, the gRPC API carries raw bytes in protobuf fields rather than base64 strings in JSON.

## Health Service

### Check

**Signature:** `Check(HealthCheckRequest) -> HealthCheckResponse`

Checks daemon health and network selection.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `status` | string | Expected `ok` on success |
| `network` | string | Network name: `default`, `local`, or `alpha` |
| `version` | string | antd crate version (e.g. `0.4.0`) |
| `evm_network` | string | EVM preset: `arbitrum-one`, `arbitrum-sepolia`, `local`, or `custom` |
| `uptime_seconds` | uint64 | Seconds since the daemon process started |
| `build_commit` | string | Short git SHA captured at build time, or empty if built outside a git checkout |
| `payment_token_address` | string | Payment token contract address, or empty if unconfigured |
| `payment_vault_address` | string | Payment vault contract address, or empty if unconfigured |

## Data Service

### Put

**Signature:** `Put(PutDataRequest) -> PutDataResponse`

Stores private data. The DataMap is returned to the caller and is not stored on-network.

### Put Public

**Signature:** `PutPublic(PutPublicDataRequest) -> PutPublicDataResponse`

Stores public data. The DataMap is stored on-network as an additional chunk.

### Get

**Signature:** `Get(GetDataRequest) -> GetDataResponse`

Fetches private data using a caller-held `data_map` string.

### Get Public

**Signature:** `GetPublic(GetPublicDataRequest) -> GetPublicDataResponse`

Fetches public data by address.

### Stream

**Signature:** `Stream(StreamDataRequest) -> stream DataChunk`

Streams private data from a caller-held `data_map` with constant memory, decrypting one batch at a time. This is the streaming counterpart of `Get` and the primitive that `StreamPublic` wraps.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `data_map` | string | Hex-encoded serialized DataMap |
| `include_progress` | bool | When `true`, the server interleaves `DownloadProgress` frames with the data frames on the same stream. Defaults to `false`, in which case the stream carries only data frames |

### Stream Public

**Signature:** `StreamPublic(StreamPublicDataRequest) -> stream DataChunk`

Resolves a public address to its DataMap and then streams the data, the public wrapper around `Stream`.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `address` | string | Hex data address |
| `include_progress` | bool | Same meaning as on `Stream`. Defaults to `false` |

Each `DataChunk` frame carries exactly one of two payloads through its `kind` oneof: `data` (a decrypted plaintext batch) or `progress` (a `DownloadProgress` update). A consumer that leaves `include_progress` at `false` receives only `data` frames.

`DownloadProgress` reports fetch progress in chunk counts:

| Name | Type | Description |
|------|------|-------------|
| `phase` | string | One of `resolving_map`, `resolved`, or `fetching` |
| `fetched` | uint64 | Chunks fetched so far in the current phase |
| `total` | uint64 | Total chunks for the current phase, or `0` while not yet known |

### Cost

**Signature:** `Cost(DataCostRequest) -> antd.v1.Cost`

Estimates storage cost for a byte payload. Accepts an optional `payment_mode` field (`"auto"`, `"merkle"`, or `"single"`).

## Chunk Service

### Get

**Signature:** `Get(GetChunkRequest) -> GetChunkResponse`

Fetches a chunk by address.

### Put

**Signature:** `Put(PutChunkRequest) -> PutChunkResponse`

Stores a raw chunk.

### PrepareChunk

**Signature:** `PrepareChunk(PrepareChunkRequest) -> PrepareChunkResponse`

Phase 1 of the external-signer single-chunk upload flow. Mirrors `POST /v1/chunks/prepare`. Single-chunk publishes always use the wave-batch payment shape.

When the chunk is already on-network, `already_stored` is `true`, the payment fields are empty, and no finalize call is needed.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `data` | bytes | Raw chunk bytes (at most one ant-protocol chunk) |

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `address` | string | Content-addressed BLAKE3 hash of the chunk bytes (hex with `0x` prefix) |
| `already_stored` | bool | `true` if the chunk was already on-network; all payment fields are empty when `true` |
| `upload_id` | string | Opaque token to pass to `FinalizeChunk`; empty when `already_stored` is `true` |
| `payment_type` | string | Always `"wave_batch"` for single-chunk publishes; empty when `already_stored` is `true` |
| `payments` | repeated PaymentEntry | Per-quote payment entries for `payForQuotes()`; see [Common messages](#common-messages) |
| `total_amount` | string | Total amount to pay in atto tokens |
| `payment_vault_address` | string | Payment vault contract address (hex with `0x` prefix) |
| `payment_token_address` | string | Payment token contract address (hex with `0x` prefix) |
| `rpc_url` | string | EVM RPC URL for submitting transactions |

### FinalizeChunk

**Signature:** `FinalizeChunk(FinalizeChunkRequest) -> FinalizeChunkResponse`

Phase 2 of the external-signer single-chunk upload flow. Mirrors `POST /v1/chunks/finalize`. Call this after the external EVM payment has landed on-chain.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `upload_id` | string | The `upload_id` returned from `PrepareChunk` |
| `tx_hashes` | map\<string, string\> | Map of `quote_hash` (hex) to `tx_hash` (hex) from the on-chain payment |

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `address` | string | Network address of the stored chunk (hex with `0x` prefix) |

## Upload Service

The Upload Service handles external-signer file and in-memory data uploads. It mirrors the REST `/v1/upload/prepare`, `/v1/data/prepare`, and `/v1/upload/finalize` surface.

The flow is two-phase: submit a prepare request, receive payment details and an `upload_id`, submit the EVM payment externally, then call `FinalizeUpload` with the transaction hashes or winner pool hash.

- `payment_type = "wave_batch"` pays with `payForQuotes()`.
- `payment_type = "merkle"` pays with `payForMerkleTree2()`.

Uploads of 64 or more chunks start on the Merkle path and smaller uploads on the wave-batch path, but the initial selection is not final: when the already-stored preflight leaves fewer than 64 chunks to pay for, or too few Merkle-capable peers are reachable, the daemon prepares a wave-batch payment instead. Branch on the returned `payment_type`, not on the submitted chunk count.

### PrepareFileUpload

**Signature:** `PrepareFileUpload(PrepareFileUploadRequest) -> PrepareUploadResponse`

Phase 1 for a local file. Returns payment details and an `upload_id`.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `path` | string | Local filesystem path on the host running `antd` |
| `visibility` | string | `"private"` (default) or `"public"`. `"public"` bundles the DataMap chunk into the payment batch; `data_map_address` is populated in the finalize response |

### PrepareDataUpload

**Signature:** `PrepareDataUpload(PrepareDataUploadRequest) -> PrepareUploadResponse`

Phase 1 for in-memory bytes. Same two-phase flow as `PrepareFileUpload` but accepts raw bytes rather than a filesystem path.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `data` | bytes | Raw bytes to upload |
| `visibility` | string | `"private"` (default) or `"public"` |

### PrepareUploadResponse (shared)

Both prepare RPCs return `PrepareUploadResponse`:

| Name | Type | Description |
|------|------|-------------|
| `upload_id` | string | Opaque token to pass to `FinalizeUpload` |
| `payment_type` | string | `"wave_batch"` or `"merkle"` |
| `payments` | repeated PaymentEntry | Wave-batch: per-quote entries for `payForQuotes()`; see [Common messages](#common-messages) |
| `merkle_batches` | repeated MerkleBatchEntry | Merkle: one entry per on-chain payment, each with its own `depth`, `pool_commitments`, and `merkle_payment_timestamp`. A single Merkle tree covers up to 256 fresh chunks; larger uploads split across several entries |
| `depth` | uint32 | Merkle, legacy single-batch: tree depth (1–8). Populated only when `merkle_batches` has exactly one entry |
| `pool_commitments` | repeated PoolCommitmentEntry | Merkle, legacy single-batch: pool commitments for `payForMerkleTree2()`; each entry has exactly 16 candidate nodes; populated only when `merkle_batches` has exactly one entry; see [Common messages](#common-messages) |
| `merkle_payment_timestamp` | uint64 | Merkle, legacy single-batch: unix timestamp for the payment. Populated only when `merkle_batches` has exactly one entry |
| `total_amount` | string | Total amount in atto tokens (`"0"` for Merkle) |
| `payment_vault_address` | string | Payment vault contract address (hex with `0x` prefix) |
| `payment_token_address` | string | Payment token contract address (hex with `0x` prefix) |
| `rpc_url` | string | EVM RPC URL for submitting transactions |

### FinalizeUpload

**Signature:** `FinalizeUpload(FinalizeUploadRequest) -> FinalizeUploadResponse`

Phase 2 for both file and data uploads. Call after the external EVM payment lands.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `upload_id` | string | The `upload_id` returned from a prepare RPC |
| `tx_hashes` | map\<string, string\> | Wave-batch: map of `quote_hash` (hex) to `tx_hash` (hex) from the on-chain payment. Empty when the prepare RPC reported no `payments` because every chunk is already stored, in which case the upload finalizes without an on-chain payment. Must be empty for Merkle |
| `winner_pool_hashes` | repeated string | Merkle: one winner pool hash (hex with `0x` prefix) per entry in `merkle_batches`, in the same order. An empty string marks a batch the signer did not pay; keep unpaid slots in place rather than compacting or reordering the list. Required over `winner_pool_hash` when the upload has more than one batch |
| `winner_pool_hash` | string | Merkle, legacy single-batch: winner pool hash from the `MerklePaymentMade` event. Accepted only when the upload has exactly one batch; must be empty for wave-batch and must not be combined with `winner_pool_hashes` |
| `store_data_map` | bool | If `true`, stores the DataMap through `antd`'s configured wallet and returns its address in `address` |

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `data_map` | string | Hex-encoded serialized DataMap. Always returned |
| `address` | string | Autonomi Network address of the stored DataMap; only set when `store_data_map` is `true` |
| `data_map_address` | string | Autonomi Network address of the bundled DataMap chunk; only set when the upload was prepared with `visibility = "public"` |
| `chunks_stored` | uint64 | Number of chunks stored on the Autonomi Network |

When the payment lands but some chunks miss quorum after retries (or belong to a batch the signer did not pay), `FinalizeUpload` returns the `ABORTED` status code with a message reporting how many chunks stored and failed. The stored chunks persist; re-prepare the same content and finalize again to store only the remainder. `ABORTED` is reported only when at least one Merkle batch was paid: when every `winner_pool_hashes` slot is empty, `FinalizeUpload` returns `FAILED_PRECONDITION` instead.

## Wallet Service

The Wallet Service mirrors the REST `/v1/wallet/*` surface. All three RPCs require `antd` to have been started with `AUTONOMI_WALLET_KEY`. When the wallet is absent, `antd` returns `failed_precondition`.

External-signer flows do not use this service — they use `UploadService` and `ChunkService.PrepareChunk`/`FinalizeChunk` instead.

### GetAddress

**Signature:** `GetAddress(GetWalletAddressRequest) -> GetWalletAddressResponse`

Returns the wallet's on-chain address.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `address` | string | Wallet address (hex with `0x` prefix) |

### GetBalance

**Signature:** `GetBalance(GetWalletBalanceRequest) -> GetWalletBalanceResponse`

Returns the wallet's token and gas balances.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `balance` | string | Token balance in atto tokens as a decimal string |
| `gas_balance` | string | Gas (native EVM token) balance in atto tokens as a decimal string |

### Approve

**Signature:** `Approve(WalletApproveRequest) -> WalletApproveResponse`

Approves the wallet to spend tokens on the payment vault contract. Safe to call repeatedly; idempotent once approval is in place.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `approved` | bool | `true` if the approve transaction succeeded |

## File Service

### Put

**Signature:** `Put(PutFileRequest) -> PutFileResponse`

Uploads a local file privately. The DataMap is returned to the caller and is not stored on-network.

### Put Public

**Signature:** `PutPublic(PutFileRequest) -> PutFilePublicResponse`

Uploads a local file publicly. Also stores the DataMap on-network as an additional chunk.

`PutFilePublicResponse` returns `address`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, and `payment_mode_used`.

### Get

**Signature:** `Get(GetFileRequest) -> GetFileResponse`

Downloads a private file using a caller-held DataMap.

### Get Public

**Signature:** `GetPublic(GetFilePublicRequest) -> GetFileResponse`

Downloads a public file to a local destination path using its on-network DataMap address.

### Cost

**Signature:** `Cost(FileCostRequest) -> antd.v1.Cost`

Estimates file upload cost. `is_public` toggles between the public and private payment shape (public bundles an extra DataMap chunk into the estimate). Accepts an optional `payment_mode` field (`"auto"`, `"merkle"`, or `"single"`).

## Event Service

### Subscribe

**Signature:** `Subscribe(SubscribeRequest) -> stream ClientEventProto`

This RPC is exposed, but the stream stays open without emitting events.

`ClientEventProto` includes:

| Name | Type | Description |
|------|------|-------------|
| `kind` | string | Event kind |
| `records_paid` | uint64 | Number of paid records |
| `records_already_paid` | uint64 | Number of already-paid records |
| `tokens_spent` | string | Tokens spent |

## Common messages

The proto files define these reusable shapes:

| Message | Fields |
|------|--------|
| `Cost` | `atto_tokens`, `file_size`, `chunk_count`, `estimated_gas_cost_wei`, `payment_mode` |
| `HealthCheckResponse` | `status`, `network`, `version`, `evm_network`, `uptime_seconds`, `build_commit`, `payment_token_address`, `payment_vault_address` |
| `PutPublicDataResponse` | `cost`, `address`, `chunks_stored`, `payment_mode_used` |
| `PutDataResponse` | `cost`, `data_map`, `chunks_stored`, `payment_mode_used` |
| `DataChunk` | `kind` oneof of `data` (bytes) or `progress` (`DownloadProgress`) |
| `DownloadProgress` | `phase`, `fetched`, `total` |
| `PutFileRequest` | `path`, `payment_mode` |
| `PutFilePublicResponse` | `address`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, `payment_mode_used` |
| `PutFileResponse` | `data_map`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, `payment_mode_used` |
| `GetFilePublicRequest` | `address`, `dest_path` |
| `GetFileRequest` | `data_map`, `dest_path` |
| `GetDataRequest` | `data_map` |
| `FileCostRequest` | `path`, `is_public`, `payment_mode` |
| `PaymentEntry` | `quote_hash`, `rewards_address`, `amount` |
| `MerkleBatchEntry` | `depth`, `pool_commitments`, `merkle_payment_timestamp` |
| `PoolCommitmentEntry` | `pool_hash`, `candidates` |
| `CandidateNodeEntry` | `rewards_address`, `amount` |

## Related pages

- [REST API](rest-api.md)
- [SDK Overview](overview.md)
- [How Language Bindings Work](language-bindings/overview.md)
