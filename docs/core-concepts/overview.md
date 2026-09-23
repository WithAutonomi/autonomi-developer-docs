# Core Concepts Overview

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
  source_repo: self_encryption
  source_ref: master
  source_commit: 4021f663612c5b963bef935b277eb65416b7d958
  verified_date: 2026-08-08
  verification_mode: current-merged-truth
-->
<!-- verification:
  source_repo: saorsa-pqc
  source_ref: main
  source_commit: 4fbb31d3d29f710726edd32e12ce7b1f64a2aae1
  verified_date: 2026-08-04
  verification_mode: current-merged-truth
-->

This page introduces the concepts that matter most when you build on Autonomi.

## Storage model

When you upload a file, self-encryption splits it into chunks and encrypts them before they are stored on the Autonomi Network. Each chunk has an address derived from its contents and cannot be changed in place.

Self-encryption also creates a **DataMap**: the information needed to find the chunks, decrypt them, and reassemble the original file. Public and private files use this same storage model. The difference is how the DataMap is handled:

- **Public uploads** publish the DataMap and return an address. Share that address so others can retrieve the file.
- **Private uploads** return the DataMap to you instead of publishing it. Keep it private and backed up; you need it to retrieve the file.

Raw chunk operations let you store bytes directly when your application needs control over its own storage format. They do not apply self-encryption or create a DataMap for you.

Read more in [Data Types](data-types.md).

## Keys, addresses, and DataMaps

Wallet keys pay for writes, public addresses retrieve public data, and a `DataMap` provides the critical retrieval material for private data.

Read more in [Keys, Addresses, and DataMaps](keys-addresses-and-datamaps.md).

## Self-encryption

Data and file uploads use self-encryption to encrypt content, split it into chunks, and produce the `DataMap` used later for retrieval. Raw chunk operations are the exception: they store the bytes you supply and do not apply self-encryption for you.

Read more in [Self-encryption](self-encryption.md).

## Post-quantum cryptography

The cryptography stack uses ML-DSA-65 for signatures and ML-KEM-768 for key encapsulation. Those algorithms matter most when you are reasoning about network identity, transport security, or the broader security model.

Read more in [Post-Quantum Cryptography](post-quantum-cryptography.md).

## Payment model

Autonomi is designed around pay-once, immutable storage. Uploads are wallet-backed writes: you pay when you store data, then retrieve it later without recurring storage fees or retrieval payments.

Read more in [Payment Model](payment-model.md).

## Reading guide

Start here depending on what you need next:

- If you are building an application: [Data Types](data-types.md), then [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
- If you need to understand wallets, public addresses, and private retrieval material: [Keys, Addresses, and DataMaps](keys-addresses-and-datamaps.md)
- If you need to understand the encryption path: [Self-encryption](self-encryption.md)
- If you need to understand upload costs and wallets: [Payment Model](payment-model.md), then [Estimate Costs and Handle Upload Payments](../guides/estimate-costs-and-handle-upload-payments.md)
- If you need the security context: [Post-Quantum Cryptography](post-quantum-cryptography.md)
