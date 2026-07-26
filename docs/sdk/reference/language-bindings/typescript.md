# TypeScript SDK

<!-- verification:
  source_repo: ant-sdk
  source_ref: main
  source_commit: 09da0f4c94fb15d928b5e9f1d4a9ae484176c995
  verified_date: 2026-07-24
  verification_mode: current-merged-truth
-->

The TypeScript SDK uses the same `antd` package as JavaScript and ships its own type definitions.

## Install

```bash
npm install antd
```

## Connect to the daemon

```typescript
import { RestClient, createClient, type RestClientOptions } from "antd";

const client = createClient();

const options: RestClientOptions = {
  baseUrl: "http://localhost:8082",
  timeout: 60_000,
};

const directClient = new RestClient(options);
```

## Store and retrieve data

```typescript
import { createClient, type DataPutPublicResult } from "antd";

async function main(): Promise<void> {
  const client = createClient();
  const result: DataPutPublicResult = await client.dataPutPublic(
    Buffer.from("Hello from TypeScript!"),
  );
  console.log(result.address);

  const data: Buffer = await client.dataGetPublic(result.address);
  console.log(data.toString());
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

## Type mappings

| Autonomi type | TypeScript type |
|------|------|
| `HealthStatus` | `{ ok: boolean; network: string; version: string; evmNetwork: string; uptimeSeconds: number; buildCommit: string; paymentTokenAddress: string; paymentVaultAddress: string }` |
| `PutResult` | `{ cost: string; address: string }` for chunk writes |
| `DataPutPublicResult` | `{ address: string; chunksStored: number; paymentModeUsed: string }` |
| `DataPutResult` | `{ dataMap: string; chunksStored: number; paymentModeUsed: string }` |
| `FilePutPublicResult` | `{ address: string; storageCostAtto: string; gasCostWei: string; chunksStored: number; paymentModeUsed: string }` |
| `FilePutResult` | `{ dataMap: string; storageCostAtto: string; gasCostWei: string; chunksStored: number; paymentModeUsed: string }` |
| `PaymentMode` | `"auto"`, `"merkle"`, or `"single"` |
| `WalletAddress` | `{ address: string }` |
| `WalletBalance` | `{ balance: string; gasBalance: string }` |
| `PaymentInfo` | `{ quoteHash: string; rewardsAddress: string; amount: string }` |
| `CandidateNodeEntry` | `{ rewardsAddress: string; amount: string }` |
| `PoolCommitmentEntry` | `{ poolHash: string; candidates: CandidateNodeEntry[] }` |
| `PrepareUploadResult` | object with `uploadId`, `paymentType`, `payments`, `totalAmount`, `paymentVaultAddress`, `paymentTokenAddress`, `rpcUrl`, plus optional `depth`, `poolCommitments`, and `merklePaymentTimestamp` for Merkle uploads |
| `FinalizeUploadResult` | `{ address: string; chunksStored: number; dataMap: string; dataMapAddress: string }` |
| `PrepareChunkResult` | `{ address: string; alreadyStored: boolean; uploadId: string; paymentType: string; payments: PaymentInfo[]; totalAmount: string; paymentVaultAddress: string; paymentTokenAddress: string; rpcUrl: string }` |
| `UploadCostEstimate` | `{ cost: string; fileSize: number; chunkCount: number; estimatedGasCostWei: string; paymentMode: string }` |
| Raw data | `Buffer` |

## Error handling

```typescript
import { NotFoundError, PaymentError, createClient } from "antd";

async function main(): Promise<void> {
  const client = createClient();

  try {
    await client.dataGetPublic("nonexistent");
  } catch (error) {
    if (error instanceof NotFoundError) {
      console.log("Not found");
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
