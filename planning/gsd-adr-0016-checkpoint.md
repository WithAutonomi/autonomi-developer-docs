# GSD Checkpoint — Concise Proposed ADR-0016

Date: 2026-08-28
Project: Autonomi Developer Documentation
Slice/question: Should public documentation describe only stable software the public can obtain?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial; Craft and clean-context pending

## Status

Blocked — Milestone A and exact root permission are approved, but the outer harness's final static external-directory deny prevents creating the required caller-owned root and brief.

Meaningful work-unit? Yes — the proposal changes the durable public source-of-truth policy.
Review cadence: per-unit
Unreviewed backlog: clean-context only

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
- Focused review of the replacement checkpoint at `dcf7c8c`: passed with no findings.

Goal verification:

- Final concise verification at `58545cd`: passed 12/12 with no gaps.
- Later ADR change: one validation line aligned with an already-authorized evidence path; focused code review passed it.

Adversarial review:

- Review at `d18a63b`: READY-WITH-NITS; no CRITICAL, HIGH, or MEDIUM findings.
- Deployed-network validation wording nit: corrected in `dfe2161` and passed focused review.
- Stale PR-body nit: corrected.

Craft Review:

- Required: Yes.
- Result: Pass at `dcf7c8c`; no CONFORMANCE, SIMPLICITY, or NIT findings.
- Report: `planning/adr-0016-craft-dcf7c8c.md`.

Clean-context review:

- Required: Yes.
- Result: Blocked before inference.
- Reason: controlled Claude panel normal/ad-hoc use lacks Jim's separate Milestone A activation verdict.
- No substitute reviewer was used.
- Evidence: `claude=official claude CLI Fable review family (Anthropic), BLOCKED: panel activation/dispatch authorization absent; no reviewer inference attempted`
- Report: `planning/adr-0016-clean-context-dcf7c8c.md`.
- Activated retry at revision `50f4462`: blocked before inference because the caller-owned root/brief was missing and outer filesystem permission refused creation.
- `models: provider=not-observed · model=not-resolved · duration=unknown`
- `claude=blocked-before-inference (caller-owned brief missing) · provider=not-observed · model=not-resolved`
- Report: `planning/adr-0016-clean-context-50f4462.md`.

## Drift / Scope Concerns

The included v0.11.2 audit is historical motivation. A fresh release audit is required before implementation. ADR acceptance does not promote a release or authorize documentation changes.

The branch is behind current `main`, but the PR merge ref is green. Any content-changing integration requires renewed review.

## Open Questions / Decisions for Jim

Milestone A activation and the narrow disposable-root authorization are resolved. The remaining blocker is static harness permission, not owner intent. This does not authorize ADR acceptance, merge, or implementation.

PR / upstream action gate:

- PR ready to raise? Already open as draft review/CI vehicle.
- Merge ready? No.
- Jim authorized merge? No.

## Recommended Next Step

Stop. Correct the outer harness permission outside this project run, or have Jim manually create and attest the root/brief. Then run a fresh controlled Claude Fable review. If it passes, return to Jim for ADR acceptance. Do not merge or implement.

## Handoff Note

The concise ADR, code review, goal verification, adversarial review, Craft Review, and CI are green. Clean-context remains blocked by static outer-harness filesystem permission despite explicit activation and root authorization. ADR-0016 remains Proposed and implementation is unauthorized.
