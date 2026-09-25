# gRPC Services

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

This page describes the gRPC surface exposed by `antd 0.14.0` on `127.0.0.1:50051` by default.

Unlike the REST API, the gRPC API carries raw bytes in protobuf fields rather than base64 strings in JSON.

`antd` does not configure authentication or Transport Layer Security (TLS) for gRPC. Loopback binding limits access to the local machine, but any process that can connect can invoke write, wallet, and local-filesystem methods. Put access controls in front of the service before binding it to an external interface.

## Limits

The gRPC server uses Tonic's default 4 MiB maximum inbound message size. Protobuf field encoding counts toward the limit, so a `bytes` field cannot carry a complete 4 MiB chunk. This limit applies to data puts, data cost requests, in-memory prepares, chunk puts, chunk prepares, and large caller-held DataMaps. The REST API accepts request bodies up to 100 MiB. File upload, file cost, and public file-download RPCs avoid transferring file bytes by passing paths on the `antd` host, but private file downloads still carry a caller-held DataMap in the request.

The Verify Service is the exception: it accepts messages up to 32 MiB so that a batch of 1024 maximal entries fits.

## Health Service

### Check

**Signature:** `Check(HealthCheckRequest) -> HealthCheckResponse`

Checks `antd` liveness, network selection, and live connectivity. `status: "ok"` does not guarantee a successful read or write.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `status` | string | Expected `ok` on success |
| `network` | string | Value selected by `--network` or `ANTD_NETWORK`; documented modes are `default` and `local` |
| `version` | string | `antd` crate version, `0.14.0` for this release |
| `evm_network` | string | Selected EVM preset string. Recognized presets include `arbitrum-one`, `arbitrum-sepolia`, `arbitrum-sepolia-test`, and `local`; other values use local defaults unless individual EVM variables override them |
| `uptime_seconds` | uint64 | Seconds since the `antd` process started |
| `build_commit` | string | Short git SHA captured at build time, or empty if built outside a git checkout |
| `payment_token_address` | string | Payment token contract address. Arbitrum One defaults to `0xa78d8321B20c4Ef90eCd72f2588AA985A4BDb684`; empty for an unconfigured custom or local setup |
| `payment_vault_address` | string | Payment vault contract address. Arbitrum One defaults to `0x9A3EcAc693b699Fc0B2B6A50B5549e50c2320A26`; empty for an unconfigured custom or local setup |
| `write_ready` | bool | Best-effort connectivity signal: `max(routing_table_size, connected_peers) >= rebootstrap_threshold`. `false` signals degraded connectivity; `true` neither checks wallet funds nor guarantees storage |
| `connected_peers` | uint32 | Identity-verified live peer connections |
| `routing_table_size` | uint32 | Entries in the Kademlia DHT routing table |
| `rebootstrap_threshold` | uint32 | Routing-table floor for automatic peer rediscovery; `3` |
| `last_store_ok_secs_ago` | optional uint64 | Age in seconds of the last successful store-type operation in this process, including all-already-stored finalization. Absent until one succeeds; REST uses `null` instead |

## Data Service

### Put

**Signature:** `Put(PutDataRequest) -> PutDataResponse`

Stores private data. The DataMap is returned to the caller and is not stored on-network.

The response's `cost.atto_tokens` is an empty string and its other cost fields have protobuf defaults because the direct data-write path does not return paid totals. `chunks_stored` covers data chunks, and `payment_mode_used` is the resolved `single` or `merkle` mode rather than the requested `auto` value.

### Put Public

**Signature:** `PutPublic(PutPublicDataRequest) -> PutPublicDataResponse`

Stores public data. The DataMap is stored on-network as an additional chunk.

The response has the same empty `cost` behavior as `Put`. `chunks_stored` counts the data chunks plus the DataMap chunk that `antd` stores separately to produce `address`. `payment_mode_used` describes the data-chunk upload. Data and chunk addresses are 64 hexadecimal characters without a `0x` prefix.

### Get

**Signature:** `Get(GetDataRequest) -> GetDataResponse`

Fetches private data using a caller-held `data_map` string.

### Get Public

**Signature:** `GetPublic(GetPublicDataRequest) -> GetPublicDataResponse`

Fetches public data by address.

An address with no stored DataMap returns `NOT_FOUND`. Missing data chunks and missing wrapper chunks needed to resolve nested DataMaps also return `NOT_FOUND`. A lookup with no connected peers also returns `NOT_FOUND`, so check `connected_peers` from `Check` before treating the address as unused.

### Stream

**Signature:** `Stream(StreamDataRequest) -> stream DataChunk`

Streams private data from a caller-held `data_map`, decrypting one batch at a time. This is the streaming counterpart of `Get` and the primitive that `StreamPublic` wraps.

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

Both streaming methods resolve nested DataMaps before opening the stream, then send the original plaintext byte length in initial response metadata under `x-content-length`. Resolution errors arrive before the first frame. No `resolving_map` progress is emitted because this work completes before streaming starts.

`DownloadProgress` reports fetch progress in chunk counts:

| Name | Type | Description |
|------|------|-------------|
| `phase` | string | `resolved` or `fetching` for these methods; `resolving_map` remains in the message vocabulary but is not emitted after pre-stream resolution |
| `fetched` | uint64 | Chunks fetched so far in the current phase |
| `total` | uint64 | Total chunks for the current phase, or `0` while not yet known |

### Cost

**Signature:** `Cost(DataCostRequest) -> antd.v1.Cost`

Returns an advisory storage and gas estimate for a byte payload. It samples up to five chunk addresses and extrapolates from the first sample with live quotes; gas is a fixed heuristic rather than a live gas-price query. The response does not expose confidence, so a zero estimate for more than five chunks means only that all samples were already stored. `payment_mode` in the response is the resolved `single` or `merkle` mode. The estimate excludes a separate public DataMap store, which `PutPublic` counts in `chunks_stored`.

## Chunk Service

### Get

**Signature:** `Get(GetChunkRequest) -> GetChunkResponse`

Fetches a chunk by address.

### Put

**Signature:** `Put(PutChunkRequest) -> PutChunkResponse`

Stores a raw chunk.

The response contains a `Cost` message whose `atto_tokens` is empty and whose other fields have protobuf defaults. The direct chunk-write path does not return its prepaid cost.

### PrepareChunk

**Signature:** `PrepareChunk(PrepareChunkRequest) -> PrepareChunkResponse`

Phase 1 of the external-signer single-chunk upload flow. Mirrors `POST /v1/chunks/prepare`. Single-chunk publishes always use the wave-batch payment shape.

When the chunk is already on-network, `already_stored` is `true`, the payment fields are empty, and no finalize call is needed.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `data` | bytes | Raw chunk bytes (at most one ant-protocol chunk) |
| `include_signed_quotes` | bool | Defaults to `false`. Request signed quotes and available commitment sidecars for [Verify Quotes](#verify-quotes) when payment is required |

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `address` | string | Content-addressed BLAKE3 hash of the chunk bytes, as 64 hexadecimal characters without a `0x` prefix |
| `already_stored` | bool | `true` if the chunk was already on-network; all payment fields are empty when `true` |
| `upload_id` | string | Opaque token to pass to `FinalizeChunk`; empty when `already_stored` is `true` |
| `payment_type` | string | Always `"wave_batch"` for single-chunk publishes; empty when `already_stored` is `true` |
| `payments` | repeated PaymentEntry | Per-quote payment entries for `payForQuotes()`; see [Common messages](#common-messages) |
| `total_amount` | string | Total amount to pay in atto tokens |
| `payment_vault_address` | string | Payment vault contract address (hex with `0x` prefix) |
| `payment_token_address` | string | Payment token contract address (hex with `0x` prefix) |
| `rpc_url` | string | EVM RPC URL for submitting transactions |
| `signed_quotes` | repeated SignedQuoteEntry | Paid quotes when requested; empty when not requested or the chunk is already stored. See [Common messages](#common-messages) |

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
| `address` | string | Network address of the stored chunk, as 64 hexadecimal characters without a `0x` prefix |

Prepared chunk state is held only in the running `antd` process. It becomes eligible for cleanup after one hour, with cleanup running every five minutes. `FinalizeChunk` consumes the state before validating transaction hashes or attempting the store, so its first call is one-shot; prepare again after any failure.

## Upload Service

The Upload Service handles external-signer file and in-memory data uploads. It mirrors the REST `/v1/upload/prepare`, `/v1/data/prepare`, and `/v1/upload/finalize` surface.

The flow is two-phase: submit a prepare request, receive payment details and an `upload_id`, submit the EVM payment externally, then call `FinalizeUpload` with the transaction hashes or winner pool hash. External signing is a request workflow, not an `antd` startup mode.

Prepared state is process-local and is lost when `antd` restarts. It becomes eligible for cleanup after one hour, and cleanup runs every five minutes. `FinalizeUpload` validates payment fields before consuming state, so a bad request leaves the paid-for upload in place and validation errors are retryable. Once validation succeeds, the call consumes the prepared state and stores the chunks. A storage shortfall after payment can keep the paid attempt under the same `upload_id` for a repeat `FinalizeUpload`, as described under [FinalizeUpload](#finalizeupload). After any other later failure, prepare again and reconcile payment.

- `payment_type = "wave_batch"` pays with `payForQuotes()`.
- `payment_type = "merkle"` pays with `payForMerkleTree2()`.

File uploads of 64 or more chunks start on the Merkle path and smaller file uploads on the wave-batch path, but the initial selection is not final: when the already-stored preflight leaves fewer than 64 chunks to pay for, or too few Merkle-capable peers are reachable, `antd` prepares a wave-batch payment instead. In-memory data prepares always use wave-batch. Branch on the returned `payment_type`, not on the submitted chunk count.

### PrepareFileUpload

**Signature:** `PrepareFileUpload(PrepareFileUploadRequest) -> PrepareUploadResponse`

Phase 1 for a local file. Returns payment details and an `upload_id`.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `path` | string | Local filesystem path on the host running `antd` |
| `visibility` | string | `"private"` (default) or `"public"`. `"public"` bundles the DataMap chunk into the payment batch; `data_map_address` is populated in the finalize response |
| `include_signed_quotes` | bool | Defaults to `false`. Include signed quotes for wave-batch responses only; Merkle responses leave the list empty |

### PrepareDataUpload

**Signature:** `PrepareDataUpload(PrepareDataUploadRequest) -> PrepareUploadResponse`

Phase 1 for in-memory bytes. Same two-phase flow as `PrepareFileUpload` but accepts raw bytes rather than a filesystem path and always returns `payment_type = "wave_batch"`. The 4 MiB inbound message limit applies.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `data` | bytes | Raw bytes to upload |
| `visibility` | string | `"private"` (default) or `"public"` |
| `include_signed_quotes` | bool | Defaults to `false`. Include signed wave-batch quotes and available commitment sidecars |

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
| `signed_quotes` | repeated SignedQuoteEntry | Paid wave-batch quotes when requested; empty for Merkle, when not requested, or when no payment is needed |
| `total_chunks` | uint64 | Full chunk count for the upload, including chunks already on-network |
| `already_stored_count` | uint64 | How many of `total_chunks` were already stored and so excluded from payment and storage |

The external signer pays for `total_chunks - already_stored_count` chunks. Use the two counts for reconciliation only, and construct the payment from the returned `payments` or `merkle_batches` entries. These fields match the REST prepare response.

### FinalizeUpload

**Signature:** `FinalizeUpload(FinalizeUploadRequest) -> FinalizeUploadResponse`

Phase 2 for both file and data uploads. Call after the external EVM payment lands.

**Request fields:**

| Name | Type | Description |
|------|------|-------------|
| `upload_id` | string | The `upload_id` returned from a prepare RPC, or the same value again after a retained partial upload |
| `tx_hashes` | map\<string, string\> | Wave-batch: map of `quote_hash` (hex) to `tx_hash` (hex) from the on-chain payment. Must cover every payment reported by prepare; an empty map is accepted when prepare reported none. Must be empty for Merkle |
| `winner_pool_hashes` | repeated string | Merkle: one winner pool hash (hex with `0x` prefix) per entry in `merkle_batches`, in the same order. An empty string marks a batch the signer did not pay; keep unpaid slots in place rather than compacting or reordering the list. Required over `winner_pool_hash` when the upload has more than one batch |
| `winner_pool_hash` | string | Merkle, legacy single-batch: winner pool hash from the `MerklePaymentMade` event. Accepted only when the upload has exactly one batch; must be empty for wave-batch and must not be combined with `winner_pool_hashes` |
| `store_data_map` | bool | If `true`, stores the DataMap through `antd`'s configured wallet and returns its address in `address` |

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `data_map` | string | Hex-encoded serialized DataMap. Always returned |
| `address` | string | Autonomi Network address of the stored DataMap, as 64 hexadecimal characters without a `0x` prefix; empty unless `store_data_map` is `true` |
| `data_map_address` | string | Autonomi Network address of the bundled DataMap chunk, as 64 hexadecimal characters without a `0x` prefix; empty unless prepare used `visibility = "public"` |
| `chunks_stored` | uint64 | Number of chunks stored on the Autonomi Network |

When prepare reports no `payments` because every chunk is already stored, `FinalizeUpload` accepts an empty wave-batch `tx_hashes` map without an on-chain payment. If payments are required, an empty map or missing quote receipt returns `INVALID_ARGUMENT` before the prepared state is consumed, so you can correct the request and retry the same ID.

When the payment lands but some chunks are still unstored after retries (or belong to a batch the signer did not pay), `FinalizeUpload` returns the `ABORTED` status code. The message starts with `Partial upload:` and reports how many chunks stored and failed, followed by a hint that says how to finish the upload. The stored chunks persist.

- `paid attempt retained`: `antd` keeps the payment proofs and the unstored chunks under the same `upload_id`. Repeat the same `FinalizeUpload` call with that `upload_id` to store the remainder against the same on-chain payment, without preparing or paying again. The payment fields are ignored on this resume, but a field that belongs to the other payment type is still rejected. Bound the retry loop, because a persistent failure returns `ABORTED` on every call. The retained attempt is process-local: it becomes eligible for cleanup one hour after the partial upload is reported and is lost if `antd` restarts.
- `re-prepare the same content`: nothing was retained. A Merkle finalize returns this when one or more `winner_pool_hashes` slots are empty, because only a fully paid batch list takes the resumable path. Prepare the same content again and finalize to pay for and store only the remainder.

`ABORTED` is reported only when at least one Merkle batch was paid: when every `winner_pool_hashes` slot is empty, `FinalizeUpload` returns `FAILED_PRECONDITION` instead.

## Verify Service

### Verify Quotes

**Signature:** `VerifyQuotes(VerifyQuotesRequest) -> VerifyQuotesResponse`

**RPC:** `antd.v1.VerifyService/VerifyQuotes`

Verifies signed payment quotes on an `antd` instance you trust, not the counterparty's instance. The method is stateless: it does not contact the Autonomi Network, require a wallet, pay, store data, or consume preparation state.

`VerifyQuotesRequest.entries` is a repeated `VerifyQuoteEntry` field with at most 1024 entries. The Verify Service accepts messages up to 32 MiB, so a full batch of maximal entries fits. Per entry, a `signed_quote` larger than 16 KiB or a `commitment_sidecar` larger than 8 KiB receives a `valid: false` verdict. The method has no authentication or rate limiting, so keep `antd` on loopback or behind your own access control.

**Entry fields:**

| Name | Type | Description |
|------|------|-------------|
| `quote_hash` | string | 32-byte hex hash from the payment entry |
| `rewards_address` | string | Hex payment recipient with `0x` prefix |
| `amount` | string | Payment amount in atto tokens as a decimal integer string |
| `signed_quote` | bytes | Unchanged `quote` bytes from the matching `SignedQuoteEntry`; match by `quote_hash`, not array position |
| `commitment_sidecar` | bytes | Unchanged sidecar from that entry; required when the quote binds a storage commitment, empty otherwise |

The method checks the quote hash, ML-DSA-65 signature, recipient, and amount, which must equal three times the signed quote price. It also checks the storage-commitment binding and the pricing formula for the claimed committed-key count. Treat the MessagePack quote and sidecar as opaque bytes, not application-defined structures.

**Response fields:**

| Name | Type | Description |
|------|------|-------------|
| `valid` | bool | True only for a nonempty batch where every entry passes |
| `entries` | repeated VerifyQuoteVerdict | Verdicts in request order |

Each `VerifyQuoteVerdict` contains:

| Name | Type | Description |
|------|------|-------------|
| `quote_hash` | string | Echo of the submitted hash |
| `valid` | bool | Whether all verification checks passed |
| `error` | string | First failed check; empty when valid |
| `quote_decoded` | bool | Whether the quote decoded; extracted fields are meaningless while false |
| `timestamp_unix_secs` | uint64 | Signed quote timestamp in Unix seconds |
| `content` | string | Chunk address as 64 hexadecimal characters |
| `price` | string | Signed quote price in atto tokens, before the three-times payment multiplier |
| `rewards_address` | string | Recipient claimed by the quote |
| `committed_key_count` | uint32 | Claimed storage-commitment key count; zero for a quote without a commitment |
| `pinned` | bool | Whether the quote binds a storage commitment |

An empty batch returns `valid: false` and no verdicts. Invalid quote bytes produce per-entry false verdicts rather than a failed RPC. More than 1024 entries returns `INVALID_ARGUMENT`; a message larger than 32 MiB is rejected by the gRPC transport before verification runs. Extracted fields can be populated even when a later verification check fails, so `quote_decoded: true` alone does not make them trustworthy.

Your application must enforce expiry, replay prevention, equality with the intended set of chunks, and limits on plausible key counts. Verification alone does not authorize payment. Merkle prepares do not expose signed quotes through `include_signed_quotes`. Generated clients without Verify Service stubs, including the Python `antd` 0.2.0 package, do not gain this RPC by connecting to a newer `antd`.

For examples of empty-batch and malformed-quote responses over HTTP, see [REST quote verification](rest-api.md#verify-quotes).

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

Uploads a local file publicly. The data chunks and the DataMap chunk are paid for in one batch and stored on-network.

`PutFilePublicResponse` returns `address`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, and `payment_mode_used`. `storage_cost_atto`, `gas_cost_wei`, and `chunks_stored` include the DataMap chunk, the same extra chunk that `Cost` adds with `is_public` set to `true`. `address` is the DataMap chunk's address, with no `0x` prefix.

### Get

**Signature:** `Get(GetFileRequest) -> GetFileResponse`

Downloads a private file using a caller-held DataMap.

### Get Public

**Signature:** `GetPublic(GetFilePublicRequest) -> GetFileResponse`

Downloads a public file to a local destination path using its on-network DataMap address.

### Cost

**Signature:** `Cost(FileCostRequest) -> antd.v1.Cost`

Returns an advisory file-upload estimate. It samples up to five data-chunk addresses and extrapolates from the first sample with live quotes; gas is a fixed heuristic rather than a live gas-price query. `is_public` defaults to `false`, while the equivalent REST field defaults to `true`. When `is_public` is `true`, the estimate adds one DataMap chunk to the count and approximates its cost from the sampled data-chunk price rather than quoting it separately. A public zero-cost estimate does not prove the DataMap store is free, and a private zero estimate is not guaranteed when more than five data chunks exist. The response's `payment_mode` is resolved to `single` or `merkle`.

## Event Service

### Subscribe

**Signature:** `Subscribe(SubscribeRequest) -> stream ClientEventProto`

This RPC is exposed, but it emits no events and completes immediately because the server drops the stream sender before returning.

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
| `Cost` | `atto_tokens`, `file_size`, `chunk_count`, `estimated_gas_cost_wei`, `payment_mode`; direct data and chunk writes return an empty `atto_tokens` value and defaults for the other fields |
| `HealthCheckResponse` | `status`, `network`, `version`, `evm_network`, `uptime_seconds`, `build_commit`, `payment_token_address`, `payment_vault_address`, `write_ready`, `connected_peers`, `routing_table_size`, `rebootstrap_threshold`, optional `last_store_ok_secs_ago` |
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
| `SignedQuoteEntry` | `quote_hash` (hex string), `quote` (MessagePack bytes), `commitment_sidecar` (MessagePack bytes, empty when unavailable or the quote does not bind a commitment) |
| `MerkleBatchEntry` | `depth`, `pool_commitments`, `merkle_payment_timestamp` |
| `PoolCommitmentEntry` | `pool_hash`, `candidates` |
| `CandidateNodeEntry` | `rewards_address`, `amount` |

## Related pages

- [REST API](rest-api.md)
- [SDK Overview](overview.md)
- [How Language Bindings Work](language-bindings/overview.md)
