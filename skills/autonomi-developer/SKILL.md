---
name: autonomi-developer
description: |
  Build applications, automations, and AI workflows on the Autonomi Network.
  Use this skill when the user wants to store or retrieve data, add Autonomi
  storage to an application, build read-only or upload-enabled features, use
  the `antd` daemon and SDK bindings, work from the `ant` CLI, build directly
  in Rust with `ant-core`, or expose Autonomi through an MCP-compatible client.
  Do not use for Autonomi 1.0, the MaidSafe-era network, `ant-quic`, or
  general EVM work that is not part of building on Autonomi.
version: 0.1.0-draft
license: MIT
repository: https://github.com/WithAutonomi/autonomi-developer-docs
homepage: https://docs.autonomi.com/developers
author: Autonomi Developer Documentation
keywords:
  - autonomi
  - ant-sdk
  - antd
  - ant-client
  - ant-core
  - ant
  - mcp
  - devnet
  - datamap
  - self-encryption
  - uploads
  - read-only

# Verification block. Re-verify before changing stable claims or examples.
verified_date: 2026-04-22
verification_mode: current-merged-truth
verified_commits:
  ant-sdk: 2ed9b14bda42fbdc604a173cc1af27be0964908f
  ant-client: b0c501a163c1a95bdbfc703892b88a8a91f7e482
  ant-node: 5a5d7d4fed766cd56d0f97f337fcd5ff049bea6a
  self_encryption: 5f9d1646231da7ca2ce60e84d010acfb6d9c29d0
  evmlib: 82f2fccff243b48de0e04ceb71ccb2aa17d810af

version_manifest_url: https://raw.githubusercontent.com/WithAutonomi/autonomi-developer-docs/main/skills/autonomi-developer/version.json
canonical_docs_url: https://docs.autonomi.com/developers
---

# Autonomi Developer

This skill makes you effective at building on the Autonomi Network without making the user read the full docs set first. Treat it as an operational guide: pick the correct Autonomi path, fetch one live reference when exact interface details matter, and do not invent Autonomi-specific APIs.

## Scope

Use this skill when the task is about:

- storing or retrieving data on Autonomi
- adding Autonomi storage to an application
- building read-only or upload-enabled features
- using `antd` and the SDK bindings
- using the `ant` CLI
- building directly in Rust with `ant-core`
- exposing Autonomi through an MCP-compatible client
- testing with a local devnet before public-network deployment

Do not use this skill for:

- Autonomi 1.0 or anything under the MaidSafe org unless the user explicitly wants historical context
- `ant-quic` or older transport docs
- general EVM, Arbitrum, IPFS, or Filecoin work unrelated to building on Autonomi

## Operating Rules

1. Check whether a newer verified version of this skill exists:

```bash
curl -fsSL https://raw.githubusercontent.com/WithAutonomi/autonomi-developer-docs/main/skills/autonomi-developer/version.json
```

If the published `version` is newer, tell the user this copy may be stale and offer to reload it. If the fetch fails, continue silently.

2. Pick one path before you start coding: SDK, CLI, Direct Rust, or MCP.

3. Fetch one live reference page once per task when you need volatile details such as install steps, exact REST or gRPC schemas, binding-specific helpers, CLI flags, or MCP tool names.

4. Do not invent Autonomi-specific details. If this skill does not name a route, flag, method, env var, or tool and you have not fetched the live reference, do not guess it.

5. For anything that uploads data, start on a local devnet first unless the user explicitly wants public-network work.

6. Ask before installing software, configuring wallets, or touching real ANT on a public network.

## Path Selector

| Path | Choose it when the user wants to... | Fetch first when details matter |
|------|-------------------------------------|---------------------------------|
| SDK | Build an application in Python, JavaScript, TypeScript, Rust, Go, Java, C#, Kotlin, Swift, Ruby, PHP, C++, Dart, or Zig through a local daemon | language page plus REST or gRPC reference |
| CLI | Work from the shell, script uploads or downloads, inspect wallets, or do operational workflows | CLI command reference |
| Direct Rust | Build daemon-free Rust with direct network control or local devnet helpers | Rust getting-started page plus library reference |
| MCP | Let an MCP-compatible client talk to Autonomi through `antd` | MCP setup page plus MCP server reference |

If the user has not chosen a path, recommend SDK first. It is the best fit for most application work.

## Fast Lookup Discipline

Use this workflow to stay fast without guessing:

1. Decide whether the feature is read-only or upload-enabled.
2. Pick a path.
3. Check the local prerequisite for that path.
4. Fetch one live page for the path-specific details.
5. Reuse that page for the rest of the task instead of re-fetching several pages.

For SDK and MCP work, the fastest first check is usually:

```bash
curl http://localhost:8082/health
```

Expected shape:

```json
{
  "status": "ok",
  "network": "default"
}
```

If the user is on a non-default host or port, ask for the base URL instead of assuming `localhost:8082`.

## Path Playbooks

### SDK

Choose SDK when the user wants normal application development in a supported language. This path goes through `antd`.

Current daemon defaults:

- REST: `http://localhost:8082`
- gRPC: `localhost:50051`
- non-default ports can be discovered through the `daemon.port` file written by `antd`

Current shared daemon surfaces you can rely on at this commit:

- `GET /health`
- `POST /v1/data/public`
- `GET /v1/data/public/{addr}`
- `POST /v1/data/private`
- `GET /v1/data/private`
- `POST /v1/data/cost`
- `GET /v1/wallet/address`
- `GET /v1/wallet/balance`
- `POST /v1/wallet/approve`
- `POST /v1/data/prepare`
- `POST /v1/upload/prepare`
- `POST /v1/upload/finalize`

Golden public-data round trip:

```bash
DATA_B64=$(printf 'Hello, Autonomi!' | base64)

curl -X POST http://localhost:8082/v1/data/public \
  -H "Content-Type: application/json" \
  -d "{\"data\":\"$DATA_B64\"}"

curl http://localhost:8082/v1/data/public/<address>
```

Keep these rules straight:

- REST binary payloads are base64 inside JSON.
- `POST /v1/data/public` returns a public address.
- `POST /v1/data/private` returns a serialized `DataMap`.
- `GET /v1/data/private` needs the `data_map` query parameter.
- read-only daemon work does not require `AUTONOMI_WALLET_KEY`

Current documented binding entry points:

- Python: `AntdClient()` or `AsyncAntdClient()`
- JavaScript and TypeScript: `createClient()`
- Go: `NewClient(...)`
- Rust SDK: `Client::new(...)`

Before writing SDK code beyond health checks and the public-data round trip, fetch the binding page for the user's language.

### CLI

Choose CLI when the user wants direct shell workflows, scripts, CI automation, wallet inspection, or quick operational tasks without `antd` in the data path.

Current CLI rules that matter in practice:

- data commands do not require the daemon
- root flags such as `--bootstrap`, `--devnet-manifest`, `--allow-loopback`, and `--evm-network` come before the subcommand
- the main top-level groups are `file`, `chunk`, `wallet`, `node`, and `update`
- uploads and wallet commands require `SECRET_KEY`

Golden public-file flow on a local devnet:

```bash
SECRET_KEY=0x... ant \
  --devnet-manifest /tmp/devnet.json \
  --allow-loopback \
  --evm-network local \
  file upload photo.jpg --public

ant \
  --devnet-manifest /tmp/devnet.json \
  --allow-loopback \
  --evm-network local \
  file download <address> -o photo_copy.jpg
```

Keep these rules straight:

- private file uploads save a local `.datamap` file instead of returning a public address
- private file downloads use `--datamap <PATH>`
- public downloads do not need a wallet

For anything beyond these patterns, fetch the CLI command reference first.

### Direct Rust

Choose Direct Rust when the user wants daemon-free Rust, native Rust types, direct client control, or built-in local devnet helpers.

Current `ant-core` surfaces you can name safely:

- `Client::connect(...)`
- `with_wallet(...)`
- `data_upload(...)`
- `data_download(...)`
- `file_upload(...)`
- `file_download(...)`
- `data_map_store(...)`
- `data_map_fetch(...)`
- `LocalDevnet::start_minimal()`
- `create_funded_client()`
- `write_manifest(...)`

Use Direct Rust when the user needs those native surfaces. Do not infer full method signatures or argument shapes from memory; fetch the Rust getting-started page and the library reference before writing the code.

### MCP

Choose MCP when an MCP-compatible client should use Autonomi through structured tools instead of raw HTTP.

Current MCP setup facts:

- server command: `antd-mcp`
- install pattern:

```bash
pip install "antd[rest]"
pip install -e antd-mcp/
```

- stdio mode: `antd-mcp`
- SSE mode: `antd-mcp --sse`
- daemon discovery order:
  - `ANTD_BASE_URL`
  - `daemon.port`
  - `http://127.0.0.1:8082`

Do not memorize MCP tool names or schemas in this skill. Fetch the MCP server reference when the task is MCP-specific.

## Concepts That Affect Implementation

### Public vs private data

Autonomi has one underlying storage primitive: encrypted chunks. Public and private data differ mainly in where the `DataMap` lives.

- public data returns an address that can be shared and fetched later
- private data returns a `DataMap` that the caller must keep
- if private retrieval is failing, check for a missing or wrong `DataMap` before anything else

### Wallet keys vs retrieval material

These are different things:

- `AUTONOMI_WALLET_KEY` pays for uploads through `antd`
- `SECRET_KEY` pays for uploads and wallet commands through `ant`
- an attached `Wallet` pays for uploads through `ant-core`
- a public address retrieves public data
- a `DataMap` retrieves private data

Do not collapse those concepts into one key-handling model.

### Read-only vs upload-enabled features

This is the first architectural split to make.

If the feature is read-only:

- no ANT is required
- no gas is required
- no wallet is required
- the daemon can run without `AUTONOMI_WALLET_KEY`

If the feature uploads data:

- local devnet gives you funded local test wallets
- public networks need ANT plus gas on the selected EVM network
- wallet setup becomes part of the feature, not an afterthought

### Local devnet first

For upload-enabled work, the shortest safe loop is:

```bash
ant dev start --ant-node-dir ../ant-node
ant dev status
ant dev wallet show
curl http://localhost:8082/health
```

The local environment gives you a running devnet, `antd --network local`, and a funded local wallet. Stop it with:

```bash
ant dev stop
```

### Payment modes

Current upload payment modes are:

- `auto`
- `merkle`
- `single`

Use `auto` unless the user has a reason to force the behavior. If the user wants explicit cost estimation before an upload, use the current cost endpoints or the path-specific reference page.

## Common Failures

### Daemon health check fails

The daemon is not running, it is on a different port, or the task should be using CLI or Direct Rust instead of SDK or MCP.

### `503` on daemon write routes

`antd` is reachable but wallet configuration is missing. Check `AUTONOMI_WALLET_KEY` or switch to an external-signer flow.

### `insufficient funds`

Distinguish between missing ANT and missing gas. Do not tell the user to fund the wallet without identifying which balance is missing.

### Private retrieval fails

Check the `DataMap` first. Private content still needs the retrieval metadata even after the content has already been paid for.

### CLI command shape looks wrong

Check whether the root flags were placed after the subcommand. In `ant`, global flags belong before `file`, `chunk`, `wallet`, `node`, or `update`.

### Tests fail against the daemon surface

Check whether the test expects raw bytes over REST. Current REST binary payloads are JSON with base64 in the `data` field.

## Hard Constraints

- Do not reference Autonomi 1.0 as if it were current.
- Do not reference `ant-quic`; Autonomi 2.0 transport docs use `saorsa-transport`.
- Do not guess endpoints, flags, method names, or contract details.
- Do not put real wallet keys into committed code.
- Do not walk a user into public-network uploads without checking that they understand the money and irreversibility involved.
- Stay on one Autonomi path unless the user explicitly asks for a comparison.

## Live References

Use these pages as the first lookup for current details:

| Need | Live page |
|------|-----------|
| Overview | `https://docs.autonomi.com/developers` |
| SDK entry point | `https://docs.autonomi.com/developers/sdk/install` |
| SDK first upload | `https://docs.autonomi.com/developers/sdk/store-data-on-the-network` |
| SDK first retrieval | `https://docs.autonomi.com/developers/sdk/retrieve-data-from-the-network` |
| SDK store and retrieve guide | `https://docs.autonomi.com/developers/sdk/how-to-guides/store-and-retrieve-data` |
| SDK daemon as service | `https://docs.autonomi.com/developers/sdk/how-to-guides/use-the-daemon-as-a-local-service` |
| REST API | `https://docs.autonomi.com/developers/sdk/reference/rest-api` |
| gRPC services | `https://docs.autonomi.com/developers/sdk/reference/grpc-services` |
| Daemon command reference | `https://docs.autonomi.com/developers/sdk/reference/daemon-command-reference` |
| Language bindings overview | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/overview` |
| Python SDK | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/python` |
| JavaScript SDK | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/javascript` |
| TypeScript SDK | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/typescript` |
| Rust SDK | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/rust` |
| Go SDK | `https://docs.autonomi.com/developers/sdk/reference/language-bindings/go` |
| CLI quickstart | `https://docs.autonomi.com/developers/cli/use-the-cli` |
| CLI command reference | `https://docs.autonomi.com/developers/cli/command-reference` |
| Direct Rust quickstart | `https://docs.autonomi.com/developers/rust/build-directly-in-rust` |
| Rust library reference | `https://docs.autonomi.com/developers/rust/library-reference` |
| MCP setup | `https://docs.autonomi.com/developers/mcp/use-the-autonomi-mcp-server` |
| MCP reference | `https://docs.autonomi.com/developers/mcp/mcp-server-reference` |
| Local devnet | `https://docs.autonomi.com/developers/guides/set-up-a-local-network` |
| Prepare a wallet | `https://docs.autonomi.com/developers/guides/prepare-a-wallet-for-uploads` |
| Payments and cost estimation | `https://docs.autonomi.com/developers/guides/estimate-costs-and-handle-upload-payments` |
| Read-only features | `https://docs.autonomi.com/developers/guides/build-read-only-features` |
| Testing | `https://docs.autonomi.com/developers/guides/test-your-application` |
| Deploy to mainnet | `https://docs.autonomi.com/developers/guides/deploy-to-mainnet` |
| Data types | `https://docs.autonomi.com/developers/core-concepts/data-types` |
| Keys, addresses, and DataMaps | `https://docs.autonomi.com/developers/core-concepts/keys-addresses-and-datamaps` |
| Self-encryption | `https://docs.autonomi.com/developers/core-concepts/self-encryption` |
| Payment model | `https://docs.autonomi.com/developers/core-concepts/payment-model` |
| System overview | `https://docs.autonomi.com/developers/architecture/system-overview` |
| Glossary | `https://docs.autonomi.com/developers/reference/glossary` |
| Source repositories | `https://docs.autonomi.com/developers/reference/source-repositories` |

## If Something Conflicts

Trust the live docs over stale memory. If the live docs and this skill disagree, tell the user the skill may be stale, use the live docs for the task in front of you, and update the skill package in this repo afterward.
