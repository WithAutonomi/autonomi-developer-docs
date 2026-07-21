# ADR-0014: Maintain the skill through the docs verification system

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification model), ADR-0005 (scheduled maintenance), ADR-0006 (update tracks and coherent releases), ADR-0009 (review automation), ADR-0010 (authoring contract), ADR-0012 (the skill), ADR-0013 (freshness and stable URLs); `planning/verification-workflow.md`; `skills/start/MAINTAINING.md`; `repo-registry.yml`; `component-registry.yml`; the sweep guard and SHA-reachability workflows

> Retrospective ADR reconstructed from the origin design sessions. Operational maintenance has evolved since the decision; mutable mechanics are documented outside this record.

## Context

The developer skill must stay accurate as its source repositories change. The docs repository already has a verification workflow and machine-readable registries that connect source components to maintained artifacts. A separate skill-only maintenance system would duplicate that model and let documentation and skill verification drift apart.

The skill also has two metadata surfaces with different responsibilities: author-facing frontmatter attached to the skill content and a runtime manifest intended for external inspection. Their shared provenance and release identity must remain coherent without forcing content-review metadata into the runtime manifest.

## Decision Drivers

- Documentation and skill maintenance should use one source-audit and verification model.
- The registry must answer which source components require skill re-verification.
- Skill content must carry review provenance appropriate to an authored artifact.
- The runtime manifest must expose the release and provenance state needed by runtimes and external consumers.
- Content, release identity, and verification provenance must not contradict one another.
- Pure verification movement must not create a content release.

## Considered Options

1. **Create a separate maintenance workflow for the skill.** Rejected: it duplicates verification machinery and lets docs and skill maintenance diverge.
2. **Treat the skill as a documentation page in the existing page mapping.** Rejected: skills and rendered documentation have different artifact and metadata contracts.
3. **Reuse the docs verification workflow, add an explicit component-to-skill dependency relationship, and keep distinct skill and runtime metadata responsibilities.** Chosen.

## Decision

The skill reuses the docs repository's `source audit → draft → verify` workflow. The repository and component registries determine the relevant sources and re-verification scope.

`feeds_skills` is the explicit component-to-skill dependency relationship. It remains distinct from page relationships so tooling can determine which skills a component affects without treating a skill as a Diátaxis page.

Skill frontmatter and the runtime manifest have distinct responsibilities:

- skill frontmatter records provenance attached to the reviewed content, including when that content was verified; and
- the runtime manifest exposes the release identity and verification provenance required for runtime and external inspection, without duplicating content-review metadata that has no runtime responsibility.

Fields shared by those surfaces must agree, and the skill body, release identity, release history, and verification provenance must form one coherent state. A pure verification refresh that changes no described surface updates provenance without changing the content version or release history.

Breaking changes to the runtime manifest's shape or to a stable manifest URL receive major-version treatment. Other release classification and the exact maintenance procedure remain defined by the skill's operational maintenance contract.

Operational mechanics live in `skills/start/MAINTAINING.md`, `repo-registry.yml`, `component-registry.yml`, and the guard and reachability workflows. Those sources may evolve without rewriting this decision, provided they preserve these invariants.

## Consequences

### Positive

- Documentation and skill verification use one maintenance model.
- `feeds_skills` provides a machine-readable dependency relationship without conflating artifact types.
- Content review metadata stays with the content while runtime metadata stays focused on runtime and external needs.
- Pure provenance refreshes do not imply a new content release.
- Breaking manifest and stable-URL changes remain visible through major-version treatment.

### Negative / Trade-offs

- Registry mappings and verification metadata must remain consistent.
- Shared release and provenance fields require synchronization across the two metadata surfaces.
- Coupling skill maintenance to the docs verification system means changes to that system can affect both artifact types.

### Neutral / Operational

- The set of components feeding the skill, exact files that move together, field-level checklists, guard behavior, and maintenance sequencing are mutable implementation details documented in the operational sources.
- Moving the skill to another repository would require preserving the dependency relationship and verification contract or superseding this decision.

## Validation

- Tooling can determine skill re-verification scope from registry relationships and detect disagreement between the dependency graph and skill provenance.
- Maintenance checks reject contradictory skill content, release, and provenance state.
- Pure verification refreshes leave the content version and release history unchanged.
- Manifest-shape and stable-manifest-URL breaks receive major-version treatment.
- Review trigger: replacing the shared verification workflow, removing the distinct `feeds_skills` relationship, changing metadata responsibilities, or allowing incoherent release and provenance state requires a superseding ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
