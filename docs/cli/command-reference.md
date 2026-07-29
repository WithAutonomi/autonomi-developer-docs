# CLI Command Reference

<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 81848a0900fa9972e9af2d323bf3b49bf8d382aa
  verified_date: 2026-07-28
  verification_mode: current-merged-truth
-->

Reference for the `ant` CLI command tree and its flags. The command tree below follows the direct-network CLI surface, and the option tables stay grouped by command family for easier scanning. Hidden or advanced flags are called out where they matter for troubleshooting.

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
└── update
```

## Root command and global flags

### `ant [OPTIONS] <COMMAND>`

The root command accepts the global flags used across data and node operations. Root flags must appear before the subcommand.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--json` | boolean | No | Emit structured JSON |
| `-b, --bootstrap <IP:PORT>` | socket list | No | Bootstrap peers for data operations. Can be comma-separated or repeated. |
| `--devnet-manifest <PATH>` | path | No | Path to a local devnet manifest JSON file |
| `--allow-loopback` | boolean | No | Allow loopback connections for local devnet or local testing |
| `--ipv4-only` | boolean | No | Disable dual-stack and force IPv4-only mode |
| `--quote-timeout-secs <N>` | integer | No | Hidden. Controls lightweight network-operation timeouts such as DHT lookups. |
| `--store-timeout-secs <N>` | integer | No | Hidden. Sets `ClientConfig.store_timeout_secs`. Non-Merkle chunk PUT response timeout is set by an internal `STORE_RESPONSE_TIMEOUT` constant; Merkle batch PUT timeout is set by `merkle_store_timeout_secs` (270 s default, library-only); chunk GET timeout is set by `--chunk-get-timeout-secs`. |
| `--chunk-get-timeout-secs <N>` | integer | No | Hidden. Per-peer response timeout for chunk retrieve operations. Default 10 s. |
| `--quote-concurrency <N>` | integer | No | Hidden. Caps the quote channel only. It does not affect store or download concurrency. |
| `--store-concurrency <N>` | integer | No | Hidden. Controls upload chunk concurrency. `--chunk-concurrency` is accepted as an alias. |
| `-v, --verbose...` | count | No | Increase log verbosity: `-v`, `-vv`, or `-vvv` |
| `--evm-network <NET>` | string | No | EVM network for payments: `arbitrum-one`, `arbitrum-sepolia`, or `local` |
| `-h, --help` | boolean | No | Print help |
| `-V, --version` | boolean | No | Print version |

**Environment:**

| Variable | Description |
|------|------|
| `SECRET_KEY` | Required for uploads and wallet commands |

**Example:**

```bash
ant --help
```

## File commands

### `ant file upload <PATH>`

Uploads a file with self-encryption and EVM payment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `PATH` | path | Yes | File to upload |
| `--public` | boolean | No | Store the DataMap on-network so anyone with the address can download the file |
| `--merkle` | boolean | No | Force Merkle batch payment |
| `--no-merkle` | boolean | No | Force single per-chunk payments |
| `--store-timeout <N>` | integer | No | Hidden. Overrides `ClientConfig.store_timeout_secs` for this upload only. See the `--store-timeout-secs` row in the [Root command and global flags](#root-command-and-global-flags) section for what that field does and does not govern. |
| `--store-concurrency <N>` | integer | No | Hidden. Overrides upload chunk concurrency for this upload. |
| `--overwrite` | boolean | No | Replace any existing `<filename>.datamap` instead of writing a suffixed `<filename>-2.datamap`. |

**Example:**

```bash
SECRET_KEY=0x<hex_private_key> ant file upload photo.jpg --public
```

### `ant file download [ADDRESS]`

Downloads a public file by address or a private file using a local DataMap file.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | string | Conditionally | Public DataMap address. Required unless `--datamap` is provided. |
| `--datamap <PATH>` | path | No | Local `.datamap` file for private download |
| `-o, --output <PATH>` | path | Conditionally | Required for address-based downloads. Optional for `--datamap` downloads that can infer the original filename. |
| `--peers <COUNT>` | integer | No | Number of closest peers to try for each chunk fetch. Accepts a positive integer. `--peer-count` is accepted as an alias. |
| `--all-peers` | boolean | No | Diagnostic mode: download the file as usual, then fetch each chunk from every selected closest peer and print ranked per-peer results. `--try-all-peers` is accepted as an alias. The number of closest peers swept per chunk comes from `--peers`, defaulting to the client close-group size. With `--json`, the per-peer results are emitted as a `chunk_peer_check` object on the download result. |

**Example:**

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg
```

The output path is your local filename. In this example, the command downloads a public JPEG of Lucky the dog and saves it as `lucky.jpg`.

Private datamap example:

```bash
ant file download --datamap photo.jpg.datamap
```

Diagnostic example (download, then rank closest-peer results for each chunk):

```bash
ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky.jpg --all-peers --peers 5
```

### `ant file cost <PATH>`

Estimates the upload cost for a file without uploading it.

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

## Chunk commands

### `ant chunk put [FILE]`

Stores a single chunk from a file or from standard input.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `FILE` | path | No | Input file. If omitted, `ant` reads from standard input. |

**Example:**

```bash
echo "hello autonomi" | SECRET_KEY=0x<hex_private_key> ant chunk put
```

### `ant chunk get <ADDRESS>`

Retrieves a single chunk by address.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ADDRESS` | string | Yes | Hex-encoded chunk address (64 hex characters) |
| `-o, --output <PATH>` | path | No | Write the chunk to a file instead of stdout |
| `--all-peers` | boolean | No | Diagnostic mode: try every selected closest peer and print ranked per-peer results. Chunk bytes are only written when `-o`/`--output` is also supplied. |
| `--peer-count <N>` | integer | No | Diagnostic mode only. Number of closest peers to try with `--all-peers`. Requires `--all-peers`. |

**Example:**

```bash
ant chunk get <chunk_address> -o chunk.bin
```

Diagnostic example (try all closest peers and rank results):

```bash
ant chunk get <chunk_address> --all-peers --peer-count 5
```

## Wallet commands

### `ant wallet address`

Prints the wallet address derived from `SECRET_KEY`.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
SECRET_KEY=0x<hex_private_key> ant wallet address
```

### `ant wallet balance`

Prints the token balance for the configured EVM network.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
SECRET_KEY=0x<hex_private_key> ant wallet balance
```

## Node commands

### `ant node daemon start`

Launches the node daemon as a detached background process. By default it binds to a random free port on `127.0.0.1` and writes the chosen port to `daemon.port` for SDK discovery.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--port <PORT>` | integer | No | Pin the HTTP port. `0` is equivalent to the default (OS-assigned). |
| `--listen-addr <IP>` | IP address | No | Bind address. Defaults to `127.0.0.1`. Binding to a non-loopback address (e.g. `0.0.0.0`) exposes node management without authentication — only do this when the network path is controlled. |

**Example:**

```bash
ant node daemon start

# Pin port and bind on all interfaces (e.g. inside a container):
ant node daemon start --listen-addr 0.0.0.0 --port 8765
```

### `ant node daemon stop`

Shuts down the running node daemon.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon stop
```

### `ant node daemon status`

Shows whether the node daemon is running and reports summary stats.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon status
```

### `ant node daemon info`

Outputs daemon connection details for programmatic use. This command always emits JSON.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node daemon info
```

### `ant node add`

Adds one or more nodes to the registry.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--rewards-address <ADDR>` | string | Yes | Wallet address for node earnings |
| `--count <N>` | integer | No | Number of nodes to add |
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

### `ant node start`

Starts all registered nodes, or one named node with `--service-name`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--service-name <NAME>` | string | No | Start one named node instead of all nodes |

**Example:**

```bash
ant node start --service-name node1
```

### `ant node status`

Shows the status of all registered nodes. Each node reports a state, shown in the table as `Running`, `Stopped`, `Starting`, `Stopping`, `Errored`, or `Evicted`. An evicted node is one the node daemon automatically stopped when its host ran low on disk. Eviction stops the node and attempts to delete its data directory to reclaim space, then keeps the node's registry record marked `Evicted`. The table row for an evicted node shows the eviction reason and the exact `ant node dismiss` command to clear it. Deletion can fail; check the eviction reason to see what was attempted, and treat `reclaimed_bytes` in the JSON output as the recorded estimate for that attempt rather than a measurement of free space now available.

When the node daemon is running and a health snapshot is available, the output opens with a fleet-health summary of `Healthy`, `Warning`, or `Critical`, followed by one line per check that is not healthy. The summary is omitted when the node daemon is stopped, and also when it is running but the snapshot cannot be retrieved.

**Parameters:**

This command has no command-specific parameters.

**Example:**

```bash
ant node status
```

**JSON output:**

Add `--json` (a root flag, so it comes before the subcommand) to emit a machine-readable payload.

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
      "version": "0.4.0",
      "status": "running",
      "pid": 48213,
      "uptime_secs": 7200
    },
    {
      "node_id": 2,
      "name": "node2",
      "version": "0.4.0",
      "status": "running",
      "pid": 48219,
      "uptime_secs": 6600
    },
    {
      "node_id": 3,
      "name": "node3",
      "version": "0.4.0",
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

### `ant node stop`

Stops all registered nodes, or one named node with `--service-name`.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--service-name <NAME>` | string | No | Stop one named node instead of all nodes |

**Example:**

```bash
ant node stop --service-name node1
```

### `ant node reset`

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

### `ant update`

Checks GitHub Releases for a newer version of the CLI, downloads it if one is available, and replaces the current executable in place.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--force` | boolean | No | Re-download even if the current version is already latest |

**Example:**

```bash
ant update
ant update --force
```

## Related pages

- [Use the CLI](use-the-cli.md)
- [Rust Library Reference](../rust/library-reference.md)
