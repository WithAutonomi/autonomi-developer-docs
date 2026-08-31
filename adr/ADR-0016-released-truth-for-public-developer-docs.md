# ADR-0016: Public documentation describes obtainable releases

- **Status:** Accepted
- **Acceptance:** Prospective — accepted by Jim Collinson as decision owner after review of PR #98 on 2026-08-31.
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (public source selection only); ADR-0004 and ADR-0006 (public provenance advancement only)
- **Superseded by:** none
- **Related:** `planning/released-antd-v0.11.2-audit.md`; PR #98

## Context

Public developer documentation is a promise about software developers can obtain and use.

Default-branch code may be unreleased, unavailable through supported installation routes, or reverted. Documentation based on it can describe a product the public cannot obtain.

A stable release is the stake in the ground against which public documentation is written and verified.

## Decision Drivers

- Developers must be able to obtain the software the documentation describes.
- Public claims must have stable, auditable provenance.
- Known release defects and limitations must be represented honestly.

## Considered Options

1. Document the latest merged source.
2. Document stable, publicly obtainable releases. Chosen.

## Decision

Public developer documentation will describe only stable or general-availability software available through supported public distribution or installation routes.

The documentation will use an explicit release baseline. For a multi-component product, it identifies compatible released components, exact shipped dependencies, and the compatible deployed Autonomi Network state where relevant.

Every technical claim must be supported by the baseline release, its exact shipped dependencies, or verified behavior against the compatible deployed network.

A documentation baseline advances only through reviewed promotion of a public release. Unreleased code may inform future documentation but cannot support default public claims.

Known defects are part of released truth. Affected capabilities must be described with their limitations and safe alternatives, or must not be presented as working.

If no released software supports a claim or task, the documentation must state that limitation rather than infer support from source.

Pre-release documentation, if published, must be clearly separated from the default public documentation.

This decision governs public documentation in this repository. It does not govern a separate developer skill.

Implementation details and sequencing belong in a reviewed specification and planning documents.

## Consequences

### Positive

- Public documentation corresponds to obtainable software.
- Releases provide stable and reproducible verification boundaries.
- Defects cannot be hidden by newer unreleased source.

### Negative / Trade-offs

- Documentation may intentionally lag merged development.
- Promoting a release baseline requires verification work.

### Neutral / Operational

- Default branches remain useful for preparing future documentation.

## Validation

- Every public technical claim resolves to exact release, shipped-dependency, or verified deployed-network evidence.
- Documented installation routes resolve to the intended public artifacts.
- Unreleased source cannot advance the public documentation baseline.
- Known broken or unverified capabilities are not presented as working.
- Every baseline change leaves a reviewed release-promotion record.

## Notes for AI-assisted work

AI tools helped draft this ADR. Jim Collinson accepted it after human review of PR #98 on 2026-08-31. The introducing PR remains reviewable until merge; once this Accepted record lands on the default branch, future changes require a superseding ADR.
