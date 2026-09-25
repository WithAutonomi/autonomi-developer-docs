# Daemon Command Reference

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Command-line options for the local daemon, `antd 0.14.0`. This background service connects applications to the Autonomi Network through REST and gRPC APIs.

## Usage

### Main command

**Command:** `antd`

Runs the local REST and gRPC gateway daemon for Autonomi.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `--rest-addr <ADDR>` | string | No | REST listen address, default `127.0.0.1:8082` (loopback only; pass `0.0.0.0:8082` to expose it beyond the local machine) |
| `--grpc-addr <ADDR>` | string | No | gRPC listen address, default `127.0.0.1:50051` (loopback only; pass `0.0.0.0:50051` to expose it beyond the local machine) |
| `--rest-port <PORT>` | integer | No | Override the REST port from `--rest-addr` |
| `--grpc-port <PORT>` | integer | No | Override the gRPC port from `--grpc-addr` |
| `--network <MODE>` | string | No | Network mode, default `default`; also supports `local` |
| `--peers <MULTIADDRS>` | string | No | Comma-separated bootstrap peer multiaddrs |
| `--ipv4-only` | flag | No | Use IPv4 only for peer connections on hosts without working IPv6. Defaults to off; `--network local` already forces IPv4. Does not change the REST or gRPC listen addresses |
| `--cors [<ORIGINS>]` | string | No | Cross-Origin Resource Sharing (CORS) origin list, comma-separated, for GET, POST, HEAD, and OPTIONS requests. Use exact origins without paths or trailing slashes. Bare `--cors` allows no origins. `*` allows any origin and is unsafe outside development; this does not add authentication |
| `--log-level <LEVEL>` | string | No | Log level: `trace`, `debug`, `info`, `warn`, `error` |
| `--quote-timeout-secs <SECONDS>` | integer | No | Override the quote and DHT timeout for lightweight network operations |
| `--store-timeout-secs <SECONDS>` | integer | No | Accepted and logged, but not read by the released client's PUT or GET paths; setting it has no operational effect |
| `--quote-concurrency <COUNT>` | integer | No | Legacy adaptive-concurrency ceiling for quote operations; it does not set a fixed concurrency |
| `--store-concurrency <COUNT>` | integer | No | Legacy adaptive-concurrency ceiling for store operations; it does not set a fixed concurrency |
| `--version` | flag | No | Print the crate version and build commit, then exit; omit the commit when built outside a git checkout |
| `-V` | flag | No | Print the crate version without the build commit, then exit |

**Environment variables:**

| Variable | Description |
|------|------|
| `ANTD_REST_ADDR` | REST listen address |
| `ANTD_GRPC_ADDR` | gRPC listen address |
| `ANTD_REST_PORT` | REST port override |
| `ANTD_GRPC_PORT` | gRPC port override |
| `ANTD_NETWORK` | Network mode |
| `ANTD_PEERS` | Comma-separated bootstrap peer multiaddrs |
| `ANTD_IPV4_ONLY` | Set to `true` to use IPv4-only peer connections, equivalent to `--ipv4-only` |
| `ANTD_CORS` | Same origin list as `--cors`. `true`, `1`, `on`, or `yes` allows no origins; `false`, `0`, `off`, or `no` disables CORS. `*` allows any origin and cannot be combined with a list |
| `ANTD_LOG_LEVEL` | Log level |
| `ANTD_QUOTE_TIMEOUT_SECS` | Quote and DHT timeout override |
| `ANTD_STORE_TIMEOUT_SECS` | Accepted but operationally ineffective store-timeout value |
| `ANTD_QUOTE_CONCURRENCY` | Legacy adaptive quote-concurrency ceiling |
| `ANTD_STORE_CONCURRENCY` | Legacy adaptive store-concurrency ceiling |
| `AUTONOMI_WALLET_KEY` | Direct-wallet private key for paid uploads |
| `EVM_NETWORK` | EVM preset: `arbitrum-one`, `arbitrum-sepolia`, `arbitrum-sepolia-test`, or `local`. Defaults to `local` for `ANTD_NETWORK=local` and `arbitrum-one` otherwise |
| `EVM_RPC_URL` | EVM RPC endpoint |
| `EVM_PAYMENT_TOKEN_ADDRESS` | Payment token contract |
| `EVM_PAYMENT_VAULT_ADDRESS` | Payment vault contract |
| `EVM_DATA_PAYMENTS_ADDRESS` | Legacy fallback for the payment vault when `EVM_PAYMENT_VAULT_ADDRESS` is unset |

**Examples:**

```bash
# Default network, default ports
antd

# Local network with explicit peers
ANTD_PEERS="/ip4/127.0.0.1/udp/12000/quic-v1/p2p/12D3Koo..." antd --network local

# Expose on all network interfaces (opt in deliberately — antd has no auth)
antd --rest-addr 0.0.0.0:8082 --grpc-addr 0.0.0.0:50051

# Let the OS assign free ports
antd --rest-port 0 --grpc-port 0

# Run with debug logging
antd --log-level debug

# Allow one browser application's origin
antd --cors http://127.0.0.1:8000

# Increase the quote timeout and lower the adaptive concurrency ceilings
antd --quote-timeout-secs 15 --quote-concurrency 16 --store-concurrency 4
```

**Response:** `antd` keeps running until it is stopped, except when displaying help or version information.

Check the binary identity without starting the gateway:

```bash
antd --version
antd -V
```

Expected output for the released binary:

```text
antd 0.14.0 (build dbf6a7d3d951)
antd 0.14.0
```

## Notes

- External signing is a prepare-and-finalize request workflow, not a daemon mode. There is no `--external-signer` flag or corresponding environment switch.
- Without `AUTONOMI_WALLET_KEY`, direct write and wallet operations fail, but prepare/finalize endpoints can use a wallet held by the caller.
- `EVM_NETWORK` selects preset RPC and contract values. Individual `EVM_*` variables override that preset. Prefer `EVM_PAYMENT_VAULT_ADDRESS`; `EVM_DATA_PAYMENTS_ADDRESS` is used only as its legacy fallback.
- Quote and store concurrency adapt independently to observed success, network errors, timeouts, and latency. Non-default legacy concurrency values below the adaptive ceilings cap the matching channel; they do not pin it to a fixed value. The historical defaults, `32` and `8`, are treated as unpinned and do not cap adaptation.
- On startup, `antd` writes a `daemon.port` file under the SDK data directory with the REST port on line 1, the gRPC port on line 2, and its process ID (PID) on line 3.

## Access boundary

`antd` provides no authentication. The default `127.0.0.1` listeners restrict access to processes on the same machine, but any process that can connect can invoke write, wallet, and local-filesystem operations. Do not bind to `0.0.0.0` or another external interface without a firewall or authenticated proxy. CORS only restricts browser origins and does not protect against non-browser clients.

## Error codes

| Code | Meaning | Resolution |
|------|---------|------------|
| invalid REST address | `--rest-addr` could not be parsed | Fix the host:port value |
| invalid gRPC address | `--grpc-addr` could not be parsed | Fix the host:port value |
| invalid CORS origin | `--cors` contains a path, lacks a scheme, or mixes `*` with other origins | Use exact `scheme://host[:port]` origins without trailing slashes |
| failed to create dual-stack network nodes | The host may not have a usable IPv6 stack | Check the startup error; on an IPv4-only host, use `--ipv4-only` or `ANTD_IPV4_ONLY=true` |
| runtime wallet/config errors | Required env vars are missing for paid operations | Set the wallet and EVM environment variables |

## Related pages

- [Build with the SDKs](../install.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Use the Daemon as a Local Service](../how-to-guides/use-the-daemon-as-a-local-service.md)
- [REST API](rest-api.md)
- [gRPC Services](grpc-services.md)
