# ADR-0016: Released truth for public developer documentation

- **Status:** Proposed
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (source-selection default and verification-mode set only); ADR-0004 (default-branch metadata-restamp semantics only)
- **Superseded by:** none
- **Related:** ADR-0005 through ADR-0007; ADR-0012 through ADR-0014; `planning/verification-workflow.md`; `planning/implementation-plan.md` §5; `WithAutonomi/ant-sdk` v0.11.2 audit; [WithAutonomi/ant-sdk issue #233](https://github.com/WithAutonomi/ant-sdk/issues/233)

## Context

ADR-0003 made `current-merged-truth` the default source for public developer documentation. This prevented speculative documentation of unmerged branches, but it did not prevent a different failure: a default branch can contain code that has not been released, is not available through a supported installation route, is incompatible with the deployed Autonomi Network, or has not been proven usable through the interface the page recommends.

That gap can make rendered documentation describe what source code intends rather than what a developer can obtain and build against. The `antd` v0.11.2 audit exposed the practical consequences. The stable release corrected ordinary Merkle writes, while several released binding and Model Context Protocol (MCP) external-signing paths remained defective or unavailable. The gRPC service also rejects a valid all-already-stored finalization and consumes its upload identifier, tracked in `ant-sdk` issue #233. Neither moving source nor the existence of an API shape is enough to call a developer journey available.

The existing `target-manifest` mode can pin a release-hardening pass, but ADR-0003 treats it as an exception and returns public docs to moving default branches afterward. Public developer documentation needs the reverse default: released, obtainable, compatible, evidence-backed behavior is the normal truth; moving source prepares the next documentation release without silently changing the public one. The rendered docs and published developer skill are two delivery forms of that same public guidance, so they must describe one released product surface.

## Decision Drivers

- Developers must be able to obtain and use the product surface that the public docs describe.
- Merged but unreleased code must not appear as an available capability.
- A multi-repository product surface must resolve to one compatible, auditable release set.
- Known defects must produce safe guidance, not optimistic claims or silent omission.
- Package and installation claims must distinguish public availability from source-directory presence.
- Exact per-surface provenance and deterministic drift detection must remain intact.
- Future-release work must remain visible without being confused with public released truth.
- Rendered docs and the published developer skill must not describe different product releases or support boundaries.

## Considered Options

1. **Retain ADR-0003: moving merged truth by default, with release constraints only for installation and version pages.** Rejected because API, behavior, architecture, examples, and compatibility can also differ between merged source and the released product developers can use.
2. **Make the existing `target-manifest` mode the permanent default.** Rejected because that mode represents an explicitly selected launch or pre-release target. Reusing it for the public released product would conflate what is being hardened with what is already available and supported.
3. **Make released truth the public default and retain a distinct target mode for explicit pre-release hardening or versioned previews.** Chosen because it keeps the public contract honest while preserving preparation for the next release.
4. **Treat release status and public availability as sufficient evidence of usability.** Rejected because an obtainable release can expose a defective or nonfunctional route. Release status proves availability, not that the documented capability works.
5. **Allow each documentation surface to select released refs independently.** Rejected because independent pins cannot establish cross-component or deployed-network compatibility. The public surface needs one auditable release set.

## Decision

Public rendered developer documentation and the published developer skill will describe **released truth** by default: the newest coherent set of released component versions that is publicly obtainable through documented standard routes, compatible with one another and the deployed Autonomi Network for the claims made, and supported by capability-specific evidence.

The verification model will retain exact per-surface provenance while changing its default:

- **`released-truth` is the default mode for public rendered documentation and the published developer skill.** Verification resolves every documented surface to exact refs in one machine-readable release manifest. A ref may identify a component's own release or the exact dependency ref shipped by another released product.
- **The release manifest represents a coherent product set, not a bag of latest tags.** Component versions, transitive refs that carry documented behavior, and deployed Autonomi Network compatibility must agree for the claims that depend on them.
- **`target-manifest` remains an explicit pre-release, launch-hardening, or release-candidate mode.** It does not become the current public developer surface before release. If target content is published, it must be isolated and clearly labelled as a versioned preview rather than replacing the default docs.
- **`current-merged-truth` is retired as a verification mode for public rendered documentation and the published skill.** Moving default branches remain research inputs for drift detection, impact assessment, and next-release preparation. A merge can open an audit queue; it cannot silently advance rendered prose or verification SHAs.

Released truth is capability-specific and evidence-based:

- “Usable” does not mean “bug-free.” A known defect is part of released truth. The docs must state the affected route, boundary, or operation and provide a safe alternative when one exists.
- A broken or unproven route must not be presented as working. Missing evidence requires the page to defer, narrow, stub, or reframe the claim rather than infer success.
- A package, binary, container, binding, or tool is available only when its documented standard installation identity resolves publicly, or when the project explicitly supports a reproducible source-install route that has been verified from a clean environment. Source-directory presence alone is not availability.
- A release is promoted into public docs only after an audit resolves exact component and dependency refs, obtainable artifacts, release-set compatibility, relevant runtime or journey evidence, and known limitations.
- When the newest release is unsuitable as the supported developer baseline, the manifest may retain the prior supported release set. That exception must be explicit, justified by evidence, and visible in the release audit; it must not happen through stale metadata or omission.

The existing verification-block invariants remain:

- Every rendered documentation surface carries one or more machine-readable verification records with source repository, ref, exact commit SHA, verification date, and verification mode.
- The published skill carries equivalent exact provenance in its defined metadata surfaces.
- A surface presented as verified never uses `source_commit: TBD`.
- Provenance mechanics remain outside rendered prose, while released defects, limitations, and safe alternatives appear in rendered guidance when developers need them.

ADR-0004 continues to govern deterministic detection and model-tiered auditing, except that this ADR supersedes its default-branch metadata-restamp semantics: default-branch movement may create next-release audit input, but released provenance changes only through release promotion. ADR-0005 through ADR-0007 continue to govern scheduling, update-track separation, and fail-closed operation. Detailed manifest schemas, promotion mechanics, migration sequencing, and automation changes belong in a follow-up specification and plan.

## Consequences

### Positive

- Public docs describe what developers can obtain and build against rather than what unreleased source suggests.
- Release, dependency, network, package, and runtime compatibility become one auditable contract.
- Known defects produce actionable guidance and upstream feedback instead of false confidence.
- Moving source remains monitored without silently changing the public product story.
- Exact provenance, fail-closed behavior, and the source-audit discipline from ADR-0003 are preserved.

### Negative / Trade-offs

- Documentation can intentionally lag merged source until a release is promoted.
- Maintaining a coherent manifest across multiple repositories and deployed-network dependencies adds release-management work.
- If release promotion is neglected, public docs can become stale even while drift detection is working.
- Capability-specific evidence and known-defect guidance require continuing judgement and maintenance.
- Some source-present bindings or APIs will remain undocumented as supported until an obtainable, verified route exists.

### Neutral / Operational

- Default-branch movement still matters: it starts impact assessment and prepares future documentation, but does not itself change released truth.
- Versioned previews may describe a target release when clearly separated from the default public docs.
- Accepted ADR-0003 remains immutable; this ADR's `Supersedes` field is the authoritative supersession link if this proposal is accepted.
- The exact release-manifest shape, migration from existing modes, release-promotion workflow, and automation updates require a separate reviewed specification and execution plan.

## Validation

This decision is satisfied when all of the following remain true:

- Every public installation or package identity resolves through its documented supported route from a clean environment.
- Every public verification record resolves to exact refs in one coherent release manifest, including shipped dependency refs where they carry documented behavior.
- Claims that depend on deployed Autonomi Network behavior are checked against a compatible deployed state.
- Getting-started and how-to journeys have evidence appropriate to the released route they recommend; missing evidence narrows or defers the claim.
- Known released defects and boundaries are represented in rendered guidance with safe alternatives where available, and material upstream defects are tracked.
- No verification record backing the default public rendered documentation or published developer skill uses `current-merged-truth`.
- `target-manifest` content never backs the default public surface; any published target content is isolated as a versioned preview and clearly labelled pre-release.
- Movement on an upstream default branch cannot by itself change public rendered prose, published skill guidance, or released verification SHAs.
- Promotion of a new release leaves an auditable record of artifacts, exact refs, compatibility, journey evidence, and accepted limitations.

Review triggers include changing the public default away from released truth, allowing merged source to advance public docs without release promotion, weakening artifact or usability evidence, or merging pre-release target content into the default public surface without clear preview isolation.

## Notes for AI-assisted work

AI tools helped draft this ADR. It remains **Proposed** until Jim Collinson reviews and accepts it. AI tools must not mark it Accepted. If accepted, future changes require a new superseding ADR rather than edits to this record.
