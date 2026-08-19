# JavaScript SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 8378338ca04d3a78db8ad0c943daf182cfd27763
  verified_date: 2026-08-19
  verification_mode: current-merged-truth
-->

The JavaScript SDK is the REST client package for `antd`.

## Install

```bash
npm install antd
```

## Connect to the daemon

```javascript
import { RestClient, createClient } from "antd";

// Default REST client
const client = createClient();

// Explicit constructor
const directClient = new RestClient({ baseUrl: "http://localhost:8082" });

// Custom URL or timeout
const remoteClient = createClient({ baseUrl: "http://custom-host:9090", timeout: 60000 });

// Auto-discover from daemon.port
const { client: discoveredClient, url } = RestClient.autoDiscover();
console.log(url);
```

## Store and retrieve data

For upload examples in this section, start `antd` in a write-enabled mode first. On the default network, that means wallet plus EVM payment configuration. On a local devnet, `ant dev start` provisions that for you.

```javascript
import { createClient } from "antd";

async function main() {
  const client = createClient();
  const status = await client.health();
  if (!status.ok) throw new Error("Daemon is not healthy");

  const result = await client.dataPutPublic(Buffer.from("Hello from JavaScript!"));
  console.log(result.address);

  const data = await client.dataGetPublic(result.address);
  console.log(data.toString());
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

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
| `PrepareUploadResult` | object with `uploadId`, `paymentType`, `payments`, `totalAmount`, `paymentVaultAddress`, `paymentTokenAddress`, `rpcUrl`, plus optional `depth`, `poolCommitments`, and `merklePaymentTimestamp` for Merkle uploads |
| `FinalizeUploadResult` | `{ address: string, chunksStored: number, dataMap: string, dataMapAddress: string }` |
| `PrepareChunkResult` | `{ address: string, alreadyStored: boolean, uploadId: string, paymentType: string, payments: PaymentInfo[], totalAmount: string, paymentVaultAddress: string, paymentTokenAddress: string, rpcUrl: string }` |
| `UploadCostEstimate` | `{ cost: string, fileSize: number, chunkCount: number, estimatedGasCostWei: string, paymentMode: string }` |
| Raw data | `Buffer` |

## Error handling

```javascript
import { NotFoundError, PaymentError, createClient } from "antd";

async function main() {
  const client = createClient();

  try {
    await client.dataGetPublic("nonexistent_address");
  } catch (error) {
    if (error instanceof NotFoundError) {
      console.log("Data not found");
    } else if (error instanceof PaymentError) {
      console.log("Insufficient funds");
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

## Full API reference

For all available daemon endpoints, see the [REST API](../rest-api.md).
