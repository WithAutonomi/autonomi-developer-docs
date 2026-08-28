# GSD Checkpoint — Concise Proposed ADR-0016

Date: 2026-08-28
Project: Autonomi Developer Documentation
Slice/question: Should public documentation describe only stable software the public can obtain?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial; Craft and clean-context pending

## Status

Revise — ADR content passed focused review, but the accumulated checkpoint contradicted the current review status. This file replaces it with the current state; exact-head review is pending.

Meaningful work-unit? Yes — the proposal changes the durable public source-of-truth policy.
Review cadence: per-unit
Unreviewed backlog: Craft and clean-context

## What happened

Jim replaced the detailed proposal with a concise target decision: public documentation describes stable or general-availability software available through supported public routes. An explicit release baseline provides exact provenance; unreleased source cannot support default public claims; defects and unsupported tasks are represented honestly.

The ADR is 481 words including metadata and headings. Skill ownership, journey models, route truth tables, release comparison, manifest schemas, and implementation mechanics are outside its scope. It partially supersedes only ADR-0003, ADR-0004, and ADR-0006.

ADR-0016 remains Proposed. No implementation, rendered docs, skill, CI, test, or Accepted ADR changed.

## Evidence

CI arbiter / green of record:

- Location: draft PR #98, https://github.com/WithAutonomi/autonomi-developer-docs/pull/98
- Exact reviewed head: `fc49173dc040425429a4cc298eb3811a23650b5a`
- ADR Governance run `33204071304`, job `98960532646`: passed
- GitBook and docs preview: passed
- Prose/sweep checks: successful scope-gate no-ops, not substantive coverage

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists.
- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20 tests.
- `git diff --check`: passed.
- Word count: 481.

Artifacts:

- `adr/ADR-0016-released-truth-for-public-developer-docs.md`
- `planning/released-antd-v0.11.2-audit.md`
- `planning/STATE.md`
- This checkpoint
- Exact-SHA reports matching `planning/adr-0016-*.md`

## Honesty Rules

- No-harness-modification: Pass. No gate, CI, test, build, or environment change.
- Baseline-diff for evidence: Pass. No failure was dismissed.
- Evidence reproducible-from-branch: Pass. Review reports and audit are committed.
- Local vs CI consistency: Pass for applicable ADR checks.

## Review Findings

Code review:

- Concise ADR review at `752099a`: passed with no findings.
- Focused evidence-wording review at `fc49173`: ADR passed; the old checkpoint had one MEDIUM consistency finding.
- Disposition: replaced the old accumulated checkpoint with this concise current record.

Goal verification:

- Final concise verification at `58545cd`: passed 12/12 with no gaps.
- Later ADR change: one validation line aligned with an already-authorized evidence path; focused code review passed it.

Adversarial review:

- Review at `d18a63b`: READY-WITH-NITS; no CRITICAL, HIGH, or MEDIUM findings.
- Deployed-network validation wording nit: corrected in `dfe2161` and passed focused review.
- Stale PR-body nit: corrected.

Craft Review:

- Required: Yes.
- Result: Not run; next gate after exact-head checkpoint review.

Clean-context review:

- Required: Yes.
- Result: Not run; follows Craft Review.

## Drift / Scope Concerns

The included v0.11.2 audit is historical motivation. A fresh release audit is required before implementation. ADR acceptance does not promote a release or authorize documentation changes.

The branch is behind current `main`, but the PR merge ref is green. Any content-changing integration requires renewed review.

## Open Questions / Decisions for Jim

No architecture decision is pending. Attended mode requires approval to rerun after the checkpoint correction.

PR / upstream action gate:

- PR ready to raise? Already open as draft review/CI vehicle.
- Merge ready? No.
- Jim authorized merge? No.

## Recommended Next Step

Rerun focused exact-head review of this checkpoint. If it passes, run Craft and clean-context. Then return to Jim for the ADR acceptance decision. Do not merge or implement.

## Handoff Note

The concise ADR, code review, goal verification, adversarial review, and CI are green. The checkpoint-consistency finding is corrected but not yet re-reviewed. Craft and clean-context remain. ADR-0016 is Proposed and implementation is unauthorized.
