# Test Your Application

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-client
  source_ref: main
  source_commit: 9475782ffc85b677aa1866f0f79fb555fca12c45
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: ant-node
  source_ref: main
  source_commit: 33e9cfb666eef361a9eec6b1663c63df04cc4f0b
  verified_date: 2026-08-26
  verification_mode: current-merged-truth
-->

Test application logic without Autonomi services first, then run integration tests in an isolated local environment before considering a paid public-network test.

The concrete examples use the Python `antd` client from the pinned `ant-sdk v0.12.0` checkout, not a separately published Python package. CLI and Direct Rust projects should apply the same test boundaries around their own adapters. For other SDK installation choices, see [SDK Language Bindings](../sdk/reference/language-bindings/overview.md).

## Prerequisites

- Python 3.10 or newer
- Git for the pinned source checkout
- For integration tests: a fresh disposable environment prepared with the exact `ant-sdk v0.12.0` and `ant-node v0.17.1` checkouts
- `protoc`, Rust, Foundry, and `anvil` for the local integration environment

The local workflow is limited to disposable, isolated environments. Its `ant dev stop` command broadly kills matching Anvil processes and deletes shared paths under `~/.local/share/ant` on non-Windows systems. Run integration tests only in a disposable runner or virtual machine, and dispose of that environment after the test.

Use `ant-sdk v0.12.0` and `ant-node v0.17.1` together for this integration setup, rather than substituting the independently released `antd 0.13.0` or `ant-node 0.20.0`. Keep it separate from newer client installations and complete the isolated test before depending on it.

## Steps

### 1. Install the pinned Python source for unit tests

Pin the `ant-sdk v0.12.0` checkout and install it into a virtual environment. The local path keeps these tests on the exact source version used by the integration setup rather than a separately published package.

```bash
#!/usr/bin/env bash
set -euo pipefail

git clone --branch v0.12.0 --depth 1 https://github.com/WithAutonomi/ant-sdk.git
test "$(git -C ant-sdk rev-parse HEAD)" = "8378338ca04d3a78db8ad0c943daf182cfd27763"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --editable "ant-sdk/antd-py[rest]" pytest

python -c 'from antd import AntdClient, DataPutPublicResult; print("antd Python source import passed")'
```

Expected output:

```text
antd Python source import passed
```

### 2. Keep unit tests independent of Autonomi services

Create `test_storage.py`:

```python
from unittest.mock import MagicMock

from antd import DataPutPublicResult


def store_message(client: object, message: bytes) -> str:
    result = client.data_put_public(message)
    return result.address


def test_store_message_returns_the_public_address() -> None:
    mock_client = MagicMock()
    mock_client.data_put_public.return_value = DataPutPublicResult(
        address="ab" * 32,
        chunks_stored=3,
        payment_mode_used="single",
    )

    address = store_message(mock_client, b"test data")

    assert address == "ab" * 32
    mock_client.data_put_public.assert_called_once_with(b"test data")
```

Run it:

```bash
#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
pytest -q test_storage.py
```

Expected output ends with:

```text
1 passed
```

This test verifies your application boundary without starting `antd`, connecting to the Autonomi Network, or making a payment.

### 3. Prepare an isolated integration environment

Use a fresh disposable runner, separate from the unit-test checkout, and follow [Set Up a Local Network](set-up-a-local-network.md). That setup pins:

- `ant-sdk v0.12.0` at `8378338ca04d3a78db8ad0c943daf182cfd27763`
- `ant-node v0.17.1` at `953e565fb713e43769e0e82dc4f424b8cc63ed7a`

It also installs both Python packages from source. Installing only `ant-sdk/ant-dev` can resolve its `antd[rest,grpc]` dependency from PyPI instead of the pinned checkout; install both to keep the same pairing.

Do not use `ant dev reset`. `ant-dev 0.1.0` first runs its broad teardown, then omits the required `preset` restart argument and fails. Do not use `ant dev stop` outside a disposable environment because it broadly terminates Anvil processes and deletes shared paths under `~/.local/share/ant` on non-Windows systems.

### 4. Run a local round-trip integration test

After the isolated local environment reports healthy, create `autonomi-local/test_integration.py` from the directory that contains `autonomi-local`:

```python
from antd import AntdClient


def test_public_data_round_trip() -> None:
    client = AntdClient()
    status = client.health()
    assert status.ok
    assert status.network == "local"

    original = b"Integration test data"
    result = client.data_put_public(original)

    assert len(result.address) == 64
    retrieved = client.data_get_public(result.address)
    assert retrieved == original
```

Run it:

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
source "$WORK_DIR/.venv/bin/activate"
python -m pip install pytest
pytest -q "$WORK_DIR/test_integration.py"
```

Expected output ends with:

```text
1 passed
```

This test uses local test funds and can automatically grant the local payment vault an unlimited allowance when the existing allowance is too low. Retain the test output. The result applies only to the source-only workflow in your isolated local environment and does not establish production compatibility.

### 5. Run bundled smoke tests

From the pinned `ant-sdk` checkout, with the local environment's virtual environment active, `ant-dev` provides these example runners:

`connect` is read-only. `data` estimates cost, performs a local paid upload, and reads the data back. Its first payment can also grant an unlimited allowance, so run it only against the isolated local environment.

```bash
#!/usr/bin/env bash
set -euo pipefail

WORK_DIR="$HOME/autonomi-local"
source "$WORK_DIR/.venv/bin/activate"
cd "$WORK_DIR/ant-sdk"
ant dev example connect
ant dev example data
```

The exact output depends on the local environment. Both commands must exit with status 0; preserve their output with the rest of your integration-test results.

### 6. Isolate the local setup in shared CI

A shared continuous integration (CI) job for this source-only local workflow must use a disposable runner, pin both source tags, install `protoc`, Rust, Foundry, both Python source packages, and preserve logs on failure.

Do not add `ant dev reset` as recovery. On a disposable runner, `ant dev stop` is contained but still uses broad process and filesystem matching; destroying the runner is the safer cleanup boundary.

## Verify it worked

Your unit layer is working when `test_storage.py` passes without any Autonomi process. Your local integration layer is working when the full health response identifies `network: local` and `test_integration.py` retrieves bytes identical to those uploaded.

Neither result proves compatibility with the deployed production Autonomi Network. Before production uploads, run a controlled paid upload and retrieval test using the checklist in [Deploy to Mainnet](deploy-to-mainnet.md).

## Common errors

**Python uses a different client version**: For this setup, install `ant-sdk/antd-py[rest,grpc]` and `ant-sdk/ant-dev` together from the pinned source checkout instead of substituting the separately published `antd` package.

**Health check never turns green**: Preserve `~/.ant-dev/antd.log` and `~/.ant-dev/devnet.log` from the disposable environment. Check `protoc`, `anvil`, source commits, and the `ant-node` path.

**Wrong daemon API shape in direct HTTP tests**: Buffered data endpoints return base64 inside JSON. The Python client decodes that field and returns `bytes`.

**Local wallet issues**: Do not use the broken reset command. Preserve the manifest and logs, dispose of the isolated environment, then create a fresh isolated run.

## Next steps

- [Set Up a Local Network](set-up-a-local-network.md)
- [Deploy to Mainnet](deploy-to-mainnet.md)
- [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
