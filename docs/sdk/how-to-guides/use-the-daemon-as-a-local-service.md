# Use the Daemon as a Local Service

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Keep the local daemon running with a service manager so your applications can use it without an open terminal. Autonomi's daemon, `antd`, is a background service that manages the connection to the Autonomi Network.

Use this setup if you want:

- A persistent local REST and gRPC endpoint
- One daemon shared by more than one app or tool
- Service-manager supervision instead of manually starting `antd` in a terminal

## Prerequisites

- `antd v0.14.0` built on the target machine using the source-build instructions in [Start the Local Daemon](../start-the-local-daemon.md#build-from-source-instead)
- A Linux host with `systemd` for the service example below
- An optional wallet key if `antd` will handle paid uploads directly

## Steps

### 1. Create a service account and install the binary

Run `antd` as an unprivileged system user and keep its writable files under `/var/lib/antd`:

```bash
sudo useradd --system --create-home --home-dir /var/lib/antd \
  --shell /usr/sbin/nologin antd
sudo install -o root -g root -m 0755 \
  /absolute/path/to/ant-sdk/antd/target/release/antd \
  /usr/local/bin/antd
```

### 2. Create an environment file

Keep the wallet key outside the unit file.

Create a root-owned file that only the `antd` group can read:

```bash
sudo install -o root -g antd -m 0640 /dev/null /etc/antd.env
sudoedit /etc/antd.env
```

For a daemon that performs paid writes directly, add:

```bash
AUTONOMI_WALLET_KEY="<hex_private_key>"
```

Leave the file empty for read-only use or external-signer uploads. On the default network, `antd v0.14.0` selects the Arbitrum One preset and canonical payment contracts. Do not add individual `EVM_RPC_URL`, `EVM_PAYMENT_TOKEN_ADDRESS`, or `EVM_PAYMENT_VAULT_ADDRESS` overrides; those activate custom payment handling that default-network storage nodes reject.

### 3. Create a systemd unit

Create `/etc/systemd/system/antd.service`:

```ini
[Unit]
Description=Autonomi antd daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=antd
Group=antd
WorkingDirectory=/var/lib/antd
Environment=HOME=/var/lib/antd
EnvironmentFile=-/etc/antd.env
ExecStart=/usr/local/bin/antd --rest-addr 127.0.0.1:8082 --grpc-addr 127.0.0.1:50051 --log-level info
UMask=0077
NoNewPrivileges=true
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

This binds `antd` to localhost instead of exposing it on every interface. `antd` has no built-in authentication, so do not expose its REST or gRPC ports directly to another machine without a firewall or authenticated proxy.

The service user can access only files permitted by normal Linux ownership and mode rules. Grant that user access to any host paths you pass to file upload or download endpoints.

### 4. Start and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable antd
sudo systemctl start antd
```

### 5. Check health and logs

```bash
sudo systemctl status antd
curl --fail-with-body http://127.0.0.1:8082/health
journalctl -u antd -f
```

If you need more detail in the logs, change `--log-level info` to `debug` or `trace` and restart the service.

### 6. Use fixed or dynamic ports

For a stable local service, keep explicit addresses as shown above. If another supervisor needs OS-assigned ports, `antd` also supports:

```bash
antd --rest-port 0 --grpc-port 0
```

In this systemd setup, the port file is written under the service account's data directory at `/var/lib/antd/.local/share/ant/sdk/daemon.port`. Applications running as another user do not discover that file automatically. Prefer fixed loopback ports for a shared service, or configure each application with the selected endpoint explicitly.

## Verify it worked

`/health` returning `status: "ok"` confirms that antd responds, not that uploads will succeed or the wallet has funds. Confirm that your application can connect to the configured REST or gRPC endpoint. See the [health reference](../reference/rest-api.md#health) for connectivity diagnostics.

## Common errors

**Port already in use**: Change `--rest-addr`, `--grpc-addr`, `--rest-port`, or `--grpc-port`.

**503 on direct write endpoints**: `antd` is running without `AUTONOMI_WALLET_KEY`. Add the key for `antd`-signed writes, or use the external-signer prepare and finalize flow.

**Startup loop in systemd**: Inspect `journalctl -u antd -f` for invalid addresses, missing binaries, or bad environment variables.

## Next steps

- [Build with the SDKs](../install.md)
- [Start the Local Daemon](../start-the-local-daemon.md)
- [Daemon Command Reference](../reference/daemon-command-reference.md)
- [REST API](../reference/rest-api.md)
