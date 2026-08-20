# ADR-0016: Released truth for public developer documentation

- **Status:** Proposed
- **Acceptance:** Prospective — pending review and explicit acceptance by Jim Collinson as decision owner.
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (public source-selection default, verification-mode set, and HEAD-based freshness semantics for default public docs and skill only); ADR-0004 (default-public source resolution, staleness detection, and provenance-advance semantics only); ADR-0006 (conditions under which metadata-only provenance may advance for default public artifacts only); ADR-0013 (default-branch stamp-refresh interpretation for published-skill provenance only); ADR-0014 (source and conditions for pure public-skill provenance refresh only)
- **Superseded by:** none
- **Related:** ADR-0005 through ADR-0007; ADR-0011 through ADR-0014; `planning/verification-workflow.md`; `planning/implementation-plan.md` §5; `planning/released-antd-v0.11.2-audit.md`; [WithAutonomi/ant-sdk issue #233](https://github.com/WithAutonomi/ant-sdk/issues/233)

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
6. **Require every public interface and journey to pass before a release set qualifies.** Rejected because an isolated defect would withdraw unaffected, evidence-backed interfaces even when the set still supplies every mandatory core outcome through complete routes.
7. **Qualify journeys locally within one coherent active release set, with a global mandatory-outcome baseline and global set fallback.** Chosen because it preserves unaffected journeys without permitting mixed versions or per-journey release fallback.

## Decision

Public rendered developer documentation and the published developer skill will describe **released truth** by default: one coherent active release set with journey-local qualification. A release set becomes active only when it passes the global release-set qualification layer, including the mandatory core-user-outcome baseline. Within that set, each developer journey receives its own evidence-backed status.

### One default-public state

There is exactly one default-public `released-truth` manifest.

- When a supported baseline exists, the manifest names exactly one active coherent release set. Every interface and journey uses the component identities in that set.
- When no eligible coherent set qualifies, the manifest records `no-supported-baseline` and names no supported release set.
- The public state never has per-journey incumbents, mixed release versions, or a journey that falls back to a component from an older or different set.
- An older-set fallback is global: it replaces the active set for every journey.
- `target-manifest` previews remain separate from the default-public state and cannot supply a fallback for any default-public journey.

### Verification modes and authorities

The verification model will retain exact per-surface provenance while changing its default:

- **`released-truth` is the default mode for public rendered documentation and the published developer skill.** Verification resolves every documented surface to exact refs in the single default-public released-truth manifest.
- **The release manifest represents a coherent product set, not a bag of latest tags.** Component versions, transitive refs that carry documented behavior, and deployed Autonomi Network compatibility must agree for the claims that depend on them.
- **The active released-truth manifest is the sole mutable machine-readable authority for active public release identities and journey support statuses.** Each promotion leaves an immutable promotion record as the evidence for why that manifest state was selected. Verification records and skill metadata identify the exact sources audited for their surfaces, but do not independently select a different active release or support status.
- **`target-manifest` remains an explicit pre-release, launch-hardening, or release-candidate mode.** It does not become the current public developer surface before release. If target content is published, it must be isolated and clearly labeled as a versioned preview rather than replacing the default docs.
- **`current-merged-truth` is retired as a verification mode for public rendered documentation and the published skill.** Moving default branches remain research inputs for drift detection, impact assessment, and next-release preparation. A merge can open an audit queue; it cannot silently advance rendered prose or verification SHAs.

### Release identities and candidate eligibility

An independently obtainable component is eligible for a `released-truth` candidate only through a stable or general-availability public distributable release identity published by its canonical publisher. That identity records its stable or general-availability publication state and canonical release URL or registry identity, immutable source identity, published artifacts and checksums where artifacts are distributed, and standard installation identity. Drafts; alpha, beta, release-candidate (RC), preview, nightly, canary, or equivalent prereleases; and branch builds are ineligible. A mutable installation alias is not a release identity and cannot establish candidate eligibility or support. Clean-install checks and default, supported, or recommended public installation commands must resolve through immutable version or digest selectors. These ineligible identities may appear only in isolated `target-manifest` preview mode, except that a mutable alias may also be mentioned as the unsupported, non-authoritative informational convenience described under promotion evidence.

A transitive shipped dependency has a different identity contract. It records the exact locked ref and an inspectable dependency path from the parent distributable release. It needs its own stable or general-availability release URL only when the public guidance presents it as independently obtainable. A transitive ref proves what a parent release shipped; it never by itself establishes that the dependency is independently installable or eligible as a released-truth candidate.

### Two qualification layers and complete routes

Qualification has two layers, evaluated in this order for each coherent candidate set:

1. **Journey qualification.** A journey has a stable identifier formed from `(interface, capability, material operation)`. Runtime and other journey evidence is keyed by that identifier. Each journey is classified as `supported`, `supported-with-known-limitation`, `unavailable`, or `deferred` within the candidate set. Missing mandatory evidence fails that journey; it cannot be inferred from source or schema presence. `supported-with-known-limitation` counts as qualified only inside a proven safe and reproducible boundary.
2. **Global release-set qualification.** The set must have stable or general-availability distributable identities, clean obtainability through every route presented as standard, provenance integrity, no artifact-wide safety or security disqualifier, coherent shipped dependencies, an identifiable compatible deployed Autonomi Network state for network-dependent claims, and a passing mandatory core-user-outcome baseline.

A **complete route** is a predeclared required set and sequence of qualified journeys under one approved interface, one coherent release set, and one compatible deployed-network state. Every required step must be `supported` or safely and reproducibly `supported-with-known-limitation`. Combining store through one interface with retrieve through another, or otherwise patching steps across interfaces, does not form a complete route and cannot pass an outcome.

The mandatory core-user-outcome baseline is committed and reviewed before candidate evaluation. It declares the mandatory outcomes and the approved complete-route shapes that may satisfy each outcome. At least one complete route must pass for every mandatory outcome. At minimum, one approved interface must complete store and retrieve end to end on the same candidate set and compatible network state. The baseline does not require every public interface to pass. Mandatory outcomes and route inventory beyond this minimum remain a separately reviewed baseline-policy detail for the later specification and plan.

Only qualified journeys and complete routes may be default or recommended. A `supported-with-known-limitation` journey may be default or recommended only within its proven safe and reproducible boundary. `unavailable` and `deferred` journeys cannot be default or recommended.

### Deterministic lifecycle and requalification

Candidate discovery reads canonical stable or general-availability publication state, independently of default-branch movement and prior watch-state observations. A stable release remains discoverable even when its source commit was already observed on a default branch before publication.

Eligible coherent release sets are ordered by a deterministic component-wise partial order. One set dominates another only when it is not older for every component under the component's immutable canonical release ordering and is newer for at least one component. A committed, predeclared, reviewed total extension with a fixed component-identity order and immutable release-identity tie-breakers extends that partial order across **all** eligible coherent release sets, not only the maximal non-dominated sets, and produces one newest-first candidate order. The incumbent is placed in that same order by its immutable release identities as the current baseline, including when changed inputs will disqualify it. Every promotion or requalification decision evaluates the ordered candidates and incumbent against all applicable qualification and promotion requirements and selects the first qualifying set. A failed maximal set does not stop evaluation: evaluation continues through the remaining maximal sets and then through older or dominated eligible sets until one qualifies or the sequence is exhausted.

For each set in that order, qualification first derives the complete journey-status matrix from one committed input snapshot and then applies global release-set qualification. The first globally qualifying set is selected. Discovery order, audit scheduling, and evidence-completion order cannot reorder evaluation or choose the result.

The incumbent is one global release set, not a collection of journey incumbents. It is requalified against the same journey and global requirements as every candidate. If it remains globally qualified, it stays active unless a strictly preferred candidate qualifies before it. A candidate at the same or a lower position cannot replace it. A strictly preferred candidate may promote despite an explicit regression in a non-baseline journey only when the manifest, rendered docs, and published skill atomically remove the affected recommendation and publish the journey's honest status, limitation, and alternative before promotion completes. Until that cross-surface downgrade is complete, the promotion has not passed. The selected set becomes the incumbent for later decisions, so a qualified incumbent cannot be displaced by an equally or less-preferred set and fallback cannot create a downgrade loop.

Promotion is not permanent. Every qualification-input change requalifies the affected journeys first, even when there is no new candidate, and then recomputes global release-set qualification. Triggers include artifact obtainability, withdrawal, or mutable-alias target movement; provenance-integrity evidence; applicable safety or security evidence; the mandatory core-outcome baseline definition or any complete-route result; newly discovered runtime or journey evidence; shipped-dependency identity, provenance, or compatibility evidence; and deployed-network identity or compatibility. A baseline-policy change remains a separate reviewed change and triggers requalification after approval. Default-branch movement alone neither qualifies nor disqualifies a candidate or incumbent unless it supplies changed evidence for one of these qualification inputs.

Artifact-wide and journey-local failures have different effects:

- Withdrawal or unobtainability of a required artifact, failed provenance integrity, an artifact-wide safety or security failure, an issue whose possible artifact-wide scope cannot be ruled out, incompatible deployed-network behavior, or loss of the final complete route for any mandatory outcome fails global qualification.
- A defect proven to be isolated to one or more journeys changes those journey statuses. If its precise journey scope remains uncertain but artifact-wide impact has been ruled out, every plausibly affected journey fails closed until the scope is established.
- An isolated journey failure can remain local, including failure of a journey that participated in a previously passing baseline route, when another approved complete route in the same active set still satisfies that mandatory outcome.
- If the active set fails global qualification, deterministic selection evaluates all eligible coherent sets in newest-first order. Selecting an older set replaces the release set for every journey; no journey remains on the newer set.
- The manifest records global `no-supported-baseline` only after all eligible coherent sets are exhausted and none supplies every mandatory outcome through the required complete routes. It must not fall back to moving source, a prerelease, a `target-manifest` preview, or an unevaluated artifact.

For example, if the SDK store journey fails but a CLI complete store-and-retrieve route still passes on the same active set and network state, SDK store becomes `unavailable` or `deferred` and is no longer recommended. CLI remains `supported`, the release set remains globally qualified, and the public surface does not fall back to an older SDK release.

### Promotion evidence

Every candidate release set requires a committed, machine-readable release manifest and an inspectable promotion record. Promotion fails closed if any mandatory field or evidence is absent. The record must contain, at minimum:

- **Immutable release identity and provenance integrity:** the public stable or general-availability distributable identity for every independently obtainable component, including canonical publication state and URL or registry identity, immutable tag object and peeled source commit where applicable, artifact names and checksums, publication timestamp, and the standard installation identity for every interface presented as installable; plus the exact locked ref and inspectable parent path for each transitive shipped dependency that carries documented behavior.
- **Clean obtainability:** a successful installation of each documented standard installation route in a fresh supported environment. Every clean-install check and every default, supported, or recommended command uses an immutable version or digest selector, and the evidence records the exact immutable identity obtained rather than only the command text. The check must prove that the package, binary, container, or source-install identity resolves to the intended Autonomi artifact and version; source-directory presence and an unrelated registry name do not pass. A mutable alias may be mentioned only as an explicitly unsupported, non-authoritative informational convenience alongside the exact immutable target observed. It cannot establish support and is never a default, supported, or recommended installation command. Movement of its target triggers requalification of whether the informational mention remains accurate, but successful requalification cannot promote the alias into a default, supported, or recommended route.
- **Release-set compatibility and deployed-network identity:** locked dependency evidence for the shipped set and, for network-dependent claims, the network environment, observation date, protocol or configuration anchor, and the most precise inspectable deployment identity available. If the deployed state cannot be identified precisely enough to reproduce a claim, that claim remains unverified and cannot be promoted.
- **Journey and runtime evidence:** a matrix keyed by stable journey identifier, mapping each covered `(interface, capability, material operation)` to its evidence and one of `supported`, `supported-with-known-limitation`, `unavailable`, or `deferred`. Source and schema inspection can establish contract existence, but cannot establish a runnable journey. Installation claims require clean-install evidence; getting-started and how-to claims require the complete documented journey to run; network-dependent behavior requires execution against the identified compatible network state.
- **Safety, limitations, and alternatives:** artifact-wide and journey-local safety and security evidence; known defects, affected versions and operations; upstream issue links for material defects; and a verified safe alternative where one exists. `supported-with-known-limitation` is permitted only when every required use remains safe and reproducible inside the stated boundary; otherwise the journey is `unavailable` or `deferred`.
- **Cross-surface consistency:** the manifest, public docs, and published developer skill must agree for every covered journey on status, known defect or limitation, safe alternative, and recommendation state. Matching refs alone is insufficient. A mismatch blocks promotion or requalification publication.
- **Objective selection:** the deterministic newest-first order of all eligible coherent release sets, each set's journey-status matrix and global qualification result, the complete routes that pass each mandatory outcome, the selected, retained, or `no-supported-baseline` result, and every explicit journey regression. Failed maximal sets remain in the record before evaluation continues to older or dominated sets.

The baseline is outcome-based, not an every-interface pass requirement. A safe alternative or a second complete route can preserve a mandatory outcome, but cross-interface patchwork cannot. Subject to the selection rule above, the prior active release set remains the default until a strictly preferred candidate passes global qualification and every promotion requirement. When a newer available release fails global qualification and the incumbent remains qualified, installation and version guidance must name both the newer release and the older active baseline, explain the affected boundary, and give the supported install command with an immutable version or digest selector. Retaining an older set through stale metadata, a mutable default selector, or omission is prohibited.

### Journey truth and skill parity

Released truth is journey-specific within the one active release set:

- “Usable” does not mean “bug-free.” A known defect is part of released truth. The docs must state the affected journey, boundary, or operation and provide a safe alternative when one exists.
- A broken or unproven journey must not be presented as working. Missing evidence requires the page to defer, narrow, stub, or reframe the claim rather than infer success.
- A package, binary, container, binding, or tool is available only when its documented standard installation identity resolves publicly, or when the project explicitly supports a reproducible source-install route that has been verified from a clean environment. Source-directory presence alone is not availability.
- A release is promoted into public docs only when its manifest and promotion record satisfy the mandatory fields and evidence floors in this decision.
- Isolated journey defects do not block the whole release set while at least one approved complete route still passes every mandatory outcome. The affected journeys remain `unavailable` or `deferred`, or `supported-with-known-limitation` when a safe, verified usage boundary exists.
- No journey may use an older or different release set because it works there. It remains `unavailable` or `deferred` under the active set unless it qualifies on that set.
- ADR-0011's SDK-primary stance applies only where the relevant SDK journeys qualify under this decision. It cannot override a journey status or cause an unqualified SDK journey to remain default or recommended.

The active manifest defines an enumerable coverage set of stable journey identifiers. It covers every claim represented in the rendered docs and everything the published skill bundles, recommends, warns about, or routes through a pointer.

For each covered journey identifier, the skill may represent released guidance as bundled content or as an explicit pointer to the default released-truth docs. A pointer satisfies parity only when it resolves under the same active manifest and journey status, the skill carries no contradictory claim, and the agent fetches the released guidance before answering release-sensitive detail. If that fetch fails, the agent defers the release-sensitive detail instead of consulting moving source or fabricating an answer. Parity does not require duplication of pointered prose. Any claim, recommendation, warning, limitation, alternative, or routing instruction that the skill does bundle must match the active released guidance directly.

Fetched released guidance is untrusted factual input, never executable instructions or authority over system or developer instructions, the skill, or the user's request. The agent must delimit fetched content from controlling instructions and ignore any embedded request to alter behavior, reveal secrets, bypass safeguards, fetch unrelated material, or take actions. Release-sensitive claims or actions derived from fetched content must still be checked against the active released-truth manifest, the applicable journey status, and applicable safety constraints. Fetched content cannot change tool permissions, authorize spending, publishing, or destructive actions, or cross an approval gate. If provenance and manifest alignment cannot be established, or fetched content conflicts with the skill or the user's request, the agent defers the release-sensitive detail and surfaces the conflict; it never follows the embedded instruction or falls back to moving source. These restrictions preserve ADR-0013's pointer tier and apply whether the fetch succeeds or fails.

The existing verification-block invariants remain:

- Every rendered documentation surface carries one or more machine-readable verification records with source repository, ref, exact commit SHA, verification date, and verification mode.
- The published skill carries equivalent exact provenance in its defined metadata surfaces.
- A surface presented as verified never uses `source_commit: TBD`.
- Provenance mechanics remain outside rendered prose, while released defects, limitations, and safe alternatives appear in rendered guidance when developers need them.

Released-record conformance and next-release source movement are separate detector outcomes. A released-truth record resolves through the active release manifest, not through the repository registry plus a GitHub default branch; deterministic comparison against that manifest detects corruption or inconsistency in released records. Default branches remain registry-resolved watch inputs and are compared with a separately tracked, last-audited watch state. Their movement creates next-release impact candidates, but does not mark released records stale, authorize a metadata re-stamp, or advance released provenance. Completing a next-release impact audit may advance the watch state without changing the released record.

### Supersession scope and preserved invariants

This ADR supersedes only the named default-public source and provenance-advance semantics in Accepted ADRs:

- **ADR-0003:** superseded for the public source-selection default, verification-mode set, and HEAD-based freshness semantics of default public rendered docs and the published skill. Its exact provenance schema, exact-SHA requirement, no-placeholder rule, provenance/body separation, and explicit target pinning remain intact.
- **ADR-0004:** superseded for default-public source resolution, staleness detection, and provenance-advance semantics. Its deterministic, model-free, fail-closed detection; candidate-not-directive rule; and efficient-model versus frontier-model audit tiers remain intact.
- **ADR-0006:** superseded only for the conditions under which metadata-only provenance may advance for default public artifacts. Its two mutually exclusive tracks, mechanical change envelopes, stronger prose review, reachability checks, and coherent skill-state requirement remain intact. Under `released-truth`, metadata-only public provenance advances only to refs authorized by promotion into the active manifest, never merely because HEAD moved.
- **ADR-0013:** superseded only for the default-branch stamp-refresh interpretation of published-skill provenance. Its three-part freshness defense, pointer content tier, runtime version check, and stable-URL contract remain intact. A skill stamp refresh now means conformance to the active released-truth manifest, not conformance to moving HEAD.
- **ADR-0014:** superseded only for the source and conditions of a pure public-skill provenance refresh. Its shared source-audit workflow, `feeds_skills` relationship, distinct metadata responsibilities, and coherent-state requirement remain intact. Pure skill provenance may advance only with a released-truth promotion. The content version and release history may remain unchanged only when bundled claims, recommendations, warnings, limitations, alternatives, and pointers remain unchanged.

ADR-0005, ADR-0007, and ADR-0011 remain intact. ADR-0011's interface stance is constrained only by the evidence-backed recommendation rule above. Detailed journey-identifier schema, route membership and sequencing, dependency mapping, propagation and atomic-publication mechanics, adapters, scheduling, baseline inventory beyond the minimum, detailed manifest and watch-state schemas, exact comparator mechanics, promotion and detection mechanics, migration sequencing, and automation changes belong in a follow-up reviewed specification and plan.

## Consequences

### Positive

- Public docs describe what developers can obtain and build against rather than what unreleased source suggests.
- Release, dependency, network, package, and runtime compatibility become one auditable contract.
- Known defects produce actionable guidance and upstream feedback instead of false confidence.
- Isolated journey defects preserve unaffected interfaces when another complete route continues to satisfy the mandatory outcome.
- Moving source remains monitored without silently changing the public product story.
- Exact provenance, fail-closed behavior, and the source-audit discipline from ADR-0003 are preserved.

### Negative / Trade-offs

- Documentation can intentionally lag merged source until a release is promoted.
- Maintaining a coherent manifest across multiple repositories and deployed-network dependencies adds release-management work.
- If promotion or incumbent requalification is neglected, public docs can become stale even while source-movement detection is working.
- Journey-specific evidence and known-defect guidance require continuing judgment and maintenance.
- Some source-present bindings or APIs will remain undocumented as supported until an obtainable, verified route exists.
- A newer qualifying set can regress an optional journey after its recommendation is atomically withdrawn and its status is published honestly.
- There is no old-release fallback for one failed journey; a journey that works only on an older set remains unavailable under the active newer set.
- Stable journey identifiers, complete-route dependency mapping, and atomic manifest/docs/skill updates add policy and implementation complexity.

### Neutral / Operational

- Default-branch movement still matters: it starts impact assessment and prepares future documentation, but does not itself change released truth.
- Versioned previews may describe a target release when clearly separated from the default public docs.
- Journey status may change without changing the active release-set identity.
- `unavailable` and `deferred` are journey-local states; `no-supported-baseline` is a global public state.
- Accepted ADRs remain immutable; this ADR's `Supersedes` field is the authoritative supersession link if this proposal is accepted.
- The deferred mechanics and inventories named above require a separate reviewed specification and execution plan.

## Validation

This decision is satisfied when all of the following remain true:

- Every clean-install check and every default, supported, or recommended public installation command uses an immutable version or digest selector, resolves through its documented supported route from a clean environment, and records the exact immutable identity obtained.
- Candidate discovery rejects drafts, prereleases of every named class, and branch builds; a mutable alias cannot establish eligibility or support.
- A stable or general-availability release remains discoverable from canonical publication state when its source commit was already observed on HEAD before publication.
- Shuffling API, registry, or filesystem discovery results does not change the eligible sets, the newest-first order over all eligible sets, or the selection outcome.
- Incomparable sets resolve identically through the committed total extension and its fixed component order and immutable release-identity tie-breakers; after each failed maximal set, evaluation continues in that order through older or dominated sets and selects the first qualifying set.
- Replaying the same committed qualification-input snapshot with a different audit schedule or evidence-completion order produces the same evaluation order and selected, retained, or no-supported-baseline outcome.
- Exactly one default-public manifest names exactly one active coherent release set, or records `no-supported-baseline` and names no supported set. Every public verification record resolves to that state, including shipped dependency refs where they carry documented behavior.
- Every release promotion record contains all seven minimum evidence groups required by this decision and identifies the predeclared mandatory core-user-outcome baseline.
- For each eligible set in deterministic newest-first order, the journey-status matrix is derived before global qualification, and the first globally qualifying set is selected.
- Candidate and incumbent qualification apply the same stable or general-availability identity, clean-obtainability, provenance-integrity, artifact-wide safety and security, coherent-dependency, deployed-network compatibility, and mandatory core-outcome requirements.
- Changing any qualification input requalifies affected journeys before recomputing the incumbent's global qualification, without requiring a new candidate. Validation changes each trigger class independently: obtainability or alias target; provenance integrity; safety or security evidence; an approved baseline definition or a complete-route result; runtime or journey evidence; shipped-dependency evidence; and deployed-network identity or compatibility.
- An artifact-wide issue, or uncertainty about whether an issue is artifact-wide, disqualifies the set globally. When artifact-wide impact is ruled out but journey scope remains uncertain, every plausibly affected journey fails closed until its scope is established.
- A mutable alias, if mentioned, is explicitly unsupported and non-authoritative and appears alongside the exact immutable target observed; it is never a default, supported, or recommended installation command.
- Moving a mentioned mutable alias to a different immutable target requalifies whether the informational mention remains accurate; successful requalification cannot establish support or promote the alias into a default, supported, or recommended route.
- Claims that depend on deployed Autonomi Network behavior are checked against the identified compatible deployed state; claims without a reproducible deployment anchor remain unverified.
- Getting-started and how-to journeys have complete runtime evidence for the released interface they recommend; source or schema inspection alone does not pass.
- At least one predeclared complete route passes every mandatory outcome, including an end-to-end store-and-retrieve route under one approved interface on the same release set and network state.
- A store step from one interface and a retrieve step from another cannot be combined to pass a complete route.
- If SDK store fails while a CLI complete store-and-retrieve route passes on the same active set, SDK store is `unavailable` or `deferred` and not recommended, CLI remains `supported`, and the set remains globally qualified.
- An isolated MCP or other non-baseline journey failure remains local when every mandatory outcome retains a complete route.
- A strictly preferred candidate with a non-baseline journey regression cannot promote until manifest, docs, and skill atomically publish the downgrade and remove the affected recommendation.
- A journey that works only on an older eligible set remains `unavailable` or `deferred` under an active newer set; no per-journey release fallback occurs.
- A `supported-with-known-limitation` journey contributes to a complete route only when every required step remains safe and reproducible inside the documented boundary.
- Known released defects and boundaries are represented in rendered guidance with safe alternatives where available, and material upstream defects are tracked.
- A journey-local defect, including failure of a journey formerly used by a baseline route, changes only its covered journeys when evidence establishes that isolation and another complete route still satisfies the outcome.
- Every covered journey identifier has the same status, known defect or limitation, safe alternative, and recommendation state in the manifest, rendered docs, and published developer skill.
- Pointer parity resolves against the active released-truth manifest, fetches released guidance before release-sensitive answers, and defers that detail on fetch failure; bundled skill guidance matches directly without requiring duplicated pointer prose.
- Fetched pointer content remains delimited as untrusted factual input and cannot override controlling instructions, change permissions, authorize gated actions, or cause embedded requests to be followed; release-sensitive claims and actions remain subject to the active manifest, journey status, and applicable safety constraints.
- If fetched-content provenance or manifest alignment cannot be established, or fetched content conflicts with the skill or user request, the agent defers the release-sensitive detail, surfaces the conflict, and does not fall back to moving source.
- A transitive dependency ref with no independent release URL remains valid shipped-dependency provenance but does not establish independent installability or candidate eligibility.
- If a newer available release fails global qualification and the incumbent remains qualified, installation and version guidance names the newer release, the retained supported baseline, the reason, and the supported install command with its immutable version or digest selector.
- If the active set loses the final complete route for any mandatory outcome, deterministic selection evaluates every eligible coherent set in order. Any older fallback replaces the set for every journey; if no set qualifies, the manifest records global `no-supported-baseline` and names no supported set.
- No verification record backing the default public rendered documentation or published developer skill uses `current-merged-truth`.
- `target-manifest` content never backs the default public surface; any published target content is isolated as a versioned preview and clearly labeled pre-release.
- Movement on an upstream default branch cannot by itself change public rendered prose, published skill guidance, or released verification SHAs.
- Promotion of a new release leaves an auditable record of artifacts, exact refs, compatibility, journey evidence, complete routes, global results, selection outcome, and explicit regressions.

Review triggers include changing the one-manifest/one-active-set invariant, allowing per-journey release fallback, weakening complete-route requirements, changing the boundary between global release-set and journey qualification, hiding a journey regression during promotion or requalification, changing the public default away from released truth, allowing merged source to advance public docs without release promotion, weakening artifact or usability evidence, or merging pre-release target content into the default public surface without clear preview isolation.

## Notes for AI-assisted work

AI tools helped draft this ADR. It remains **Proposed** until Jim Collinson reviews and accepts it. AI tools must not mark it Accepted. If accepted, future changes require a new superseding ADR rather than edits to this record.
