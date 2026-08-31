# GSD Checkpoint — Accepted ADR-0016

Date: 2026-08-31
Project: Autonomi Developer Documentation
Slice/question: Should public documentation describe only stable software the public can obtain?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial; prior proposal Craft passed; acceptance-record Craft not yet run; clean-context Jim-waived for ADR-0016

## Status

Continue — ADR-0016 is Accepted by Jim and merge authorization is settled. Complete the final adversarial rerun, Craft Review, any needed focused consistency check, and green process-required ADR Governance plus GitHub branch-protection-required checks on the resulting final head as mechanical gates, then merge PR #98 under Jim's 2026-08-31 authorization. Implementation remains unauthorized.

Meaningful work-unit? Yes — the decision changes the durable public source-of-truth policy.
Review cadence: acceptance-record code review and verification completed; exact-head adversarial review returned `NOT-READY`; rerun adversarial and Craft Review after this remediation
Unreviewed backlog: final adversarial rerun, acceptance-record Craft Review, focused consistency check as needed, and CI on the resulting final head; clean-context remains explicitly Jim-waived for ADR-0016

## What happened

Jim replaced the detailed proposal with a concise target decision: public documentation describes stable or general-availability software available through supported public routes. An explicit release baseline provides exact provenance; unreleased source cannot support default public claims; defects and unsupported tasks are represented honestly.

The ADR is 497 words including metadata and headings. Skill ownership, journey models, route truth tables, release comparison, manifest schemas, and implementation mechanics are outside its scope. It partially supersedes only ADR-0003, ADR-0004, and ADR-0006.

Jim's explicit human decision, supplied in chat on 2026-08-31, is to accept ADR-0016 via PR #98 and authorize it to be accepted and merged. Writing `Accepted` implements Jim's decision; it is not autonomous AI acceptance.

No implementation, rendered docs, skill, CI, test, harness, or other ADR changed. Implementation remains unauthorized without a separate approved spec, plan, and slice plus a fresh release audit. The introducing PR remains reviewable until merge; after ADR-0016 lands on the default branch, it is immutable and later changes require a superseding ADR.

## Evidence

CI arbiter / green of record:

- Location: PR #98, https://github.com/WithAutonomi/autonomi-developer-docs/pull/98 (open, non-draft)
- Rule: process-required ADR Governance and GitHub branch-protection-required prose, sweep, and sweep SHA reachability checks on the resulting final PR head are the green of record. ADR Governance is process-required but is not GitHub branch-protection-required.
- Reviewed acceptance head: `e2d54b26e5d510419885345e22a2374d46aeb710`.
- Process-required ADR Governance run `33392124485`, job `99487983002`: associated with head `e2d54b2` and executed on clean synthetic merge ref `c53dfc6d1b422099ed5dadb2406f0d8876409920`; checkout, all 20 tests, and governance passed.
- GitHub branch-protection-required prose run `33392124442`, job `99487983034`: green `not applicable` scope-gate no-op; main validation was skipped.
- GitHub branch-protection-required sweep run `33392124448`, job `99487983102`: green `not applicable` scope-gate no-op; main validation was skipped.
- GitHub branch-protection-required sweep SHA reachability run `33392124434`, job `99487982641`: green `not applicable` scope-gate no-op; main validation was skipped.
- GitBook status `GitBook`: passed.
- GitBook status `GitBook - docs.autonomi.com/developers/`: passed.
- The resulting final head after this reconciliation must receive green process-required ADR Governance and GitHub branch-protection-required checks before merge.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists.
- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20/20 tests.
- ant-sdk blob ref length check: passed, 31 refs checked and all are 40 characters.
- `git diff --check`: passed.
- Word count: 497.

Artifacts:

- `adr/ADR-0016-released-truth-for-public-developer-docs.md`
- `planning/released-antd-v0.11.2-audit.md`
- `planning/STATE.md`
- This checkpoint
- `planning/adr-0016-acceptance-code-review-e2d54b2.md`
- `planning/adr-0016-acceptance-verification-e2d54b2.md`
- `planning/adr-0016-acceptance-adversarial-e2d54b2.md`
- Exact-SHA reports matching `planning/adr-0016-*.md`

## Honesty Rules

- No-harness-modification: Pass. No gate, CI, test, build, or environment change.
- Baseline-diff for evidence: Pass. No failure was dismissed.
- Evidence reproducible-from-branch: Pass.
- Local vs CI consistency: Pass at reviewed head `e2d54b2`. Merge remains conditioned on green process-required ADR Governance and GitHub branch-protection-required checks on the resulting final head.

## Review Findings

Code review:

- Acceptance-record review range: `b0d01f41cc1a688699a3614ab4f3243362542a4f..e2d54b26e5d510419885345e22a2374d46aeb710`.
- Result: `passed` with no findings.
- ADR governance passed with 1 ADR checked; all 20 governance tests passed; diff and protected-scope checks passed.
- Only the three expected files changed.
- ADR-0016 changed only Status, Acceptance, and the final note. Its decision remained unchanged and the ADR contained 497 words.
- Acceptance, merge authorization, the final-head CI condition for process-required ADR Governance plus GitHub branch-protection-required checks, implementation prohibition, clean-context waiver, and default-branch immutability were coherent.
- Report: `planning/adr-0016-acceptance-code-review-e2d54b2.md`.

Goal verification:

- Verification range: `b0d01f41cc1a688699a3614ab4f3243362542a4f..e2d54b26e5d510419885345e22a2374d46aeb710`.
- Result: `passed`, 7/7.
- The human-acceptance basis names Jim Collinson, PR #98, and 2026-08-31.
- ADR-0015 permits an Accepted-status transition within an ADR's introducing pull request and places immutability at the default branch.
- Only authorized scopes changed; ADR governance, all 20 tests, and the diff check passed.
- At review time the remote needed the acceptance commits. That condition has since been satisfied, and CI associated with `e2d54b2` is green as recorded above.
- Report: `planning/adr-0016-acceptance-verification-e2d54b2.md`.

Adversarial review:

- Required: Yes.
- Result: `NOT-READY` at exact head `e2d54b26e5d510419885345e22a2374d46aeb710`. This reconciliation commit remediates the recorded findings; final adversarial rerun has not passed yet.
- HIGH: the live PR body contradicted acceptance and merge authorization and had stale head, count, and merge-ref evidence. Disposition: the orchestrator corrected the live PR body before this commit.
- MEDIUM: state and checkpoint still marked completed code review, verification, and CI pending and lacked branch-local code-review and 7/7 verification reports. Disposition: this commit reconciles both records and adds the reports.
- LOW: generic `required checks` wording obscured that ADR Governance is process-required but not GitHub branch-protection-required; branch protection requires only prose, sweep, and sweep SHA reachability, all `not applicable` no-ops here. Disposition: this commit uses explicit wording.
- No content or governance failure: the ADR decision remained unchanged at 497 words, local checks passed, and ADR-0015 alignment was correct.
- Reviewer: OpenAI GPT-5.6-sol, the same provider/model as the earlier review. The implementer provider is unrecorded, so independence evidence is weaker.
- Report: `planning/adr-0016-acceptance-adversarial-e2d54b2.md`.

Craft Review:

- Required: Yes.
- Previous proposal result: Pass at `dcf7c8c`; no CONFORMANCE, SIMPLICITY, or NIT findings. Report: `planning/adr-0016-craft-dcf7c8c.md`.
- Previous evidence-remediation result: Pass at `1091016`; no CONFORMANCE, SIMPLICITY, or NIT findings. Report: `planning/adr-0016-evidence-remediation-craft-1091016.md`.
- Acceptance-record result: Not run. The exact-head adversarial `NOT-READY` result blocked it.
- Final Craft Review after this remediation is a mandatory merge condition and has not passed yet.

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

No further acceptance or merge decision is pending. ADR-0016 is Accepted by Jim, and Jim authorized merge of PR #98 on 2026-08-31. Final adversarial rerun, Craft Review, a focused consistency check as needed, and green process-required ADR Governance plus GitHub branch-protection-required checks on the resulting final head are mechanical pre-merge conditions. This authorization does not authorize implementation.

PR / upstream action gate:

- PR status: already open and non-draft.
- Merge ready? No — conditional on final adversarial rerun, Craft Review, any needed focused consistency check, and green process-required ADR Governance plus GitHub branch-protection-required checks on the resulting final head.
- Jim authorized merge? Yes — on 2026-08-31.

## Recommended Next Step

Run the final adversarial rerun, Craft Review, and a focused consistency check as needed. Then obtain green process-required ADR Governance and GitHub branch-protection-required prose, sweep, and sweep SHA reachability checks on the resulting final head and merge PR #98 under Jim's authorization. Do not begin implementation.

## Handoff Note

ADR-0016 is Accepted by Jim, and merge authorization is settled. Acceptance-record code review and 7/7 verification passed, and CI associated with `e2d54b2` is green. Exact-head adversarial review at `e2d54b2` returned `NOT-READY`; this commit remediates its PR-body, living-record, report, and CI-wording findings. Final adversarial rerun and Craft Review remain mandatory, with a focused consistency check as needed and green process-required ADR Governance plus GitHub branch-protection-required checks on the resulting final head. Clean-context remains explicitly Jim-waived for ADR-0016. Do not begin implementation. Once merged, ADR-0016 is immutable and later changes require a superseding ADR.
