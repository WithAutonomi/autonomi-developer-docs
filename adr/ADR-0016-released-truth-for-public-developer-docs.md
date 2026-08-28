# ADR-0016: Public documentation describes obtainable releases

- **Status:** Proposed
- **Acceptance:** Prospective; pending human review and acceptance by Jim Collinson
- **Date:** 2026-08-12
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0003 (public source-selection default only); ADR-0004 and ADR-0006 (default-branch-driven public provenance advancement only)
- **Superseded by:** none
- **Related:** `planning/released-antd-v0.11.2-audit.md`; PR #98; follow-up specification and planning documents

## Context

Public developer documentation is a promise about software developers can obtain and use.

Code on a default branch may not have been released, may not be available through a supported installation route, and may be reverted before release. Documentation based on that code can describe a product that does not exist for the public.

A stable release is the stake in the ground against which public documentation is written and verified.

## Decision Drivers

- Developers must be able to obtain the software the documentation describes.
- Public claims must have stable, auditable provenance.
- Known release defects and limitations must be represented honestly.

## Considered Options

1. Document the latest merged source.
2. Document stable, publicly obtainable releases. Chosen.

## Decision

Public developer documentation will describe only stable or general-availability software that the public can obtain through supported distribution or installation routes.

The documentation will use an explicit release baseline. Where the product spans multiple components, that baseline will identify a coherent set of compatible released components, their exact shipped dependencies, and the compatible deployed Autonomi Network state where relevant.

Every technical claim must be supported by the baseline release, its exact shipped dependencies, or verified behavior against the compatible deployed network.

A documentation baseline advances only through reviewed promotion of a new public release. Code that has not been released may inform preparation for future documentation, but it cannot support claims in the default public documentation.

Known defects are part of released truth. Affected capabilities must be described with their limitations and safe alternatives, or must not be presented as working.

If no released software supports a claim or developer task, the documentation must state that limitation rather than infer support from unreleased source.

Pre-release documentation, if published, must be clearly separated from the default public documentation.

This decision governs public documentation in this repository. It does not decide where a separate developer skill lives or how that skill is assembled.

Implementation details and sequencing belong in a reviewed specification and planning documents.

## Consequences

### Positive

- Public documentation corresponds to software developers can obtain.
- Releases provide stable and reproducible verification boundaries.
- Defects cannot be hidden by newer unreleased source.

### Negative / Trade-offs

- Documentation may intentionally lag merged development.
- Promoting a release baseline requires verification work.

### Neutral / Operational

- Default branches remain useful for preparing future documentation.

## Validation

- Every public technical claim resolves to exact released provenance.
- Documented installation routes resolve to the intended public artifacts.
- Unreleased source cannot advance the public documentation baseline.
- Known broken or unverified capabilities are not presented as working.
- Every baseline change leaves a reviewed release-promotion record.

## Notes for AI-assisted work

AI may draft but not accept this ADR. Human acceptance is required. Changes to an Accepted decision require a superseding ADR.
