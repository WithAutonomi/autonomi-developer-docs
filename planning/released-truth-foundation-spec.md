# Released-truth foundation specification

Status: ADR-0019 accepted; local implementation, verification, Craft Review, and PR #110 CI passed. Hermes/Claude clean-context review remains pending.

Issue: [#103 — adopt released truth in rules and tooling](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103)

## Objective

Apply [ADR-0016](../adr/ADR-0016-released-truth-for-public-developer-docs.md) as the default authoring and maintenance rule without pretending that legacy verification blocks have already been migrated.

## Public source-of-truth contract

`target-manifest.yml` is the single machine-readable container for the selected public release set. A public technical claim is verified only when its verification block matches a reviewed release or source profile in that manifest.

Component profiles may advance through separate reviewed promotions only when each promotion preserves one compatible active release set, including shipped dependencies and deployed-network compatibility wherever relevant. Profiles are evidence mechanisms, not independent fallback baselines. Exact evidence depends on the component: packages, binaries, shipped dependencies, protocol versions, deployed-network behavior, or another audited release artifact.

Default-branch source remains useful for preparing future documentation and locating likely implementation files. It cannot support a new or refreshed default-public claim.

## Verification modes during migration

The five verification fields and two modes remain unchanged.

- `target-manifest` is the authoritative mode for public technical documentation.
- Existing `current-merged-truth` blocks remain historical records of the verification mode defined by ADR-0003. Under ADR-0016, they are ineligible as evidence for new or refreshed default-public claims and are frozen as migration debt.

No third transitional mode is introduced. A page can temporarily contain both modes when one component has been promoted and another remains migration debt. This is a physical migration state, not a mixed active baseline and not a fully verified page. Only claims supported by `target-manifest` evidence may be added or refreshed. Legacy-backed claims remain untouched migration debt. If work touches such a claim, or combines legacy and released evidence for one claim or developer journey, stop and migrate or defer it.

## Authoring behavior

For a new page or a technical update:

1. Identify the component and affected pages through the registries.
2. Find its reviewed release profile in `target-manifest.yml`.
3. Audit exact public artifacts and shipped dependencies required by the claim.
4. Write and verify only against that baseline.
5. Add or update `target-manifest` blocks through an atomic promotion.

If no reviewed profile exists, stop. Add the component to the migration inventory and prepare a profile or defer the technical change. Never fall back to `main`.

Pure editorial changes may preserve an existing legacy block byte-for-byte. They do not renew its date, SHA, or verification status.

## Scanner behavior

The deterministic scanner keeps validating every verification block's shape, mode, and repository identity.

It handles blocks as follows:

- `target-manifest`: continue listing them in `target_manifest_skipped` because moving-ref resolution does not apply; enrolled release profiles are evaluated through release discovery.
- `current-merged-truth`: list them in the additive `migration_backlog` array with their location and recorded provenance. Do not resolve their refs, compare them with branch heads, or emit ordinary drift records. This includes legacy blocks on components already enrolled in release discovery.

[ADR-0019](../adr/ADR-0019-evidence-capable-release-fallbacks.md) records the resulting fallback boundary. Release-provider evidence fails closed when a fallback cannot reproduce the complete required evidence; Git remains available where exact Git objects are themselves the evidence.

The `records` array remains the candidate list consumed by the existing audit loop. After this unit, documentation records enter it only through an enrolled release profile. The new backlog field is informational and does not create PRs or issues on each run; issue #104 is the migration ledger.

`migration_backlog` is always present. On a successful scan it is sorted by page path and numeric block line and contains one object per legacy block with exactly these fields:

```json
{
  "location": "docs/example.md:8",
  "repo": "ant-sdk",
  "ref": "main",
  "recorded_sha": "0123456789abcdef0123456789abcdef01234567"
}
```

On a fail-closed report it is an empty array. `target-manifest` blocks never appear in it. A mixed-mode page contributes only its legacy blocks. Duplicate legacy blocks remain separate entries because their line-qualified locations differ.

Malformed blocks, unknown modes, and unknown repositories still fail the whole scan. Release-provider failures retain their existing fail-closed behavior.

## Promotion invariants

The proven pilot invariants remain binding:

- Discovery can propose but never approve a release.
- Manifest entries, matching page blocks, and a dated promotion record move atomically.
- Exact tags resolve to exact commits.
- Unrelated verification blocks remain byte-identical.
- Human review and merge approve a promotion.
- Manual evidence profiles are valid when automation would not earn its maintenance cost.

## Profile boundary for Unit 3

The CLI and Browser profiles are pilots, not templates to copy across the estate. Unit 3 must define a small common baseline record plus strict component-specific evidence profiles.

Unit 3 must support:

- public artifacts that do not use npm or platform binaries;
- source-only tagged releases;
- several packages released from one repository;
- reviewed growth of a baseline's page scope;
- grouped promotion of shared pages;
- byte preservation of every unrelated legacy and released block;
- experimental or pre-release software only in dedicated, clearly separated, explicitly labeled documentation approved for that scope. It never qualifies stable or general-availability default-public claims. The existing Browser SDK treatment is case-specific and does not establish a general separation rule.

Unit 3 must preserve the existing verification-block schema. If implementation proves that impossible, stop and prepare a Proposed ADR superseding ADR-0003 rather than changing the schema inside a feature branch.

## Completion criteria

The foundation is complete when:

- repository instructions name released truth as the default;
- no scanner path resolves a legacy block against a moving branch;
- every legacy block appears in `migration_backlog` and remains byte-identical;
- released profiles continue to emit release candidates and fail closed on bad evidence;
- the routine instructions cannot interpret migration debt as ordinary drift;
- `planning/released-truth-migration-inventory-2026-10-28.md` records the structural snapshot and distinguishes it from the later release/artifact inventory;
- the current inventory and next CLI promotion unit are recorded;
- full local checks and independent review pass.
