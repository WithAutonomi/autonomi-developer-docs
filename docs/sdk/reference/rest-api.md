# REST API

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

This page describes the REST surface exposed by `antd`. By default, the daemon listens on `http://localhost:8082`.

All current REST payloads are JSON. When you send or receive binary data, the bytes are base64-encoded inside a `data` field.

## Health

### Health Check

**Endpoint:** `GET /health`

Returns daemon health and the selected network.

**Response:**

```json
{
  "status": "ok",
  "network": "default",
  "version": "0.6.1",
  "evm_network": "arbitrum-one",
  "uptime_seconds": 12345,
  "build_commit": "529280c3",
  "payment_token_address": "0xde817De9d8AC8C3aA10C3Ed0EE5FCB6C53cE7B0a",
  "payment_vault_address": "0x607483B50C5F06c25cDC316b6d1E071084EeC9f5"
}
```

All six fields (`version`, `evm_network`, `uptime_seconds`, `build_commit`, `payment_token_address`, `payment_vault_address`) are always present. On a local devnet, `payment_token_address` and `payment_vault_address` may be empty strings, and `build_commit` is empty when the binary was built outside a git checkout.

**Example:**

```bash
curl http://localhost:8082/health
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
  "payment_mode_used": "auto"
}
```

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/public \
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
curl http://localhost:8082/v1/data/public/<addr>
```

### Stream Public Data

**Endpoint:** `GET /v1/data/public/{addr}/stream`

Streams a public object by address with constant memory, decrypting one batch at a time instead of buffering the whole object into a JSON body. Use this for large objects.

The response framing depends on the `Accept` header:

- Default (any `Accept` other than `application/x-ndjson`): a raw `application/octet-stream` body of the decrypted plaintext. The `Content-Length` header is set from the object's original size, so a client detects a failed download as a short read.
- `Accept: application/x-ndjson`: newline-delimited JSON (NDJSON) frames, one JSON object per line, so the caller can drive a determinate progress bar. A leading `{"type":"meta","total_size":<bytes>}` frame is followed by interleaved `{"type":"progress",...}` and `{"type":"data","chunk":"<base64>"}` frames, and a terminal `{"type":"error","message":"..."}` frame if the download fails partway. Each `progress` frame carries `phase` (`"resolving_map"`, `"resolved"`, or `"fetching"`), `fetched` (chunks fetched so far), and `total` (chunks for the phase, or `0` while still unknown).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `addr` | path | Yes | 64-character hex data address |

**Example:**

```bash
# Raw bytes
curl http://localhost:8082/v1/data/public/<addr>/stream -o object.bin

# Progress framing
curl -H "Accept: application/x-ndjson" \
  http://localhost:8082/v1/data/public/<addr>/stream
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
  "payment_mode_used": "auto"
}
```

**Example:**

```bash
DATA_B64=$(printf 'Secret message' | base64)

curl -X POST http://localhost:8082/v1/data \
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
curl -X POST http://localhost:8082/v1/data/get \
  -H "Content-Type: application/json" \
  -d '{"data_map":"<hex_encoded_datamap>"}'
```

### Estimate Data Cost

**Endpoint:** `POST /v1/data/cost`

Estimates the storage cost for a data payload without uploading it.

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
  "payment_mode": "auto"
}
```

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/cost \
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
  "cost": "<atto_token_amount>",
  "address": "<64_hex_address>"
}
```

**Example:**

```bash
CHUNK_B64=$(printf 'chunk bytes' | base64)

curl -X POST http://localhost:8082/v1/chunks \
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
curl http://localhost:8082/v1/chunks/<addr>
```

### Prepare a Single-Chunk Upload

**Endpoint:** `POST /v1/chunks/prepare`

Prepares one raw chunk for the external-signer flow. The daemon computes the chunk address, checks whether the chunk is already stored, and returns either the existing address or the payment details needed before finalizing.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded raw chunk bytes |

**Response:**

When the chunk already exists on-network:

```json
{
  "address": "<64_hex_address>",
  "already_stored": true
}
```

When payment is required:

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

**Example:**

```bash
CHUNK_B64=$(printf 'chunk bytes' | base64)

curl -X POST http://localhost:8082/v1/chunks/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$CHUNK_B64\"}"
```

### Finalize a Single-Chunk Upload

**Endpoint:** `POST /v1/chunks/finalize`

Stores a chunk prepared by `POST /v1/chunks/prepare` after the external signer has submitted the matching payment transaction.

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
curl -X POST http://localhost:8082/v1/chunks/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"}}'
```

## Files

These endpoints work on paths visible to the machine running `antd`.

### Upload a Public File

**Endpoint:** `POST /v1/files/public`

Uploads a local file publicly. Also stores the DataMap on-network as an additional chunk and returns its network address.

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
  "payment_mode_used": "auto"
}
```

**Example:**

```bash
curl -X POST http://localhost:8082/v1/files/public \
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
curl -X POST http://localhost:8082/v1/files/public/get \
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
  "payment_mode_used": "auto"
}
```

**Example:**

```bash
curl -X POST http://localhost:8082/v1/files \
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
curl -X POST http://localhost:8082/v1/files/get \
  -H "Content-Type: application/json" \
  -d '{"data_map":"<hex_encoded_datamap>","dest_path":"/absolute/path/to/downloaded.pdf"}'
```

### Estimate File Cost

**Endpoint:** `POST /v1/files/cost`

Estimates upload cost for a local file.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `is_public` | boolean | No | Defaults to `true` |
| `payment_mode` | string | No | `auto`, `merkle`, or `single` |

**Response:**

```json
{
  "cost": "<atto_token_amount>",
  "file_size": <bytes>,
  "chunk_count": <chunk_count>,
  "estimated_gas_cost_wei": "<wei_amount>",
  "payment_mode": "auto"
}
```

**Example:**

```bash
curl -X POST http://localhost:8082/v1/files/cost \
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
curl http://localhost:8082/v1/wallet/address
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
curl http://localhost:8082/v1/wallet/balance
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
curl -X POST http://localhost:8082/v1/wallet/approve \
  -H "Content-Type: application/json" \
  -d '{}'
```

## External signer flow

### Prepare a Data Upload

**Endpoint:** `POST /v1/data/prepare`

Prepares an in-memory data upload for external signing.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `data` | string | Yes | Base64-encoded payload |
| `visibility` | string | No | `"private"` (default) or `"public"`. When `"public"`, the serialized DataMap is bundled into the same external-signer payment batch and published on-network on finalize; `data_map_address` is then present in the finalize response. |

**Response:**

The response varies by `payment_type`.

The daemon starts uploads of 64 or more chunks on the Merkle path and smaller uploads on the wave-batch path. The initial selection is not final: when the already-stored preflight leaves fewer than 64 chunks to pay for, or too few Merkle-capable peers are reachable, the daemon prepares a wave-batch payment instead. Clients must branch on the returned `payment_type`, not on the submitted chunk count.

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

Merkle variant:

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

Each `pool_commitments` entry contains exactly 16 candidate payments. The example above shows one candidate for brevity.

`merkle_batches` holds one entry per on-chain payment. A single Merkle tree covers up to 256 fresh chunks (roughly 1 GiB); a larger upload splits across several batches, and the external signer calls `payForMerkleTree2()` once per entry. The top-level `depth`, `pool_commitments`, and `merkle_payment_timestamp` are legacy single-batch fields, present only when `merkle_batches` has exactly one entry and mirroring that entry. They are omitted for a multi-batch upload, so read payment details from `merkle_batches`.

Both variants include `total_chunks` and `already_stored_count`. `total_chunks` is the full chunk count for the upload, including chunks already on-network; `already_stored_count` is how many of those were already stored and so excluded from payment and from the PUT. The difference between the two counts is why a prepared upload can cost less than the raw file size implies; use it for reconciliation only, and construct the payment from the returned `payments` or `merkle_batches` entries.

**Example:**

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/prepare \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"
```

### Prepare a File Upload

**Endpoint:** `POST /v1/upload/prepare`

Prepares a file upload for external signing.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `path` | string | Yes | Local file path |
| `visibility` | string | No | `"private"` (default) or `"public"`. `"public"` bundles the serialized DataMap chunk into the same payment batch and stores it on-network; its address is returned on finalize via `data_map_address`. |

**Response:** Same `payment_type`-based shape as `POST /v1/data/prepare`

**Example:**

```bash
curl -X POST http://localhost:8082/v1/upload/prepare \
  -H "Content-Type: application/json" \
  -d '{"path":"/absolute/path/to/document.pdf"}'
```

### Finalize an Upload

**Endpoint:** `POST /v1/upload/finalize`

Finalizes a prepared upload after the external signer has submitted the matching payment transaction.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `upload_id` | string | Yes | Value returned by a prepare endpoint |
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

`address` is only present when `store_data_map` is `true`; that path uses the daemon's own wallet to store the DataMap. `data_map_address` is only present when the upload was prepared with `visibility:"public"`; it is the network address of the bundled DataMap chunk whose payment was included in the same external-signer batch as the data chunks.

**Examples:**

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{"0xquote":"0xtx"},"store_data_map":true}'
```

Wave-batch upload where every chunk is already stored, so prepare reported no `payments`:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","tx_hashes":{}}'
```

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hash":"0x...","store_data_map":true}'
```

Multi-batch Merkle upload, one winner hash per `merkle_batches` entry:

```bash
curl -X POST http://localhost:8082/v1/upload/finalize \
  -H "Content-Type: application/json" \
  -d '{"upload_id":"<hex_id>","winner_pool_hashes":["0x...","0x..."],"store_data_map":true}'
```

When part of an upload stores but the rest misses quorum after retries, finalize returns `502` with the `PARTIAL_UPLOAD` code and machine-readable counts:

```json
{
  "error": "Partial upload: 200/256 chunks stored, 56 failed after retries: ...",
  "code": "PARTIAL_UPLOAD",
  "chunks_stored": 200,
  "chunks_failed": 56,
  "total_chunks": 256
}
```

The stored chunks persist. Re-prepare the same content and finalize again to pay for and store only the missing remainder.

A partial upload is reported only when at least one Merkle batch was paid. When every `winner_pool_hashes` slot is empty, finalize returns `402` with the `PAYMENT_REQUIRED` code instead.

## Error codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `400` | Bad request | Check base64 encoding, address length, data map format, and local paths |
| `402` | Payment required | Fund the configured wallet or reduce the upload size. On external-signer finalize: no Merkle batch was paid, so pay at least one batch |
| `404` | Not found | Check the address or `upload_id` |
| `413` | Payload too large | Split the upload or switch to file endpoints |
| `500` | Internal server error | Check daemon logs and retry |
| `502` | Network unreachable | Confirm the daemon can reach the Autonomi network |
| `502` (`PARTIAL_UPLOAD`) | Some chunks stored, others failed quorum after retries | Re-prepare the same content and finalize again to store only the remainder; the response carries `chunks_stored`, `chunks_failed`, and `total_chunks` |
| `503` | Service unavailable | Configure a wallet before calling wallet or write endpoints |

## Related pages

- [Build with the SDKs](../install.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Store Data on the Network](../store-data-on-the-network.md)
- [Store and Retrieve Data with the SDKs](../how-to-guides/store-and-retrieve-data.md)
