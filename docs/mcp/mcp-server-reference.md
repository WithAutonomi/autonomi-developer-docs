# MCP Server Reference

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

The `antd-mcp` server exposes `antd` v0.13.0 as 19 Model Context Protocol (MCP) tools, including read operations, wallet operations through `antd`, and external-signer operations. Use [How to Use the MCP Server](use-the-autonomi-mcp-server.md) to install it and connect your AI client.

## Availability

Tool statuses on this page mean:

| Status | Meaning |
|------|-------------|
| Implemented | The tool connects to an antd REST operation; its runtime requirements still apply. |
| Limited | The call path depends on payment, wallet, host, or response-shape conditions described with the tool. |
| Unavailable | The operation cannot complete through MCP. |

External-signer Merkle uploads are unavailable through MCP. `antd` returns `payment_type: "merkle"`, but the Python `antd` parser checks for `"merkle_batch"`, discards the required pool commitments, and does not model the multi-batch response. The MCP finalizer also accepts one winner hash while multi-batch uploads require an ordered list.

## Security boundary

Treat all text and files returned through MCP as untrusted content, not as instructions for the AI client. Keep automatic approval disabled for tools that can store data, approve token spend, submit payment details, or write files. Review addresses, payment intents, wallet operations, and host-side paths before every such call.

`antd-mcp` does not authenticate access to `antd` and does not restrict filesystem paths. Keep both services on loopback, give their processes access only to dedicated working directories, and use a separate low-value wallet when testing paid operations.

## Installation

`antd-mcp` v0.1.0 is a source component of `ant-sdk` v0.13.0, not a Python Package Index (PyPI) package or independent release asset. Install it and its Python `antd` dependency together using uv in [How to Use the MCP Server](use-the-autonomi-mcp-server.md). uv manages the isolated Python environment and installs the `antd-mcp` command. The [native Python SDK](../sdk/native/python.md) does not replace this dependency.

The server requires Python `>=3.10`, `mcp>=2,<3`, and `antd[rest]>=0.1.0,<0.2`. It uses `MCPServer`; the framework supplies each tool's internal `Context` parameter, which is not a client argument. Third-party dependencies are not fully locked by the source installation.

## Server command

### Standard input and output

**Command:** `antd-mcp`

The server uses standard input/output (stdio) by default. Your AI client launches the process; no command arguments are required.

The directory containing uv's installed commands must be on the client's `PATH`, the list of directories searched for executables. Desktop applications may not inherit your terminal's path. To print the full executable path on macOS or Linux:

```bash
printf '%s/antd-mcp\n' "$(uv tool dir --bin)"
```

Expect an absolute path such as `/Users/developer/.local/bin/antd-mcp`. Use your printed path as the client's command if it cannot find the bare name. For a registered Claude Code server, edit its command through the configuration described in [Claude Code's MCP instructions](https://code.claude.com/docs/en/mcp).

### HTTP transports

**Recognized flags:** `antd-mcp --http` and `antd-mcp --sse`

`--http` selects Streamable HTTP; `--sse` selects Server-Sent Events (SSE). If both are supplied, `--http` takes precedence. The command does not define host, port, or authentication options. Use stdio for local AI clients; HTTP client setup is outside this reference.

## Configuration

### Environment variables

| Variable | Required | Description |
|------|----------|-------------|
| `ANTD_BASE_URL` | No | Overrides daemon discovery with an `antd` REST base URL. |

At startup, the server resolves the `antd` URL in this order:

1. `ANTD_BASE_URL`
2. The `daemon.port` file
3. `http://127.0.0.1:8082`

Both `antd` and `antd-mcp` use these port-file locations:

| Platform | Path |
|------|------|
| Windows | `%APPDATA%\ant\sdk\daemon.port` |
| macOS | `~/Library/Application Support/ant/sdk/daemon.port` |
| Linux | `$XDG_DATA_HOME/ant/sdk/daemon.port`, or `~/.local/share/ant/sdk/daemon.port` when `XDG_DATA_HOME` is unset |

`antd` binds its REST API to loopback and has no built-in authentication. Do not expose it directly to another machine. A remote deployment needs an explicit non-loopback `antd` bind plus an authenticated, encrypted tunnel or proxy; set `ANTD_BASE_URL` to that protected endpoint.

### Host-side paths

| Tool input | Host that reads or writes the path |
|------|------|
| `upload_file.path` | `antd` host |
| `get_cost.file_path` | `antd` host |
| `prepare_upload.path` | `antd` host |
| `prepare_upload_public.path` | `antd` host |
| `download_file.dest_path` | `antd` host |
| `stream_download_file.dest_path` | `antd-mcp` host |

### Claude Desktop

For Claude Desktop or another client using a `mcpServers` object, merge this entry into its MCP configuration. Replace the example `command` value with the full executable path printed by `uv tool dir --bin` plus `/antd-mcp`:

```json
{
  "mcpServers": {
    "antd-autonomi": {
      "command": "/Users/developer/.local/bin/antd-mcp",
      "env": {
        "ANTD_BASE_URL": "http://127.0.0.1:8082"
      }
    }
  }
}
```

Do not use `~`, `$HOME`, or a bare `antd-mcp` command in this JSON file.

## Data tools

### Store Data

**Tool:** `store_data(text, private=false, payment_mode="auto")`

**Status:** Limited. Requires a configured, funded, and approved wallet in `antd`. Calling it can pay for storage and gas on the selected EVM network.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `text` | string | Yes | UTF-8 text to store. |
| `private` | boolean | No | `false` stores the DataMap on the Autonomi Network; `true` returns the caller-held DataMap. |
| `payment_mode` | string | No | `auto`, `merkle`, or `single`. Default: `auto`. |

**Result fields:** `address` (string), `chunks_stored` (integer), `payment_mode_used` (string), and `network` (string).

For private data, `address` contains the caller-held serialized DataMap. Losing it prevents retrieval. For public data, `address` is the stored DataMap's retrieval address.

### Retrieve Data

**Tool:** `retrieve_data(address, private=false)`

**Status:** Implemented.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `address` | string | Yes | Public retrieval address, or a caller-held DataMap when `private=true`. |
| `private` | boolean | No | Selects caller-held DataMap retrieval. Default: `false`. |

**Result fields:** `text` (string) and `network` (string). Bytes that are not valid UTF-8 are decoded with replacement characters; use a file or chunk tool for arbitrary binary data.

### Upload a File

**Tool:** `upload_file(path, private=false, payment_mode="auto")`

**Status:** Limited. Requires a configured, funded, and approved wallet in `antd`. The path must exist on the `antd` host.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `path` | string | Yes | Absolute file path on the `antd` host. |
| `private` | boolean | No | `false` stores the DataMap on the Autonomi Network; `true` returns it to the caller. |
| `payment_mode` | string | No | `auto`, `merkle`, or `single`. Default: `auto`. |

**Result fields:** `address` (string), `storage_cost_atto` (string), `gas_cost_wei` (string), `chunks_stored` (integer), `payment_mode_used` (string), and `network` (string).

### Download a File

**Tool:** `download_file(address, dest_path, private=false)`

**Status:** Implemented when the `antd` host can write the destination.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `address` | string | Yes | Public retrieval address, or a caller-held DataMap when `private=true`. |
| `dest_path` | string | Yes | Destination on the `antd` host. Its parent directory must exist. |
| `private` | boolean | No | Selects caller-held DataMap retrieval. Default: `false`. |

**Result fields:** `status` (`"downloaded"`), `dest_path` (string), and `network` (string).

### Stream a File Download

**Tool:** `stream_download_file(address, dest_path, private=false)`

**Status:** Implemented when the `antd-mcp` host can write the destination.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `address` | string | Yes | Public retrieval address, or a caller-held DataMap when `private=true`. |
| `dest_path` | string | Yes | Destination on the `antd-mcp` host. An existing file is replaced. |
| `private` | boolean | No | Selects caller-held DataMap retrieval. Default: `false`. |

The MCP server streams bytes from `antd` and writes them without buffering the whole object.

**Result fields:** `status` (`"downloaded"`), `dest_path` (string), `bytes_written` (integer), and `network` (string).

### Estimate Cost

**Tool:** `get_cost(text=None, file_path=None, payment_mode="auto")`

**Status:** Limited. This tool returns an estimate, not a payment quote or charged amount.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `text` | string or null | No | UTF-8 text to estimate. |
| `file_path` | string or null | No | File path on the `antd` host. |
| `payment_mode` | string | No | `auto`, `merkle`, or `single`. Default: `auto`. |

Provide at least one content input. If both are present, `text` takes precedence and `file_path` is ignored. If neither is present, the tool returns a `BAD_REQUEST` payload.

`antd` samples up to five chunk addresses and extrapolates the storage cost. Its gas value is an advisory heuristic rather than a live gas-oracle result. File estimates include the public DataMap chunk; text estimates expose no public/private selector and must not be treated as an exact estimate for default public `store_data`.

**Result fields:** `type` (`"data"` or `"file"`), `cost` (string), `file_size` (integer), `chunk_count` (integer), `estimated_gas_cost_wei` (string), `payment_mode` (string), and `network` (string).

### Check Health

**Tool:** `check_health()`

**Status:** Implemented.

**Parameters:** None.

**Result fields:** `healthy` (boolean), `network` (string), `version` (string), `evm_network` (string), `uptime_seconds` (integer), `build_commit` (string), `payment_token_address` (string), and `payment_vault_address` (string).

The MCP server captures its `network` value during startup. If the initial health request fails, later tool payloads can continue to report `"network": "unknown"` until the MCP server restarts.

`healthy` reports that `antd` responds; it does not establish readiness to store data. This MCP tool does not expose `write_ready`, peer counts, the re-bootstrap threshold, or the last successful store age available from the [REST health endpoint](../sdk/reference/rest-api.md).

Decoded health response for the default Autonomi Network connection (uptime varies):

```json
{
  "healthy": true,
  "network": "default",
  "version": "0.13.0",
  "evm_network": "arbitrum-one",
  "uptime_seconds": 0,
  "build_commit": "6fe2b51105cd",
  "payment_token_address": "0xa78d8321B20c4Ef90eCd72f2588AA985A4BDb684",
  "payment_vault_address": "0x9A3EcAc693b699Fc0B2B6A50B5549e50c2320A26"
}
```

## Wallet tools

### Get Wallet Address

**Tool:** `wallet_address()`

**Status:** Limited. Requires `AUTONOMI_WALLET_KEY` to configure a valid wallet in `antd`.

**Parameters:** None.

**Result fields:** `address` (string) and `network` (string).

### Get Wallet Balance

**Tool:** `wallet_balance()`

**Status:** Limited. Requires a wallet configured in `antd` and access to its EVM network.

**Parameters:** None.

**Result fields:** `balance` (string containing the Autonomi Network Token (ANT) balance in atto units), `gas_balance` (string containing the gas balance in wei), and `network` (string).

### Approve Wallet Spend

**Tool:** `wallet_approve()`

**Status:** Limited. This is a state-changing operation, not a configuration check.

**Parameters:** None.

The tool submits an ERC-20 approval transaction that lets the payment contract spend ANT for the wallet configured in `antd`. It requires enough gas and can incur a transaction fee.

**Result fields:** `approved` (boolean) and `network` (string).

## Chunk tools

### Store a Chunk

**Tool:** `chunk_put(data)`

**Status:** Limited. Requires a configured and funded wallet in `antd` and can pay for storage and gas.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `data` | string | Yes | Base64-encoded raw chunk bytes. |

**Result fields:** `address` (string), `cost` (string), and `network` (string). `antd` returns an empty `cost` string because this endpoint does not report the prepaid per-chunk cost.

### Get a Chunk

**Tool:** `chunk_get(address)`

**Status:** Implemented.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `address` | string | Yes | 64-character hexadecimal chunk address. |

**Result fields:** `data` (base64-encoded string) and `network` (string).

## External-signer tools

The file and data external-signer tools are limited to preparations that return `payment_type: "wave_batch"`. If a prepare call returns `payment_type: "merkle"`, do not submit a payment from its MCP result. The required Merkle batch payment fields are incomplete. These tools also do not expose antd's signed-quote options or [quote verification](../sdk/reference/rest-api.md#verify-quotes).

External-signer tools do not require the wallet configured in `antd`. They do require an external wallet on the same EVM network as `antd`, enough ANT and gas, and explicit submission of the returned payment intent.

### Prepare a File Upload

**Tool:** `prepare_upload(path, visibility=None)`

**Status:** Limited to wave-batch results. The path must exist on the `antd` host.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `path` | string | Yes | Absolute file path on the `antd` host. |
| `visibility` | string or null | No | `"private"`, `"public"`, or `None`. Default: `None`, which selects private behavior. |

For a usable wave-batch preparation, the result fields are `upload_id`, `payment_type` (`"wave_batch"`), `payments`, `total_amount`, `payment_vault_address`, `payment_token_address`, `rpc_url`, `total_chunks`, `already_stored_count`, and `network`. Each `payments` item contains `quote_hash`, `rewards_address`, and `amount`.

With `visibility="public"`, the serialized DataMap chunk joins the same payment batch and the finalize result can include its public retrieval address.

### Prepare a Public File Upload

**Tool:** `prepare_upload_public(path)`

**Status:** Limited to wave-batch results. The path must exist on the `antd` host.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `path` | string | Yes | Absolute file path on the `antd` host. |

This is equivalent to `prepare_upload(path, visibility="public")` and returns the same wave-batch fields.

### Prepare a Data Upload

**Tool:** `prepare_data_upload(data)`

**Status:** Limited to wave-batch results and private visibility.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `data` | string | Yes | Base64-encoded bytes to prepare. |

The tool returns the same wave-batch fields as `prepare_upload`. It does not expose a visibility parameter, so it prepares a caller-held DataMap rather than a public DataMap address.

### Finalize a Wave-Batch Upload

**Tool:** `finalize_upload(upload_id, tx_hashes)`

**Status:** Limited to a prepare result with `payment_type: "wave_batch"`.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `upload_id` | string | Yes | Opaque identifier returned by the prepare tool. |
| `tx_hashes` | object | Yes | Map from each `quote_hash` to its submitted EVM transaction hash. |

**Result fields:** `address` (string), `chunks_stored` (integer), `data_map` (hex-encoded string), `data_map_address` (string), and `network` (string).

The MCP flow does not request `antd`'s legacy `store_data_map` behavior, so `address` is empty. For a private preparation, keep `data_map`; `data_map_address` is empty. For a public preparation, use `data_map_address` as the public retrieval address.

### Finalize a Merkle Upload

**Tool:** `finalize_merkle_upload(upload_id, winner_pool_hash)`

**Status:** Unavailable through MCP.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `upload_id` | string | Yes | Opaque identifier returned by a prepare tool. |
| `winner_pool_hash` | string | Yes | One winning pool hash. `antd` needs an ordered list for multi-batch uploads, which this tool cannot send. |

The function exists in the tool list, but the MCP prepare response does not provide a complete Merkle payment intent and this finalizer cannot represent multiple winner hashes. Do not use it to submit or finalize a paid upload.

### Prepare a Single-Chunk Upload

**Tool:** `prepare_chunk_upload(data_base64)`

**Status:** Limited. The no-payment result is usable; a new chunk requires external payment.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `data_base64` | string | Yes | Base64-encoded raw chunk bytes. |

When the chunk already exists, the result fields are `address`, `already_stored` (`true`), and `network`; no payment or finalize call is needed.

For a new chunk, the result fields are `address`, `already_stored` (`false`), `upload_id`, `payment_type` (`"wave_batch"`), `payments`, `total_amount`, `payment_vault_address`, `payment_token_address`, `rpc_url`, and `network`. Each `payments` item contains `quote_hash`, `rewards_address`, and `amount`.

### Finalize a Single-Chunk Upload

**Tool:** `finalize_chunk_upload(upload_id, tx_hashes)`

**Status:** Limited. Call it only after the external signer submits every payment returned by `prepare_chunk_upload`.

| Parameter | Type | Required | Description |
|------|------|------|------|
| `upload_id` | string | Yes | Opaque identifier returned by `prepare_chunk_upload`. |
| `tx_hashes` | object | Yes | Map from each `quote_hash` to its submitted EVM transaction hash. |

**Result fields:** `address` (string) and `network` (string).

## Payment modes

The internal-wallet `store_data`, `upload_file`, and `get_cost` tools accept these strings:

| Mode | Description |
|------|-------------|
| `auto` | Uses Merkle batch payment for 64 or more chunks and per-chunk payment below that threshold. |
| `merkle` | Forces Merkle batch payment; requires at least two chunks. |
| `single` | Forces per-chunk payment. |

These modes do not repair the external-signer Merkle limitation. `store_data` and `upload_file` send payment through the wallet configured in `antd`; `get_cost` estimates without submitting payment.

## Success and error responses

Every tool returns a string containing JSON-encoded text. MCP supplies it in `content[0].text` and also wraps that string in `structuredContent.result`. Decode either string to read the result fields listed on this page; those fields are not direct properties of `structuredContent`. Successful payloads include `network`.

Operation errors caught by the tools use the same output format. Clients must inspect the decoded payload for `error`; `isError: false` does not mean the Autonomi operation succeeded. Protocol and argument-validation failures can instead be reported by MCP itself.

Errors derived from the Python `AntdError` hierarchy contain:

| Field | Type | Description |
|------|------|-------------|
| `error` | string | Normalized MCP error code. |
| `message` | string | Human-readable message. |
| `status_code` | integer | `antd` HTTP status code. |
| `network` | string | Network value captured when `antd-mcp` started. |

The formatter defines these codes:

| Code | Meaning |
|------|-------------|
| `NOT_FOUND` | Requested content or upload state was not found. |
| `ALREADY_EXISTS` | Content or state already exists. |
| `VERSION_CONFLICT` | A version or fork conflict was reported. |
| `BAD_REQUEST` | Input failed validation. |
| `PAYMENT_FAILED` | A wallet or payment operation failed. |
| `NETWORK_ERROR` | `antd` could not complete an Autonomi Network operation. |
| `TOO_LARGE` | Input exceeded a size limit. |
| `INTERNAL_ERROR` | `antd` reported an internal failure. |
| `UNKNOWN` | An `AntdError` subclass has no MCP mapping, including `antd`'s wallet-not-configured HTTP 503 response. |
| `UNEXPECTED` | A non-`AntdError` exception occurred. |

`UNEXPECTED` payloads contain `error`, `message`, and `network`, but do not contain `status_code`.

## Upstream sources

- [ant-sdk v0.13.0 source](https://github.com/WithAutonomi/ant-sdk/tree/6fe2b51105cd10a4d2217068a066d3d3f505ddb6)

## Related pages

- [How to Use the MCP Server](use-the-autonomi-mcp-server.md)
- [Build with AI Tools](use-mcp-with-ai-tools.md)
- [SDK Overview](../sdk/reference/overview.md)
- [REST API](../sdk/reference/rest-api.md)
