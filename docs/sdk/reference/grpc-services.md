# gRPC Services

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 7a113b390522d76d28b8f3e5b4078f9c9418d46f
  verified_date: 2026-05-26
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

### Stream Public

**Signature:** `StreamPublic(StreamPublicDataRequest) -> stream DataChunk`

This RPC is exposed, but the handler returns `UNIMPLEMENTED`.

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

Estimates file upload cost. Accepts an optional `payment_mode` field (`"auto"`, `"merkle"`, or `"single"`).

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

The proto files define these shared shapes:

| Message | Fields |
|------|--------|
| `Cost` | `atto_tokens`, `file_size`, `chunk_count`, `estimated_gas_cost_wei`, `payment_mode` |
| `HealthCheckResponse` | `status`, `network`, `version`, `evm_network`, `uptime_seconds`, `build_commit`, `payment_token_address`, `payment_vault_address` |
| `PutPublicDataResponse` | `cost`, `address` |
| `PutDataResponse` | `cost`, `data_map` |
| `PutFilePublicResponse` | `address`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, `payment_mode_used` |
| `PutFileResponse` | `data_map`, `storage_cost_atto`, `gas_cost_wei`, `chunks_stored`, `payment_mode_used` |
| `GetFilePublicRequest` | `address`, `dest_path` |
| `GetFileRequest` | `data_map`, `dest_path` |
| `GetDataRequest` | `data_map` |

## Related pages

- [REST API](rest-api.md)
- [SDK Overview](overview.md)
- [How Language Bindings Work](language-bindings/overview.md)
