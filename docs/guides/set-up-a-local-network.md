# Set Up a Local Network

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Set up an isolated local Autonomi Network with `ant-dev 0.1.0` from the `ant-sdk v0.12.0` checkout, and understand its known teardown risk before starting it.

`ant-dev 0.1.0` starts `ant-devnet`, provisions local EVM contracts and a funded test wallet, and launches `antd`. Use this source-only workflow only for isolated local testing. Its teardown command performs broad process termination and data deletion, so use a disposable virtual machine or similarly isolated environment rather than a workstation that holds other Autonomi data or runs other Anvil processes.

This guide uses `ant-sdk v0.12.0` with `ant-node v0.17.1`. Keep these versions together rather than substituting the independently released `antd 0.13.0` or `ant-node 0.20.0`. Before depending on the local environment, complete every verification step below in your disposable environment.

## Prerequisites

- A disposable virtual machine or isolated development environment
- Rust toolchain
- Python 3.10 or newer
- `protoc` (Protocol Buffers compiler) available on your machine
- Foundry's `anvil` for the local EVM testnet: install a fixed [official release](https://github.com/foundry-rs/foundry/releases), verify its published checksum, and check `anvil --version`. Do not pipe the moving online installer into a shell.
- Git
- `curl`

## Steps

### 1. Check out the exact versions

Use the exact version tags rather than moving default branches:

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
mkdir "$WORK_DIR"

git clone --branch v0.12.0 --depth 1 https://github.com/WithAutonomi/ant-sdk.git "$WORK_DIR/ant-sdk"
git clone --branch v0.17.1 --depth 1 https://github.com/WithAutonomi/ant-node.git "$WORK_DIR/ant-node"

test "$(git -C "$WORK_DIR/ant-sdk" rev-parse HEAD)" = "8378338ca04d3a78db8ad0c943daf182cfd27763"
test "$(git -C "$WORK_DIR/ant-node" rev-parse HEAD)" = "953e565fb713e43769e0e82dc4f424b8cc63ed7a"

printf 'Pinned commits match\n'
```

Expected output:

```text
Pinned commits match
```

### 2. Install both Python packages from source

`ant-dev` depends on the Python `antd` package. Install both from the pinned checkout in a virtual environment so a separately published package cannot silently replace either part of this pairing:

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
python3 -m venv "$WORK_DIR/.venv"
source "$WORK_DIR/.venv/bin/activate"

python -m pip install \
  --editable "$WORK_DIR/ant-sdk/antd-py[rest,grpc]" \
  --editable "$WORK_DIR/ant-sdk/ant-dev"

ant dev start --help
```

Expected output begins with:

```text
usage: ant dev start
```

This installs the `ant` command provided by the source-only `ant-dev` package. It is not the direct CLI from `ant-client`.

Keep the virtual environment active only while using `ant-dev` so its `ant` command does not shadow [the direct CLI](../cli/use-the-cli.md).

### 3. Confirm the isolation boundary

Do not continue on a machine where either of these is true:

- another project is running `anvil`
- `~/.local/share/ant/nodes` or `~/.local/share/ant/spill` contains data you need

`ant-dev 0.1.0` force-kills every matching `anvil` process on POSIX systems when you run `ant dev stop`. On every non-Windows system it also recursively deletes those two directories. The deletion path is hard-coded and is not restricted to data created by the active `ant-dev` run.

There is no safely bounded teardown command in `ant-dev 0.1.0`. The safety measure for this guide is environmental isolation: discard the disposable environment after testing. Do not run `ant dev stop` on a shared workstation.

### 4. Start the local environment

From the directory that contains the two pinned checkouts:

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
source "$WORK_DIR/.venv/bin/activate"

test "$(git -C "$WORK_DIR/ant-sdk" rev-parse HEAD)" = "8378338ca04d3a78db8ad0c943daf182cfd27763"
test "$(git -C "$WORK_DIR/ant-node" rev-parse HEAD)" = "953e565fb713e43769e0e82dc4f424b8cc63ed7a"

ant dev start --ant-node-dir "$WORK_DIR/ant-node"
```

If startup succeeds, the output ends with `=== Ready! ===`, followed by the REST and gRPC addresses and `Wallet: configured`.

The first run compiles `ant-devnet` in release mode and `antd` in debug mode. If startup times out, inspect `~/.ant-dev/devnet.log` and `~/.ant-dev/antd.log`. Do not repeatedly restart without first checking for orphaned processes in the disposable environment.

A successful local start launches:

- a local `ant-devnet`
- a generated devnet manifest with bootstrap peers plus local wallet and EVM payment settings
- `antd --network local`
- a wallet-enabled local environment with REST health on `http://localhost:8082/health`

When startup succeeds, local testing gives you:

- a network to upload to
- an `antd` process to call
- a wallet you can inspect
- token and gas balances for upload testing

### 5. Check status and wallet

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
source "$WORK_DIR/.venv/bin/activate"

ant dev status
ant dev wallet show
```

`ant dev status` checks the local processes and the `antd` health endpoint. `ant dev wallet show` prints the configured local wallet address, token balance, and gas balance.

A successful wallet check includes `Address`, `Balance`, and `Gas balance`. These checks confirm that the local wallet is configured; they do not prove that an upload will succeed.

### 6. Verify the complete health response

```bash
#!/usr/bin/env bash
set -euo pipefail

HEALTH=$(curl --fail --show-error http://127.0.0.1:8082/health)

python3 -c '
import json
import sys

health = json.loads(sys.argv[1])
required = {
    "status",
    "network",
    "version",
    "evm_network",
    "uptime_seconds",
    "build_commit",
    "payment_token_address",
    "payment_vault_address",
}
missing = required.difference(health)
if missing:
    raise SystemExit(f"Missing fields: {sorted(missing)}")
if (
    health["status"] != "ok"
    or health["network"] != "local"
    or health["version"] != "0.12.0"
    or health["evm_network"] != "local"
):
    raise SystemExit(f"Unexpected health response: {health}")
if not health["payment_token_address"] or not health["payment_vault_address"]:
    raise SystemExit("Local payment contract addresses are missing")
print("Local antd health check passed")
' "$HEALTH"
```

A successful health check prints:

```text
Local antd health check passed
```

### 7. Run a local write/read round trip

This operation is limited to isolated local testing and uses local test funds only. The first direct-wallet payment can also submit an automatic transaction granting the local payment vault an unlimited token allowance.

```bash
#!/usr/bin/env bash
set -euo pipefail

printf 'Local network test' > local-original.bin
DATA_B64=$(base64 < local-original.bin | tr -d '\n')

UPLOAD=$(curl --fail --show-error \
  --request POST \
  --header "Content-Type: application/json" \
  --data "{\"data\":\"${DATA_B64}\",\"payment_mode\":\"auto\"}" \
  http://127.0.0.1:8082/v1/data/public)

ADDRESS=$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["address"])' "$UPLOAD")

curl --fail --show-error \
  "http://127.0.0.1:8082/v1/data/public/${ADDRESS}/stream" \
  --output local-downloaded.bin

cmp local-original.bin local-downloaded.bin
printf 'Local write/read round trip passed for %s\n' "$ADDRESS"
```

A successful run prints a 64-character address after `Local write/read round trip passed for`.

### 8. Dispose of the isolated environment

Do not use `ant dev reset`; `ant-dev 0.1.0` first runs the broad teardown described above, then omits the required `preset` restart argument and fails.

Do not use `ant dev stop` on a shared workstation. End the disposable virtual machine or isolated environment instead. `ant-dev 0.1.0` has no in-tool teardown command that bounds process termination and data cleanup to resources created by that run.

## Verify it worked

Inside the disposable environment, confirm all three results:

- `ant dev status` reports a healthy `antd` process
- `ant dev wallet show` reports the expected local wallet and balances
- the write/read script prints a 64-character address and `cmp` exits successfully

Passing these checks validates your isolated environment. It does not establish compatibility with the production Autonomi Network.

## Common errors

**Cannot install ant-dev**: Install both `ant-sdk/antd-py[rest,grpc]` and `ant-sdk/ant-dev` from the pinned checkout in the same virtual environment.

**No local environment running**: Check the pinned `ant-node` path and inspect both files under `~/.ant-dev` before retrying.

**Cannot reach the health endpoint**: Use `ant dev status`, `ant dev logs`, and `~/.ant-dev/devnet.log` inside the disposable environment.

**Wallet not configured**: Check that the generated `~/.ant-dev/devnet-manifest.json` contains an `evm` block. Do not use the broken reset command; preserve the logs before disposing of the environment.

**Need to stop a shared environment**: There is no safely bounded teardown command in `ant-dev 0.1.0`. Do not substitute broad `pkill` or directory deletion commands.

## Next steps

- [Start the Local Daemon](../sdk/start-the-local-daemon.md)
- [Prepare a Wallet for Uploads](prepare-a-wallet-for-uploads.md)
- [Store Data on the Network](../sdk/store-data-on-the-network.md)
- [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
- [Estimate Costs and Handle Upload Payments](estimate-costs-and-handle-upload-payments.md)
