# Python Client Reference

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the Python client library in your application to store and retrieve data. It sends requests to a local daemon, a separate background service called **antd** that connects to the Autonomi Network. Follow [Start the Local Daemon](../../start-the-local-daemon.md) before connecting. This reference covers REST; synchronous and asynchronous REST/gRPC clients are available.

## Install

Use Python 3.10 or later. Install the [antd package](https://pypi.org/project/antd/) with its REST dependencies in your project's virtual environment. To create one:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'antd[rest]'
```

Check that `python3 --version` reports 3.10 or later before creating the environment. The `rest` extra supplies the HTTP dependency; `grpc` and `all` supply gRPC-only or combined dependencies. Installing the client does not install or start antd. Examples on this page use the `antd` package 0.2 with antd 0.14. Save each Python example as `app.py` and run it with `python app.py`.

## Connect to antd

With the local service running, `AntdClient()` uses `http://localhost:8082` with a 300-second timeout.

```python
from antd import AntdClient


def main() -> None:
    client = AntdClient()
    try:
        health = client.health()
        print(f"antd version: {health.version}")
    except Exception as exc:
        raise SystemExit(f"antd request failed: {exc}") from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
```

A successful run prints:

```text
antd version: <version>
```

For a different port, pass `base_url` to `AntdClient`. Port discovery is explicit: import `discover_daemon_url` from `antd` and use its result, or `http://localhost:8082` if it returns an empty string. The health result does not include peer counts or `write_ready`; use the [REST health endpoint](../rest-api.md#health) for those fields. A successful health check is not a guarantee that an upload will succeed.

## Retrieve public data

Retrieve a public JPEG without a wallet. This example writes `example.jpg` in your working directory, replacing a file with that name if one exists.

```python
from pathlib import Path

from antd import AntdClient


def main() -> None:
    client = AntdClient()
    try:
        data = client.data_get_public(
            "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a"
        )
        Path("example.jpg").write_bytes(data)
        print(f"Saved {len(data)} bytes to example.jpg")
    except Exception as exc:
        raise SystemExit(f"Retrieval failed: {exc}") from exc
    finally:
        client.close()


if __name__ == "__main__":
    main()
```

Expected output:

```text
Saved 138931 bytes to example.jpg
```

## Data methods

| Method | Input | Result |
|------|------|------|
| `health()` | None | `HealthStatus` |
| `data_get_public(address)` | Public address as a 64-character hexadecimal string | `bytes` |
| `data_get(data_map)` | Caller-held DataMap as a hexadecimal string | `bytes` |
| `data_put_public(data)` | `bytes` | `DataPutPublicResult`; retrieve with its `address` |
| `data_put(data)` | `bytes` | `DataPutResult`; retain its `data_map` for retrieval |

The retrieval methods above return the complete content in memory. Keep private DataMaps secure: anyone with the DataMap can retrieve the content.

## Type mappings

| Autonomi type | Python type |
|------|------|
| `HealthStatus` | `antd.HealthStatus` |
| `PutResult` | `antd.PutResult` for chunk writes |
| `DataPutPublicResult` | `antd.DataPutPublicResult` |
| `DataPutResult` | `antd.DataPutResult` |
| `FilePutPublicResult` | `antd.FilePutPublicResult` |
| `FilePutResult` | `antd.FilePutResult` |
| `PaymentMode` | `antd.PaymentMode` |
| `UploadCostEstimate` | `antd.UploadCostEstimate` |
| `WalletAddress` | `antd.WalletAddress` |
| `WalletBalance` | `antd.WalletBalance` |
| `PrepareUploadResult` | `antd.PrepareUploadResult` |
| `FinalizeUploadResult` | `antd.FinalizeUploadResult` |
| Raw data | `bytes` |

## Error handling

An address with no stored data raises `NotFoundError`, a subclass of `AntdError`.

```python
from antd import AntdClient, AntdError, NotFoundError


def main() -> None:
    client = AntdClient()
    try:
        client.data_get_public("0" * 64)
    except NotFoundError:
        print("No data is stored at that address")
    except AntdError as exc:
        print(f"antd request failed: {exc}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
```

Output when the valid address is not stored:

```text
No data is stored at that address
```

External-signer finalize methods raise `PartialUploadError`, a subclass of `NetworkError`, when some chunks remain unstored; it carries `chunks_stored`, `chunks_failed`, `total_chunks`, `retryable`, and `retention_known`. When `retryable` is `True`, repeating the same finalize call with the same upload ID stores the remainder without paying again; see the [external-signer guide](../../how-to-guides/use-external-signers-for-upload-payments.md) for the other cases.

## Store and retrieve data

`data_put_public` uploads content and returns a shareable address; `data_put` returns a private DataMap instead. Both accept `payment_mode`, using `PaymentMode.AUTO` by default. Follow [Store Data on the Network](../../store-data-on-the-network.md) for wallet and upload setup.

Uploads require a configured wallet and Ethereum Virtual Machine (EVM) payment settings. They can spend funds and publish data permanently. Confirm the intended network, payment contracts, and budget before uploading; a successful health check or retrieval does not establish upload readiness. Use the [local-development setup](../../../guides/set-up-a-local-network.md) to assess your integration before committing funds.

### External-signer limitations

REST and gRPC expose wallet operations and external-signer prepare/finalize methods, but their response fields are not identical. The Python REST parser expects `payment_type: "merkle_batch"`, while antd returns `payment_type: "merkle"`, so it drops Merkle pool commitments. Its gRPC convenience methods also omit multi-batch fields and do not support multi-batch Merkle finalization. Do not use the Python convenience client for Merkle preparation; use the raw [REST external-signer workflow](../../how-to-guides/use-external-signers-for-upload-payments.md) instead.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).

## Related pages

- [Native Python SDK](../../native/python.md): connect directly without a local service, using a different package and API.
- [Native SDKs](../../native/README.md): language options for direct connections.
