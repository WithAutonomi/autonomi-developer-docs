# Release-following CLI specification

Status: Specification for review; no implementation or baseline promotion is authorized by this file.

Issue: [#103 — adopt released truth in rules and tooling](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103)

## Objective

Detect a stable public `ant` CLI release from GitHub Releases and npm, reconcile both publication channels to one exact source commit, map the result to the existing `ant-cli` documentation set, and prepare a human-reviewed baseline and documentation update. Discovery emits evidence for an audit. It never promotes a release, edits a page, merges, or publishes.

This specification applies [ADR-0016's released-truth decision](../adr/ADR-0016-released-truth-for-public-developer-docs.md#decision) through the existing deterministic scanner, audit loop, GitHub artifact topology, and metadata/prose tracks. It does not introduce a third verification mode, a new update track, or new deduplication semantics.

## Non-goals

- Automatically approving, promoting, merging, or publishing a release.
- Treating a Git tag, a default-branch commit, or one publication channel as sufficient release evidence.
- Following `ant-core` as part of the `ant-cli` release track. The two components may share a repository and commit but retain separate baselines.
- Migrating every existing verification block or normalizing the browser-only manual manifest entries.
- Updating shared pages from a CLI-only audit.
- Changing the hosted routine's schedule, model, credentials, or enabled state.
- Defining an Inventory endpoint or schema.
- Adding `blocked_*` outcomes, release fingerprints, installer fingerprints, or closed-PR suppression.
- Replacing the existing manual-review fingerprint or the one-open-updater-PR collision rule.

## Terms

- **Release observation:** Provider evidence read from GitHub, npm, or an unversioned installer. An observation is not an approved baseline.
- **Candidate:** Complete GitHub and npm observations that agree on stable version and exact source commit and differ from the reviewed baseline. A candidate can enter audit but cannot change the manifest or a page by itself.
- **Release baseline:** A reviewed `release_baselines.entries` record in `target-manifest.yml` that identifies the obtainable release supporting named pages.
- **Promotion:** The reviewed, guard-covered change that adds or advances a release baseline and changes only fully audited page verification blocks and any required prose.
- **Release context:** The publication channel represented by one component baseline. Version 1 defines only `stable`.
- **Mapped page:** A page derived from `component-registry.yml` `feeds_pages` for the selected component.
- **Shared page:** A mapped page whose reverse component map contains any component other than `ant-cli`.
- **Installer observation:** The immutable Git blob and source commit observed for a moving, unversioned installer URL. Isolated audit later records the CLI version that the blob selects.

## Authority and invariants

Authority is applied in this order:

1. [ADR-0016](../adr/ADR-0016-released-truth-for-public-developer-docs.md#decision) requires stable, publicly obtainable software, exact released provenance, reviewed baseline promotion, and honest limitations.
2. A reviewed release-baseline entry in `target-manifest.yml` is the selected public documentation baseline for its component and context.
3. Official GitHub Release and npm registry responses are direct public publication evidence used to propose a candidate.
4. The exact tagged source tree and shipped-dependency evidence support the claims audited for that candidate.
5. Page prose, prior audit notes, research memos, and provider release notes do not select or approve a baseline.

The implementation must preserve these invariants:

- Discovery emits a candidate and never writes the manifest or pages.
- GitHub and npm must agree on the stable version and exact source commit.
- Provider access, parsing, or response-shape failure uses the scanner's existing whole-run error behavior. The scanner emits empty `records` and `release_candidates`; the routine may open its existing failure issue but no PR.
- A successfully fetched but conflicting or incomplete release observation becomes existing per-record manual review. It does not change a baseline or page.
- Existing manual-review issues retain the fingerprint defined by [the routine's manual-review format](routines/upstream-sweep.md#manual-review-issue-format): record location, source repository, and `recorded_sha..head_sha`.
- Existing `claude/sweep-*` metadata and `claude/prose-*` rendered-content tracks remain distinct as required by [ADR-0006](../adr/ADR-0006-separate-metadata-and-prose-update-tracks.md#decision).
- Existing verification blocks retain the five fields and two modes fixed by [ADR-0003](../adr/ADR-0003-verification-block-source-of-truth.md#decision). No `component` field or new mode is added.
- Unmigrated blocks stay byte-identical and remain a visible backlog. There is no fallback to merged source.
- Inventory can later replace discovery input. It cannot approve a baseline or displace direct public evidence without a later approved decision.

These boundaries keep this specification within the Accepted ADRs. A Proposed successor is required before implementation if any stop condition in this file cannot be preserved.

## Additive target-manifest schema

### Coexistence

The existing top-level `scope` and `sources` maps remain unchanged and continue to describe the browser-only manual pin. Version 1 adds an optional top-level `release_baselines` map:

```yaml
scope:
  # Existing manual browser scope remains byte-identical.

sources:
  # Existing manual browser sources remain byte-identical.

release_baselines:
  schema_version: 1
  entries:
    "<component>/<context>":
      component: "<string: component-registry key>"
      context: stable
      version: "<stable-semver>"
      source:
        repo: "<string: repo-registry key>"
        tag: "<string: configured release tag>"
        commit: "<lowercase-40-hex>"
      github_release:
        id: "<positive-integer>"
        api_url: "<official-release-api-url>"
        release_url: "<official-release-url>"
        published_at: "<RFC-3339-timestamp>"
        draft: false
        prerelease: false
        checksum_asset:
          name: "<configured-checksum-name>"
          id: "<positive-integer>"
          url: "<official-immutable-asset-url>"
          digest: "sha256:<64-lowercase-hex>"
        platforms:
          "<target>":
            archive:
              name: "<configured-archive-name>"
              id: "<positive-integer>"
              url: "<official-immutable-asset-url>"
              digest: "sha256:<64-lowercase-hex>"
            signature:
              name: "<archive-name>.sig"
              id: "<positive-integer>"
              url: "<official-immutable-asset-url>"
              digest: "sha256:<64-lowercase-hex>"
      npm:
        package: "<configured-meta-package>"
        dist_tag: latest
        version: "<stable-semver>"
        metadata_url: "<official-versioned-npm-metadata-url>"
        integrity: "sha512-<base64>"
        git_head: "<lowercase-40-hex>"
        platforms:
          "<same-target>":
            package: "<configured-platform-package>"
            version: "<same-stable-semver>"
            metadata_url: "<official-versioned-npm-metadata-url>"
            integrity: "sha512-<base64>"
            git_head: "<same-lowercase-40-hex>"
      installers:
        - platform: "<enum: linux-macos|windows>"
          url: "<configured-raw-installer-url>"
          source_commit: "<lowercase-40-hex-path-commit>"
          blob_sha: "<git-blob-sha>"
          evidence_url: "<official-immutable-blob-url>"
          selected_version: "<stable-semver-observed-in-isolated-audit>"
      shipped_dependencies:
        "<dependency>":
          version: "<stable-semver>"
          source_repo: "<string: repo-registry key>"
          source_commit: "<lowercase-40-hex>"
          evidence_url: "<official-immutable-source-url>"
      scoped_pages:
        - "<repository-relative-page-path>"
      promotion:
        record: "planning/sweeps/<YYYY-MM-DD>.md"
```

This is an illustrative schema, not valid manifest content: typed placeholders show each required field and collection shape once. The field contract and test matrix are normative and apply to every configured platform, including all five required GitHub/npm platform pairs; the installer selections and promotion record require authorized audit and review.

Official GitHub and npm evidence observed on 2026-10-26 agrees on stable `ant` CLI `0.3.12` at exact source commit `6096b1c8caf6688d6825fcb9ff61fa1b590d984b`: [official GitHub release](https://github.com/WithAutonomi/ant-client/releases/tag/ant-cli-v0.3.12) and [official npm metadata](https://registry.npmjs.org/@withautonomi/ant/0.3.12). This is an observed candidate only, not an approved baseline; promotion still requires the complete audit and separate reviewed promotion PR.

### Field contract

- `release_baselines.schema_version` is the integer `1`.
- `entries` is keyed by `<component>/<context>`. The key must equal the entry's `component` and `context`; version 1 permits `context: stable` only.
- `version` is a stable Semantic Versioning value without a prerelease or build suffix.
- `source.repo` must equal the component's `repo` in `component-registry.yml`, must exist in `repo-registry.yml`, and must not be excluded. `tag` must match discovery configuration. `commit` is a lowercase 40-hex commit after tag peeling.
- `github_release` records one public, non-draft, non-prerelease release and the required assets. IDs are positive integers. URLs must point to the configured GitHub repository. Every digest is the provider's `sha256:<64 lowercase hex>` value.
- `npm` records the `latest` meta-package and all five platform packages. Every package version must equal the baseline version. Every `git_head` must equal `source.commit`. Every integrity is a non-empty `sha512-...` Subresource Integrity value from npm.
- The same five target keys must occur under `github_release.platforms` and `npm.platforms`. This is the platform-pairing evidence; no independent page map is stored.
- `installers` records exactly the Linux/macOS shell installer and Windows PowerShell installer in that order. `source_commit` is the lowercase 40-hex latest commit reachable from the configured moving ref that changed the installer path. `blob_sha` is the immutable Git blob at that path in `source_commit`, and `evidence_url` addresses that blob. `selected_version` is the version the isolated audit observed the installer selecting.
- `shipped_dependencies` contains only dependencies needed to support claims on `scoped_pages`. The first CLI baseline includes `ant-core` because both pages describe data, payment, update, and node-management behavior implemented through the shipped workspace component. It does not copy the complete lockfile or enumerate unrelated transitive packages.
- `scoped_pages` contains repository-root-relative paths, sorted lexicographically, with no duplicates. Each path must derive from the selected component's `feeds_pages`. The first promotion permits only the two CLI pages named under [Page matching and staged promotion](#page-matching-and-staged-promotion).
- `promotion.record` is the repository-root-relative `planning/sweeps/YYYY-MM-DD.md` audit record added in the same promotion PR. On the default branch, that file and manifest entry have passed the same human review. No `reviewed_at` or `verified_date` is invented before review and audit.

### Strict validation

The validator must use a duplicate-key-detecting YAML loader. Duplicate YAML keys, duplicate component/context identities, duplicate paths, duplicate asset names or IDs, and duplicate platform pairings fail validation.

Top-level keys are limited to the existing `scope`, existing `sources`, and optional `release_baselines`. Every map under `release_baselines` rejects unknown keys. Every field above is required except that `shipped_dependencies` may be absent when no scoped claim needs shipped-dependency evidence. Empty strings, placeholders, wrong scalar types, unrecognized contexts, malformed versions, malformed hashes, absent files, and mismatched repository/component/page relationships fail closed.

The validator accepts the existing `scope` and `sources` subtrees without translating them into release entries. Their existing bytes remain protected during the first CLI unit. A later migration may introduce and review a separate schema for normalizing those manual entries; version 1 does not infer, rewrite, or delete them.

`release_baselines` may be absent while the mechanism is introduced. Absence means no release baseline has been approved for automated following; it does not authorize fallback to `main`.

## Discovery configuration

Discovery configuration is added to the existing `ant-cli` component. `feeds_pages` remains the sole component-to-page map:

```yaml
ant-cli:
  repo: ant-client
  kind: rust-binary
  path: ant-cli/
  topics:
    - cli
    - node-management
  release_discovery:
    stable:
      github:
        tag_pattern: '^ant-cli-v(?P<version>(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))$'
        reject_drafts: true
        reject_prereleases: true
        checksum_asset: SHA256SUMS.txt
        platforms:
          aarch64-apple-darwin: tar.gz
          aarch64-unknown-linux-musl: tar.gz
          x86_64-apple-darwin: tar.gz
          x86_64-pc-windows-msvc: zip
          x86_64-unknown-linux-musl: tar.gz
      npm:
        package: '@withautonomi/ant'
        dist_tag: latest
        platform_packages:
          aarch64-apple-darwin: '@withautonomi/ant-darwin-arm64'
          aarch64-unknown-linux-musl: '@withautonomi/ant-linux-arm64'
          x86_64-apple-darwin: '@withautonomi/ant-darwin-x64'
          x86_64-pc-windows-msvc: '@withautonomi/ant-win32-x64'
          x86_64-unknown-linux-musl: '@withautonomi/ant-linux-x64'
      installers:
        - platform: linux-macos
          ref: main
          path: install.sh
          url: https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.sh
        - platform: windows
          ref: main
          path: install.ps1
          url: https://raw.githubusercontent.com/WithAutonomi/ant-client/main/install.ps1
```

### GitHub selection

1. Request GitHub Releases pages of 100 records and follow pagination until no next page exists.
2. Keep only tags matching the anchored component pattern.
3. Reject `draft: true`, reject `prerelease: true`, parse the captured version as Semantic Versioning, and independently reject any prerelease or build suffix.
4. Order eligible releases by Semantic Versioning descending, not provider order or publication time, and select the highest.
5. Resolve `refs/tags/<tag>`. A lightweight tag must point to a commit. For an annotated tag, follow tag objects until the target type is `commit`. The resulting 40-hex SHA is the GitHub source identity.
6. Require one archive and one `.sig` file for each configured target plus `SHA256SUMS.txt`. Names are `ant-{version}-{target}.{archive}` and the same name plus `.sig`. Missing or duplicate required names make the fetched candidate incomplete. Additional release assets do not affect completeness and are not copied into the baseline.

The five archive/signature pairs and checksum file are proportionate to the public claims: the CLI page advertises macOS, Linux, and Windows; npm publishes five matching CPU/operating-system packages; the release instructions offer signatures and checksums. The contract mirrors the release workflow and the observed stable packaging. It does not require speculative notarization, attestation, download-count, or vulnerability fields.

### npm selection

1. Read the configured `latest` distribution tag, then fetch that exact meta-package version.
2. Parse the version as Semantic Versioning and reject any prerelease or build suffix even if `latest` points to one.
3. Require `version`, `dist.integrity`, `gitHead`, and `optionalDependencies` on the meta-package.
4. Require every configured platform package in `optionalDependencies` at the exact selected version, then fetch each exact package and require its `version`, `dist.integrity`, and `gitHead`.
5. Pair each npm package with the same target key used by the GitHub archive. A missing package, version mismatch, missing field, or pairing mismatch makes the fetched candidate incomplete.

## Reconciliation

Reconcile only after both providers have completed successfully. GitHub and npm stable versions must be equal; the peeled GitHub commit, npm meta-package `gitHead`, and every platform-package `gitHead` must be equal; and all required GitHub assets and npm platform pairings must be complete.

### Immutable comparison projection

Normalize both the observation and incumbent baseline to one ordered projection before comparing them. Equality and same-version mutation detection use exactly:

- `component`, `context`, and stable `version`;
- source repository, tag, and peeled commit;
- GitHub release ID; checksum asset name, ID, and digest; then, sorted by `(target, role, name)`, every required archive and signature's target, role, name, ID, and digest;
- npm meta-package name, distribution tag, version, integrity, and `gitHead`; then, sorted by target, every required platform package's target, package name, version, integrity, and `gitHead`; and
- required shipped-dependency `(name, version, source_repo, source_commit)` pairings only when the configured deterministic discovery adapter can establish all four values from immutable release evidence. Version 1 CLI discovery does not establish these pairings, so they are audit-added evidence and are absent from both sides of the discovery comparison.

URLs, `published_at`, observation or `generated_at` timestamps, provider response order, download counts, installer evidence, `scoped_pages`, and `promotion` do not participate in this projection. URLs remain evidence locators and are validated separately. Canonical map keys and tuple lists are lexicographically sorted before equality comparison.

An identical projection means no release drift. A complete agreeing observation with a greater stable Semantic Versioning value is a candidate. A changed projection at the same or a lower version is existing per-record manual review, with no downgrade. A complete agreement with no incumbent is an initial candidate. Provider disagreement or incomplete required evidence is also existing per-record manual review.

The candidate's `source`, `github_release`, and `npm` fields expose the normalized release evidence represented by this projection. `pages` and `records` identify its documentation scope but do not participate in equality. Installer execution and selected version, shipped-dependency evidence, archive/checksum/signature verification results, final `scoped_pages`, and `promotion` are added only by the audit; they are not candidate fields and discovery must not imply that they have been checked.

### Release-driven page records

Every run evaluates every enrolled `release_baselines.entries` item. Every `target-manifest` page block, including an enrolled block, remains listed in `target_manifest_skipped`. That array continues to mean only “skipped from moving-ref resolution”; it never means “ignored by release discovery.” Release discovery separately synthesizes one seven-field record for every path in the entry's `scoped_pages` and appends it to top-level `records`. Candidate `records` refer to these newly synthesized records and never depend on records emitted by the legacy moving-ref walk.

For an enrolled entry, read each scoped page and select verification blocks whose `source_repo` equals `entry.source.repo` and whose `verification_mode` is `target-manifest`. There must be exactly one. That block must also have `source_ref == entry.source.tag` and `source_commit == entry.source.commit`. A missing block, multiple matches, any field mismatch, a missing page, or a page absent from the component's derived `feeds_pages` fails the whole scanner run as malformed incumbent state. For an initial candidate with no entry, apply the same exactly-one rule to each mapped page using `source_repo == component.repo`; its existing mode/ref/commit may still be `current-merged-truth`, but malformed or multiple component blocks fail closed. This matching is by page path and block fields, never by provider order or a page line retained from an earlier walk.

Each release-driven record has the following exact values:

- `location`: the matched block's current `<repository-relative page>:<opening line>`;
- `scope`: the literal `docs`;
- `repo`: the component/entry source repository;
- `ref`: the agreeing observation's tag for no-change, candidate, and installer-only cases; for disagreement or incompleteness, the selected valid GitHub tag when one exists, otherwise the incumbent tag, or the matched block's `source_ref` when no incumbent exists;
- `recorded_sha`: the matched page block's `source_commit` (which strict incumbent matching requires to equal the baseline commit after promotion);
- `head_sha`: the peeled agreeing GitHub commit for no-change, candidate, and installer-only cases; for disagreement or incompleteness, the peeled GitHub commit when valid, otherwise a valid npm `gitHead`, otherwise the incumbent commit, and finally `recorded_sha`; and
- `drifted`: the literal comparison `recorded_sha != head_sha`.

Thus no-change records use the incumbent tag/commit and have `drifted: false`; candidate records use the newer observed tag/commit and have `drifted: true`; disagreement/incomplete records use the deterministic fallback above; and installer-only drift keeps the reconciled release tag/commit, commonly producing `drifted: false`. A `release_manual_review` notice bypasses the routine's no-drift short-circuit for disagreement, incompleteness, or installer drift. The notice carries the reason and normalized evidence rather than overloading the SHA pair with an installer blob or moving-ref commit.

Provider transport, authentication, HTTP, JSON/YAML parse, or response-shape failure returns top-level `status: "error"`, exit code `2`, empty `records`, and empty `release_candidates`. The existing routine opens its fresh failure issue and no PR, preserving [ADR-0007's whole-run behavior](../adr/ADR-0007-fail-closed-and-github-artifact-topology.md#decision).

When valid provider responses conflict or lack candidate evidence, the scanner keeps `status: "ok"`, emits the synthesized affected-page records, and adds a deterministic `release_manual_review` notice naming the locations and reason. The audit loop classifies those records `ambiguous`, uses the existing manual-review issue format and fingerprint, and continues with unrelated records. This is the existing per-record behavior, not a new release outcome.

The fingerprint and original issue body remain exactly as specified in [the routine's manual-review format](routines/upstream-sweep.md#manual-review-issue-format). On an exact fingerprint match, reuse the issue without editing its body and immediately append a dated comment containing the current reason plus canonical, sorted GitHub, npm, and installer baseline/current evidence from the notice. Include exact release/tag/commit, asset IDs/digests, package versions/integrities/`gitHead` values, and installer URL/path/source commit/blob/evidence URL where present. This evidence comment is required even when no PR is opened; the existing later `Tracked in <PR URL>. (Run date <today>.)` comment remains unchanged when a PR exists. Changed secondary evidence is therefore visible without changing the Accepted fingerprint or body semantics.

### Moving installers

The shell and PowerShell URLs remain unversioned user-facing installation routes. Observe both configured URLs on every scanner run, independently of whether release discovery finds a candidate. First require each raw URL's owner, repository, ref, and path to equal its configuration. For each `(repo, ref, path)`, request the latest path commit (`per_page=1`) from the official GitHub commits API, require it to be reachable from `ref`, then fetch that path at the exact commit and record this normalized metadata: platform, configured URL, repo, ref, path, lowercase 40-hex `source_commit`, Git blob SHA, and immutable blob evidence URL. This commit is stable across unrelated movement of the configured branch and supplies the recorded blob.

Any transport, authentication, parse, response-shape, missing-history, or blob-linkage failure is a provider failure with the existing top-level error behavior. A successful observation emits an informational notice so the first live read-only run and no-candidate runs prove that both URLs were checked; this notice is evidence, not an outcome or fingerprint.

For an enrolled baseline, compare each current `(platform, url, source_commit, blob_sha, evidence_url)` tuple with its reviewed installer tuple. Missing, duplicate, or changed evidence marks every scoped page record ambiguous through `release_manual_review`, even when the GitHub/npm projection equals the baseline. The record's `recorded_sha` and `head_sha` remain the reconciled release commits defined above; the notice and issue comment carry the exact baseline and current installer tuples. Do not emit an installer-specific outcome or fingerprint.

The deterministic scanner never executes an installer and does not claim a selected version. During the later audit, download the already observed immutable blob into an isolated environment, record the selected version, and require it to equal the reconciled GitHub/npm version. A mismatch blocks promotion of the affected page and uses existing per-record manual review.

## Page matching and staged promotion

1. Read `ant-cli.feeds_pages` and prepend `docs/` to each registry path.
2. Build the reverse page-to-components map from every component's `feeds_pages` in the same registry.
3. Include each mapped page and its sorted component set in the candidate report.
4. Treat a page as shared when the reverse map contains a component other than `ant-cli`.
5. Audit all mapped pages for CLI contradictions.

After `ant-cli` release discovery is enrolled, an `ant-client` verification block on an `ant-cli` mapped page is not advanced against `main`. Component-only pages receive release-driven records. Shared or otherwise unmigrated records are held unchanged in the explicit backlog/manual-review path until their component claims can be separated and audited. This prevents the legacy scanner path from becoming a merged-source fallback during migration.

The first promotion may change and promote only:

- `docs/cli/use-the-cli.md`
- `docs/cli/command-reference.md`

Each page requires a complete audit against the exact released binary/source, GitHub assets, npm packages, installer behavior, commands, flags, examples, output claims, limitations, and relevant platform behavior. If required runtime evidence is unavailable or prohibited, the page remains unpromoted.

The following mapped/shared pages must be inspected and listed in the promotion record as clear, contradictory, or unresolved, but their prose and verification blocks remain unchanged in the first unit:

- `docs/index.md`
- `docs/guides/overview.md`
- `docs/guides/build-read-only-features.md`
- `docs/guides/deploy-to-mainnet.md`
- `docs/guides/prepare-a-wallet-for-uploads.md`
- `docs/reference/source-repositories.md`
- `docs/reference/glossary.md`

This list is the first-unit backlog derived from `feeds_pages`, not a second persistent page map. Later units recalculate it from the registry.

On reviewed promotion, each of the two CLI blocks keeps `source_repo`, `source_ref`, `source_commit`, `verified_date`, and `verification_mode`. Set `source_ref` to the exact release tag, `source_commit` to the peeled commit, `verified_date` to the real completed audit date, and `verification_mode` to `target-manifest`. Do not add fields. Every unmigrated block remains byte-identical.

## Scanner report compatibility

The scanner retains the existing top-level fields and meanings documented by [ADR-0004](../adr/ADR-0004-deterministic-scanner-model-audit-loop.md#neutral--operational):

```text
status
generated_at
records
target_manifest_skipped
notices
errors
```

It adds one top-level field:

```text
release_candidates
```

`release_candidates` is always an array and is empty on error, no agreement, incomplete evidence, or no drift. Each candidate contains `component`, `context`, `version`, `source`, `github_release`, `npm`, `pages`, and `records`. `source`, `github_release`, and `npm` use the manifest field shapes above. Installer, shipped-dependency, scoped-page, and promotion evidence is added by the audit, so discovery does not claim it in the candidate. Each page has `path` and a sorted `components` array. Each record is a release-driven record synthesized under the rules above with only the existing seven fields: `location`, `scope`, `repo`, `ref`, `recorded_sha`, `head_sha`, and `drifted`. No existing field is removed or renamed.

Candidate order is `(component, context)`. Page and record order is `(path, line)`. Platform keys, asset names, dependency keys, and component lists are lexicographic. Provider response order cannot affect output. `generated_at` remains the existing diagnostic timestamp; no observation timestamp, publication timestamp, download count, API response order, or page line number participates in identity or deduplication.

No release or installer fingerprint is created. Manual-review deduplication continues to use the existing per-record fingerprint. Duplicate proposal prevention continues to use the existing open-PR collision across both updater branch families. A closed PR receives no new suppression state; after it closes, later runs follow existing discovery and collision behavior.

## Candidate-to-promotion flow and guards

1. Run the existing one-open-updater-PR collision check across `claude/sweep-*` and `claude/prose-*`. Any open match causes the existing silent exit.
2. Run deterministic discovery and reconciliation.
3. For a candidate, fetch exact source identities, perform the authenticity audit below, audit all mapped pages, inspect installer behavior, and run practical verification under [source audit → draft → verify](verification-workflow.md#required-workflow).
4. Route a no-prose promotion through `claude/sweep-*`. Route any rendered change through draft `claude/prose-*`. The two tracks never touch the same page in separate PRs.
5. Add the proposed baseline, the two audited verification-block promotions, and one promotion record atomically in the selected PR. Add rendered changes only on the prose track.
6. CI validates schema, evidence relationships, allowed files, rendered-content separation, and exact correspondence between the entry and promoted blocks.
7. A human reviews the evidence and PR. Merge remains the action that makes the proposed baseline authoritative on the default branch.

### Promotion authenticity audit

This audit is a later promotion requirement, not part of deterministic discovery and not authorized for execution by this specification review.

1. Create an isolated temporary directory and download into it the exact checksum file and every required archive and advertised signature selected by release asset ID. Do not substitute a same-named local or moving-URL file.
2. Compute SHA-256 for every downloaded file and require equality with each asset's GitHub provider digest. Parse the downloaded checksum file strictly, require exactly one entry for every required archive and no conflicting duplicate, and require each computed archive hash to equal its checksum-file entry.
3. Audit the exact tagged source and release workflow to identify the release's canonical public verification key, signature tool and version/format, signed-object convention, and signing context or namespace. Pin the key by its source location plus cryptographic fingerprint or equivalent immutable identity; a release note or signature filename alone is not authority.
4. Using that canonical material, verify every archive's advertised signature against the exact downloaded archive. Run verification from the isolated directory with explicit file paths and no ambient key selection.
5. Record in `promotion.record` every downloaded asset name/ID/provider digest/computed hash, parsed checksum entry, exact key identity and audited source, tool/version, signing context, complete commands, exit results, and any platform or runtime limits. Secrets and private key material are never recorded.

If canonical key/tool/context evidence is missing, contradictory, or not applicable to every advertised signature, or if any digest, checksum, or signature verification fails, stop. Do not edit pages, add or advance the baseline, or weaken tests, fixtures, harnesses, guards, or commands to obtain green evidence.

The existing guards presently reject `target-manifest.yml` and any target-manifest block mutation. The implementation slice must change that mechanism explicitly rather than bypass it:

- Keep the two existing branch families and their ordinary envelopes.
- Permit coordinated release-baseline promotion only when the strict validator passes, the changed blocks belong to `scoped_pages`, and each promoted block exactly matches the proposed entry.
- Keep the existing browser `scope`, `sources`, and browser target-manifest blocks byte-identical during the CLI unit.
- Make release-sensitive diff detection branch-independent. A PR under any other branch name that changes `target-manifest.yml`, adds/removes/changes a target-manifest block, or changes a promotion record must fail with an instruction to use the applicable existing branch family. A new branch name cannot obtain a scope-gated green no-op.
- Keep rendered prose forbidden on `claude/sweep-*`; keep `claude/prose-*` as the stronger rendered-content route.
- Keep SHA reachability and Repository Tests as CI evidence. Release tags replace moving-ref ancestry for promoted release blocks, so the release validator checks exact tag peeling and commit equality rather than silently skipping provenance.

These are test/CI/guard mechanism changes. They require an expressly approved mechanism slice before any file is edited.

## Failure modes and duplicate handling

The preceding contracts control failure handling: [Strict validation](#strict-validation) covers manifest duplicates and unknown keys; [Reconciliation](#reconciliation) and [Release-driven page records](#release-driven-page-records) distinguish provider failure from successful disagreement or incomplete evidence; [Moving installers](#moving-installers) applies the same distinction to commit/blob evidence; and [Page matching and staged promotion](#page-matching-and-staged-promotion) keeps contradictory shared and unmigrated pages unchanged. These rules also preserve initial candidates without merged-source fallback, component-specific tag filtering, and per-record review when required source comparison fails.

[Scanner report compatibility](#scanner-report-compatibility) preserves the existing fingerprint, body, collision, and closed-PR behavior. A matching open issue is reused without editing its body, receives the required dated current-evidence comment immediately, and receives the unchanged tracking comment later if a PR exists. An open updater PR still causes the existing silent collision exit. A paid upload, production write, unsupported platform claim, or unavailable runtime evidence stops promotion and leaves the affected page unpromoted.

## Inventory adapter seam

Discovery should expose a small provider boundary that returns the normalized GitHub/npm evidence shape consumed by reconciliation. Direct adapters use official public GitHub and npm responses. A future Inventory adapter may return the same shape and replace polling mechanics.

Inventory remains a replaceable discovery input, not baseline authority. Until a later approved decision changes this rule, candidate evidence must still resolve to direct public release/package URLs and exact source identities, and promotion still requires the same page audit, guards, review, and manifest record. No code may depend on an unpublished Inventory endpoint, field name, authentication method, or identifier.

## Concrete implementation slice

### Goal

Implement offline-fixture-first CLI release discovery, strict additive baseline validation, compatible scanner reporting, routine routing, and guard enforcement. Demonstrate the observed candidate above only as a candidate. Do not promote a baseline or edit documentation pages in this slice.

### Allowed files

- `component-registry.yml`
- `scripts/sweep_poll.py`
- `scripts/validate_release_baselines.py` (new)
- `scripts/tests/test_sweep_poll.py`
- `scripts/tests/test_release_following.py` (new)
- `scripts/tests/test_doc_guards.py`
- `planning/routines/upstream-sweep.md`
- `planning/routines/upstream-sweep-prompt.md`
- `.github/workflows/sweep-guard.yml`
- `.github/workflows/prose-guard.yml`
- `.github/workflows/sweep-sha-reachability.yml`
- `.github/workflows/repository-tests.yml` only if needed to invoke the new repository validator in CI
- One new implementation checkpoint or verification record under `planning/`

### Forbidden in the implementation slice

- `target-manifest.yml`
- `docs/**`
- `adr/**`
- `repo-registry.yml`
- `CLAUDE.md`
- Hosted routine schedule, enabled state, model, secrets, or permissions
- New dependencies
- Commit, push, PR, issue, merge, publish, release, paid operation, or production write without separate authorization

### Offline fixture-first matrix

Fixtures must cover:

1. The unchanged browser-only manual manifest with no `release_baselines`.
2. A valid additive version 1 entry and two separate component/context entries sharing one repository and commit.
3. Duplicate YAML keys, duplicate component/context identity, every unknown-key level, malformed values, placeholders, missing files, and mismatched pages.
4. GitHub pagination beyond one page, provider-order independence, Semantic Versioning ordering, drafts, GitHub prereleases, SemVer prereleases, lightweight tags, and annotated tag peeling.
5. The five archive/signature pairs plus checksum; missing, duplicate, or wrong-target assets; irrelevant extra assets.
6. npm `latest`, stable/prerelease rejection, missing integrity or `gitHead`, meta-package optional-dependency mismatch, missing platform package, wrong version, wrong commit, and all five valid pairings.
7. Release or installer provider access, parse, shape, or commit/blob-linkage failures producing top-level error with empty records/candidates.
8. Successfully fetched disagreement or incompleteness producing the specified release-driven records and a manual-review notice, with no candidate or baseline/page mutation.
9. Agreement with no incumbent producing a candidate; exact projection equality producing no release drift; a greater complete release producing a candidate; and lower or same-version-mutated projection evidence producing manual review. URL, timestamp, order, and download-count changes alone do not produce release drift.
10. Installer metadata observation on every run, including no-candidate runs; immutable source-commit/blob agreement; and mismatch while release providers equal baseline, using existing per-record ambiguity and no installer outcome/fingerprint. Isolated selected-version execution remains an audit fixture, not scanner behavior.
11. `feeds_pages` and reverse-map derivation, the two first-unit pages, all seven deferred pages, byte-identical legacy blocks, and strict missing/multiple/mismatched enrolled-block failures.
12. Existing output fields unchanged, additive `release_candidates`, deterministic release-driven records for no-change/candidate/disagreement/installer cases, retained `target_manifest_skipped`, and no timestamp in identity/deduplication.
13. Existing `claude/sweep-*`/`claude/prose-*` collision and envelope behavior, valid atomic release promotion fixtures, browser-pin byte preservation, metadata/prose separation, and rejection of a protected change under an unrelated branch name.
14. No closed-PR suppression, unchanged existing per-record fingerprint/body formatting, and a reused issue's dated comment containing exact current normalized conflict evidence even when no PR exists.
15. Local authenticity fixtures for provider hashes, checksum entries, every advertised signature, canonical key/tool/context evidence, and each fail-closed condition; no live archive or signature download occurs in the implementation slice.

All provider responses, tag objects, registries, installers, manifests, docs, and Git histories in these tests are local fixtures or mocks. Offline tests make no network calls.

### Bounded live read-only checks

After offline tests pass, run one scanner invocation against the official public providers. It must read GitHub Releases, tag objects, npm metadata, and both installers' path-commit/blob metadata on that run. It must not download release archives or signatures, download or execute an installer, install a package globally, alter personal configuration, use a wallet, or write to the Autonomi Network.

The observed check must match the observed-candidate paragraph above and report it as a candidate, not as an approved baseline. If live evidence differs, preserve the raw diagnostic and stop rather than updating expectations to force green.

### Commands

```bash
python3 -B -m unittest discover -s scripts/tests -p 'test_release_following.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_sweep_poll.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_doc_guards.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'
python3 -I scripts/validate_release_baselines.py
python3 -I scripts/adr-governance.py
git diff --check
python3 scripts/sweep_poll.py
```

The live scanner command runs last and is read-only. Its output must be retained in the implementation evidence without committing generated output.

### Acceptance criteria

- Every case in the offline fixture-first matrix passes without network access, including strict acceptance of the unchanged browser manual manifest and rejection of invalid release entries.
- Each run satisfies the exact [release-driven record contract](#release-driven-page-records), [immutable comparison projection](#immutable-comparison-projection), [failure handling](#failure-modes-and-duplicate-handling), and per-run installer source-commit/blob checks.
- The component registry remains the sole page map; the two first-unit pages and seven-page backlog retain the staged behavior above.
- The bounded live check matches the observed-candidate paragraph, observes both installer identities, and does not approve or promote a baseline or change a page.
- Existing update tracks, collision behavior, browser pins, unmigrated blocks, and branch-independent guards are preserved.
- Promotion satisfies every step of the [promotion authenticity audit](#promotion-authenticity-audit), including exact provider/checksum comparison and every advertised signature verification with the source-audited key, tool, and context recorded in the promotion record.
- Repository Tests on the implementation PR are the green of record. Local checks alone do not establish readiness.

### Stop conditions

Stop and return a checkpoint before proceeding if implementation would require:

- automatic promotion, a third update track, a new verification mode, or a verification-block schema change;
- a new whole-run/per-record outcome model;
- a release or installer fingerprint, changed manual-review fingerprint, changed collision rule, or closed-PR suppression;
- fallback to merged source or mutation of an unmigrated block;
- alteration of the existing browser manual entries or blocks;
- treating Inventory as authority;
- a new dependency, public API, data model beyond this specified manifest/report addition, or unrelated restructure;
- weakening target-manifest protection, prose review, CI coverage, or fail-closed behavior;
- page promotion without complete evidence, or any paid/production operation;
- workflow, guard, test-harness, build, or environment changes outside the exact approved mechanism slice;
- an Accepted ADR conflict or any inability to preserve the invariants in this specification.

## Verification and review plan

The [Repository Tests workflow](../.github/workflows/repository-tests.yml) is the CI green of record for implementation. The existing guard workflows remain required evidence when their substantive scopes apply. This uncommitted specification has no CI run.

| Lane | Requirement and source | Selection | Due point | Disposition |
|---|---|---|---|---|
| Verifier | Required by this work unit | Requested | Specification checkpoint | Check the specification against the packet, issue requirements, manifest, scanner, registries, workflows, and Accepted ADR clauses; run the two authorized text-safe commands. |
| Craft | Required for this meaningful shared-repository specification unit | Requested | Specification checkpoint | Review for repository convention, internal consistency, minimality, and absence of advisory-only outcome/fingerprint additions. |
| Clean-context | Required by the production-bound profile | Requested | First working CLI milestone, before PR/merge readiness | Not yet due; no waiver or deferral of the required milestone review. |
| Adversarial | Required once at the feature milestone | Requested | First working CLI milestone | At gate; not due for this specification-only checkpoint. |

At the first working CLI milestone, use the repository's configured stable v3 clean-context procedure: run argument-free `prepare.py` from the canonical clean committed root; use its returned paths for the caller-owned private brief and dispatch; run argument-free `dispatch.py` into a fresh named `cleancontext`; persist the complete validated result to a caller-owned private ledger outside the checkout; then run and validate argument-free `release.py`. This procedure is not due and must not run at this specification checkpoint.

Craft is required for every meaningful implementation unit. Clean-context and one adversarial review converge at the first working CLI milestone. No implementation unit may be marked Done from the specification review.

## Owner decision

No owner decision is needed to settle this specification. The asset contract, failure routing, page scope, migration boundary, and guard approach remain within the stated constraints and Accepted ADRs.

## Advisory research disposition

Research notes generated during the audit were used only as advisory locators and were not retained as project artifacts. Direct repository artifacts, Accepted ADRs, and official public provider observations support this specification. The advisory proposal's `blocked_disagreement`, `blocked_incomplete`, `installer_review`, release fingerprint, installer fingerprint, and closed-PR suppression are not adopted because they would change existing outcome or deduplication contracts and require separate decision review.
