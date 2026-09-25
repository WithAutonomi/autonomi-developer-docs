# Node.js SDK

Use `@withautonomi/ant-sdk` to connect directly to the Autonomi Network from Node.js. Your application loads the compiled network library; no separate daemon is required. This reference covers installation, connection and retrieval methods, JavaScript types, and errors, with a public-read example. The package includes TypeScript declarations.

To manage networking outside your application instead, [start the local daemon](../start-the-local-daemon.md) and use its service-backed clients.

## Install

Use Node.js 16 or later. In a new project directory, run:

```bash
npm init -y
npm install @withautonomi/ant-sdk
```

npm installs the JavaScript interface and the native binary for your platform. Keep optional dependencies enabled. This package runs in Node.js, not browser code.

## Connection and retrieval API

The default import in the example exposes `sdk.Client`. Connection and retrieval methods return promises; await them before using the client or content.

| Method | Return type | Purpose |
|--------|-------------|---------|
| `sdk.Client.connectDefault(dataDir?)` | `Promise<Client>` | Connect using built-in public peers, with no payment wallet attached. |
| `client.dataGetPublic(addressHex)` | `Promise<Buffer>` | Retrieve public content by its address. |
| `client.dataGetPrivate(dataMapHex)` | `Promise<Buffer>` | Retrieve private content using its serialized DataMap. |
| `client.fileDownloadPublic(addressHex, destPath)` | `Promise<void>` | Download public content to a destination path string. |
| `client.fileDownloadPrivate(dataMapHex, destPath)` | `Promise<void>` | Download private content to a destination path string. |

Omit the optional `dataDir` string to use the default local state location. Supplying a directory changes process-wide `HOME`, not state isolated to one client. See [client lifetime](../reference/native-sdks.md#client-lifetime) before overriding it or embedding the client in a long-running application.

### Public-read example

Create `retrieve.mjs` with this program. It connects with the defaults and reads a public JPEG without a wallet or payment. The program writes the returned bytes itself so it can refuse to overwrite an existing `downloaded.jpg`.

```javascript
import sdk from '@withautonomi/ant-sdk';
import { writeFile } from 'node:fs/promises';

const address = '711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a';

try {
  console.log('Connecting...');
  const client = await sdk.Client.connectDefault();
  const bytes = await client.dataGetPublic(address);
  await writeFile('downloaded.jpg', bytes, { flag: 'wx' });
  console.log(`Saved ${bytes.length} bytes to downloaded.jpg`);
  process.exit(0);
} catch (error) {
  console.error('Download failed:', error instanceof Error ? error.message : error);
  process.exit(1);
}
```

Run it as a standalone program:

```bash
node retrieve.mjs
```

This is a standalone download script: `process.exit()` terminates the process and its native background work. Do not copy that exit into a long-running server. The client has no explicit close method or per-request cancellation argument; a JavaScript timeout does not stop native work.

Open `downloaded.jpg` to view the image. A successful run prints:

```text
Connecting...
Saved 138931 bytes to downloaded.jpg
```

## Type mappings

| Value | JavaScript type | Format |
|-------|-----------------|--------|
| Public address (`addressHex`) | `string` | 64 hexadecimal characters, without `0x`; replace `address` to read another public file. |
| Private DataMap (`dataMapHex`) | `string` | Hex-encoded serialized DataMap, not a public address or raw file bytes. |
| Retrieved content | `Buffer` | File content, not text decoded by the SDK. |

Keep a private DataMap secret and backed up: anyone who has it can retrieve the content.

## Errors

Catch rejected promises with `try` / `catch`. Native client errors use the generic `GenericFailure` status and a descriptive message, not a distinct stable code for each failure. File-system errors such as `EEXIST` come from Node.js file operations separately.

- **File already exists:** preserve or rename `downloaded.jpg` before running again.
- **Native binding cannot load:** keep npm's optional dependencies enabled. Native packages cover x64 and ARM64 on macOS, Windows, and Linux (glibc or musl). This package runs in Node.js, not browser code.
- **Connection or retrieval fails:** check UDP connectivity and the full address. A network failure does not mean the file is missing.

## Full API reference

See the [Native SDK Reference](../reference/native-sdks.md) for storage methods, upload result fields, payment configuration, external signing, and client lifetime. The default read-only client is not configured for paid uploads.

## Related pages

- Other SDK languages include [Python](python.md) and [.NET](csharp.md).
- [Build with the SDKs](../install.md): compare direct libraries and service-backed clients.
