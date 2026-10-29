# CLI Command Reference

<!-- verification:
  source_repo: ant-client
  source_ref: ant-cli-v0.3.12
  source_commit: 6096b1c8caf6688d6825fcb9ff61fa1b590d984b
  verified_date: 2026-10-29
  verification_mode: target-manifest
-->

Reference for the released `ant` CLI command tree and its flags. The option tables stay grouped by command family for easier scanning. Hidden or advanced flags are called out where they matter for troubleshooting.

## Command tree

```text
ant
├── node
│   ├── add
│   ├── daemon
│   │   ├── start
│   │   ├── stop
│   │   ├── status
│   │   └── info
│   ├── dismiss
│   ├── logs
│   │   └── forward
│   │       ├── enable
│   │       ├── disable
│   │       └── status
│   ├── reset
│   ├── start
│   ├── status
│   └── stop
├── wallet
│   ├── address
│   └── balance
├── file
│   ├── upload
│   ├── download
│   └── cost
├── chunk
│   ├── put
│   └── get
├── pointer
│   ├── keygen
│   ├── address
│   ├── create
│   ├── update
│   ├── transfer
│   ├── finality
│   ├── controller
│   ├── get
│   └── resolve
├── manifest
│   ├── create
│   ├── list
│   ├── show
│   ├── link
│   ├── export
│   └── download
└── update
```

## Root command and global flags

### Root command

**Command:** `ant [OPTIONS] <COMMAND>`

The root command accepts flags used across data and node operations. Connection and payment flags must appear before the subcommand. The global `--json` flag can appear before or after it.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--json` | boolean | No | Request structured JSON from commands that support it. Wallet and chunk commands keep their normal text or raw-byte output. |
| `-b, --bootstrap <ADDRESS>` | multiaddress list | No | QUIC bootstrap peers for data operations. Can be comma-separated or repeated. Legacy `IP:PORT` values are accepted. |
| `--devnet-manifest <PATH>` | path | No | Path to a local devnet manifest JSON file |
| `--allow-loopback` | boolean | No | Allow loopback connections for local devnet or local testing |
| `--ipv4-only` | boolean | No | Disable dual-stack and force IPv4-only mode |
| `--quote-timeout-secs <N>` | integer | No | Hidden. Controls lightweight network-operation timeouts such as DHT lookups. |
| `--store-timeout-secs <N>` | integer | No | Hidden. Sets `ClientConfig.store_timeout_secs`. Non-Merkle chunk PUT response timeout is set by an internal `STORE_RESPONSE_TIMEOUT` constant; Merkle batch PUT timeout is set by `merkle_store_timeout_secs` (270 s default, library-only); chunk GET timeout is set by `--chunk-get-timeout-secs`. |
| `--chunk-get-timeout-secs <N>` | integer | No | Hidden. Per-peer response timeout for chunk retrieve operations. Default 10 s. |
| `--quote-concurrency <N>` | integer | No | Hidden and deprecated. Caps the adaptive quote channel only, except that the legacy default `32` is ignored. It does not affect store or download concurrency. |
| `--store-concurrency <N>` | integer | No | Hidden and deprecated. Caps the adaptive store channel only, except that the legacy default `8` is ignored. `--chunk-concurrency` is accepted as an alias. |
| `-v, --verbose...` | count | No | Increase log verbosity: `-v`, `-vv`, or `-vvv` |
| `--evm-network <NET>` | string | No | EVM network for payments: `arbitrum-one`, `arbitrum-sepolia`, or `local`. Defaults to `arbitrum-one`, except when a devnet manifest that carries an EVM block is loaded. |
| `-h, --help` | boolean | No | Print help |
| `-V, --version` | boolean | No | Print version |

When you load a devnet manifest that carries an EVM block, set `--evm-network` explicitly. Pass `local` to use the manifest's EVM configuration, or pass `arbitrum-one` or `arbitrum-sepolia` to override it. Omitting the flag is rejected so a payment cannot silently target the wrong network. Selecting a preset alongside such a manifest prints a warning that the manifest's EVM configuration is ignored. A manifest without an EVM block, or a run with no manifest, still defaults to `arbitrum-one`.

**Environment:**

| Variable | Description |
|------|------|
| `SECRET_KEY` | Required for wallet commands, file and chunk uploads, pointer writes, manifest creation that uploads files, and every manifest export using `--compact` |

**Example:**

```bash
ant --help
```

## File commands

### Upload a file

**Command:** `ant file upload <PATH>`

Uploads a file with self-encryption and EVM payment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PATH` | path | Yes | File to upload |
| `--public` | boolean | No | Store the DataMap on the Autonomi Network so anyone with the address can download the file |
| `--merkle` | boolean | No | Force Merkle batch payment |
| `--no-merkle` | boolean | No | Force single per-chunk payments |
| `--store-timeout <N>` | integer | No | Hidden legacy option. Overrides `ClientConfig.store_timeout_secs` for this invocation, but does not govern upload PUT timeouts. |
| `--store-concurrency <N>` | integer | No | Hidden and deprecated. Caps the adaptive store channel for this upload, except that the legacy default `8` is ignored. |
| `--overwrite` | boolean | No | Replace any existing `<filename>.datamap` instead of writing a suffixed `<filename>-2.datamap`. |

**Example:**

```bash
ant file upload photo.jpg --public
```

After a successful upload, the CLI attempts to record the file in the local manifest history. The normal output includes the file's SHA-256 and, when the history record can be written, an ID you can pass to `ant manifest download`. If the history write fails, the CLI warns you without changing the successful upload result.

### Download a file

**Command:** `ant file download [ADDRESS]`

Downloads a public file by address or a private file using a local DataMap file.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | string | Conditionally | Public DataMap address as 64 hexadecimal characters or an `ant://ADDRESS` link. Required unless `--datamap` is provided. |
| `--datamap <PATH>` | path | No | Local `.datamap` file for private download |
| `-o, --output <PATH>` | path | No | Output path. Defaults to the hexadecimal address for address-based downloads, or to the original filename inferred from a `.datamap` filename. |
| `--peers <COUNT>` | integer | No | Number of closest peers to try for each chunk fetch. Accepts a positive integer. `--peer-count` is accepted as an alias. |
| `--all-peers` | boolean | No | Diagnostic mode: download the file as usual, then fetch each chunk from every selected closest peer and print ranked per-peer results. `--try-all-peers` is accepted as an alias. The number of closest peers swept per chunk comes from `--peers`, defaulting to the client close group size. With `--json`, the per-peer results are emitted as a `chunk_peer_check` object on the download result. |
| `--download-diagnostics <PATH>` | path | No | Write one JSON Lines record per normal chunk-fetch attempt. Cannot be combined with `--all-peers`. |

**Example:**

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg
```

The output path is your local filename. In this example, the command downloads a public JPEG of Lucky the dog and saves it as `lucky.jpg`.

Private DataMap example:

```bash
ant file download --datamap photo.jpg.datamap
```

Diagnostic example (download, then rank closest-peer results for each chunk):

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg --all-peers --peers 5
```

### Estimate file cost

**Command:** `ant file cost <PATH>`

Estimates the upload cost for a file without uploading it. The command encrypts the file locally to determine its chunk count and queries the Autonomi Network for prices. It does not require a wallet or make a payment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PATH` | path | Yes | File to estimate |
| `--merkle` | boolean | No | Force Merkle batch payment mode for the estimate |
| `--no-merkle` | boolean | No | Force single payment mode for the estimate |

**Example:**

```bash
ant file cost photo.jpg --merkle
```

## Commands for chunks

### Store a chunk

**Command:** `ant chunk put [FILE]`

Stores a single chunk from a file or from standard input.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `FILE` | path | No | Input file. If omitted, `ant` reads from standard input. |

**Example:**

```bash
printf 'hello Autonomi\n' | ant chunk put
```

### Retrieve a chunk

**Command:** `ant chunk get <ADDRESS>`

Retrieves a single chunk by address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | string | Yes | Hex-encoded chunk address (64 hex characters) |
| `-o, --output <PATH>` | path | No | Write the chunk to a file instead of stdout |
| `--all-peers` | boolean | No | Diagnostic mode: try every selected closest peer and print ranked per-peer results. Bytes for the chunk are only written when `-o`/`--output` is also supplied. |
| `--peer-count <N>` | integer | No | Diagnostic mode only. Number of closest peers to try with `--all-peers`. Requires `--all-peers`. |

**Example:**

```bash
: "${CHUNK_ADDRESS:?Set CHUNK_ADDRESS to a 64-character chunk address}"
ant chunk get "$CHUNK_ADDRESS" -o chunk.bin
```

Diagnostic example (try all closest peers and rank results):

```bash
: "${CHUNK_ADDRESS:?Set CHUNK_ADDRESS to a 64-character chunk address}"
ant chunk get "$CHUNK_ADDRESS" --all-peers --peer-count 5
```

## Pointer commands

Pointers are owner-signed mutable references. Generating a key and deriving its pointer address are offline operations. Creating, updating, and transferring a pointer are paid operations that require `SECRET_KEY` for the payment wallet. A transfer is irreversible after its final state is stored.

Protect every generated key file. A pointer's owner key cannot be changed.

### Generate an owner key

**Command:** `ant pointer keygen --output <PATH>`

Creates an ML-DSA-65 owner key file offline. The command refuses to overwrite an existing file.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `-o, --output <PATH>` | path | Yes | File to create for the owner key. |

**Example:**

```bash
ant pointer keygen --output pointer-owner.key
```

### Show a pointer address

**Command:** `ant pointer address --key <PATH>`

Derives the pointer address owned by a key file without connecting to the Autonomi Network.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `-k, --key <PATH>` | path | Yes | Owner key file. |

**Example:**

```bash
ant pointer address --key pointer-owner.key
```

### Create a pointer

**Command:** `ant pointer create --key <PATH> [--kind <KIND>] <TARGET>`

Creates the pointer owned by the key and pays to store its first target. The command refuses before payment if the pointer already exists.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `-k, --key <PATH>` | path | Yes | Owner key file. |
| `TARGET` | hexadecimal string | Yes | 64-character target address. |
| `--kind <KIND>` | string | No | Target type: `chunk` or `pointer`. Default `chunk`. |

**Example:**

```bash
: "${SECRET_KEY:?Set SECRET_KEY to the payment wallet private key}"
: "${TARGET_ADDRESS:?Set TARGET_ADDRESS to a 64-character target address}"
ant pointer create --key pointer-owner.key --kind chunk "$TARGET_ADDRESS"
```

### Update a pointer

**Command:** `ant pointer update --key <PATH> [--kind <KIND>] <TARGET>`

Pays to store a new target for the pointer owned by the key.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `-k, --key <PATH>` | path | Yes | Owner key file. |
| `TARGET` | hexadecimal string | Yes | 64-character target address. |
| `--kind <KIND>` | string | No | Target type: `chunk` or `pointer`. Default `chunk`. |

**Example:**

```bash
: "${SECRET_KEY:?Set SECRET_KEY to the payment wallet private key}"
: "${TARGET_ADDRESS:?Set TARGET_ADDRESS to a 64-character target address}"
ant pointer update --key pointer-owner.key --kind chunk "$TARGET_ADDRESS"
```

### Transfer a pointer

**Command:** `ant pointer transfer --key <PATH> <RECIPIENT>`

Pays to store a final state that permanently hands control to another pointer. Before paying, the command refuses if the pointer is already final, the recipient does not exist, or the recipient leads back to this pointer.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `-k, --key <PATH>` | path | Yes | Owner key file. |
| `RECIPIENT` | hexadecimal string | Yes | 64-character address of the recipient pointer. |

**Example:**

```bash
: "${SECRET_KEY:?Set SECRET_KEY to the payment wallet private key}"
: "${RECIPIENT_POINTER:?Set RECIPIENT_POINTER to the recipient pointer address}"
ant pointer transfer --key pointer-owner.key "$RECIPIENT_POINTER"
```

### Check pointer finality

**Command:** `ant pointer finality <ADDRESS>`

Asks the close group whether one final state has majority agreement with no rival. Check this before relying on a transfer.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | hexadecimal string | Yes | 64-character pointer address. |

**Example:**

```bash
: "${POINTER_ADDRESS:?Set POINTER_ADDRESS to a 64-character pointer address}"
ant pointer finality "$POINTER_ADDRESS"
```

### Find the controlling pointer

**Command:** `ant pointer controller <ADDRESS>`

Follows transfers to the pointer whose owner controls resolution.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | hexadecimal string | Yes | 64-character pointer address. |

**Example:**

```bash
: "${POINTER_ADDRESS:?Set POINTER_ADDRESS to a 64-character pointer address}"
ant pointer controller "$POINTER_ADDRESS"
```

### Read a pointer

**Command:** `ant pointer get <ADDRESS>`

Reads one pointer record without following its target.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | hexadecimal string | Yes | 64-character pointer address. |

**Example:**

```bash
: "${POINTER_ADDRESS:?Set POINTER_ADDRESS to a 64-character pointer address}"
ant pointer get "$POINTER_ADDRESS"
```

### Resolve a pointer chain

**Command:** `ant pointer resolve <ADDRESS>`

Follows a pointer chain and prints the target at its end.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | hexadecimal string | Yes | 64-character pointer address. |

**Example:**

```bash
: "${POINTER_ADDRESS:?Set POINTER_ADDRESS to a 64-character pointer address}"
ant pointer resolve "$POINTER_ADDRESS"
```

## Manifest commands

A manifest describes a set of files. You can share it as a `.ant` file or an `ant://manifest/...` link. The manifest itself is not stored on the Autonomi Network. Uploading new files or publishing private DataMaps is paid; listing, inspecting, linking, and exporting without compaction can run offline.

### Create a manifest

**Command:** `ant manifest create [PATHS]...`

Uploads supplied files and writes a manifest. To create one without uploading, add existing public files with `--public-file`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PATHS` | path list | No | Files or directories to upload. One directory contributes its contents under the directory name. |
| `-o, --output <PATH>` | path | No | Output file. Defaults to `<name>.ant`. |
| `--name <NAME>` | string | No | Manifest name and default extraction-directory name. |
| `--compact` | boolean | No | Reference files by public address when their DataMap is already stored. Does not publish by itself. |
| `--public` | boolean | No | Store each uploaded file's DataMap so anyone with its address can retrieve it. |
| `--follow-symlinks` | boolean | No | Follow symbolic links to regular files instead of skipping them. |
| `--public-file <ADDRESS[=PATH]>` | string list | No | Add an existing public file, optionally under a chosen manifest path. Repeatable. |
| `--embed-public <ADDRESS[=PATH]>` | string list | No | Fetch and embed an existing public file's DataMap. Requires the Autonomi Network but no wallet. Repeatable. |
| `--torrent-hash <HEX>` | hexadecimal string | No | Record a 40-character BitTorrent v1 or 64-character v2 info hash. Repeat to include both. |
| `--merkle` | boolean | No | Force Merkle batch payment. |
| `--no-merkle` | boolean | No | Force per-chunk payment. |
| `--overwrite` | boolean | No | Replace an existing output file. |
| `--link` | boolean | No | Also print a manifest link. |

**Example:**

Creates an offline manifest around the public Lucky image:

```bash
ant manifest create \
  --name lucky \
  --public-file 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a=lucky.jpg \
  --output lucky.ant \
  --overwrite
```

### List recorded uploads

**Command:** `ant manifest list`

Lists locally recorded uploads, newest first.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant manifest list
```

### Show a manifest

**Command:** `ant manifest show <SOURCE>`

Lists entries from a manifest file, manifest link, or recorded upload ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SOURCE` | string | Yes | `.ant` file, manifest link, or upload ID. |

**Example:**

```bash
ant manifest show lucky.ant
```

### Print a manifest link

**Command:** `ant manifest link <SOURCE>`

Prints the manifest as an `ant://manifest/...` link, using the short published form for embedded DataMaps.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SOURCE` | string | Yes | `.ant` file, manifest link, or upload ID. |

**Example:**

```bash
ant manifest link lucky.ant
```

### Export a manifest

**Command:** `ant manifest export <SOURCE>`

Writes a manifest to a `.ant` file. Compaction replaces embedded DataMaps with public addresses. Using `--compact` always requires `SECRET_KEY` and a network connection, even when every DataMap is already public. If a DataMap is still private, the CLI asks before publishing it in interactive text mode; publishing is paid and makes the file public. In JSON or non-interactive use, pass `--yes` when publication is required.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SOURCE` | string | Yes | `.ant` file, manifest link, or upload ID. |
| `-o, --output <PATH>` | path | No | Output file. Defaults to `<name>.ant`. |
| `--compact` | boolean | No | Replace embedded DataMaps with public addresses. Always requires `SECRET_KEY`; may require paid publication. |
| `-y, --yes` | boolean | No | Publish private DataMaps without asking. Required for publication in JSON or non-interactive use. |
| `--overwrite` | boolean | No | Replace an existing output file. |
| `--link` | boolean | No | Also print the exported manifest as a link. |

**Example:**

```bash
ant manifest export lucky.ant --output lucky-copy.ant --overwrite
```

### Download a manifest

**Command:** `ant manifest download <SOURCE>`

Downloads the files described by a manifest.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `SOURCE` | string | Yes | `.ant` file, manifest link, or upload ID. |
| `-o, --output <PATH>` | path | No | Extraction directory. Defaults to the manifest name, or the current directory when unnamed. |
| `--select <PATH>` | string list | No | Download selected entries or directories. Repeatable. |
| `--overwrite` | boolean | No | Replace existing regular files at target paths. |
| `--concurrency <N>` | integer | No | Number of entries downloaded at once. Default `1`. |

**Example:**

```bash
ant manifest download lucky.ant --output lucky-files
```

## Wallet commands

### Show the wallet address

**Command:** `ant wallet address`

Prints the wallet address derived from `SECRET_KEY`.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant wallet address
```

### Show the wallet balance

**Command:** `ant wallet balance`

Prints the Autonomi Network Token (ANT) balance for the configured EVM network. It does not report the ETH balance used for transaction fees.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant wallet balance
```

## Node commands

### Start node management

**Command:** `ant node daemon start`

Launches the node-management service as a detached background process. By default it binds to a random free port on `127.0.0.1` and writes the chosen port to `ant/daemon.port`. This file belongs to node management; SDK discovery reads the separate `ant/sdk/daemon.port` file written by `antd`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--port <PORT>` | integer | No | Pin the HTTP port. `0` is equivalent to the default (OS-assigned). |
| `--listen-addr <IP>` | IP address | No | Bind address. Defaults to `127.0.0.1`. Binding to a non-loopback address (e.g. `0.0.0.0`) exposes node management without authentication; use it only across a controlled connection. |
| `--log-path <PATH>` | path | No | Write daily rotating node-management logs using this path as the log-family name. The service retains 30 daily files. Without this option, the service does not write its own log file. |

**Example:**

```bash
ant node daemon start

# Pin port and bind on all interfaces (e.g. inside a container):
ant node daemon start --listen-addr 0.0.0.0 --port 8765
```

### Stop node management

**Command:** `ant node daemon stop`

Shuts down the running node daemon.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon stop
```

### Show node-management status

**Command:** `ant node daemon status`

Shows whether the node daemon is running and reports summary stats.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon status
```

### Show node-management information

**Command:** `ant node daemon info`

Outputs daemon connection details. The default output is human-readable; add the root `--json` flag for programmatic use.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon info
ant --json node daemon info
```

### Enable log forwarding

**Command:** `ant node logs forward enable`

Records consent to forward node logs to the Autonomi beta log endpoint. If the node-management service is running, forwarding starts immediately. Otherwise, the setting takes effect the next time that service starts.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--token <TOKEN>` | string | Conditionally | Write-only beta program token. Required the first time; re-enabling can reuse the stored token. |
| `--endpoint <URL>` | URL | No | Override the forwarding endpoint. Intended for testing with a local sink. |
| `--level <LEVEL>` | string | No | Lowest forwarded level: `trace`, `debug`, `info`, `warn`, or `error`. Defaults to `info`. |

**Example:**

```bash
: "${BETA_TOKEN:?Set BETA_TOKEN to the supplied beta program token}"
ant node logs forward enable --token "$BETA_TOKEN" --level info
```

### Disable log forwarding

**Command:** `ant node logs forward disable`

Stops forwarding node logs without changing the nodes themselves.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node logs forward disable
```

### Check log forwarding

**Command:** `ant node logs forward status`

Shows whether forwarding is enabled, whether it is active, which nodes are included, and delivery statistics.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node logs forward status
ant --json node logs forward status
```

### Add nodes

**Command:** `ant node add`

Adds one or more nodes to the registry.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--rewards-address <ADDR>` | string | Yes | Wallet address for node earnings |
| `--count <N>` | integer | No | Number of nodes to add. Default `1`. |
| `--node-port <PORT|RANGE>` | string | No | Node port or port range |
| `--data-dir-path <PATH>` | path | No | Custom data directory prefix |
| `--log-dir-path <PATH>` | path | No | Custom log directory prefix |
| `--path <PATH>` | path | No | Local node binary path |
| `--version <X.Y.Z>` | string | No | Download a specific node version |
| `--url <URL>` | string | No | Download a node archive from a URL |
| `--bootstrap <ADDRS>` | string list | No | Bootstrap peers for the node binary itself |
| `--evm-network <NET>` | string | No | EVM network the node uses for storage payments: `arbitrum-one` or `arbitrum-sepolia`. Default `arbitrum-one`. |
| `--upgrade-channel <CHANNEL>` | string | No | Release channel the node tracks for automatic upgrades: `stable` or `beta` |
| `--env <K=V>` | string list | No | Node environment variables |

**Example:**

```bash
ant node add --rewards-address 0xYourWallet --count 1

# Pin the node to the stable upgrade channel:
ant node add --rewards-address 0xYourWallet --count 1 --upgrade-channel stable
```

### Start nodes

**Command:** `ant node start`

Starts all registered nodes, or one named node with `--service-name`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--service-name <NAME>` | string | No | Start one named node instead of all nodes |

**Example:**

```bash
ant node start --service-name node1
```

### Show node status

**Command:** `ant node status`

Shows the status of all registered nodes. Each node reports a state, shown in the table as `Running`, `Stopped`, `Starting`, `Stopping`, `Errored`, or `Evicted`. An evicted node is one the node daemon automatically stopped when its host ran low on disk. Eviction stops the node and attempts to delete its data directory to reclaim space, then keeps the node's registry record marked `Evicted`. The table row for an evicted node shows the eviction reason and the exact `ant node dismiss` command to clear it. Deletion can fail; check the eviction reason to see what was attempted, and treat `reclaimed_bytes` in the JSON output as the recorded estimate for that attempt rather than a measurement of free space now available.

When the node daemon is running and a health snapshot is available, the output opens with a fleet-health summary of `Healthy`, `Warning`, or `Critical`, followed by one line per check that is not healthy. The summary is omitted when the node daemon is stopped, and also when it is running but the snapshot cannot be retrieved.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node status
```

**JSON output:**

Add `--json` before or after the subcommand to emit a machine-readable payload.

```bash
ant --json node status
```

The payload has these top-level fields:

| Field | Type | Description |
|------|------|-------------|
| `nodes` | array | One object per registered node. |
| `total_running` | integer | Count of nodes reported as `running` or `starting`. |
| `total_stopped` | integer | Count of every other node, including `stopped`, `stopping`, `errored`, and `evicted`. |
| `health` | object or null | Fleet-health snapshot. It is `null` when the node daemon is stopped, and also when it is running but the snapshot cannot be retrieved, so `null` alone does not mean the node daemon is stopped. |

Each `nodes` entry has these fields:

| Field | Type | Description |
|------|------|-------------|
| `node_id` | integer | Node ID used by the other `ant node` commands. |
| `name` | string | Service name of the node. |
| `version` | string | Node binary version. |
| `status` | string | One of `running`, `stopped`, `starting`, `stopping`, `errored`, `evicted`. |
| `pid` | integer | Process ID. Present only while the node is running. |
| `uptime_secs` | integer | Seconds since the node process started. Present only while the node is running. |
| `eviction` | object | Eviction detail. Present only when `status` is `evicted`. |

An `eviction` object has these fields:

| Field | Type | Description |
|------|------|-------------|
| `reason` | string | Human-readable explanation of the eviction. |
| `evicted_at` | integer | Unix epoch seconds at which the eviction occurred. |
| `reclaimed_bytes` | integer | Approximate bytes reclaimed by deleting the node's data directory. `0` when the deletion did not succeed, in which case the reason explains that manual cleanup may be needed. |

When present, the `health` object has an `overall` level (`green`, `warning`, or `critical` — the worst level across all checks) and a `checks` array. Each `checks` entry has these fields:

| Field | Type | Description |
|------|------|-------------|
| `kind` | string | Check type. The supported value is `disk_space`. |
| `level` | string | `green`, `warning`, or `critical`. |
| `summary` | string | Human-readable, user-facing one-liner. |
| `partition` | string | Optional. Opaque identifier of the partition the finding concerns. Present for `disk_space` checks; omitted for other check kinds. |
| `available_bytes` | integer | Optional. Free bytes on the partition. Present for `disk_space` checks; omitted for other check kinds. |
| `eviction_threshold_bytes` | integer | Optional. Free-space floor at which an eviction triggers. Present for `disk_space` checks; omitted for other check kinds. |
| `candidate` | object | Optional. Names the node that would be evicted next, with `node_id` (integer), `data_dir` (string), and `size_bytes` (integer, the space its eviction would free). Omitted when no candidate applies — a candidate is only produced when at least two running nodes share the partition and the level is not `green`. |

Example payload with two running nodes that share a partition and one previously evicted node. The disk-space check is at `warning`, so it names the smaller running node as the next eviction candidate:

```json
{
  "nodes": [
    {
      "node_id": 1,
      "name": "node1",
      "version": "0.18.0",
      "status": "running",
      "pid": 48213,
      "uptime_secs": 7200
    },
    {
      "node_id": 2,
      "name": "node2",
      "version": "0.18.0",
      "status": "running",
      "pid": 48219,
      "uptime_secs": 6600
    },
    {
      "node_id": 3,
      "name": "node3",
      "version": "0.18.0",
      "status": "evicted",
      "eviction": {
        "reason": "Automatically evicted to reclaim disk space: only 480 MiB free on its partition. Its data directory was deleted, recovering ~2.00 GiB.",
        "evicted_at": 1720800000,
        "reclaimed_bytes": 2147483648
      }
    }
  ],
  "total_running": 2,
  "total_stopped": 1,
  "health": {
    "overall": "warning",
    "checks": [
      {
        "kind": "disk_space",
        "level": "warning",
        "summary": "Disk space low on dev:2049: 900 MiB free. An eviction may occur once it reaches 500 MiB; node 2 would be evicted next.",
        "partition": "dev:2049",
        "available_bytes": 943718400,
        "eviction_threshold_bytes": 524288000,
        "candidate": {
          "node_id": 2,
          "data_dir": "/home/alice/.local/share/ant/nodes/node-2",
          "size_bytes": 1073741824
        }
      }
    ]
  }
}
```

### Dismiss a node from the registry

**Command:** `ant node dismiss <NODE_ID>`

Removes a node's registry entry so it no longer appears in `ant node status`. This clears the record for a node the node daemon evicted for low disk, though it is not restricted to evicted nodes.

Dismissal behavior depends on the node daemon:

- When the node daemon is running, dismiss removes any node that is not running. It refuses to dismiss a running node and asks you to stop it first.
- When the node daemon is stopped, dismiss removes the registry entry directly and does not stop any process. Dismiss a node only when it is not running, so you do not leave an orphaned node process behind.

Dismissing removes the registry entry only; it does not itself reclaim disk space. After an eviction, read the eviction reason to see whether cleanup succeeded, and treat `reclaimed_bytes` as the recorded estimate for that attempt, not proof of current free space. Before adding a replacement node, check the actual free disk space on the affected partition and free space manually if the eviction did not. Once enough capacity is available, dismiss the `Evicted` record, then add a replacement node with `ant node add` if you still need it.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `<NODE_ID>` | integer | Yes | ID of the node to dismiss, as shown in the `ant node status` list. |

**Example:**

```bash
ant node dismiss 3
```

Output:

```text
✓ Dismissed node 3 (node3)
```

### Stop nodes

**Command:** `ant node stop`

Stops all registered nodes, or one named node with `--service-name`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--service-name <NAME>` | string | No | Stop one named node instead of all nodes |

**Example:**

```bash
ant node stop --service-name node1
```

### Reset nodes

**Command:** `ant node reset`

Resets node state, including data, logs, and registry information.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--force` | boolean | No | Skip the confirmation prompt |

**Example:**

```bash
ant node reset --force
```

## Update command

### Update the CLI

**Command:** `ant update`

For installations made from release downloads or the shell/PowerShell installers, checks GitHub Releases for a newer version of the CLI, downloads it if one is available, and replaces the current executable in place. The downloaded archive's ML-DSA-65 signature is verified against the embedded release signing key before installation. When the extracted binary can report its version, a mismatch stops the update.

For npm installations, use:

```sh
npm update -g @withautonomi/ant
```

`ant update` does not replace an npm-managed executable. When an update is available or you pass `--force`, it directs you to npm instead; if the version is already current, it reports that no update is needed. The channel and replacement options below apply to installations managed by `ant update`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--channel <CHANNEL>` | string | No | Release channel to update along: `stable` or `beta`. Defaults to the channel the running binary belongs to |
| `--force` | boolean | No | Re-download even if the current version is already latest |

Without `--channel`, the channel is inferred from the running binary: a `-beta.N` build tracks `beta` and every other build tracks `stable`. On `beta`, both `-beta.N` and stable releases are accepted and the highest wins; release candidates (`-rc.N`) are rejected on both channels. Because a beta build outranks the stable release it was cut from, `--channel stable` cannot walk a beta build backwards and reports that you are already up to date; leaving the beta channel means installing a stable build manually.

**Example:**

```bash
ant update
ant update --force
ant update --channel beta
```

## Related pages

- [Use the CLI](use-the-cli.md)
- [Rust Library Reference](../rust/library-reference.md)
