# ADR-0006: Separate metadata and prose update tracks

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification blocks), ADR-0004 (execution tiers), ADR-0009 (review and automation boundary), ADR-0010 (authoring contract), ADR-0014 (skill maintenance); `planning/routines/upstream-sweep.md`; the sweep guard and SHA-reachability workflows; commits `e5869c5` (2026-05-05), `7b23c92` (2026-05-08), `ddeb45a` (2026-05-09)

> Retrospective ADR. The metadata-only track shipped 2026-05-04; the prose-impacting track and its enforcement were added 2026-05-05 and hardened through 2026-05-09.

## Context

Upstream drift has two materially different forms. Some changes leave developer-facing content accurate and require only verification provenance to move. Other changes alter a documented surface and require rendered prose or examples to change.

Combining both forms in one undifferentiated update makes low-risk provenance refreshes expensive to review and lets higher-risk prose changes hide in metadata noise. Because automated routines author these updates, the distinction cannot depend on author discipline alone.

## Decision Drivers

- Metadata-only refreshes must remain quick to verify without weakening confidence in their provenance.
- Developer-facing changes require stronger review than mechanical provenance movement.
- Automated updates need mechanically enforced boundaries between the two change classes.
- Skill content, release metadata, and verification provenance must describe one coherent state.
- Any changed verification commit must remain reachable from its declared source.

## Considered Options

1. **Use one update track for all drift.** Rejected: reviewers cannot distinguish mechanical provenance movement from developer-facing changes without reading every update in full.
2. **Classify updates only through labels or author declarations.** Rejected: declarations can be missing or inaccurate and do not prevent one change class from crossing into the other.
3. **Use mutually exclusive, mechanically enforced metadata-only and prose-impacting tracks.** Chosen.

## Decision

Routine updates use two mutually exclusive tracks:

- The **metadata-only track** may refresh verification provenance but must not change rendered prose or other developer-facing content.
- The **prose-impacting track** carries changes to rendered content and receives stronger review treatment appropriate to developer-facing claims.

Each track has a mechanically enforced change envelope. The enforcement must reject changes that cross the selected track's boundary and must verify that changed source commit identifiers are reachable from their declared sources.

Skill maintenance follows the same separation. A skill body change and its release metadata form one coherent release state. A pure verification refresh may move provenance without changing the skill's content release version or release history.

## Consequences

### Positive

- Review effort matches the risk of the update.
- Prose cannot hide inside a metadata-only refresh.
- Mechanical enforcement applies consistently regardless of whether a routine or a person authors the change.
- Skill content, release identity, and provenance cannot silently describe different states.
- Changed verification commits are checked against source history.

### Negative / Trade-offs

- Two update envelopes and a reachability check must be maintained.
- A single upstream change can produce separate updates when it has both metadata-only and prose impact across different artifacts.
- Classification still requires judgement before an update enters either envelope.

### Neutral / Operational

- Branch conventions, workflow names, allowed paths, batching rules, review gestures, and CI implementation details are mutable mechanics documented in `planning/routines/upstream-sweep.md` and the guard workflows.
- The historical commits linked above preserve provenance for the original implementation and its hardening.

## Validation

- Automated checks reject rendered-content changes from the metadata-only track and reject incoherent skill content, release, or provenance state.
- Changed verification commits are checked for reachability from their declared sources.
- Prose-impacting updates receive the stronger review treatment defined by the current review workflow.
- Review trigger: changing the mutually exclusive track model, weakening mechanical enforcement, removing stronger prose review, or allowing incoherent skill release state requires a superseding ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
