# Released antd v0.11.2 Audit

- Date: 2026-08-11
- Documentation baseline: [`af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`](https://github.com/WithAutonomi/autonomi-developer-docs/commit/af6d0e9da96dd9b7d31105accbeb9b6a181aaf37)
- Emergency branch baseline: `2e11cdc908a04d31bc35a6d998211cdb7949ce93` on `docs/released-antd-safety`, before this audit commit; this local-only historical identifier is unavailable from the remote
- Original audit commit: `16bdb4de6dc6a109b70238b31956685db839318d`; this local-only historical identifier is unavailable from the remote, and the committed branch-local copy of this audit is the reproducible review artifact
- Audit mode: attended knowledge-work checkpoint; no implementation or PR action is authorized

## Snapshot status

This is the dated motivating snapshot recorded on 2026-08-11. Its technical findings, exact technical source refs, source links, and evidence limits remain inspectable evidence for Proposed ADR-0016. Its source-of-truth analysis, target-manifest application, recommended remediation, and statements about whether an ADR existed record the policy position before ADR-0016 was proposed. They are preserved as historical context, not as current policy or authorization.

## Executive verdict

The result is mixed. Stable `antd` v0.11.2 is the release the affected developer documentation must describe. It restores source-correct ordinary `auto`, `merkle`, and `single` writes and estimates, and its released `ant-core` dependency has strong unit and paid Merkle end-to-end (E2E) coverage. The raw daemon REST response and gRPC contract represent external wave-batch and Merkle preparation correctly, but gRPC has an all-already-stored finalization defect described below.

The release does not establish a complete daemon-and-binding payment matrix. Six binding defects remain in Python REST, Elixir REST, Lua, Ruby REST, PHP, and Zig. MCP forces the defective Python REST path. Separately, the daemon's gRPC finalize handler rejects the valid all-already-stored wave-batch case, and every typed gRPC binding inherits that server behavior. The exact release evidence contains no wallet-funded daemon REST, gRPC, MCP, or language-binding matrix and no external-signer boundary matrix at 63, 64, 256, and 257 chunks.

The 45-file emergency branch fixes durable installation and documentation defects, but its v0.11.1 premise and blanket forced-`single` guidance are superseded. It is not publishable as-is. Remediation should start from fresh `origin/main` and selectively port durable fixes.

## Source-of-truth split

The repository's two truth needs must remain separate:

1. **Installation, downloads, package identities, and version claims:** use the latest stable release that a user can obtain. On the audit date that is `antd` v0.11.2, including its downloadable binaries and container images.
2. **Technical behavior tied to released `antd`:** use the v0.11.2 source commit and the dependency chain resolved by that release. This is the correct basis for daemon payment behavior, request and response contracts, and released bindings.
3. **Technical behavior not pinned to released `antd`:** use moving default-branch heads under `current-merged-truth`, selected per page and component. Mixed pages may therefore need separate release and moving-head verification blocks.

The release split prevents moving source from making unavailable artifacts look installable, while avoiding an old release pin for unrelated architecture and network claims.

## Stable release and dependency chain

### ant-sdk v0.11.2

- Release: [v0.11.2](https://github.com/WithAutonomi/ant-sdk/releases/tag/v0.11.2), published `2026-08-10T08:35:03Z`.
- Annotated tag object: [`108d64115f5ec5b85a50ec1e24c8c3123e11c502`](https://api.github.com/repos/WithAutonomi/ant-sdk/git/tags/108d64115f5ec5b85a50ec1e24c8c3123e11c502).
- Peeled source commit: [`3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15`](https://github.com/WithAutonomi/ant-sdk/commit/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15).
- `ant-sdk/main` also resolved to `3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15` during this audit.
- The release has 11 downloadable GitHub assets: `antd-darwin-arm64`, `antd-linux-amd64`, `antd-linux-arm64`, `antd-linux-install.sh`, `antd-linux-x64.deb`, `antd-linux-x64.rpm`, `antd-macos.pkg`, `antd-windows-amd64.exe`, `antd-windows-x64-setup.msi`, `antd-windows-x64-setup.wixpdb`, and `SHA256SUMS`.
- The release workflow also publishes `withautonomi/antd:v0.11.2` on [Docker Hub](https://hub.docker.com/r/withautonomi/antd) and `ghcr.io/withautonomi/antd:v0.11.2` on [GitHub Container Registry](https://github.com/orgs/WithAutonomi/packages/container/package/antd). Container images are additional distribution surfaces, not part of the 11-asset GitHub count.

### Released dependencies

| Component | Released ref | Exact source | Evidence |
|---|---|---|---|
| `ant-core` in ant-client | `ant-cli-v0.3.2` | [`3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b`](https://github.com/WithAutonomi/ant-client/commit/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b) | [`antd/Cargo.toml`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/Cargo.toml#L7-L10) and [`antd/Cargo.lock`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/Cargo.lock#L805-L810) |
| ant-protocol | `v2.3.1` | [`2566ed454ee82d5bd2588071077911b30284002b`](https://github.com/WithAutonomi/ant-protocol/commit/2566ed454ee82d5bd2588071077911b30284002b) | v2.3.1 release source used by the locked `ant-protocol` 2.3.1 crate |
| evmlib | annotated `v0.9.0` | peeled [`28fc354b3723850cfa7afea10d07a13a0617a035`](https://github.com/WithAutonomi/evmlib/commit/28fc354b3723850cfa7afea10d07a13a0617a035) | [`antd/Cargo.toml`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/Cargo.toml#L8-L11) and locked evmlib 0.9.0 |

The evmlib tag is annotated; its tag object is distinct from the peeled source commit. The ant-client and ant-protocol refs resolve directly to the commits shown.

## CI and test evidence

### ant-sdk

- [Release run 31369627409](https://github.com/WithAutonomi/ant-sdk/actions/runs/31369627409) is green at the v0.11.2 source SHA. All nine jobs pass: `Build (aarch64-unknown-linux-gnu)`, `Build (x86_64-unknown-linux-gnu)`, `Build (x86_64-pc-windows-msvc)`, `Build (aarch64-apple-darwin)`, `Package Windows (.msi, x64)`, `Docker (multi-arch)`, `Package macOS (.pkg, arm64)`, `Package Linux (deb/rpm/script)`, and `Create Release`.
- [General CI run 31197781579](https://github.com/WithAutonomi/ant-sdk/actions/runs/31197781579) is green at the exact source SHA, but it contains only `Check (antd)`, `Check (antd-rust)`, and `Security audit`. The workflow runs format, clippy, docs, and Rust tests for `antd` and `antd-rust`; it does not run the other bindings or MCP.
- FFI has a separate workflow and surface. It is not evidence that the daemon bindings in the table below were tested.

### ant-client

- [CI run 30492539700](https://github.com/WithAutonomi/ant-client/actions/runs/30492539700) and [CI run 30492541939](https://github.com/WithAutonomi/ant-client/actions/runs/30492541939) both pass at exact release SHA `3e6bdd28...`. Their jobs include unit and E2E suites on Linux and macOS, including `Merkle E2E` on both operating systems.
- The separate [pr-checks run 30492541163](https://github.com/WithAutonomi/ant-client/actions/runs/30492541163) failed only `linear-link` and `pr-template`; `self-test` passed. This is Linear/template governance failure, not a code-test failure.

### Exact core coverage

The released core evidence establishes the following:

- [`ant-core/tests/merkle_unit.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/tests/merkle_unit.rs#L17-L120) covers `auto` at 63/64, forced Merkle's one-address rejection and two-address minimum, forced `single`, and partition counts including 65, 256, and 257.
- The inline Merkle tests additionally pin singleton-tail rebalancing and the pre-spend rejection for an external batch above 256 addresses: [`merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/merkle.rs#L2205-L2380).
- [`ant-core/tests/e2e_merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/tests/e2e_merkle.rs#L54-L149) performs forced-Merkle file and in-memory data upload/download round trips.
- The same E2E file pays real local EVM settlements at the 65- and 257-address boundaries and checks complete proof sets and padded-leaf cost scaling: [`e2e_merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/tests/e2e_merkle.rs#L284-L406).

This coverage does **not** establish either of these matrices:

- a wallet-funded `antd` REST, gRPC, MCP, and language-binding write matrix; or
- an external-signer 63/64/256/257 prepare, on-chain sign/pay, and finalize matrix.

## Released behavior matrix

### Ordinary daemon-funded writes and estimates

The raw daemon accepts `auto`, `merkle`, and `single`, defaults an absent mode to `auto`, and forwards that mode into ordinary data/file writes and estimates. Relevant sources are [`types.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/types.rs#L382-L400), [`rest/data.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/rest/data.rs#L16-L50), and [`rest/files.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/rest/files.rs#L11-L95). Cost handlers use the same mode parser.

The released core defaults to `auto`, uses Merkle at 64 or more chunks, allows forced Merkle from two chunks, and keeps forced `single` on the per-chunk path: [`merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/merkle.rs#L165-L176) and [`merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/merkle.rs#L470-L478).

Ordinary MCP writes use the Python REST client's normal data/file operations and inherit these source-correct modes. They no longer require forced `single`. This statement does not extend to MCP's external-signer tools, which are defective as described below.

### External signing

- **Files:** after the already-stored preflight, fewer than 64 payable chunks use wave-batch; 64 through 256 use one Merkle tree; more than 256 are rejected before candidate collection or spend. Sources: [`file.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/file.rs#L1534-L1635) and [`merkle.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/merkle.rs#L452-L468).
- **In-memory data:** external signing is wave-batch-only. Ordinary daemon-funded in-memory data can use Merkle, but [`data_prepare_upload_with_visibility`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/data.rs#L225-L369) explicitly constructs `ExternalPaymentInfo::WaveBatch`.
- **Raw REST:** the daemon returns `payment_type: "wave_batch"` with payments or `payment_type: "merkle"` with depth, pool commitments, and timestamp. Finalize requires the matching `tx_hashes` or `winner_pool_hash`: [`upload.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/rest/upload.rs#L24-L114) and [`upload.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/rest/upload.rs#L194-L356).
- **Raw gRPC:** the proto uses the same `"wave_batch"`/`"merkle"` discriminator and typed fields: [`upload.proto`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/proto/antd/v1/upload.proto#L9-L145). However, when all prepared chunks are already stored, core returns a valid empty wave-batch intent and accepts no-payment finalization, while the gRPC handler removes the pending upload and then rejects the empty `tx_hashes` map. The request fails, the `upload_id` is consumed, and no DataMap result is returned. REST accepts a present empty `tx_hashes` object. Sources: [`file.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/file.rs#L1554-L1562), [`batch.rs`](https://github.com/WithAutonomi/ant-client/blob/3e6bdd28f5af3c7601ca919640bf8dfccf4f8d6b/ant-core/src/data/client/batch.rs#L337-L342), [`grpc/service.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/grpc/service.rs#L1078-L1107), and [`rest/upload.rs`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd/src/rest/upload.rs#L223-L267). This is tracked upstream in [`ant-sdk` issue #233](https://github.com/WithAutonomi/ant-sdk/issues/233).

The raw prepare contracts and ordinary paths are source-correct, but the gRPC finalize edge case above is defective. No funded daemon E2E exercises the complete contracts.

## Six released binding defects

All six defects are present at v0.11.2 source commit `3264b514...`.

1. **Python REST:** `_parse_prepare_result` checks for `payment_type == "merkle_batch"`, while the daemon emits `"merkle"`. It therefore keeps `pool_commitments` empty for a real Merkle response. The gRPC mapper correctly checks `"merkle"`. Sources: [`antd-py/src/antd/_rest.py`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-py/src/antd/_rest.py#L215-L251) and [`antd-py/src/antd/_grpc.py`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-py/src/antd/_grpc.py#L113-L160).
2. **Elixir REST:** `parse_prepare_response` has the same wrong `"merkle_batch"` branch. The gRPC mapper correctly checks `"merkle"`. Sources: [`antd-elixir/lib/antd/client.ex`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-elixir/lib/antd/client.ex#L764-L812) and [`antd-elixir/lib/antd/grpc_client.ex`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-elixir/lib/antd/grpc_client.ex#L807-L854).
3. **Lua:** `build_prepare_result` checks `"merkle_batch"`, so a real `"merkle"` response loses its pool commitments. Source: [`antd-lua/src/antd/client.lua`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-lua/src/antd/client.lua#L250-L304).
4. **Ruby REST:** `parse_prepare_response` checks `"merkle_batch"`; Ruby gRPC correctly checks `"merkle"`. Sources: [`antd-ruby/lib/antd/client.rb`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-ruby/lib/antd/client.rb#L429-L470) and [`antd-ruby/lib/antd/grpc_client.rb`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-ruby/lib/antd/grpc_client.rb#L489-L524).
5. **PHP:** `PrepareUploadResult` is intentionally wave-only, has no typed Merkle fields, and the client exposes only wave `finalizeUpload`; there is no typed Merkle finalize operation. Sources: [`antd-php/src/Models/PrepareUploadResult.php`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-php/src/Models/PrepareUploadResult.php#L6-L39) and [`antd-php/src/AntdClient.php`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-php/src/AntdClient.php#L764-L776), [`AntdClient.php`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-php/src/AntdClient.php#L909-L936).
6. **Zig:** file/data prepare returns raw JSON rather than a typed external-payment model. `finalizeUpload` posts the caller-supplied JSON unchanged, discards its `upload_id` argument, and exposes no typed Merkle finalize operation. Source: [`antd-zig/src/antd.zig`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-zig/src/antd.zig#L430-L457).

### Why tests mask the defects

- Python, Elixir, Lua, and Ruby REST tests repeat the incorrect `"merkle_batch"` fixture and assert that shape, rather than feeding the daemon's real `"merkle"` discriminator. Anchors: [Python](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-py/tests/test_rest_client.py#L197-L224), [Elixir](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-elixir/test/antd/client_test.exs#L714-L765), [Lua](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-lua/spec/client_spec.lua#L453-L513), and [Ruby](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-ruby/test/test_client.rb#L363-L426).
- PHP tests cover wave preparation/finalize but no Merkle model or finalize: [`AntdClientTest.php`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-php/tests/AntdClientTest.php#L501-L599).
- Zig tests cover request helpers and chunk finalize but not the broken full-upload body: [`tests.zig`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-zig/src/tests.zig#L317-L451).
- MCP constructs `AsyncAntdClient(transport="rest")`: [`server.py`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-mcp/src/antd_mcp/server.py#L13-L30). For a real `payment_type: "merkle"`, Python REST preserves the discriminator but produces an empty commitment list, which MCP serializes as `pool_commitments: []`: [`server.py`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-mcp/src/antd_mcp/server.py#L545-L570). MCP tests mock the client above the parser and therefore never exercise this failure: [`test_server.py`](https://github.com/WithAutonomi/ant-sdk/blob/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15/antd-mcp/tests/test_server.py#L138-L193).

## All-binding snapshot

`A/M/S` means ordinary `auto`, `merkle`, and `single` data/file writes and estimates. “Source-correct” does not mean funded runtime-verified. The exact-release column records evidence actually run at the release SHA, not tests that exist only in a source tree.

| Surface | Ordinary modes | External-signer source result | Exact-release test evidence | Public installability at audit date |
|---|---|---|---|---|
| C++ | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored gRPC finalize defect | None in exact-SHA general CI | Source-only; no public package |
| C# | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored gRPC finalize defect | None in exact-SHA general CI | Source-only; no NuGet package |
| Dart | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored gRPC finalize defect | None in exact-SHA general CI | Source package name `antd` collides on pub.dev |
| Elixir | A/M/S source-correct | REST defective; gRPC mapping inherits all-already-stored finalize defect | None; REST fixture repeats defect | Source-only; no Hex package |
| Go | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored finalize defect | No Go test job at exact release SHA | **Public:** Go proxy `v0.11.2` resolves to `antd-go/v0.11.2` at `3264b514...` |
| Java | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored finalize defect | None in exact-SHA general CI | Source-only; no intended Maven artifact resolved |
| JavaScript / TypeScript | A/M/S source-correct | REST wave/Merkle source-correct | None in exact-SHA general CI | Source package name `antd` collides with Ant Design on npm |
| Kotlin | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored finalize defect | None in exact-SHA general CI | Source-only; no intended Maven artifact resolved |
| Lua | A/M/S source-correct | REST defective discriminator | None; fixture repeats defect | Source-only; no intended LuaRocks package resolved |
| PHP | A/M/S source-correct | Wave-only model/finalize; no typed Merkle | None; wave mocks only | Source-only; no intended Packagist package resolved |
| Python | A/M/S source-correct | REST parser defective; gRPC mapping inherits all-already-stored finalize defect | None; REST fixture repeats defect | Exact-source install route identified from source metadata; no clean-install or runtime verification; no PyPI release |
| Ruby | A/M/S source-correct | REST parser defective; gRPC mapping inherits all-already-stored finalize defect | None; REST fixture repeats defect | Source-only; no intended RubyGems package resolved |
| Rust | A/M/S source-correct | REST source-correct; gRPC mapping inherits all-already-stored finalize defect | `Check (antd-rust)` runs tests | Exact-source install route identified from source metadata; no clean-install or runtime verification; no crates.io package |
| Swift | A/M/S source-correct | Typed gRPC wave/Merkle mapping; inherits all-already-stored finalize defect | None in exact-SHA general CI | Source-only; no public package release |
| Zig | A/M/S source-correct | Raw JSON; full finalize drops `upload_id`; no typed Merkle | None; no full-upload finalize test | Source-only; no public package |
| MCP | Direct A/M/S writes source-correct | Defective because it forces Python REST | None; mocks sit above parser | Source-only Python project; no public MCP package |

The Go proxy identity is `github.com/WithAutonomi/ant-sdk/antd-go@v0.11.2`. Source metadata identifies exact-Git-source install routes for Python and Rust, but this audit did not clean-install or runtime-verify them, and they are not PyPI or crates.io releases. npm's `antd` is Ant Design, and pub.dev's `antd` is also unrelated. The FFI/mobile surface is separate from these daemon bindings and should not be used to infer binding package support.

## Moving-head snapshot and drift

These moving heads were resolved on 2026-08-11 for claims that remain under `current-merged-truth`:

| Repository | Default branch | Audit head |
|---|---|---|
| ant-sdk | `main` | [`3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15`](https://github.com/WithAutonomi/ant-sdk/commit/3264b514dac9ed361a7426d6d6d5ae6a8e7b6b15) |
| ant-client | `main` | [`d4b6fbc1ec5dd957734b4de3b2f463233a7dfdb2`](https://github.com/WithAutonomi/ant-client/commit/d4b6fbc1ec5dd957734b4de3b2f463233a7dfdb2) |
| ant-node | `main` | [`187cbb1909e1492a67fe9dea70d3ff163f8e889d`](https://github.com/WithAutonomi/ant-node/commit/187cbb1909e1492a67fe9dea70d3ff163f8e889d) |
| saorsa-core | `main` | [`5bdc200aee2a6977e5179b757280730e43251b37`](https://github.com/WithAutonomi/saorsa-core/commit/5bdc200aee2a6977e5179b757280730e43251b37) |
| saorsa-transport | `main` | [`c27773fadff58e91901c319c1a3bfaecec3dcaeb`](https://github.com/WithAutonomi/saorsa-transport/commit/c27773fadff58e91901c319c1a3bfaecec3dcaeb) |
| saorsa-pqc | `main` | [`4fbb31d3d29f710726edd32e12ce7b1f64a2aae1`](https://github.com/saorsa-labs/saorsa-pqc/commit/4fbb31d3d29f710726edd32e12ce7b1f64a2aae1) |
| self_encryption | `master` | [`4021f663612c5b963bef935b277eb65416b7d958`](https://github.com/WithAutonomi/self_encryption/commit/4021f663612c5b963bef935b277eb65416b7d958) |
| evmlib | `main` | [`88e20df634f7c80f16777d38a1598c9b651b41b5`](https://github.com/WithAutonomi/evmlib/commit/88e20df634f7c80f16777d38a1598c9b651b41b5) |
| ant-merkle | `master` | [`176ab0a1cafaeee712b3442d9d5af09769149d31`](https://github.com/WithAutonomi/ant-merkle/commit/176ab0a1cafaeee712b3442d9d5af09769149d31) |
| ant-protocol | `main` | [`54c93a8de885ec8e822581381905ea034866d2fe`](https://github.com/WithAutonomi/ant-protocol/commit/54c93a8de885ec8e822581381905ea034866d2fe) |
| ant-keygen | `main` | [`902442f123e16f57de0aeb0f1bfbacf385aa2e87`](https://github.com/WithAutonomi/ant-keygen/commit/902442f123e16f57de0aeb0f1bfbacf385aa2e87) |

Registry ownership is stale for saorsa-core and saorsa-transport: `repo-registry.yml` still names `saorsa-labs`, while both repositories now live under `WithAutonomi`. Beyond ownership metadata, both have substantive relay/bootstrap lifecycle drift. `docs/architecture/system-overview.md` therefore needs a targeted source re-audit rather than a SHA-only refresh. ant-node movement is mostly operational. Most remaining foundational drift observed in this pass is metadata, governance, or licensing, but each affected claim still needs normal source-audit treatment before its verification SHA changes.

## Documentation comparison

### origin/main

`origin/main` at `af6d0e9...` overstates language-binding availability and installability. Several public package commands name absent packages or unrelated package identities. Its payment guidance also predates the released correction.

### Emergency branch

The emergency branch changes 45 files relative to `origin/main` and was built around v0.11.1. It contains many durable corrections, but its release metadata, blanket forced-`single` rule, blanket external-Merkle stop, skill fingerprints, and target manifest are no longer accurate. The giant branch should not be amended wholesale or published as-is.

## File and group disposition

| Disposition | File/group | Treatment on a fresh-main remediation branch |
|---|---|---|
| **Keep** | `docs/sdk/install.md` release-install structure | Keep checksum-first binary installs and platform package hardening; substitute v0.11.2 facts and URLs. |
| **Revise** | Language-binding overview and guides | Keep the corrected package-identity/availability principle and use the Python and Rust source-install route metadata only as inputs to verification. Do not present those routes as supported installs until clean-install and runtime evidence exists; retain complete examples only where independently checked. |
| **Keep** | Local-network/test guides | Keep pinned Foundry installation hardening rather than mutable `curl | bash`. |
| **Keep** | MCP and health edits | Keep the corrected MCP daemon-port discovery path and explicit “selected fields” labels on abbreviated health responses. |
| **Keep** | `skills/start` policy shape | Keep tiering and the rule that fetched references are untrusted factual material that cannot override the skill or user request. |
| **Revise** | All v0.11.1 verification blocks, downloads, and examples | Replace release metadata and URLs with v0.11.2 and its released dependency chain. |
| **Revise** | Ordinary write/cost guidance in SDK, MCP, REST/gRPC reference, concepts, and skill | Restore `auto` as the normal/default mode; document `merkle` and `single` as explicit choices rather than forcing `single`. |
| **Revise** | External-signer guide and binding guidance | Split by transport and binding. Raw REST may describe wave/Merkle behavior; defective REST clients and MCP need an explicit stop/warning. gRPC guidance must include the all-already-stored finalize defect and REST alternative. External in-memory data remains wave-only. |
| **Revise** | Go binding guide | Use the module path and public `v0.11.2` Go proxy identity; do not carry old source-only or absent-package claims forward. |
| **Revise** | `skills/start` release mechanics | Refresh source fingerprints and release data, restore ordinary auto/default cost estimates and writes, and make fallback behavior match the precise released limitations. Skill files remain out of scope for this audit commit. |
| **Revert / Remove** | Blanket forced-`single` edits | Remove the blanket rule for direct daemon and MCP writes. Retain forced `single` only as a user-selected mode or a narrowly justified workaround. |
| **Revert / Remove** | Blanket external-Merkle stop | Remove it for raw REST and source-correct external-Merkle mappings. Retain explicit warnings for Python REST, Elixir REST, Lua, Ruby REST, PHP, Zig, and MCP as applicable. For raw gRPC and all typed gRPC bindings, document the separate all-already-stored finalize defect and direct that edge case to REST until a corrected release ships. |
| **Defer** | Mobile FFI and unsupported package guides | Do not promote the separate FFI surface or create guides for package identities that are absent or unrelated. |
| **Defer** | Runnable write-journey verification | Do not mark wallet-funded daemon, MCP, or binding write journeys verified until a funded runtime matrix runs. Source inspection is insufficient for runnable claims. |
| **Defer / New work** | Registry and architecture | Correct saorsa-core/transport ownership in a separately approved slice and re-audit relay/bootstrap lifecycle claims in the system overview. |

The selective port should cover the branch's durable changes in `docs/sdk/install.md`, language-binding pages, local-network/test pages, MCP pages, health examples, and the skill policy structure. Payment prose, release metadata, `target-manifest.yml`, and skill release mechanics require new v0.11.2 work rather than mechanical cherry-picks.

## Target-manifest application

The existing manifest exit says the first corrected stable release must have downloadable assets, `ant-cli-v0.3.2` or later, and “the full payment matrix passing.” v0.11.2 meets the first two conditions and has green core Merkle CI, including paid 65/257 boundaries. It does not meet a literal complete daemon/binding/external-signer matrix because that matrix was not run. The phrase “full payment matrix” is underspecified: it does not define interfaces, modes, boundaries, funding, or required bindings.

The old v0.11.1 pins cannot remain in place. v0.11.2 is the latest stable security release, is publicly downloadable, and fixes direct Merkle behavior.

ADR-0003 and the original implementation plan already define `target-manifest` as the mechanism for launch and release hardening. This released-`antd` safety work was designed to apply that mechanism: pin affected user-facing `antd` surfaces to a released dependency set, verify actual behavior, and document defects and safe alternatives. The appropriate bounded action is therefore to repin the affected surface to v0.11.2 and rewrite the manifest's underspecified exit condition around named evidence gaps.

Repin only the bounded released-`antd` safety surface to v0.11.2 and its released dependency chain. Rewrite manifest scope and exit criteria so they name the unresolved external-signer and binding evidence instead of claiming an undefined full matrix.

- Bounded scope: release-critical `antd` pages stay on a stable, inspectable set and the manifest explicitly records evidence gaps. Pages about other components are outside this `antd` correction rather than being implicitly certified by the `antd` release. Under ADR-0003 they retain their existing mode until a separately scoped audit changes it.
- Governance: this is an operational use of Accepted ADR-0003's `target-manifest` mode. ADR-0003 governs the mode and verification schema but does not select a particular release. No new ADR is required for the bounded v0.11.2 application.

Changing the permanent repository-wide default from `current-merged-truth` to released-and-usable truth would be a separate architectural decision requiring a Proposed ADR that supersedes ADR-0003. No such Proposed ADR existed on the audit date. That wider policy question should not block correcting the bounded released-`antd` surface under the mechanism already approved.

## Recommended remediation shape

1. Start a fresh branch from `origin/main`, not from the 45-file emergency branch.
2. Selectively port durable installation, package-identity, prerequisite, complete-example, Foundry, MCP discovery, health-label, binding-availability, and skill-policy fixes.
3. Update all release truth to v0.11.2 and state the interface-specific limitations precisely.
4. Restore ordinary direct writes and estimates to `auto` by default.
5. Restrict external-Merkle warnings to defective transports/bindings, keep source-correct guidance available, and document the gRPC all-already-stored finalize defect with REST as the safe alternative.
6. Require a funded runtime matrix before marking runnable write journeys verified.
7. Handle saorsa registry ownership and system-overview drift in separately approved work.

No PR, push, merge, publish, release, rendered-doc edit, source edit, CI edit, test edit, target-manifest edit, ADR edit, or skill edit is part of this audit slice.

## Reproducible evidence commands

Representative commands used for the audit follow. They require `gh`, `curl`, and public network access; none changes repository state.

The original audit also used a local comparison against `2e11cdc908a04d31bc35a6d998211cdb7949ce93` while that commit was available locally. That comparison is no longer remotely reproducible and is not readiness evidence. This committed audit copy preserves the historical findings.

```bash
gh release view v0.11.2 --repo WithAutonomi/ant-sdk \
  --json tagName,publishedAt,isDraft,isPrerelease,targetCommitish,assets,url
gh api repos/WithAutonomi/ant-sdk/git/ref/tags/v0.11.2
gh api repos/WithAutonomi/ant-sdk/git/tags/108d64115f5ec5b85a50ec1e24c8c3123e11c502

gh run view 31369627409 --repo WithAutonomi/ant-sdk \
  --json headSha,status,conclusion,url,jobs
gh run view 31197781579 --repo WithAutonomi/ant-sdk \
  --json headSha,status,conclusion,url,jobs
gh run view 30492539700 --repo WithAutonomi/ant-client \
  --json headSha,status,conclusion,url,jobs
gh run view 30492541939 --repo WithAutonomi/ant-client \
  --json headSha,status,conclusion,url,jobs
gh run view 30492541163 --repo WithAutonomi/ant-client \
  --json headSha,status,conclusion,url,jobs

gh api repos/WithAutonomi/ant-sdk/commits/main
gh api repos/WithAutonomi/ant-client/git/ref/tags/ant-cli-v0.3.2
gh api repos/WithAutonomi/ant-protocol/git/ref/tags/v2.3.1
gh api repos/WithAutonomi/evmlib/git/ref/tags/v0.9.0

curl --fail --silent --show-error \
  https://proxy.golang.org/github.com/withautonomi/ant-sdk/antd-go/@v/v0.11.2.info
```

Canonical source URLs are linked in each findings section. Moving-head queries used `gh api repos/<owner>/<repo>/commits/<default-branch>` on 2026-08-11.

## Uncertainties and evidence limits

- No broad documentation CI arbiter covers this manual branch; local evidence is weaker and cannot be called docs CI-green.
- No wallet-funded runtime daemon matrix was run for REST, gRPC, MCP, or bindings.
- No external-signer funded boundary matrix was run at 63, 64, 256, and 257.
- Exact-release general CI does not run Python, C++, C#, Dart, Elixir, Go, Java, JavaScript/TypeScript, Kotlin, Lua, PHP, Ruby, Swift, Zig, or MCP tests. Existing source tests do not substitute for exact-release CI, and several mask the defects above.
- Public registries can change after the audit timestamp. Go proxy v0.11.2 was the only intended public binding identity resolved during the audit. Python and Rust exact-source install routes were identified from source metadata but were not clean-install or runtime-verified, and they are not public package releases.
- Moving heads are a dated snapshot, not stable release pins. Technical claims must be re-audited if those SHAs move before remediation.
- The audit did not edit `target-manifest.yml`. At the audit date, the intended bounded next step was to repin its released-`antd` scope to v0.11.2 under ADR-0003, subject to approval of the remediation slice.
