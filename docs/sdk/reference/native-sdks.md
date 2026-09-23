# Native SDK Reference

The libraries in the native Python, Node.js, and C# SDKs connect directly to the Autonomi Network from your application, without a separate background service.

## Clients and capabilities

Use `Client` from Python's `ant_ffi` module, Node.js's `@withautonomi/ant-sdk` package, or C#'s `AntFfi` namespace. These static connection methods use built-in production bootstrap peers:

| Capability | Python | Node.js | C# |
|------------|--------|---------|----|
| Read without a payment wallet | `connect_default()` | `connectDefault()` | `ConnectDefault(dataDir)` |
| Attach your wallet key for paid uploads | `connect_default_with_wallet(private_key)` | `connectDefaultWithWallet(privateKey)` | `ConnectDefaultWithWallet(privateKey, dataDir)` |
| Prepare uploads for an external wallet to sign | `connect_default_for_external_signer()` | `connectDefaultForExternalSigner()` | `ConnectDefaultForExternalSigner(dataDir)` |

Call these methods on `Client` and await the result. The read-only constructor attaches no wallet or payment configuration. Wallet-backed constructors use your supplied key; they do not create or fund a wallet. External-signer constructors configure payments without holding a wallet key. Both payment-enabled choices use Arbitrum One.

Python and Node.js also accept an optional final state-directory argument, `data_dir` or `dataDir`. C# signatures above pass that directory explicitly. See [Client lifetime](#client-lifetime) before overriding it.

## Retrieve data

Use a public address to retrieve shared content, or a private DataMap to retrieve private content. A public address is a string of 64 hexadecimal characters without `0x`. A private DataMap is a hex-encoded serialized value, not a public address: anyone who has it can retrieve the content. Keep it secret and backed up.

| Operation | Python | Node.js | C# |
|-----------|--------|---------|----|
| Public content in memory | `data_get_public(address_hex)` | `dataGetPublic(addressHex)` | `DataGetPublic(addressHex)` |
| Private content in memory | `data_get_private(data_map_hex)` | `dataGetPrivate(dataMapHex)` | `DataGetPrivate(dataMapHex)` |
| Public content to disk | `file_download_public(address_hex, dest_path)` | `fileDownloadPublic(addressHex, destPath)` | `FileDownloadPublic(addressHex, destPath)` |
| Private content to disk | `file_download_private(data_map_hex, dest_path)` | `fileDownloadPrivate(dataMapHex, destPath)` | `FileDownloadPrivate(dataMapHex, destPath)` |

All four operations are asynchronous instance methods. In-memory retrieval returns Python `bytes`, a Node.js `Buffer`, or C# `byte[]`. File-download methods take a destination path string and complete without returning file content: Python returns `None`, Node.js returns `Promise<void>`, and C# returns `Task`.

## Store data with a wallet

Uploads can spend funds and store permanent data. Use a wallet-backed client with Autonomi Network Token (ANT) for storage and gas funds for blockchain transactions. Keep private keys out of source code and logs.

| Operation | Python | Node.js | C# |
|-----------|--------|---------|----|
| Upload a public file | `file_upload_public(path, payment_mode)` | `fileUploadPublic(path, paymentMode)` | `FileUploadPublic(path, paymentMode)` |
| Upload a private file | `file_upload_private(path, payment_mode)` | `fileUploadPrivate(path, paymentMode)` | `FileUploadPrivate(path, paymentMode)` |
| Upload public bytes | `data_put_public(data, payment_mode)` | `dataPutPublic(data, paymentMode)` | `DataPutPublic(data, paymentMode)` |
| Upload private bytes | `data_put_private(data, payment_mode)` | `dataPutPrivate(data, paymentMode)` | `DataPutPrivate(data, paymentMode)` |

Pass paths as strings. In-memory uploads accept Python `bytes`, Node.js `Uint8Array` (including `Buffer`), or C# `byte[]`. Await the upload result before retaining its retrieval value.

### Payment modes

Pass exported enum values, not strings.

| Choice | Python | Node.js and C# |
|--------|--------|----------------|
| Let the SDK choose | `PaymentMode.AUTO` | `PaymentMode.Auto` |
| Merkle batch payment | `PaymentMode.MERKLE` | `PaymentMode.Merkle` |
| Per-quote payment | `PaymentMode.SINGLE` | `PaymentMode.Single` |

### Upload results

Public file and byte uploads return `FilePutPublicResult` and `DataPutPublicResult`; private uploads return `FilePutPrivateResult` and `DataPutPrivateResult`.

| Value | Python field | Node.js and C# field | Present on |
|-------|--------------|---------------------|------------|
| Shareable public address | `address` | `address` | Public results |
| Secret private DataMap | `data_map` | `dataMap` | Private results |
| Number of chunks stored | `chunks_stored` | `chunksStored` | All four results |
| Payment mode used | `payment_mode_used` | `paymentModeUsed` | All four results |
| Storage cost, in atto-tokens | `storage_cost_atto` | `storageCostAtto` | File results only |
| Gas cost, in wei | `gas_cost_wei` | `gasCostWei` | File results only |

C# result properties use lower camel case: `result.address` and `result.dataMap`, not `result.Address` or `result.DataMap`. Counts are Python `int`, Node.js `number`, or C# `ulong`. Cost amounts are base-10 strings; preserve integer precision rather than converting them to floating-point numbers.

Public file uploads include the DataMap in their upload payment batch. Public in-memory uploads store the content first, then store its DataMap separately. Do not assume those methods have identical payment behavior.

### Estimates and approval

| Operation | Python | Node.js | C# |
|-----------|--------|---------|----|
| Estimate file cost | `estimate_file_cost(path, payment_mode)` | `estimateFileCost(path, paymentMode)` | `EstimateFileCost(path, paymentMode)` |
| Approve token spending | `wallet_approve()` | `walletApprove()` | `WalletApprove()` |

The asynchronous estimate returns `CostEstimate`. Check `confidence`: a zero estimate from incomplete sampling does not prove free storage. The estimate excludes the extra public DataMap chunk. Its `estimated_gas_cost_wei` (Python) or `estimatedGasCostWei` (Node.js/C#) is a decimal string based on a heuristic, not a live gas quote.

**Obtain explicit authorization before approving.** Wallet approval grants the configured payment vault the maximum token allowance (`2^256 - 1`), not an allowance limited to one file. It can submit a blockchain transaction and spend gas.

Direct-wallet uploads can also grant that unlimited allowance automatically when the existing allowance is too low. Obtain authorization before the upload as well: its first payment may spend gas on both approval and payment.

## External wallet signing

Use an external-signer client when another wallet holds the key and signs payments. Keep the same client instance from preparation through finalization.

| Operation | Python | Node.js | C# |
|-----------|--------|---------|----|
| Prepare a file | `prepare_file_upload(path, visibility)` | `prepareFileUpload(path, visibility)` | `PrepareFileUpload(path, visibility)` |
| Prepare bytes | `prepare_data_upload(data, visibility)` | `prepareDataUpload(data, visibility)` | `PrepareDataUpload(data, visibility)` |
| Build transaction requests | `payment_transactions(upload_id)` | `paymentTransactions(uploadId)` | `PaymentTransactions(uploadId)` |
| Finalize per-quote payments | `finalize_upload(upload_id, tx_hashes)` | `finalizeUpload(uploadId, txHashes)` | `FinalizeUpload(uploadId, txHashes)` |
| Finalize Merkle payment | `finalize_upload_merkle(upload_id, winner_pool_hash)` | `finalizeUploadMerkle(uploadId, winnerPoolHash)` | `FinalizeUploadMerkle(uploadId, winnerPoolHash)` |
| Discard preparation | `cancel_upload(upload_id)` | `cancelUpload(uploadId)` | `CancelUpload(uploadId)` |

Preparation takes `Visibility.PUBLIC` or `Visibility.PRIVATE` in Python; Node.js and C# use `Visibility.Public` or `Visibility.Private`. It returns `PreparedUploadInfo`. Retain `upload_id` and inspect `payment_type` in Python, or `uploadId` and `paymentType` in Node.js/C#.

Transaction building returns ordered `TxRequest` values, not signed or submitted transactions. Have your wallet review, sign, and submit them in order, waiting for each successful receipt before continuing. The requests include token approval followed by payment; unlike wallet approval above, these approvals use the quoted total for per-quote payments or a calculated upper bound for Merkle payment.

Choose finalization by payment type:

- `PaymentType.WAVE_BATCH` in Python or `PaymentType.WaveBatch` in Node.js/C#: map every payment request's `quote_hashes` (Python) or `quoteHashes` (Node.js/C#) to its transaction hash. Pass a Python dictionary, Node.js object, or C# `Dictionary<string, string>`; both hash keys and values use `0x`-prefixed hex. If everything was already stored, finalize with an empty map.
- `PaymentType.MERKLE` in Python or `PaymentType.Merkle` in Node.js/C#: pass the winning pool hash from the payment receipt. The helper is `merkle_winner_pool_hash(rpc_url, vault_address, tx_hash)` in Python, `merkleWinnerPoolHash(rpcUrl, vaultAddress, txHash)` in Node.js, or `AntFfiMethods.MerkleWinnerPoolHash(rpcUrl, vaultAddress, txHash)` in C#.

Finalization returns `ExternalUploadResult`: a DataMap, an address for public uploads only, chunk count, storage cost, and gas cost. Field casing and amount types follow the upload-result table; there is no payment-mode field on this result.

### Payment and retry limits

- External signing supports one Merkle payment batch per upload. Preparation rejects uploads requiring multiple Merkle batches; do not interpret this as a fixed file-size limit.
- An empty preparation `payments` list or Merkle `total_amount` / `totalAmount` of `"0"` does not mean free storage. Check `already_stored` / `alreadyStored` and the payment type.
- Prepared uploads are client-local state, not persistent resume handles. There is no automatic expiry. Cancellation is synchronous and returns a boolean indicating whether an entry was removed; it releases preparation, not an on-chain payment.
- **A storage failure during paid finalization consumes the prepared state.** Preparing again obtains new quotes; old transaction hashes cannot safely be reused. Preserve payment records and do not automatically pay again. Malformed hash input and a mismatched finalization method are rejected before consuming state, so those specific mistakes can be corrected on the same preparation.

## Client lifetime

Supplying `data_dir` / `dataDir` changes process-wide `HOME` inside the native library, not a directory isolated to that client. Use one client per process; use a dedicated worker process if your application needs separate state or a different home directory.

The Node.js client has no explicit close method or per-request cancellation argument. A JavaScript timeout does not stop native work. For bounded standalone jobs, process termination also stops native background work; do not put `process.exit()` into a long-running server.

C# clients expose `Dispose()`; use `using` to release the native handle. Asynchronous C# methods return `Task` or `Task<T>` without an `Async` suffix, and the methods listed here take no `CancellationToken`.

For C#, you need a .NET 8-compatible runtime and a matching native library. The package bundles `win-x64`, `win-arm64`, `linux-x64`, `linux-arm64`, `osx-x64`, and `osx-arm64`; it has no Linux musl-specific library. Native Node.js requires its platform binary, supplied through npm's optional dependencies; it is not a browser SDK.

## Errors

Python exposes `ClientError`; C# exposes `ClientException`. Native Node.js failures reject promises as JavaScript errors with a generic failure status and a message, not a distinct stable code for every native error. A failed upload does not establish that no money was spent.

| Symptom | What to check |
|---------|---------------|
| Invalid address | Use a complete public hex address, not a URL or private DataMap. |
| Connection or retrieval failure | Check UDP connectivity and the address. A timeout does not prove the data is absent. |
| Wallet/payment configuration error | Use a wallet-backed constructor for direct paid uploads or the external-signer constructor for preparation and finalization. |
| Native library cannot load | Match the process architecture to the installed native binary. For Node.js, keep npm's optional dependencies enabled. |

## Related pages

- [Python SDK](../native/python.md)
- [Node.js SDK](../native/nodejs.md)
- [.NET SDK](../native/csharp.md)
- [Build with the SDKs](../install.md)
- [Keys, Addresses, and DataMaps](../../core-concepts/keys-addresses-and-datamaps.md)
