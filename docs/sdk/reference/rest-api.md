# REST API

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

This page describes the REST surface exposed by `antd 0.14.0`. By default, `antd` listens on `http://127.0.0.1:8082`.

REST request and response bodies are JSON except for data streaming responses. Binary payloads use base64-encoded `data` fields; signed quotes and their commitment sidecars use the base64 fields described under [Quote verification](#quote-verification).

`antd` has no authentication. Loopback binding limits access to the local machine, but any process that can connect can invoke write, wallet, and local-filesystem endpoints. If you expose the listener on another interface, put a firewall or authenticated proxy in front of it. Configure Cross-Origin Resource Sharing (CORS) with an exact origin list, for example `--cors http://127.0.0.1:8000`. Bare `--cors` allows no origins; `--cors '*'` allows any webpage to call the API, including wallet endpoints, and is unsafe outside development. CORS does not restrict non-browser clients.

Handler responses include an `x-request-id` header that you can match with daemon logs. When CORS is enabled, preflight responses bypass that middleware and do not include the header.

The downloadable OpenAPI schema is incomplete for external signing: it omits multi-batch Merkle fields and incorrectly rejects public in-memory preparation. Use the request and response fields below rather than generating an external-signer client from that schema alone.

## Limits

- The maximum REST request body is 100 MiB. Base64 encoding and the surrounding JSON count toward this limit, so the maximum raw in-memory payload is smaller.
- `POST /v1/verify/quotes` has its own 40 MiB request-body limit; see [Verify Quotes](#verify-quotes).
- Hex-decoded DataMaps are limited to 10 MiB on `POST /v1/data/get`, `POST /v1/data/stream`, and `POST /v1/files/get`.
- File endpoints pass a local path rather than transferring file bytes through the REST body limit.

## Health

### Health Check

**Endpoint:** `GET /health`

Returns `antd` liveness, the selected network, and a live connectivity snapshot. HTTP `200` and `status: "ok"` do not mean that reads or writes will succeed.

**Response:**

```json
{
  "status": "ok",
  "network": "default",
  "version": "0.14.0",
  "evm_network": "arbitrum-one",
  "uptime_seconds": 12345,
  "build_commit": "dbf6a7d3d951",
  "payment_token_address": "0xa78d8321B20c4Ef90eCd72f2588AA985A4BDb684",
  "payment_vault_address": "0x9A3EcAc693b699Fc0B2B6A50B5549e50c2320A26",
  "write_ready": true,
  "connected_peers": 7,
  "routing_table_size": 2,
  "rebootstrap_threshold": 3,
  "last_store_ok_secs_ago": null
}
```

All fields shown are always present; the counts and times are illustrative. On a local devnet, `payment_token_address` and `payment_vault_address` may be empty strings, and `build_commit` is empty when the binary was built outside a git checkout.

| Field | Type | Meaning |
|------|------|---------|
| `write_ready` | boolean | Best-effort connectivity signal: `max(routing_table_size, connected_peers) >= rebootstrap_threshold`. `false` signals degraded connectivity; `true` does not check wallet configuration or funds and does not guarantee storage |
| `connected_peers` | integer | Identity-verified live peer connections |
| `routing_table_size` | integer | Entries in the Kademlia DHT routing table |
| `rebootstrap_threshold` | integer | Routing-table floor for automatic peer rediscovery; `3` |
| `last_store_ok_secs_ago` | integer or null | Seconds since the last successful data, file, or chunk write, or upload finalization, in this process; `null` until one succeeds. An all-already-stored finalization also updates this marker |

**Example:**

```bash
curl http://127.0.0.1:8082/health
```

## Data

### Store Public Data

**Endpoint:** `POST /v1/data/public`

Stores public data and returns the public address that can be shared with readers.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded payload |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "address": "<64_hex_address>",
  "chunks_stored": <chunk_count>,
  "payment_mode_used": "single"
}
```

`payment_mode_used` reports the resolved mode, so a request using `auto` returns either `single` or `merkle`. `chunks_stored` counts the data chunks plus the DataMap chunk that `antd` stores separately to produce `address`.

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://127.0.0.1:8082/v1/data/public \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

### Get Public Data

**Endpoint:** `GET /v1/data/public/{addr}`

Fetches public data by address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `addr` | path | Yes | 64-character hex data address |

**Response:**

```json
{
  "data": "SGVsbG8sIEF1dG9ub21pIQ=="
}
```

**Example:**

```bash
: "${ADDRESS:?Set ADDRESS to a 64-character public data address}"
curl "http://127.0.0.1:8082/v1/data/public/${ADDRESS}"
```

### Stream Public Data

**Endpoint:** `GET /v1/data/public/{addr}/stream`

Streams a public object by address, decrypting one batch at a time instead of buffering the whole object into a JSON body. Use this for large objects. `antd` resolves nested DataMaps before opening the response so the byte length describes the plaintext object, not an intermediate serialized map. Resolution failures return an error before streaming begins.

The response framing depends on the `Accept` header:

- Default (any `Accept` other than `application/x-ndjson`): a raw `application/octet-stream` body of the decrypted plaintext. The `Content-Length` header is set from the object's original size, so a client detects a failed download as a short read.
- `Accept: application/x-ndjson`: newline-delimited JSON (NDJSON) frames, one JSON object per line, so the caller can drive a determinate progress bar. A leading `{"type":"meta","total_size":<bytes>}` frame is followed by interleaved `{"type":"progress",...}` and `{"type":"data","chunk":"<base64>"}` frames, and an `{"type":"error","message":"..."}` frame if the download fails partway. Each `progress` frame carries `phase`, `fetched` (chunks fetched so far), and `total` (chunks for the phase). The download starts from a resolved map, so no `resolving_map` progress is emitted; expect `resolved` and `fetching` phases. Treat an error frame as a failed download even if progress frames follow it.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `addr` | path | Yes | 64-character hex data address |

**Example:**

```bash
: "${ADDRESS:?Set ADDRESS to a 64-character public data address}"

# Raw bytes
curl "http://127.0.0.1:8082/v1/data/public/${ADDRESS}/stream" -o object.bin

# Progress framing
curl -H "Accept: application/x-ndjson" \
  "http://127.0.0.1:8082/v1/data/public/${ADDRESS}/stream"
```

### Store Private Data

**Endpoint:** `POST /v1/data`

Stores private data. The DataMap is returned to the caller and is not stored on-network.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded payload |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "data_map": "<hex_encoded_datamap>",
  "chunks_stored": <chunk_count>,
  "payment_mode_used": "single"
}
```

`payment_mode_used` reports the resolved mode, so a request using `auto` returns either `single` or `merkle`.

**Example:**

```bash
DATA_B64=$(printf 'Secret message' | base64)

curl -X POST http://127.0.0.1:8082/v1/data \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

### Get Private Data

**Endpoint:** `POST /v1/data/get`

Retrieves private data using a caller-held DataMap. Uses POST so the hex-encoded DataMap (which can be many KB) goes in the request body rather than a URL query string.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data_map` | string | Yes | Hex-encoded serialized DataMap |

**Response:**

```json
{
  "data": "U2VjcmV0IG1lc3NhZ2U="
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/data/get \
  -H "Content-Type: application/json" \
  -d '{"data_map":"<hex_encoded_datamap>"}'
```

### Stream Private Data

**Endpoint:** `POST /v1/data/stream`

Streams private data from a caller-held DataMap without buffering the complete plaintext in a JSON response. The response framing follows [Stream Public Data](#stream-public-data): raw `application/octet-stream` by default, or NDJSON progress and data frames when the request accepts `application/x-ndjson`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data_map` | string | Yes | Hex-encoded serialized DataMap |

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/data/stream \
  -H "Content-Type: application/json" \
  -d '{"data_map":"<hex_encoded_datamap>"}' \
  -o object.bin

curl --no-buffer -X POST http://127.0.0.1:8082/v1/data/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/x-ndjson" \
  -d '{"data_map":"<hex_encoded_datamap>"}'
```

### Estimate Data Cost

**Endpoint:** `POST /v1/data/cost`

Returns an advisory storage and gas estimate for a data payload without uploading it. `antd` samples up to five chunk addresses spread across the payload and extrapolates from the first sample that returns live quotes. The gas value is a fixed heuristic, not a live gas-price query.

The response does not expose estimate confidence. If `cost` is `"0"` and `chunk_count` is greater than five, only the sampled chunks were known to be stored; unsampled chunks may still require payment. This endpoint also excludes the separate DataMap store performed by a public direct write, which `POST /v1/data/public` counts in `chunks_stored`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded payload |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "cost": "<atto_token_amount>",
  "file_size": <bytes>,
  "chunk_count": <chunk_count>,
  "estimated_gas_cost_wei": "<wei_amount>",
  "payment_mode": "single"
}
```

`payment_mode` is the mode selected for the estimate, not the requested `auto` value.

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://127.0.0.1:8082/v1/data/cost \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

## Chunks

### Store a Chunk

**Endpoint:** `POST /v1/chunks`

Stores a raw chunk.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded chunk bytes |

**Response:**

```json
{
  "cost": "",
  "address": "<64_hex_address>"
}
```

The direct chunk-write path does not return its prepaid storage cost, so `cost` is always an empty string. Use an explicit data or file cost endpoint when you need an advisory estimate.

**Example:**

```bash
CHUNK_B64=$(printf 'chunk bytes' | base64)

curl -X POST http://127.0.0.1:8082/v1/chunks \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$CHUNK_B64\"}"
```

### Get a Chunk

**Endpoint:** `GET /v1/chunks/{addr}`

Retrieves a raw chunk by address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `addr` | path | Yes | 64-character hex chunk address |

**Response:**

```json
{
  "data": "Y2h1bmsgYnl0ZXM="
}
```

**Example:**

```bash
: "${CHUNK_ADDRESS:?Set CHUNK_ADDRESS to a 64-character chunk address}"
curl "http://127.0.0.1:8082/v1/chunks/${CHUNK_ADDRESS}"
```

### Prepare a Single-Chunk Upload

**Endpoint:** `POST /v1/chunks/prepare`

Prepares one raw chunk for the external-signer flow. `antd` computes the chunk address, checks whether the chunk is already stored, and returns either the existing address or the payment details needed before finalizing.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded raw chunk bytes |
| `include_signed_quotes` | boolean | No | Defaults to `false`. Request signed quotes for [offline verification](#quote-verification) when payment is required |

**Response:**

When the chunk already exists on-network:

```json
{
  "address": "<64_hex_address>",
  "already_stored": true
}
```

When payment is required, the default response is:

```json
{
  "address": "<64_hex_address>",
  "already_stored": false,
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
  "rpc_url": "http://127.0.0.1:8545"
}
```

With `include_signed_quotes: true`, a payment-required response also includes the [signed quote entries](#signed-quote-entries). An already-stored chunk response omits them, even when requested.

**Example:**

```bash
CHUNK_B64=$(printf 'chunk bytes' | base64)

curl -X POST http://127.0.0.1:8082/v1/chunks/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$CHUNK_B64\"}"
```

### Finalize a Single-Chunk Upload

**Endpoint:** `POST /v1/chunks/finalize`

Stores a chunk prepared by `POST /v1/chunks/prepare` after the external signer has submitted the matching payment transaction. The prepare state lives only in the running `antd` process. It becomes eligible for cleanup after one hour, and the cleanup task runs every five minutes.

The first finalize attempt removes the prepared chunk before transaction hashes are parsed or the store is attempted. The `upload_id` cannot be retried, including after malformed hashes or a network failure; prepare the chunk again to obtain a new ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `upload_id` | string | Yes | Value returned by `POST /v1/chunks/prepare` |
| `tx_hashes` | object | Yes | Map of `quote_hash` to the transaction hash returned by the external payment |

**Response:**

```json
{
  "address": "<64_hex_address>"
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/chunks/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

## Files

These endpoints work on paths visible to the machine running `antd`.

### Upload a Public File

**Endpoint:** `POST /v1/files/public`

Uploads a local file publicly. The data chunks and the DataMap chunk are paid for in one batch and stored on-network, and the response returns the DataMap's network address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "address": "<64_hex_address>",
  "storage_cost_atto": "<atto_token_amount>",
  "gas_cost_wei": "<wei_amount>",
  "chunks_stored": 42,
  "payment_mode_used": "single"
}
```

`storage_cost_atto`, `gas_cost_wei`, and `chunks_stored` include the DataMap chunk, the same extra chunk that `POST /v1/files/cost` adds with `is_public: true`. `payment_mode_used` is the resolved `single` or `merkle` mode.

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/files/public \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf"}'
```

### Download a Public File

**Endpoint:** `POST /v1/files/public/get`

Downloads a public file using its on-network DataMap address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `address` | string | Yes | 64-character hex on-network DataMap address |
| `dest_path` | string | Yes | Local destination path |

**Response:** HTTP `200 OK` with no JSON body

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/files/public/get \
  -H "Content-Type: application/json" \
  -d '{"address":"<64_hex_address>","dest_path":"/absolute/path/to/downloaded.pdf"}'
```

### Upload a Private File

**Endpoint:** `POST /v1/files`

Uploads a local file privately. The DataMap is returned to the caller and is not stored on-network.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "data_map": "<hex_encoded_datamap>",
  "storage_cost_atto": "<atto_token_amount>",
  "gas_cost_wei": "<wei_amount>",
  "chunks_stored": 42,
  "payment_mode_used": "single"
}
```

`payment_mode_used` is the resolved `single` or `merkle` mode.

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/files \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf"}'
```

### Download a Private File

**Endpoint:** `POST /v1/files/get`

Downloads a file using a caller-held DataMap (no address lookup required).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data_map` | string | Yes | Hex-encoded serialized DataMap |
| `dest_path` | string | Yes | Local destination path |

**Response:** HTTP `200 OK` with no JSON body

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/files/get \
  -H "Content-Type: application/json" \
  -d '{"data_map":"<hex_encoded_datamap>","dest_path":"/absolute/path/to/downloaded.pdf"}'
```

### Estimate File Cost

**Endpoint:** `POST /v1/files/cost`

Returns an advisory upload estimate for a local file. `antd` samples up to five data-chunk addresses spread across the file and extrapolates from the first sample that returns live quotes. The gas value is a fixed heuristic, not a live gas-price query.

With `is_public: true`, `antd` adds one DataMap chunk to `chunk_count` and approximates its storage cost from the sampled per-data-chunk price. It does not quote that DataMap chunk separately, so a public zero-cost estimate does not prove that the DataMap store is free. For a private estimate, zero is exact when every data chunk was sampled and already stored; if more than five data chunks exist, zero means only that every sample was already stored.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `is_public` | boolean | No | Defaults to `true`; the equivalent gRPC field defaults to `false` |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "cost": "<atto_token_amount>",
  "file_size": <bytes>,
  "chunk_count": <chunk_count>,
  "estimated_gas_cost_wei": "<wei_amount>",
  "payment_mode": "single"
}
```

`payment_mode` is the mode selected for the estimate, not the requested `auto` value.

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/files/cost \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf","is_public":true}'
```

## Wallet

### Get Wallet Address

**Endpoint:** `GET /v1/wallet/address`

Returns the configured wallet address.

**Response:**

```json
{
  "address": "0x1234abcd..."
}
```

**Example:**

```bash
curl http://127.0.0.1:8082/v1/wallet/address
```

### Get Wallet Balance

**Endpoint:** `GET /v1/wallet/balance`

Returns token and gas balances.

**Response:**

```json
{
  "balance": "<atto_token_balance>",
  "gas_balance": "<wei_balance>"
}
```

**Example:**

```bash
curl http://127.0.0.1:8082/v1/wallet/balance
```

### Approve Wallet Spend

**Endpoint:** `POST /v1/wallet/approve`

Approves token spend for payment contracts.

**Parameters:** None

**Response:**

```json
{
  "approved": true
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/wallet/approve \
  -H "Content-Type: application/json" \
  -d '{}'
```

## External signer flow

### Prepare a Data Upload

**Endpoint:** `POST /v1/data/prepare`

Prepares an in-memory data upload for external signing. This endpoint always returns the wave-batch payment shape, regardless of chunk count.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded payload |
| `visibility` | string | No | `"private"` (default) or `"public"`. When `"public"`, the serialized DataMap is bundled into the same external-signer payment batch and published on-network on finalize; `data_map_address` is then present in the finalize response. |
| `include_signed_quotes` | boolean | No | Defaults to `false`. Include signed wave-batch quotes and available commitment sidecars for [offline verification](#quote-verification) |

**Response:**

The response uses `payment_type: "wave_batch"`.

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
  "rpc_url": "http://127.0.0.1:8545",
  "total_chunks": 12,
  "already_stored_count": 4
}
```

File prepares can instead return this Merkle variant:

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
  "rpc_url": "http://127.0.0.1:8545",
  "total_chunks": 128,
  "already_stored_count": 0
}
```

Each `pool_commitments` entry contains exactly 16 candidate payments. The example above abbreviates that repeated structure.

`merkle_batches` holds one entry per on-chain payment. A single Merkle tree covers up to 256 fresh chunks (roughly 1 GiB); a larger upload splits across several batches, and the external signer calls `payForMerkleTree2()` once per entry. The top-level `depth`, `pool_commitments`, and `merkle_payment_timestamp` are legacy single-batch fields, present only when `merkle_batches` has exactly one entry and mirroring that entry. They are omitted for a multi-batch upload, so read payment details from `merkle_batches`.

Both variants include `total_chunks` and `already_stored_count`. `total_chunks` is the full chunk count for the upload, including chunks already on-network; `already_stored_count` is how many of those were already stored and so excluded from payment and from the PUT. The difference between the two counts is why a prepared upload can cost less than the raw file size implies; use it for reconciliation only, and construct the payment from the returned `payments` or `merkle_batches` entries.

With `include_signed_quotes: true`, wave-batch prepares also return `signed_quotes`, containing the [signed quote entries](#signed-quote-entries) for the payments. This array is empty when no payment is needed. Without the opt-in, the field is omitted. Merkle prepares omit it even when requested.

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://127.0.0.1:8082/v1/data/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

### Prepare a File Upload

**Endpoint:** `POST /v1/upload/prepare`

Prepares a file upload for external signing.

`antd` starts file uploads of 64 or more chunks on the Merkle path and smaller uploads on the wave-batch path. The initial selection is not final: when the already-stored preflight leaves fewer than 64 chunks to pay for, or too few Merkle-capable peers are reachable, `antd` prepares a wave-batch payment instead. Branch on the returned `payment_type`, not on the submitted chunk count.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `visibility` | string | No | `"private"` (default) or `"public"`. `"public"` bundles the serialized DataMap chunk into the same payment batch and stores it on-network; its address is returned on finalize via `data_map_address`. |
| `include_signed_quotes` | boolean | No | Defaults to `false`. Include signed quotes for wave-batch responses only; Merkle responses omit them |

**Response:** The wave-batch or Merkle shape shown under `POST /v1/data/prepare`

**Example:**

```bash
curl -X POST http://127.0.0.1:8082/v1/upload/prepare \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf"}'
```

### Finalize an Upload

**Endpoint:** `POST /v1/upload/finalize`

Finalizes a prepared upload after the external signer has submitted the matching payment transaction.

Prepared state is held only by the running `antd` process; restarting it invalidates every `upload_id`. State becomes eligible for cleanup after one hour, with cleanup running every five minutes. Payment fields, including a transaction hash for every expected wave-batch quote, are validated before state is consumed, so a bad request leaves the paid-for upload in place and you can correct it and retry the same ID. Once validation succeeds, finalize consumes the prepared state and stores the chunks. A storage shortfall after payment returns `PARTIAL_UPLOAD` and, when its `retryable` flag is `true`, keeps the paid attempt under the same `upload_id` for a retry. Any other later failure, such as a payment-verification error or a failed `store_data_map` store, requires a new prepare call and payment reconciliation.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `upload_id` | string | Yes | Value returned by a prepare endpoint, or the same value again after a retryable `PARTIAL_UPLOAD` |
| `tx_hashes` | object | No | Wave-batch only: map of `quote_hash` to `tx_hash` |
| `winner_pool_hashes` | array | No | Merkle: one winner pool hash per entry in the prepare response's `merkle_batches`, in the same order. An empty string or `null` in a slot marks a batch the signer did not pay; keep unpaid slots in place rather than compacting or reordering the list |
| `winner_pool_hash` | string | No | Merkle, legacy single-batch: winner pool hash emitted by `MerklePaymentMade`. Accepted only when the upload has exactly one batch; do not combine it with `winner_pool_hashes` |
| `store_data_map` | boolean | No | If `true`, also stores the DataMap on-network |

Provide `tx_hashes` when the prepare response returned `payment_type: "wave_batch"`. When that response reported no `payments` because every chunk is already stored on the Autonomi Network, send an empty `tx_hashes` object; finalize completes without any on-chain payment. When it returned `payment_type: "merkle"`, provide `winner_pool_hashes` with one hash per `merkle_batches` entry; a single-batch upload may instead provide `winner_pool_hash`.

**Response:**

```json
{
  "data_map": "<hex_encoded_datamap>",
  "address": "<64_hex_address>",
  "data_map_address": "<64_hex_address>",
  "chunks_stored": <chunk_count>
}
```

`address` is only present when `store_data_map` is `true`; that path uses the wallet configured in `antd` to store the DataMap. `data_map_address` is only present when the upload was prepared with `visibility:"public"`; it is the Autonomi Network address of the bundled DataMap chunk whose payment was included in the same external-signer batch as the data chunks.

**Examples:**

```bash
curl -X POST http://127.0.0.1:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"},"store_data_map":true}'
```

Wave-batch upload where every chunk is already stored, so prepare reported no `payments`:

```bash
curl -X POST http://127.0.0.1:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{}}'
```

```bash
curl -X POST http://127.0.0.1:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hash":"0x...","store_data_map":true}'
```

Multi-batch Merkle upload, one winner hash per `merkle_batches` entry:

```bash
curl -X POST http://127.0.0.1:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hashes":["0x...","0x..."],"store_data_map":true}'
```

When part of an upload stores but the rest is still unstored after retries, finalize returns `502` with the `PARTIAL_UPLOAD` code, machine-readable counts, and a `retryable` flag:

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

The stored chunks persist. Branch on `code` rather than the HTTP status, then on `retryable`:

- `retryable: true`: `antd` keeps the payment proofs and the unstored chunks under the same `upload_id`. Repeat the same finalize request with that `upload_id` to store the remainder against the same on-chain payment. Do not prepare again or pay again. `antd` ignores `tx_hashes`, `winner_pool_hash`, and `winner_pool_hashes` on this resume, but still rejects a field that belongs to the other payment type. Bound the retry loop, because a persistent failure returns `PARTIAL_UPLOAD` on every call. The retained attempt is process-local: it becomes eligible for cleanup one hour after the partial upload is reported and is lost if `antd` restarts.
- `retryable: false`: nothing was retained. A Merkle finalize returns this when one or more `winner_pool_hashes` slots are unpaid, because only a fully paid batch list takes the resumable path. Re-prepare the same content and finalize again to pay for and store only the missing remainder.

A partial upload is reported only when at least one Merkle batch was paid. When every `winner_pool_hashes` slot is empty, finalize returns `402` with the `PAYMENT_REQUIRED` code instead.

## Quote verification

Use signed quotes to check payment details before paying through an external signer. Verification runs on an `antd` instance you trust, not the counterparty's instance. It does not need a wallet, contact the Autonomi Network, pay, store data, or consume an `upload_id`.

### Signed quote entries

Opt in with `include_signed_quotes: true` on a data, file, or chunk prepare request. Each returned `signed_quotes` entry has these fields:

| Name | Type | Description |
|------|------|-------------|
| `quote_hash` | string | Hex hash with `0x` prefix; match it to the corresponding `payments` entry by hash, not array position |
| `quote` | string | Base64-encoded MessagePack signed quote; pass unchanged as `signed_quote` to verification |
| `commitment_sidecar` | string, optional | Base64-encoded MessagePack storage commitment, the signed record bound to the quote; omitted when unavailable or the quote does not bind one |

Treat the serialized quote and sidecar as opaque bytes. A quote that binds a commitment fails verification without its matching sidecar. Merkle prepares do not expose signed quotes through this option. The Python `antd` and Node.js `@withautonomi/antd` 0.2.0 clients do not expose the opt-in or verification helpers; use these REST fields directly rather than assuming those packages provide matching methods.

### Verify Quotes

**Endpoint:** `POST /v1/verify/quotes`

Checks each quote's hash, ML-DSA-65 signature, rewards address, and payment amount. The amount must equal three times the signed quote price. It also checks the storage-commitment binding and requires the price to match the pricing formula for the claimed committed-key count.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `entries` | array | Yes | Up to 1024 quote/payment entries; an empty array returns `valid: false` |

Each entry contains:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `quote_hash` | string | Yes | 32-byte hex hash from the payment entry |
| `rewards_address` | string | Yes | Hex payment recipient with `0x` prefix |
| `amount` | string | Yes | Payment amount in atto tokens, as a decimal integer string |
| `signed_quote` | string | Yes | Unchanged `quote` from the matching signed quote entry |
| `commitment_sidecar` | string | Conditional | Unchanged sidecar; required when the quote binds a storage commitment |

**Limits:**

- At most 1024 entries per call.
- Request bodies on this route are limited to 40 MiB. A larger body is rejected with `413` before it is parsed.
- Per entry, a `signed_quote` longer than 21,848 base64 characters (16 KiB decoded) or a `commitment_sidecar` longer than 10,924 base64 characters (8 KiB decoded) receives a `valid: false` verdict without being decoded.
- The endpoint has no authentication or rate limiting, like the wallet endpoints. Keep `antd` on loopback or behind your own access control.

**Response:** HTTP `200` with `valid` and an `entries` array in request order. Overall `valid` is true only for a nonempty array where every entry passes. Invalid quote contents produce per-entry false verdicts, not a successful payment authorization. More than 1024 entries returns `400` / `BAD_REQUEST`, and a body over 40 MiB returns `413`; malformed request bodies and field types can receive framework rejection responses instead.

Each verdict contains:

| Name | Type | Description |
|------|------|-------------|
| `quote_hash` | string | Echo of the submitted hash |
| `valid` | boolean | Whether every verification check passed |
| `error` | string, optional | First failed check; omitted when valid |
| `timestamp_unix_secs` | integer, optional | Signed quote timestamp in Unix seconds |
| `content` | string, optional | Chunk address as 64 hexadecimal characters |
| `price` | string, optional | Signed quote price in atto tokens, before the three-times payment multiplier |
| `rewards_address` | string, optional | Recipient claimed by the signed quote |
| `committed_key_count` | integer, optional | Claimed storage-commitment key count; zero for a quote without a commitment |
| `pinned` | boolean, optional | Whether the quote binds a storage commitment |

Extracted fields can be present after decoding even if a later check fails. They are claims, not trusted values unless verification succeeds. Your application must separately enforce expiry, replay prevention, equality with the intended set of chunks, and limits on plausible key counts. A valid signature and pricing check alone do not authorize payment.

**Example:** Check the endpoint with an empty batch, without preparing or paying for an upload:

```bash
curl --fail-with-body --silent --show-error \
  -X POST http://127.0.0.1:8082/v1/verify/quotes \
  -H "Content-Type: application/json" \
  -d '{"entries":[]}'
```

Expected response:

```json
{"valid":false,"entries":[]}
```

A deliberately malformed quote also returns HTTP `200`, with a failed verdict:

```bash
curl --fail-with-body --silent --show-error \
  -X POST http://127.0.0.1:8082/v1/verify/quotes \
  -H "Content-Type: application/json" \
  -d '{"entries":[{"quote_hash":"0x0000000000000000000000000000000000000000000000000000000000000000","rewards_address":"0x0000000000000000000000000000000000000000","amount":"0","signed_quote":"!"}]}'
```

Expected response:

```json
{
  "valid": false,
  "entries": [{
    "quote_hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "valid": false,
    "error": "signed_quote is not valid base64: Invalid symbol 33, offset 0."
  }]
}
```

These checks exercise empty and malformed input only; they do not demonstrate valid-signature verification or a paid upload.

## Error codes

| HTTP status | Handler code | Meaning | Resolution |
|------|------|---------|------------|
| `400` | `BAD_REQUEST` | Invalid base64, hex, DataMap, payment mode, visibility, payment fields, local path, or more than 1024 verification entries | Correct the request. Malformed JSON may instead receive a framework-generated rejection body. Invalid quote contents in `/v1/verify/quotes` return per-entry verdicts under HTTP `200` |
| `402` | `PAYMENT_REQUIRED` | Payment failed or no Merkle batch was paid | Fund the configured wallet or submit the required external payment |
| `404` | `NOT_FOUND` | No DataMap is stored at the requested address, a chunk needed for retrieval is missing, or a prepared `upload_id` or in-memory chunk was not found | Confirm the address or DataMap, and check `connected_peers` in `/health`, because a lookup with no connected peers also returns `NOT_FOUND`. For an `upload_id`, prepare again if process-local state expired, was consumed, or was lost on restart |
| `404` | Framework response | No route matched the requested path | Correct the endpoint path |
| `405` | Framework response | The route does not support the HTTP method | Use the method documented for the endpoint |
| `409` | `ALREADY_EXISTS` | The requested record is already stored | Use the returned or computed content address instead of repeating the write |
| `413` | `TOO_LARGE`, or framework rejection | A handler rejected an in-memory operation, the request body exceeded 100 MiB, or a `/v1/verify/quotes` body exceeded 40 MiB | Use a file endpoint or reduce the request body |
| `415` | Framework response | A JSON endpoint did not receive `Content-Type: application/json` | Add the JSON content-type header |
| `422` | Framework response | JSON parsed but could not be converted to the endpoint's request fields | Check required fields and their types |
| `500` | `INTERNAL_ERROR` | Serialization, encryption, protocol, or internal task failure | Inspect the error message and match `x-request-id` with `antd` logs before retrying |
| `501` | `NOT_IMPLEMENTED` | The requested behavior is not implemented | Use a supported endpoint |
| `502` | `NETWORK_ERROR` | `antd` could not complete a network operation | Confirm peer connectivity and retry |
| `502` | `PARTIAL_UPLOAD` | Some chunks stored while others are still unstored after retries | Check `retryable`. When `true`, repeat the same external-signer finalize call with the same `upload_id`. When `false`, nothing was retained: retry the direct upload, or prepare the same content again and finalize to store only the remainder. The response includes `chunks_stored`, `chunks_failed`, `total_chunks`, and `retryable` |
| `503` | `SERVICE_UNAVAILABLE` | A direct write or wallet operation needs a wallet that is not configured in `antd` | Set `AUTONOMI_WALLET_KEY`, or use the external-signer prepare/finalize flow for writes |
| `504` | `TIMEOUT` | A network operation exceeded its deadline | Check connectivity and retry |

Handler-generated errors always include a human-readable `error` and a machine-readable `code`:

```json
{
  "error": "Bad request: address must be exactly 64 hex characters",
  "code": "BAD_REQUEST"
}
```

A lookup of a well-formed public address with no stored DataMap returns `404`:

```json
{
  "error": "Record not found: DataMap chunk not found at <64_hex_address>",
  "code": "NOT_FOUND"
}
```

A `404` does not prove that the data is absent: when `antd` has no connected peers, a lookup also returns `NOT_FOUND`. Check `connected_peers` in [Health Check](#health-check) before treating the address as unused.

Prefer `code` over the HTTP status where they diverge. For example, `PARTIAL_UPLOAD` arrives as `502`, the same status as `NETWORK_ERROR`. `PARTIAL_UPLOAD` also includes `chunks_stored`, `chunks_failed`, `total_chunks`, and `retryable`.

## Related pages

- [Build with the SDKs](../install.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Store Data on the Network](../store-data-on-the-network.md)
- [Store and Retrieve Data with the SDKs](../how-to-guides/store-and-retrieve-data.md)
- [gRPC Services](grpc-services.md)
- [Daemon Command Reference](daemon-command-reference.md)
