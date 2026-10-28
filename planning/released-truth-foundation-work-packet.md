# GSD Work Packet — released-truth foundation

Date: 2026-10-28
Prepared by: OpenCode
Requested agent/tool: OpenCode with independent verifier, Craft, and adversarial review
Role requested: Planner / Implementer / Verifier / Coordinator
Review mode: Full shared-repository profile

## Project / workspace

Project: Autonomi Developer Documentation
Repo/path: `/Users/jimcollinson/code/autonomi-developer-docs/.worktrees/released-truth-default`
Current source of truth: Accepted ADRs, merged `main` at `bc581e1aeaccc49136a2c3799cf8b1005c9d5ffe`, and issues [#103](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103) and [#104](https://github.com/WithAutonomi/autonomi-developer-docs/issues/104)

## Goal

Make released truth the safe repository-wide default before migrating the remaining documentation. New or refreshed public claims must use a reviewed public release. Existing `current-merged-truth` blocks remain visible migration debt but cannot advance against moving branches.

## Read first

- [ADR-0016: Public documentation describes obtainable releases — documentation repository](../adr/ADR-0016-released-truth-for-public-developer-docs.md)
- [ADR-0003: Verification-block source-of-truth model — documentation repository](../adr/ADR-0003-verification-block-source-of-truth.md)
- [ADR-0004: Tiered execution — documentation repository](../adr/ADR-0004-deterministic-scanner-model-audit-loop.md)
- [ADR-0006: Separate metadata and prose update tracks — documentation repository](../adr/ADR-0006-separate-metadata-and-prose-update-tracks.md)
- [ADR-0007: Fail-closed operation and GitHub artifact topology — documentation repository](../adr/ADR-0007-fail-closed-and-github-artifact-topology.md)
- [ADR-0019: Require complete release evidence and isolate legacy records — documentation repository](../adr/ADR-0019-evidence-capable-release-fallbacks.md) (Accepted by Jim Collinson on 2026-10-28)
- `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, and `planning/verification-workflow.md`
- `planning/release-following-cli-spec.md` and `planning/release-baseline-maintenance.md`
- `target-manifest.yml`, `component-registry.yml`, `scripts/sweep_poll.py`, and `scripts/validate_release_baselines.py`

## Stage

Implementation and verification of the first safety unit. ADR-0019 was accepted by Jim Collinson on 2026-10-28.

## Approved slice

Jim approved proceeding with the full released-truth rollout after reviewing the CLI and Browser SDK pilots. This packet authorizes the first bounded unit:

1. Record the repository-wide foundation contract and staged plan.
2. Align authoring and contributor instructions with ADR-0016.
3. Treat legacy `current-merged-truth` blocks as read-only migration debt.
4. Stop the deterministic scanner from resolving or proposing moving-branch updates for those blocks.
5. Emit the legacy blocks in the additive `migration_backlog` report field defined by the foundation specification.
6. Update scanner tests and routine instructions for that behavior.
7. Record a current migration inventory.

## Scope

- Planning artifacts for the foundation and migration sequence.
- Authoring rules and page-template verification examples.
- Scanner behavior and its offline tests.
- Routine documentation required to consume the additive report honestly.
- `planning/released-truth-migration-inventory-2026-10-28.md`, a dated structural snapshot of legacy blocks, mapped shared pages, and missing technical-page mappings. This is not the later release/artifact inventory.

## Out of scope

- Changing any rendered documentation page or existing verification block.
- Adding or advancing a release baseline.
- Promoting CLI `0.3.12`.
- Generalizing the CLI or Browser evidence schemas.
- Solving same-repository shared-page identity or scope expansion in code.
- Activating the hosted routine.
- Opening a pull request, merging, or publishing without a later explicit owner gate.

## Constraints / forbidden actions

- Preserve the five verification fields and the two modes fixed by ADR-0003.
- Preserve deterministic scanning, separate prose/metadata tracks, failure topology, fingerprints, and human merge review.
- Do not edit an Accepted ADR.
- Do not represent a legacy block as released or freshly verified.
- Do not fall back to a moving branch when no release baseline exists.
- Do not modify CI, test invocation, environment setup, or the release validator in this unit.

## Unattended mode / rigor profile

Unattended mode: No

Rigor profile: Full. This is shared, production-bound process code implementing an Accepted ADR.

| Lane | Requirement and selection | Due point | Deferral |
|---|---|---|---|
| Craft | Required and requested | Packet/spec checkpoint and implementation checkpoint | Planning PASS; implementation review remains due |
| Adversarial | Required and requested | Completed foundation milestone, before PR readiness | None |
| Clean-context | Required and requested | Before PR readiness | None; historical authentication failures do not count as a pass |

## Verification required

Meaningful work-unit: Yes. It changes the repository's authoring contract and removes a public moving-source update path.

Run:

```bash
python3 -B -m unittest discover -s scripts/tests -p 'test_sweep_poll.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'
python3 -I scripts/validate_release_baselines.py
python3 -I scripts/adr-governance.py
git diff --check
```

Required behavior:

- every `current-merged-truth` block appears exactly once in `migration_backlog`, including blocks on CLI-enrolled pages;
- the backlog has the exact fields and ordering defined by the specification;
- legacy blocks produce no ordinary drift records and no branch-resolution network or Git calls;
- Browser pins remain in `target_manifest_skipped`;
- CLI release discovery still emits its release-driven records and candidates;
- mixed-mode pages place only their legacy blocks in the backlog;
- malformed blocks fail before network access and error reports contain an empty backlog;
- the routine instructions cannot create a PR or issue merely because backlog entries exist.

CI arbiter: Repository Tests and applicable GitHub/GitBook checks on a later authorized pull request. Until then, local evidence is provisional.

## Stop conditions

Stop and report if:

- preserving correctness requires a third verification mode or a changed verification-block schema;
- the scanner cannot stop moving-branch advancement without changing the accepted outcome topology or fingerprints;
- the unit requires editing `.github/`, test invocation, environment setup, or the release validator;
- a legacy block must be changed to make tests pass;
- implementation begins to absorb the profile/shared-page mechanism reserved for Unit 3;
- any PR, merge, publication, routine activation, destructive operation, or ADR acceptance is proposed.

## Required output

Return the specification and plan, exact files changed, test evidence, current migration counts, review results, unresolved profile/shared-page decisions, and a recommendation for the next bounded unit.

## Planning review checkpoint

- Craft Review `ses_e7d06431bffev7JUBkAznintuC`: PASS after correcting inconsistent review status and duplicated inventory responsibilities.
- ADR review `ses_e7d064313ffeP0OEZ974rBxDaA`: Unit 1 authorized with wording corrections; no Proposed ADR required.
- Goal verification `ses_e7d06430bffegF7pWv36IQe0nZ`: PASS after correcting report-shape, inventory, test, status, sequencing, and wording gaps.
- Implementation inspection revealed that removing the obsolete moving-ref resolver also retires ADR-0007's explicit `git ls-remote` fallback. The earlier no-ADR conclusion was superseded by this implementation finding. Jim accepted ADR-0019 on 2026-10-28.
- Final implementation goal verification `ses_e7ca22a3fffeDKHS9k3v1qOguS`: PASS, 8/8 conditions verified after malformed-block validation was tightened.
- Final implementation Craft Review `ses_e7ca22a37ffemq1GIeW7Gmjbe3`: PASS with no remaining findings.
