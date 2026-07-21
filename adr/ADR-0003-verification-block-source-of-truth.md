# ADR-0003: Verification-block source-of-truth model for developer docs

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0001 (Adopt ADRs); `planning/verification-workflow.md`; `planning/implementation-plan.md` §8; original build 2026-04-02 → 2026-04-22 (repo baseline `a1110ea`, "Reverify against current merged truth" `3eaf653`)

> Retrospective ADR. The decision was taken and implemented across April 2026; this record captures it after the fact so the reasoning is preserved. Evidence is cited in **Related** and **Validation**.

## Context

The Autonomi developer docs describe fast-moving upstream code (`ant-sdk`, `ant-client`, `ant-node`, `ant-protocol`, `saorsa-*`, and others). Documentation that drifts from the code is worse than no documentation: it silently misleads developers. The repo needed a way to state, for every technical claim on every page, *exactly which upstream commit that claim was verified against*, so drift is detectable mechanically rather than by re-reading everything by eye.

A second tension: docs must describe the latest merged default-branch source truth, not the expected future product shape. Installation, download, package, and version surfaces have an additional constraint: they must describe artifacts a developer can actually install or download, even when merged source is newer. Without explicit rules, pages tend to drift toward aspirational descriptions of unmerged branches or present unreleased artifacts as available. But a launch-hardening pass needs the opposite of following moving branches — the ability to pin a set of pages to a fixed release target.

## Decision Drivers

- Drift must be **detectable by a machine**, not only by human review.
- Every rendered claim must be **traceable to an exact upstream commit SHA**.
- Docs must default to **current merged default-branch source truth**, never future state; installation, download, package, and version surfaces must additionally stay within installable or released truth.
- A launch/release pass must be able to **pin** pages to fixed refs without inverting the day-to-day default.
- Provenance metadata must not leak into rendered prose.

## Considered Options

1. **No embedded provenance** — track freshness out-of-band (a spreadsheet, issue tracker, or reviewer memory). Rejected: unmaintainable, not machine-checkable, drifts immediately.
2. **Page-level "last reviewed" date only.** Rejected: a date says *when* someone looked, not *what upstream state* was true; it cannot detect that upstream moved.
3. **Per-surface verification records pinning `(source_repo, source_ref, source_commit, verified_date, verification_mode)`, with two explicit modes.** Chosen.

## Decision

We will embed **verification metadata** in the docs and skill sources as the single machine-readable record of what each documented surface was verified against.

- Every rendered documentation surface carries one or more `<!-- verification: ... -->` blocks in `docs/**/*.md`. Each block records the full declared schema: `source_repo`, `source_ref`, `source_commit` (an exact SHA), `verified_date`, and `verification_mode`.
- The skill uses equivalent YAML metadata rather than documentation comment blocks. `skills/start/SKILL.md` frontmatter carries `verified_date`, `verification_mode`, and a per-repo `verified_commits` SHA map. The runtime `skills/start/version.json` manifest mirrors only the fields needed at runtime or for external inspection, including `version`, `verification_mode`, and `verified_commits`; it deliberately omits `verified_date`, which records when the skill content was reviewed.
- Two verification modes are defined, and they are an **invariant of the model**:
  - **`current-merged-truth`** (default): verify against the latest merged commit on the upstream default branch at audit time. Unmerged branches and PRs are out of scope.
  - **`target-manifest`**: launch/release-hardening mode. Verify against refs pinned in `target-manifest.yml`; **do not** follow moving default branches for pages in this mode.
- A page presented as verified must never carry `source_commit: TBD`.
- Provenance/verification language lives only in the comment blocks and metadata — never in rendered body text.

This model is the foundation the automation in ADR-0004 through ADR-0007 operates on: the scanner, the guards, and the routine all read and write these blocks and nothing else about freshness.

## Consequences

### Positive

- Drift becomes a deterministic diff: compare each `source_commit` against upstream HEAD (see ADR-0004). No human re-reading required to *detect* staleness.
- Every claim is auditable to an exact SHA, so a reviewer can reproduce the evidence.
- The default keeps docs aligned with merged source truth, while install and release surfaces remain honest about artifacts developers can obtain; the `target-manifest` escape hatch supports launch hardening without weakening the default.

### Negative / Trade-offs

- Authors and automation must keep the blocks accurate; a stale-but-present block is a false "verified" signal, so block integrity itself must be guarded (ADR-0006) and reachability-checked (ADR-0007).
- Multi-repo pages carry multiple blocks, adding markup weight to sources.

### Neutral / Operational

- The rendered-documentation block schema (`source_repo`, `source_ref`, `source_commit`, `verified_date`, `verification_mode`) and the skill metadata split described above become stable contracts that downstream tools depend on; changing either is itself an architectural change requiring a superseding ADR.
- `target-manifest` blocks are deliberately excluded from automated bumping (see ADR-0007) so a launch pin is never silently overwritten.

## Validation

- The scanner (`scripts/sweep_poll.py`) parses every block and fails closed on a malformed block (missing `source_repo`/`source_ref`/`source_commit`/`verification_mode`) or an unknown mode — so a schema violation is caught, not ignored.
- `sweep-sha-reachability` (CI) confirms every recorded SHA is reachable on the declared upstream ref.
- Review trigger: any change to the block schema, the mode set, or the "no `TBD`" rule must supersede this ADR rather than edit it.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
