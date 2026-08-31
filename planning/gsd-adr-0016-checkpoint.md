# GSD Checkpoint — Concise Proposed ADR-0016

Date: 2026-08-29
Project: Autonomi Developer Documentation
Slice/question: Should public documentation describe only stable software the public can obtain?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial, Craft (passed); clean-context Jim-waived for ADR-0016

## Status

Revise — ADR substance passed, but its evidence remediation remains under review until fresh review and exact-head CI pass.

Meaningful work-unit? Yes — the proposal changes the durable public source-of-truth policy.
Review cadence: per-unit
Unreviewed backlog: this evidence remediation requires fresh review and exact-head CI; clean-context is explicitly Jim-waived for ADR-0016

## What happened

Jim replaced the detailed proposal with a concise target decision: public documentation describes stable or general-availability software available through supported public routes. An explicit release baseline provides exact provenance; unreleased source cannot support default public claims; defects and unsupported tasks are represented honestly.

The ADR is 481 words including metadata and headings. Skill ownership, journey models, route truth tables, release comparison, manifest schemas, and implementation mechanics are outside its scope. It partially supersedes only ADR-0003, ADR-0004, and ADR-0006.

ADR-0016 remains Proposed. No implementation, rendered docs, skill, CI, test, or Accepted ADR changed.

## Evidence

CI arbiter / green of record:

- Location: PR #98, https://github.com/WithAutonomi/autonomi-developer-docs/pull/98 (open, non-draft)
- Rule: required checks on the current PR head are the green of record.
- Historical pre-remediation head: `42b5bfef3bde33ff785fa28cb03fb0e3038d05c3`.
- ADR Governance run `33245584910`, job `99082354387`: passed substantively; checkout, regression tests, and governance checks ran successfully.
- Prose run `33245584905`, job `99082354434`: successful scope-gate no-op (`not applicable`); checkout, setup, and the main prose validation were skipped.
- Sweep run `33245584892`, job `99082354463`: successful scope-gate no-op (`not applicable`); checkout, setup, and the main metadata-envelope validation were skipped.
- Sweep SHA reachability run `33245584906`, job `99082354330`: successful scope-gate no-op (`not applicable`); checkout, setup, and the main reachability validation were skipped.
- GitBook status `GitBook`: passed.
- GitBook status `GitBook - docs.autonomi.com/developers/`: passed.
- These checks are historical pre-remediation evidence. The evidence-repair commit requires fresh exact-head CI.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists.
- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20 tests.
- ant-sdk blob ref length check: passed, 31 refs checked and all are 40 characters.
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
- Evidence reproducible-from-branch: Pending. This correction removes the known unreachable commands; fresh re-review remains pending.
- Local vs CI consistency: Pending. Pre-remediation checks passed; the evidence-repair commit requires fresh exact-head CI.

## Review Findings

Code review:

- Concise ADR review at `752099a`: passed with no findings.
- Focused evidence-wording review at `fc49173`: ADR passed; the old checkpoint had one MEDIUM consistency finding.
- Disposition: replaced the old accumulated checkpoint with this concise current record.
- Focused review of the replacement checkpoint at `dcf7c8c`: passed with no findings.
- Attended code review of `7b8b537`: HIGH evidence-reproducibility finding; two GitHub compare calls in the audit targeted local-only commit `2e11cdc908a04d31bc35a6d998211cdb7949ce93` and failed remotely. This correction removes the unreachable commands; fresh re-review and exact-head CI remain pending.
- Re-review of `6e9f056`: MEDIUM CI-scope record issue and LOW clean-context waiver-date record issue. This correction records prose, sweep, and sweep SHA reachability as successful scope-gate no-ops with substantive validation skipped and dates the waiver from commit `f3f3bdc`; fresh review and exact-head CI remain pending.

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
- Result: Not run — one-off Jim waiver after the controlled panel attempts were blocked before inference.
- Initial attempt at `dcf7c8c`: blocked before inference because the separate Milestone A activation verdict was absent. Report: `planning/adr-0016-clean-context-dcf7c8c.md`.
- Jim later activated normal and ad-hoc controlled external reviews; activation absence is no longer the current blocker.
- Post-activation attempt at `50f4462`: blocked before inference because the caller-owned disposable root and `brief.md` were missing and the outer filesystem mechanism refused their creation. Report: `planning/adr-0016-clean-context-50f4462.md`.
- Jim then authorized the credential-free brief and disposable root for revision `0df9bfd`; the outer harness's static external-directory denial still blocked creation before inference.
- No model ran, and no same-model substitute review was used.
- Final disposition: Not run; Jim's `waive and present` declaration was recorded in commit `f3f3bdc735d5357ea4a03741163a800510a8b61c` on 2026-08-29 after the controlled panel attempts failed before inference. This one-off waiver applies only to ADR-0016.

## Drift / Scope Concerns

The included v0.11.2 audit is historical motivation. A fresh release audit is required before implementation. ADR acceptance does not promote a release or authorize documentation changes.

Merge commit `42b5bfef3bde33ff785fa28cb03fb0e3038d05c3` integrated current base `49e202c818bab1be780b81c28e5d0718cfb89b1c`. Any future content-changing integration requires renewed review.

## Open Questions / Decisions for Jim

The acceptance decision waits for the evidence remediation's fresh review and exact-head CI. The clean-context waiver does not itself accept the ADR or authorize merge or implementation.

PR / upstream action gate:

- PR status: already open and non-draft.
- Merge ready? No; the evidence remediation requires fresh review and exact-head CI.
- Jim authorized merge? No.

## Recommended Next Step

Rerun checks, review, and exact-head CI for this evidence repair, then present Proposed ADR-0016 for the acceptance decision. Acceptance, merge, and implementation remain separate unauthorized actions.

## Handoff Note

The concise ADR's substance passed code review, goal verification, adversarial review, and Craft Review. Clean-context is explicitly waived for ADR-0016. The evidence repair now requires fresh review and exact-head CI before the acceptance decision; ADR-0016 remains Proposed, and acceptance, merge, and implementation remain unauthorized.
