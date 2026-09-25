# Python SDK

Use `ant-sdk` to connect directly to the Autonomi Network from Python. Your application loads the network library through `ant_ffi`; no separate daemon is required. This reference covers installation, connection and retrieval methods, Python types, and errors, with a public-read example.

To manage networking outside your application instead, [start the local daemon](../start-the-local-daemon.md) and use its service-backed clients.

## Install

Use Python 3.9 or later. In a new working directory, create and activate a virtual environment. These commands use a macOS/Linux shell:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install ant-sdk
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead. The package includes the network library your program loads. Install `ant-sdk`; import it as `ant_ffi`.

## Connection and retrieval API

Import `Client` from `ant_ffi`. Await the connection method to obtain a client, then await retrieval methods on that instance.

| Method | Result after awaiting | Purpose |
|--------|-----------------------|---------|
| `Client.connect_default(data_dir=None)` | `Client` | Connect using built-in public peers, with no payment wallet attached. |
| `client.data_get_public(address_hex)` | `bytes` | Retrieve public content by its address. |
| `client.data_get_private(data_map_hex)` | `bytes` | Retrieve private content using its serialized DataMap. |
| `client.file_download_public(address_hex, dest_path)` | `None` | Download public content to a destination path string. |
| `client.file_download_private(data_map_hex, dest_path)` | `None` | Download private content to a destination path string. |

Omit `data_dir` to use the default local state location. Supplying a directory changes process-wide `HOME`, not state isolated to one client; see [client lifetime](../reference/native-sdks.md#client-lifetime) before overriding it.

### Public-read example

Create `retrieve.py` with this program. It connects with the defaults and reads a public JPEG without a wallet or payment. The program writes the returned bytes itself so it can refuse to overwrite an existing `downloaded.jpg`.

```python
import asyncio
import sys

from ant_ffi import Client, ClientError

ADDRESS = "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a"


async def main():
    print("Connecting...", flush=True)
    client = await Client.connect_default()
    content = await client.data_get_public(ADDRESS)
    with open("downloaded.jpg", "xb") as output:
        output.write(content)
    print(f"Saved {len(content)} bytes to downloaded.jpg")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ClientError, OSError, ValueError) as error:
        sys.exit(f"Download failed: {error}")
```

Run it in the activated environment:

```bash
python retrieve.py
```

Open `downloaded.jpg` to view the image. A successful run prints:

```text
Connecting...
Saved 138931 bytes to downloaded.jpg
```

## Type mappings

| Value | Python type | Format |
|-------|-------------|--------|
| Public address (`address_hex`) | `str` | 64 hexadecimal characters, without `0x`; replace `ADDRESS` to read another public file. |
| Private DataMap (`data_map_hex`) | `str` | Hex-encoded serialized DataMap, not a public address or raw file bytes. |
| Retrieved content | `bytes` | File content, not text decoded by the SDK. |

Keep a private DataMap secret and backed up: anyone who has it can retrieve the content.

## Errors

Catch `ClientError` around awaited client calls. Its variants include `ClientError.InvalidInput`, `ClientError.InitializationFailed`, `ClientError.NetworkError`, and `ClientError.Timeout`; each carries a `reason` string. Python file operations can raise `OSError` separately, as handled in the example.

- **No matching distribution:** native packages cover macOS 11+ on Intel or Apple Silicon, Linux with glibc 2.28+ on x86-64 or ARM64, and Windows x86-64. Check your Python version and platform.
- **Cannot import ant_ffi:** activate the environment where you installed `ant-sdk`.
- **File already exists:** preserve or rename `downloaded.jpg` before running again.
- **Connection or retrieval fails:** check UDP connectivity and the full address. A network failure does not mean the file is missing.

## Full API reference

See the [Native SDK Reference](../reference/native-sdks.md) for storage methods, upload result fields, payment configuration, external signing, and client lifetime. The default read-only client is not configured for paid uploads.

## Related pages

- Other SDK languages include [Node.js](nodejs.md) and [.NET](csharp.md).
- [Build with the SDKs](../install.md): compare direct libraries and service-backed clients.
