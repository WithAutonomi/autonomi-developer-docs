# ADR-0016: Released truth for public developer documentation

- **Status:** Proposed
- **Acceptance:** Prospective — pending review and explicit acceptance by Jim Collinson as decision owner.
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (source-selection default and verification-mode set only); ADR-0004 (source resolution and drift semantics for the default public surface only)
- **Superseded by:** none
- **Related:** ADR-0005 through ADR-0007; ADR-0012 through ADR-0014; `planning/verification-workflow.md`; `planning/implementation-plan.md` §5; `planning/released-antd-v0.11.2-audit.md`; [WithAutonomi/ant-sdk issue #233](https://github.com/WithAutonomi/ant-sdk/issues/233)

## Context

ADR-0003 made `current-merged-truth` the default source for public developer documentation. This prevented speculative documentation of unmerged branches, but it did not prevent a different failure: a default branch can contain code that has not been released, is not available through a supported installation route, is incompatible with the deployed Autonomi Network, or has not been proven usable through the interface the page recommends.

That gap can make rendered documentation describe what source code intends rather than what a developer can obtain and build against. The `antd` v0.11.2 audit exposed the practical consequences. The stable release corrected ordinary Merkle writes, while several released binding and Model Context Protocol (MCP) external-signing paths remained defective or unavailable. The gRPC service also rejects a valid all-already-stored finalization and consumes its upload identifier, tracked in `ant-sdk` issue #233. Neither moving source nor the existence of an API shape is enough to call a developer journey available.

The inspectable audit in `planning/released-antd-v0.11.2-audit.md` records the exact release refs, artifact identities, continuous integration (CI) evidence, behavior matrix, known defects, and evidence gaps that motivated this proposal. It is a dated evidence snapshot, not a replacement for canonical release artifacts or source. Its policy recommendation predates this ADR and is preserved as historical context, not as current authority.

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

Public rendered developer documentation and the published developer skill will describe **released truth** by default: the newest coherent release set that passes the mandatory public-baseline evidence below. The release set must be publicly obtainable through documented standard routes, compatible with its shipped dependencies and the deployed Autonomi Network for the claims made, and supported by capability-specific evidence.

The verification model will retain exact per-surface provenance while changing its default:

- **`released-truth` is the default mode for public rendered documentation and the published developer skill.** Verification resolves every documented surface to exact refs in one machine-readable release manifest. A ref may identify a component's own release or the exact dependency ref shipped by another released product.
- **The release manifest represents a coherent product set, not a bag of latest tags.** Component versions, transitive refs that carry documented behavior, and deployed Autonomi Network compatibility must agree for the claims that depend on them.
- **`target-manifest` remains an explicit pre-release, launch-hardening, or release-candidate mode.** It does not become the current public developer surface before release. If target content is published, it must be isolated and clearly labeled as a versioned preview rather than replacing the default docs.
- **`current-merged-truth` is retired as a verification mode for public rendered documentation and the published skill.** Moving default branches remain research inputs for drift detection, impact assessment, and next-release preparation. A merge can open an audit queue; it cannot silently advance rendered prose or verification SHAs.

Every candidate release set requires a committed, machine-readable release manifest and an inspectable promotion record. Promotion fails closed if any mandatory field or evidence is absent. The record must contain, at minimum:

- **Immutable release identity:** the public version and release URL for each component, immutable tag object and peeled source commit where applicable, exact shipped dependency refs, artifact names and checksums, publication timestamp, and the standard installation identity for every interface presented as installable.
- **Clean obtainability:** a successful installation of each documented standard installation route in a fresh supported environment. The check must prove that the package, binary, container, or source-install identity resolves to the intended Autonomi artifact and version; source-directory presence and an unrelated registry name do not pass.
- **Release-set compatibility and deployed-network identity:** locked dependency evidence for the shipped set and, for network-dependent claims, the network environment, observation date, protocol or configuration anchor, and the most precise inspectable deployment identity available. If the deployed state cannot be identified precisely enough to reproduce a claim, that claim remains unverified and cannot be promoted.
- **Capability and runtime evidence:** a matrix mapping each public interface, capability, and material operation to its evidence and one of `supported`, `supported-with-known-limitation`, `unavailable`, or `deferred`. Source and schema inspection can establish contract existence, but cannot establish a runnable journey. Installation claims require clean-install evidence; getting-started and how-to claims require the complete documented journey to run; network-dependent behavior requires execution against the identified compatible network state.
- **Known limitations and alternatives:** known defects, affected versions and operations, upstream issue links for material defects, and a verified safe alternative where one exists. `supported-with-known-limitation` is permitted only when the supported usage remains safe and reproducible; otherwise the capability is `unavailable` or `deferred`.
- **Cross-surface consistency:** the public docs and published developer skill must map every covered interface and capability to the same support status, known defect or limitation, and safe alternative. Matching refs alone is insufficient. A mismatch blocks promotion.
- **Objective supported-baseline retention:** the incumbent supported release set, the candidate release set, each result against the predeclared mandatory public baseline, and the resulting promote-or-retain outcome. A candidate replaces the incumbent only when every mandatory promotion requirement passes. If any requirement fails, the incumbent remains the supported default only for journeys where it continues to satisfy applicable obtainability, safety and security, deployed-network compatibility, and mandatory baseline requirements. A withdrawn or unobtainable, unsafe or insecure, incompatible, or baseline-noncompliant incumbent is disqualified for the affected journey. If no qualifying incumbent exists, the candidate remains unpromoted, affected guidance is narrowed or withdrawn, and public guidance explicitly states that no supported baseline exists for that journey until a released candidate passes.

The mandatory public baseline is committed and reviewed before a candidate audit; changing it is a separate reviewed policy change, not part of producing promotion evidence. It includes, at minimum, a clean standard installation plus successful store and retrieve journeys for every interface the public docs present as the default or recommended way to use Autonomi. A safe alternative may preserve a non-baseline capability, but it cannot waive a mandatory baseline failure. Subject to the incumbent qualification rule above, the prior supported release set remains the default until a candidate passes every promotion requirement. When a newer available release is unsuitable and the incumbent remains qualified, installation and version guidance must name both that newer release and the older supported baseline, explain the affected boundary, and give the supported install command; retaining an older baseline through stale metadata or omission is prohibited. When the incumbent is disqualified, the affected guidance must instead narrow or withdraw the journey and state that no supported baseline exists until a released candidate passes.

Released truth is capability-specific and evidence-based:

- “Usable” does not mean “bug-free.” A known defect is part of released truth. The docs must state the affected route, boundary, or operation and provide a safe alternative when one exists.
- A broken or unproven route must not be presented as working. Missing evidence requires the page to defer, narrow, stub, or reframe the claim rather than infer success.
- A package, binary, container, binding, or tool is available only when its documented standard installation identity resolves publicly, or when the project explicitly supports a reproducible source-install route that has been verified from a clean environment. Source-directory presence alone is not availability.
- A release is promoted into public docs only when its manifest and promotion record satisfy the mandatory fields and evidence floors in this decision.
- Non-baseline capabilities do not block the whole release set when their status and guidance are honest. They remain `unavailable` or `deferred`, or `supported-with-known-limitation` when a safe, verified usage boundary exists.

The existing verification-block invariants remain:

- Every rendered documentation surface carries one or more machine-readable verification records with source repository, ref, exact commit SHA, verification date, and verification mode.
- The published skill carries equivalent exact provenance in its defined metadata surfaces.
- A surface presented as verified never uses `source_commit: TBD`.
- Provenance mechanics remain outside rendered prose, while released defects, limitations, and safe alternatives appear in rendered guidance when developers need them.

ADR-0004 continues to govern deterministic detection, fail-closed behavior, and model-tiered auditing, but this ADR supersedes its source-resolution and drift semantics for the default public surface. Released-record conformance and next-release source movement are separate detector outcomes. A released-truth record resolves through the active release manifest, not through the repository registry plus a GitHub default branch; deterministic comparison against that manifest detects corruption or inconsistency in released records. Default branches remain registry-resolved watch inputs and are compared with a separately tracked, last-audited watch state. Their movement creates next-release impact candidates, but does not mark released records stale, authorize a metadata re-stamp, or advance released provenance. Completing a next-release impact audit may advance the watch state without changing the released record. Metadata-only and prose audit tiers remain, but public SHAs change only through release promotion. ADR-0005 through ADR-0007 continue to govern scheduling, update-track separation, and fail-closed operation. Detailed manifest and watch-state schemas, promotion and detection mechanics, migration sequencing, and automation changes belong in a follow-up specification and plan.

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
- Capability-specific evidence and known-defect guidance require continuing judgment and maintenance.
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
- Every release promotion record contains all seven minimum evidence groups required by this decision and identifies the predeclared mandatory public baseline.
- Claims that depend on deployed Autonomi Network behavior are checked against the identified compatible deployed state; claims without a reproducible deployment anchor remain unverified.
- Getting-started and how-to journeys have complete runtime evidence for the released interface they recommend; source or schema inspection alone does not pass.
- Known released defects and boundaries are represented in rendered guidance with safe alternatives where available, and material upstream defects are tracked.
- Every covered capability has the same status, known defect or limitation, and safe alternative in the rendered docs and published developer skill.
- If a newer available release fails the mandatory baseline and the incumbent remains qualified, installation and version guidance names the newer release, the retained supported baseline, the reason, and the supported install command.
- If an incumbent becomes withdrawn or unobtainable, unsafe or insecure, incompatible with the deployed Autonomi Network, or noncompliant with the mandatory baseline, affected guidance narrows or withdraws the journey and states that no supported baseline exists until a released candidate passes.
- No verification record backing the default public rendered documentation or published developer skill uses `current-merged-truth`.
- `target-manifest` content never backs the default public surface; any published target content is isolated as a versioned preview and clearly labeled pre-release.
- Movement on an upstream default branch cannot by itself change public rendered prose, published skill guidance, or released verification SHAs.
- Promotion of a new release leaves an auditable record of artifacts, exact refs, compatibility, journey evidence, and accepted limitations.

Review triggers include changing the public default away from released truth, allowing merged source to advance public docs without release promotion, weakening artifact or usability evidence, or merging pre-release target content into the default public surface without clear preview isolation.

## Notes for AI-assisted work

AI tools helped draft this ADR. It remains **Proposed** until Jim Collinson reviews and accepts it. AI tools must not mark it Accepted. If accepted, future changes require a new superseding ADR rather than edits to this record.
