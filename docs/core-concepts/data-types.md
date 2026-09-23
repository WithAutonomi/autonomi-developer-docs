# Data Types

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

Autonomi stores content as immutable, content-addressed chunks. As a developer, you work through data, file, or raw chunk operations. Data and file operations produce a `DataMap` as retrieval metadata: public workflows publish it and return an address, while private workflows return it to you.

## Why it matters

Because Autonomi stores content as immutable, content-addressed chunks, you need to understand how data, file, and raw chunk operations package, publish, and retrieve that content. This page also explains how public and private `DataMap` handling fits into those operations.

## One storage primitive underneath

Autonomi has one underlying storage primitive: the chunk.

When you upload data or a file:

- self-encryption turns the content into encrypted chunks
- a `DataMap` records how those chunks fit back together
- public and private workflows mainly differ in where that `DataMap` lives

A `DataMap` is not a separate storage primitive. It is retrieval metadata.

## Content-addressed and immutable

When you upload data to Autonomi, the stored result is content-addressed rather than mutable. In practice, that means:

- changing the content produces a different address
- public data and public file uploads can be retrieved from their content-derived addresses
- private workflows still store content-addressed chunks, but you keep the retrieval metadata locally in a `DataMap`

This is why Autonomi is immutable rather than update-in-place.

## Developer-facing operations at a glance

| Operation or material | Under the hood | Typical use |
|------|------|------|
| Public data | Self-encrypted chunks plus a published `DataMap` address | Shared payloads, app data, public content |
| Private data | Self-encrypted chunks plus a client-held `DataMap` | Content whose `DataMap` you keep client-side |
| Raw chunk | Caller-supplied bytes stored directly without automatic self-encryption | Small payloads and low-level tooling |
| File | Self-encrypted chunks plus a file-oriented `DataMap` flow | Uploading and downloading files from disk |
| `DataMap` | Retrieval metadata for chunked content | Private retrieval, public file addressing, later downloads |

## Public and private data

Public and private data are not two different low-level storage systems.

- In public workflows, the `DataMap` is stored or published so the content can be retrieved by address.
- In private workflows, the `DataMap` stays with you and is not stored publicly.

In the [`antd`](../sdk/use-antd.md) REST API, you can see this difference clearly:

- `POST /v1/data/public` returns a public address
- `POST /v1/data` returns a serialized `DataMap` (the `DataMap` is not stored on the Autonomi Network)

In both cases, the underlying content is still stored as chunks.

## Chunks

Chunks are the low-level storage unit. The [CLI](../cli/use-the-cli.md) exposes them through `ant chunk put` and `ant chunk get`, and `antd` exposes them through `/v1/chunks`. These raw chunk operations store the supplied bytes directly; they do not run self-encryption first.

Use chunk operations when you are building low-level tooling or want explicit control over single-chunk payloads. For most application data, use public/private data or file uploads instead.

## Files

File uploads wrap the same chunk-and-DataMap model for content that already lives on disk.

`antd` and the CLI both provide private and public file workflows:

- `antd` exposes private and public file upload/download endpoints
- `ant` supports both public file uploads and private uploads that keep a local `.datamap` file

Use `antd` or CLI file operations when you want the tooling to handle file-system input and output directly instead of working with raw byte arrays.

## DataMap

A `DataMap` is the retrieval metadata that ties uploaded content back to its encrypted chunks.

In the [SDK](../sdk/install.md) and CLI interfaces, a `DataMap` shows up in two main ways:

- private uploads return it directly to you
- public uploads store it on the Autonomi Network and return an address that can be fetched later

This is one of the main differences between public and private workflows.

## Practical example

These interfaces map onto the operations as follows:

- use `POST /v1/data/public` when you want the `DataMap` stored on the Autonomi Network and returned as an address
- use `POST /v1/data` when you want the `DataMap` returned to you directly
- use `POST /v1/files/public` or `ant file upload ... --public` when you want a file to be publicly retrievable
- use `POST /v1/files` or `ant file upload ...` without `--public` when you want to keep the `DataMap` locally
- use `POST /v1/chunks` or `ant chunk put ...` when you want to store caller-supplied bytes as one raw chunk

## Related pages

- [Store and Retrieve Data with the SDKs](../sdk/how-to-guides/store-and-retrieve-data.md)
- [Payment Model](payment-model.md)
- [Keys, Addresses, and DataMaps](keys-addresses-and-datamaps.md)
- [Self-encryption](self-encryption.md)
