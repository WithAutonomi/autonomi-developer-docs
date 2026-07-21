# ADR-0009: Human review until independent panel automation is proven

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0005 (routine venue and billing), ADR-0006 (update tracks), ADR-0007 (fail-closed topology), ADR-0010 (repository authoring policy); `planning/adr-implementation-conformance.md`

> Retrospective ADR capturing both the current safety boundary and the accepted future architecture. The independent AI review panel and automatic progression are intended architecture, not yet built.

## Context

The destination is a fully automated pipeline in which upstream changes can progress into accurate documentation without routine human intervention. Accuracy must remain demonstrable and tested rather than assumed.

The present system does not have an automated reviewer with enough independent evidence to replace human review safely. This ADR preserves the human boundary while recording the intended panel architecture so the interim control is not mistaken for the destination.

## Decision Drivers

- Wrong documentation is worse than stale documentation, so uncertain changes must not progress automatically.
- The end state removes routine human intervention without removing independent review.
- Review must test changes against source evidence and repository policy, not rely on the generator's confidence.
- Disagreement and uncertainty need a human escalation path.
- Review independence must reduce correlated errors between generation and approval.
- Automation must advance only on measured evidence.

## Considered Options

1. **Allow automatic progression without an independent review architecture.** Rejected: structural checks alone do not establish the accuracy of developer-facing claims.
2. **Keep human review permanently.** Rejected as the destination: it makes routine maintenance depend on human availability.
3. **Keep human review as the current safety boundary and replace it only with a proven independent AI review panel that escalates uncertainty.** Chosen.

## Decision

Human review remains the merge safety boundary until the intended independent AI review panel is implemented and has met a defined evidence threshold.

The accepted future architecture is:

- multiple independent AI reviewers assess each change against source-of-truth evidence and repository policy;
- panel lanes are independent across providers or model families so one generator or model does not approve its own work through a correlated review;
- a clean change progresses automatically when the panel agrees and the required evidence is present;
- disagreement, uncertainty, insufficient evidence, and failed checks escalate to a human rather than progressing automatically; and
- the metadata-only and prose-impacting tracks may cross the evidence threshold independently.

The panel architecture and automatic progression are not yet built. ADR-0005 remains authoritative for execution venue and billing constraints; those operational concerns do not define the panel's reviewer lanes here.

## Consequences

### Positive

- Human review protects accuracy until an independently reviewed replacement is proven.
- The automated destination remains an explicit architectural commitment.
- Independent reviewers reduce correlated blind spots between generation and approval.
- Human attention is reserved for disagreement, uncertainty, and incomplete evidence once the panel exists.
- Each update track can advance without weakening the safety boundary for the other.

### Negative / Trade-offs

- Human review remains a throughput constraint until the panel is implemented and proven.
- A genuinely independent panel is more complex than a single automated reviewer.
- Measuring readiness and maintaining escalation paths add operational work.

### Neutral / Operational

- Rollout order, evidence windows, numerical thresholds, concrete providers, model versions, credentials, and review harnesses belong in the panel specification and implementation plan.
- Replacing human control does not alter the verification source-of-truth model, update-track envelopes, or fail-closed topology.

## Validation

- Until the panel is built and proven, routine changes require human approval to progress.
- A future panel specification defines measurable evidence, reviewer independence, agreement handling, and human escalation before automatic progression is enabled.
- Each track must meet the specified evidence threshold independently.
- Review trigger: weakening human control before the panel qualifies, removing reviewer independence or human escalation, or abandoning the fully automated destination requires a superseding ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
