# ADR-0015: Retrospective acceptance and the Accepted-ADR immutability boundary

- **Status:** Accepted
- **Acceptance:** Prospective — accepted by Jim Collinson as decision owner after review of PR 73 on 2026-07-16.
- **Date:** 2026-07-15
- **Decision owners:** Jim Collinson
- **Supersedes:** ADR-0001 (lifecycle entry and immutability timing only)
- **Superseded by:** none
- **Related:** PR 73; ADR-0002 through ADR-0014; `adr/README.md`; `adr/TOOLING.md`; `.adr-kit.yaml`; `scripts/adr-governance.py`

## Context

ADR-0001 requires every new decision to start as Proposed and makes Accepted ADRs immutable. That rule fits prospective decisions created under an established review process, but this repo also needs to record decisions made before ADR governance existed.

Those retrospective records have no honest historical proposal or reviewer stage to reconstruct. Marking them Proposed would imply that the underlying decisions remain undecided, while inventing reviewers or an earlier acceptance event would falsify the record. At the same time, an ADR's introducing pull request must remain reviewable: corrections made before merge are part of establishing the final record, not post-acceptance rewriting of repository history.

## Decision Drivers

- Preserve an honest account of decisions made before ADR governance existed.
- Never invent historical reviewers, proposal stages, or acceptance ceremonies.
- Let the original decision owner confirm whether a retrospective record is faithful.
- Keep introducing pull requests reviewable until their final content is agreed.
- Preserve strict immutability once an Accepted record reaches the default branch.
- Keep prospective decisions under ADR-0001's Proposed-first human-review process.

## Considered Options

1. **Require retrospective records to start Proposed.** Rejected: this misstates settled historical decisions as presently undecided and creates a halfway status with no real prospective decision to make.
2. **Treat Accepted content as immutable from its first feature-branch commit.** Rejected: review corrections would require superseding ADRs before the original record had even merged.
3. **Allow owner-confirmed retrospective acceptance, with immutability beginning on the default branch.** Chosen: it keeps the historical record honest while preserving a clear, enforceable immutability boundary.

## Decision

Prospective decisions continue to start as Proposed and require human review before acceptance.

A retrospective ADR may be introduced as Accepted when:

- the decision predates the repo's ADR process;
- the original decision owner confirms that the ADR faithfully records the decision made;
- the ADR carries `Acceptance: Retrospective` metadata stating that basis; and
- any implementation gaps are tracked separately rather than hidden by rewriting the decision.

An ADR's introducing pull request remains reviewable until merge. Accepted-ADR immutability begins when the record lands on the default branch. From that point onward, changing the decision or record requires a new superseding ADR.

The new ADR's `Supersedes` field is the authoritative forward link. An older Accepted ADR remains byte-identical; supersession does not require adding a backlink to it.

## Consequences

### Positive

- Retrospective records describe historical decisions without fictional process metadata.
- The original decision owner, rather than implementation drift, establishes whether the reconstruction is faithful.
- Pull-request review can correct a record before it becomes immutable repository history.
- The default branch provides a deterministic immutability boundary for tooling.

### Negative / Trade-offs

- An Accepted ADR can change across commits in its introducing pull request, so branch-local status alone does not prove immutability.
- Reviewers must distinguish corrections within an introducing PR from forbidden edits to an Accepted record already on the default branch.
- The exception depends on an identifiable original decision owner; it cannot legitimize unattributed retrospective decisions.

### Neutral / Operational

- `.adr-kit.yaml` continues to declare human acceptance required and forbids AI acceptance.
- Governance checks require Acceptance metadata on newly introduced Accepted ADRs and compare merged Accepted records byte-for-byte with the proposed result.
- ADR-0001's general adoption, Proposed-first prospective lifecycle, and supersession rules remain in force outside the retrospective exception and immutability timing clarified here.

## Validation

- A new prospective Accepted ADR without Acceptance metadata fails governance.
- A new owner-confirmed retrospective Accepted ADR remains reviewable within its introducing PR.
- Editing, deleting, renaming, or replacing an Accepted ADR already present on the comparison base fails governance.
- Review trigger: changing who may confirm retrospective acceptance, or moving the immutability boundary away from the default branch, requires a superseding ADR.

## Notes for AI-assisted work

AI tools helped draft this ADR. Jim Collinson accepted it after human review on 2026-07-16. Future changes require a superseding ADR.
