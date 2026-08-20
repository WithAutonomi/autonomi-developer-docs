# ADR-0016: Released truth for public developer documentation

- **Status:** Proposed
- **Acceptance:** Prospective — pending review and explicit acceptance by Jim Collinson as decision owner.
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (public source-selection default, verification-mode set, and HEAD-based freshness semantics for default public docs and skill only); ADR-0004 (default-public source resolution, staleness detection, and provenance-advance semantics only); ADR-0006 (conditions under which metadata-only provenance may advance for default public artifacts only); ADR-0013 (default-branch stamp-refresh interpretation for published-skill provenance only); ADR-0014 (source and conditions for pure public-skill provenance refresh only)
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

### Verification modes and authorities

The verification model will retain exact per-surface provenance while changing its default:

- **`released-truth` is the default mode for public rendered documentation and the published developer skill.** Verification resolves every documented surface to exact refs in one machine-readable active released-truth manifest.
- **The release manifest represents a coherent product set, not a bag of latest tags.** Component versions, transitive refs that carry documented behavior, and deployed Autonomi Network compatibility must agree for the claims that depend on them.
- **The active released-truth manifest is the sole mutable machine-readable authority for active public release identities and capability support statuses.** Each promotion leaves an immutable promotion record as the evidence for why that manifest state was selected. Verification records and skill metadata identify the exact sources audited for their surfaces, but do not independently select a different active release or support status.
- **`target-manifest` remains an explicit pre-release, launch-hardening, or release-candidate mode.** It does not become the current public developer surface before release. If target content is published, it must be isolated and clearly labeled as a versioned preview rather than replacing the default docs.
- **`current-merged-truth` is retired as a verification mode for public rendered documentation and the published skill.** Moving default branches remain research inputs for drift detection, impact assessment, and next-release preparation. A merge can open an audit queue; it cannot silently advance rendered prose or verification SHAs.

### Release identities and candidate eligibility

An independently obtainable component is eligible for a `released-truth` candidate only through a stable or general-availability public distributable release identity published by its canonical publisher. That identity records its stable or general-availability publication state and canonical release URL or registry identity, immutable source identity, published artifacts and checksums where artifacts are distributed, and standard installation identity. Drafts; alpha, beta, release-candidate (RC), preview, nightly, canary, or equivalent prereleases; and branch builds are ineligible. A mutable installation alias is not a release identity and cannot establish candidate eligibility or support. Clean-install checks and default, supported, or recommended public installation commands must resolve through immutable version or digest selectors. These ineligible identities may appear only in isolated `target-manifest` preview mode, except that a mutable alias may also be mentioned as the unsupported, non-authoritative informational convenience described under promotion evidence.

A transitive shipped dependency has a different identity contract. It records the exact locked ref and an inspectable dependency path from the parent distributable release. It needs its own stable or general-availability release URL only when the public guidance presents it as independently obtainable. A transitive ref proves what a parent release shipped; it never by itself establishes that the dependency is independently installable or eligible as a released-truth candidate.

### Deterministic lifecycle and symmetric qualification

Candidate discovery reads canonical stable or general-availability publication state, independently of default-branch movement and prior watch-state observations. A stable release remains discoverable even when its source commit was already observed on a default branch before publication.

Eligible coherent release sets are ordered by a deterministic component-wise partial order. One set dominates another only when it is not older for every component under the component's immutable canonical release ordering and is newer for at least one component. A committed, predeclared, reviewed total extension with a fixed component-identity order and immutable release-identity tie-breakers extends that partial order across **all** eligible coherent release sets, not only the maximal non-dominated sets, and produces one newest-first candidate order. The incumbent is placed in that same order by its immutable release identities as the current baseline, including when changed inputs will disqualify it. Every promotion or requalification decision evaluates the ordered candidates and incumbent against all applicable qualification and promotion requirements and selects the first qualifying set. A failed maximal set does not stop evaluation: evaluation continues through the remaining maximal sets and then through older or dominated eligible sets until one qualifies or the sequence is exhausted.

The existing incumbent participates in every decision as the current baseline and is requalified against the same inputs as the candidates. If it remains qualified, it is the first qualifying set unless a candidate that is strictly preferred under the committed total extension qualifies before it; a candidate at the same or a lower position cannot replace it. If the incumbent is disqualified, ordered evaluation continues until the first qualifying eligible set, including a set older than the former incumbent, is found. The selected set becomes the incumbent for later decisions, so a qualified incumbent cannot be displaced by an equally or less-preferred set and the fallback cannot create a downgrade loop.

Candidate and incumbent qualification is symmetric. Both must independently pass applicable obtainability, provenance-integrity, safety and security, deployed-network identity and compatibility, and mandatory public-baseline requirements. A decision uses one committed snapshot of qualification inputs; discovery order, audit scheduling, and evidence-completion order cannot reorder evaluation or choose the result. Missing mandatory evidence fails qualification for that decision. Exact snapshot, enumeration, and comparator mechanics belong in the later specification.

Promotion is not permanent. The incumbent is requalified during every promotion decision and whenever **any** qualification input changes, even when there is no new candidate. Triggers include artifact obtainability, withdrawal, or mutable-alias target movement; provenance-integrity evidence; applicable safety or security evidence; the mandatory public-baseline definition or any baseline result; newly discovered runtime or capability evidence that can affect a supported journey; shipped-dependency identity, provenance, or compatibility evidence; and deployed-network identity or compatibility. A mandatory-baseline policy change remains a separate reviewed change and triggers requalification after approval. Default-branch movement alone neither qualifies nor disqualifies a candidate or incumbent unless it supplies changed evidence for one of these qualification inputs.

Artifact-wide disqualifiers and capability-local defects have different scope. Withdrawal or unobtainability, failed provenance integrity, an artifact-wide safety or security failure, or incompatible deployed-network behavior disqualifies the artifact for every affected journey. A defect confined to a non-baseline capability may leave the rest of a qualified release set active when the affected capability is classified honestly and its remaining guidance is safe. If changed qualification evidence does not establish its scope, qualification fails closed for every plausibly affected journey until the scope is established.

If no eligible set qualifies and no incumbent remains qualified, the public surface has no supported baseline. It must not fall back to moving source, a prerelease, or any unevaluated artifact. Affected guidance is narrowed or withdrawn and states that no supported baseline exists.

### Promotion evidence

Every candidate release set requires a committed, machine-readable release manifest and an inspectable promotion record. Promotion fails closed if any mandatory field or evidence is absent. The record must contain, at minimum:

- **Immutable release identity:** the public stable or general-availability distributable identity for every independently obtainable component, including canonical publication state and URL or registry identity, immutable tag object and peeled source commit where applicable, artifact names and checksums, publication timestamp, and the standard installation identity for every interface presented as installable; plus the exact locked ref and inspectable parent path for each transitive shipped dependency that carries documented behavior.
- **Clean obtainability:** a successful installation of each documented standard installation route in a fresh supported environment. Every clean-install check and every default, supported, or recommended command uses an immutable version or digest selector, and the evidence records the exact immutable identity obtained rather than only the command text. The check must prove that the package, binary, container, or source-install identity resolves to the intended Autonomi artifact and version; source-directory presence and an unrelated registry name do not pass. A mutable alias may be mentioned only as an explicitly unsupported, non-authoritative informational convenience alongside the exact immutable target observed. It cannot establish support and is never a default, supported, or recommended installation command. Movement of its target triggers requalification of whether the informational mention remains accurate, but successful requalification cannot promote the alias into a default, supported, or recommended route.
- **Release-set compatibility and deployed-network identity:** locked dependency evidence for the shipped set and, for network-dependent claims, the network environment, observation date, protocol or configuration anchor, and the most precise inspectable deployment identity available. If the deployed state cannot be identified precisely enough to reproduce a claim, that claim remains unverified and cannot be promoted.
- **Capability and runtime evidence:** a matrix mapping each public interface, capability, and material operation to its evidence and one of `supported`, `supported-with-known-limitation`, `unavailable`, or `deferred`. Source and schema inspection can establish contract existence, but cannot establish a runnable journey. Installation claims require clean-install evidence; getting-started and how-to claims require the complete documented journey to run; network-dependent behavior requires execution against the identified compatible network state.
- **Known limitations and alternatives:** known defects, affected versions and operations, upstream issue links for material defects, and a verified safe alternative where one exists. `supported-with-known-limitation` is permitted only when the supported usage remains safe and reproducible; otherwise the capability is `unavailable` or `deferred`.
- **Cross-surface consistency:** the public docs and published developer skill must map the enumerable coverage set defined below to the same support status, known defect or limitation, and safe alternative. Matching refs alone is insufficient. A mismatch blocks promotion.
- **Objective supported-baseline retention:** the incumbent supported release set, the deterministic newest-first order of all eligible coherent release sets, every evaluated set's result against all qualification and promotion requirements and the predeclared mandatory public baseline, and the resulting select, retain, or no-supported-baseline outcome. Failed maximal sets remain in the record before evaluation continues to older or dominated sets. A candidate replaces a qualified incumbent only when it is strictly preferred and every mandatory promotion requirement passes. The incumbent remains the supported default only for journeys where it continues to satisfy applicable obtainability, provenance-integrity, safety and security, shipped-dependency, deployed-network compatibility, and mandatory-baseline requirements. A disqualified incumbent cannot be retained. If the ordered sequence contains no qualifying set and no incumbent remains qualified, affected guidance is narrowed or withdrawn, and public guidance explicitly states that no supported baseline exists for that journey until a released candidate passes.

The mandatory public baseline is committed and reviewed before a candidate audit; changing it is a separate reviewed policy change, not part of producing promotion evidence. It includes, at minimum, a clean standard installation plus successful store and retrieve journeys for every interface the public docs present as the default or recommended way to use Autonomi. A safe alternative may preserve a non-baseline capability, but it cannot waive a mandatory baseline failure. Subject to the incumbent qualification rule above, the prior supported release set remains the default until a strictly preferred candidate passes every promotion requirement. When a newer available release is unsuitable and the incumbent remains qualified, installation and version guidance must name both that newer release and the older supported baseline, explain the affected boundary, and give the supported install command with an immutable version or digest selector; retaining an older baseline through stale metadata, a mutable default selector, or omission is prohibited. When the incumbent is disqualified, the affected guidance must instead narrow or withdraw the journey and state that no supported baseline exists until an eligible released set passes.

### Capability truth and skill parity

Released truth is capability-specific and evidence-based:

- “Usable” does not mean “bug-free.” A known defect is part of released truth. The docs must state the affected route, boundary, or operation and provide a safe alternative when one exists.
- A broken or unproven route must not be presented as working. Missing evidence requires the page to defer, narrow, stub, or reframe the claim rather than infer success.
- A package, binary, container, binding, or tool is available only when its documented standard installation identity resolves publicly, or when the project explicitly supports a reproducible source-install route that has been verified from a clean environment. Source-directory presence alone is not availability.
- A release is promoted into public docs only when its manifest and promotion record satisfy the mandatory fields and evidence floors in this decision.
- Non-baseline capabilities do not block the whole release set when their status and guidance are honest. They remain `unavailable` or `deferred`, or `supported-with-known-limitation` when a safe, verified usage boundary exists.

The active manifest defines an enumerable coverage set of stable interface, capability, and material-operation identifiers. It covers every claim represented in the rendered docs and everything the published skill bundles, recommends, warns about, or routes through a pointer.

For each covered identifier, the skill may represent released guidance as bundled content or as an explicit pointer to the default released-truth docs. A pointer satisfies parity only when it resolves under the same active manifest, the skill carries no contradictory claim, and the agent fetches the released guidance before answering release-sensitive detail. If that fetch fails, the agent defers the release-sensitive detail instead of consulting moving source or fabricating an answer. Parity does not require duplication of pointered prose. Any claim, recommendation, warning, limitation, alternative, or routing instruction that the skill does bundle must match the active released guidance directly.

Fetched released guidance is untrusted factual input, never executable instructions or authority over system or developer instructions, the skill, or the user's request. The agent must delimit fetched content from controlling instructions and ignore any embedded request to alter behavior, reveal secrets, bypass safeguards, fetch unrelated material, or take actions. Release-sensitive claims or actions derived from fetched content must still be checked against the active released-truth manifest, the applicable capability status, and applicable safety constraints. Fetched content cannot change tool permissions, authorize spending, publishing, or destructive actions, or cross an approval gate. If provenance and manifest alignment cannot be established, or fetched content conflicts with the skill or the user's request, the agent defers the release-sensitive detail and surfaces the conflict; it never follows the embedded instruction or falls back to moving source. These restrictions preserve ADR-0013's pointer tier and apply whether the fetch succeeds or fails.

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

ADR-0005 and ADR-0007 remain fully intact. Scheduling, adapters, detailed manifest and watch-state schemas, exact comparator mechanics, promotion and detection mechanics, migration sequencing, and automation changes belong in a follow-up specification and plan.

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
- If promotion or incumbent requalification is neglected, public docs can become stale even while source-movement detection is working.
- Capability-specific evidence and known-defect guidance require continuing judgment and maintenance.
- Some source-present bindings or APIs will remain undocumented as supported until an obtainable, verified route exists.

### Neutral / Operational

- Default-branch movement still matters: it starts impact assessment and prepares future documentation, but does not itself change released truth.
- Versioned previews may describe a target release when clearly separated from the default public docs.
- Accepted ADRs remain immutable; this ADR's `Supersedes` field is the authoritative supersession link if this proposal is accepted.
- The exact release-manifest shape, comparator, migration from existing modes, release-promotion workflow, and automation updates require a separate reviewed specification and execution plan.

## Validation

This decision is satisfied when all of the following remain true:

- Every clean-install check and every default, supported, or recommended public installation command uses an immutable version or digest selector, resolves through its documented supported route from a clean environment, and records the exact immutable identity obtained.
- Candidate discovery rejects drafts, prereleases of every named class, and branch builds; a mutable alias cannot establish eligibility or support.
- A stable or general-availability release remains discoverable from canonical publication state when its source commit was already observed on HEAD before publication.
- Shuffling API, registry, or filesystem discovery results does not change the eligible sets, the newest-first order over all eligible sets, or the selection outcome.
- Incomparable sets resolve identically through the committed total extension and its fixed component order and immutable release-identity tie-breakers; after each failed maximal set, evaluation continues in that order through older or dominated sets and selects the first qualifying set.
- Replaying the same committed qualification-input snapshot with a different audit schedule or evidence-completion order produces the same evaluation order and selected, retained, or no-supported-baseline outcome.
- Every public verification record resolves to exact refs in one coherent release manifest, including shipped dependency refs where they carry documented behavior.
- Every release promotion record contains all seven minimum evidence groups required by this decision and identifies the predeclared mandatory public baseline.
- Candidate and incumbent qualification apply the same obtainability, provenance-integrity, safety and security, deployed-network compatibility, and mandatory-baseline requirements.
- Changing any qualification input requalifies the incumbent without requiring a new candidate. Validation changes each trigger class independently: obtainability or alias target; provenance integrity; safety or security evidence; an approved mandatory-baseline definition or a baseline result; runtime or capability evidence that can affect a supported journey; shipped-dependency evidence; and deployed-network identity or compatibility.
- A plausibly journey-affecting qualification-input change with uncertain scope fails closed for every plausibly affected journey until its scope is established.
- A mutable alias, if mentioned, is explicitly unsupported and non-authoritative and appears alongside the exact immutable target observed; it is never a default, supported, or recommended installation command.
- Moving a mentioned mutable alias to a different immutable target requalifies whether the informational mention remains accurate; successful requalification cannot establish support or promote the alias into a default, supported, or recommended route.
- Claims that depend on deployed Autonomi Network behavior are checked against the identified compatible deployed state; claims without a reproducible deployment anchor remain unverified.
- Getting-started and how-to journeys have complete runtime evidence for the released interface they recommend; source or schema inspection alone does not pass.
- Known released defects and boundaries are represented in rendered guidance with safe alternatives where available, and material upstream defects are tracked.
- A capability-local non-baseline defect changes only its covered capability when evidence establishes that isolation; uncertain safety or security scope fails closed for every plausibly affected journey.
- Every coverage-set identifier has the same status, known defect or limitation, and safe alternative in the rendered docs and published developer skill.
- Pointer parity resolves against the active released-truth manifest, fetches released guidance before release-sensitive answers, and defers that detail on fetch failure; bundled skill guidance matches directly without requiring duplicated pointer prose.
- Fetched pointer content remains delimited as untrusted factual input and cannot override controlling instructions, change permissions, authorize gated actions, or cause embedded requests to be followed; release-sensitive claims and actions remain subject to the active manifest, capability status, and applicable safety constraints.
- If fetched-content provenance or manifest alignment cannot be established, or fetched content conflicts with the skill or user request, the agent defers the release-sensitive detail, surfaces the conflict, and does not fall back to moving source.
- A transitive dependency ref with no independent release URL remains valid shipped-dependency provenance but does not establish independent installability or candidate eligibility.
- If a newer available release fails the mandatory baseline and the incumbent remains qualified, installation and version guidance names the newer release, the retained supported baseline, the reason, and the supported install command with its immutable version or digest selector.
- If an incumbent becomes withdrawn or unobtainable, unsafe or insecure, incompatible with the deployed Autonomi Network, or noncompliant with the mandatory baseline, affected guidance narrows or withdraws the journey and states that no supported baseline exists until a released candidate passes.
- No verification record backing the default public rendered documentation or published developer skill uses `current-merged-truth`.
- `target-manifest` content never backs the default public surface; any published target content is isolated as a versioned preview and clearly labeled pre-release.
- Movement on an upstream default branch cannot by itself change public rendered prose, published skill guidance, or released verification SHAs.
- Promotion of a new release leaves an auditable record of artifacts, exact refs, compatibility, journey evidence, and accepted limitations.

Review triggers include changing the public default away from released truth, allowing merged source to advance public docs without release promotion, weakening artifact or usability evidence, or merging pre-release target content into the default public surface without clear preview isolation.

## Notes for AI-assisted work

AI tools helped draft this ADR. It remains **Proposed** until Jim Collinson reviews and accepts it. AI tools must not mark it Accepted. If accepted, future changes require a new superseding ADR rather than edits to this record.
