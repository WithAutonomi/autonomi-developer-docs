# JavaScript Client Reference

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: a4accf1fb617a8b4d8b53e928a279d212411540f
  verified_date: 2026-08-20
  verification_mode: current-merged-truth
-->

Use the JavaScript client library in your Node.js application to store and retrieve data. It sends requests to a local daemon, a separate background service called **antd** that connects to the Autonomi Network. Follow [Start the Local Daemon](../../start-the-local-daemon.md) before connecting. This reference covers the REST client.

## Install

Use Node.js 18 or later. Install [@withautonomi/antd](https://www.npmjs.com/package/@withautonomi/antd/v/0.1.0) in your application directory:

```bash
npm install @withautonomi/antd
```

Installing the client does not install or start antd. Keep the `@withautonomi/` scope: the npm package named `antd` is the unrelated Ant Design library. Save each example as `app.mjs` and run it with `node app.mjs`.

## Connect to antd

With the local service running, `createClient()` uses `http://localhost:8082` with a 300,000-millisecond timeout.

```javascript
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const health = await client.health();
  console.log(`antd version: ${health.version}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

A successful run prints:

```text
antd version: <version>
```

For a different port, pass `baseUrl` to `createClient`. Alternatively, import `RestClient` from the package and call `RestClient.autoDiscover()` to read antd's port file. It returns `{ client, url }`; an empty `url` means the client uses the default URL. The health result does not include peer counts or `write_ready`; use the [REST health endpoint](../rest-api.md#health) for those fields. A successful health check is not a guarantee that an upload will succeed.

## Retrieve public data

Retrieve a public JPEG without a wallet. This example writes `example.jpg` in your working directory, replacing a file with that name if one exists.

```javascript
import { writeFile } from "node:fs/promises";
import { createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();
  const data = await client.dataGetPublic(
    "711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a",
  );
  await writeFile("example.jpg", data);
  console.log(`Saved ${data.length} bytes to example.jpg`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

Expected output:

```text
Saved 138931 bytes to example.jpg
```

## Data methods

All methods below return promises.

| Method | Input | Result |
|------|------|------|
| `health()` | None | `HealthStatus` |
| `dataGetPublic(address)` | Public address as a 64-character hexadecimal string | `Buffer` |
| `dataGet(dataMap)` | Caller-held DataMap as a hexadecimal string | `Buffer` |
| `dataPutPublic(data)` | `Buffer` | `DataPutPublicResult`; retrieve with its `address` |
| `dataPut(data)` | `Buffer` | `DataPutResult`; retain its `dataMap` for retrieval |

The retrieval methods above return the complete content in memory. Keep private DataMaps secure: anyone with the DataMap can retrieve the content.

## Type mappings

| Autonomi type | JavaScript type |
|------|------|
| `HealthStatus` | object with `ok`, `network`, `version`, `evmNetwork`, `uptimeSeconds`, `buildCommit`, `paymentTokenAddress`, and `paymentVaultAddress` |
| `PutResult` | `{ cost: string, address: string }` for chunk writes |
| `DataPutPublicResult` | `{ address: string, chunksStored: number, paymentModeUsed: string }` |
| `DataPutResult` | `{ dataMap: string, chunksStored: number, paymentModeUsed: string }` |
| `FilePutPublicResult` | `{ address: string, storageCostAtto: string, gasCostWei: string, chunksStored: number, paymentModeUsed: string }` |
| `FilePutResult` | `{ dataMap: string, storageCostAtto: string, gasCostWei: string, chunksStored: number, paymentModeUsed: string }` |
| `PaymentMode` | string values: `auto`, `merkle`, or `single` |
| `WalletAddress` | `{ address: string }` |
| `WalletBalance` | `{ balance: string, gasBalance: string }` |
| `PaymentInfo` | `{ quoteHash: string, rewardsAddress: string, amount: string }` |
| `CandidateNodeEntry` | `{ rewardsAddress: string, amount: string }` |
| `PoolCommitmentEntry` | `{ poolHash: string, candidates: CandidateNodeEntry[] }` |
| `PrepareUploadResult` | object with `uploadId`, `paymentType`, `payments`, `totalAmount`, `paymentVaultAddress`, `paymentTokenAddress`, `rpcUrl`, `totalChunks`, `alreadyStoredCount`, plus optional `depth`, `poolCommitments`, and `merklePaymentTimestamp` for Merkle uploads |
| `FinalizeUploadResult` | `{ address: string, chunksStored: number, dataMap: string, dataMapAddress: string }` |
| `PrepareChunkResult` | `{ address: string, alreadyStored: boolean, uploadId: string, paymentType: string, payments: PaymentInfo[], totalAmount: string, paymentVaultAddress: string, paymentTokenAddress: string, rpcUrl: string }` |
| `UploadCostEstimate` | `{ cost: string, fileSize: number, chunkCount: number, estimatedGasCostWei: string, paymentMode: string }` |
| Raw data | `Buffer` |

## Error handling

antd can report a missing DataMap as an internal error instead of not found. Handle `InternalError`, but do not interpret every internal error as missing data. Confirm the address with its publisher and inspect the error message.

```javascript
import { InternalError, createClient } from "@withautonomi/antd";

async function main() {
  const client = createClient();

  try {
    await client.dataGetPublic("0".repeat(64));
  } catch (error) {
    if (error instanceof InternalError) {
      console.log(`Internal error; confirm the address and inspect the cause: ${error.message}`);
    } else {
      throw error;
    }
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Output shape for an internal error:

```text
Internal error; confirm the address and inspect the cause: <error details>
```

## Store and retrieve data

`dataPutPublic` uploads content and returns a shareable address; `dataPut` returns a private DataMap instead. Both accept an optional `{ paymentMode }` argument, using `"auto"` by default. Follow [Store Data on the Network](../../store-data-on-the-network.md) for wallet and upload setup.

Uploads require a configured wallet and Ethereum Virtual Machine (EVM) payment settings. They can spend funds and publish data permanently. Confirm the intended network, payment contracts, and budget before uploading; a successful health check or retrieval does not establish upload readiness. Use the [local-development setup](../../../guides/set-up-a-local-network.md) to assess your integration before committing funds.

For an external signer, the client's Merkle prepare/finalize helpers expose a single batch, not the complete multi-batch response and finalization fields. Use the raw [REST external-signer workflow](../../how-to-guides/use-external-signers-for-upload-payments.md) for multi-batch Merkle uploads.

## Full API reference

For all available **antd** endpoints, see the [REST API](../rest-api.md).

## Related pages

- [Native Node.js SDK](../../native/nodejs.md): connect directly without a local service, using a different package and API.
- [Native SDKs](../../native/README.md): language options for direct connections.
