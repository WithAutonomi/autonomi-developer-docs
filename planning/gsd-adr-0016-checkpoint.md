# GSD Checkpoint — Accepted ADR-0016

Date: 2026-08-31
Project: Autonomi Developer Documentation
Slice/question: Should public documentation describe only stable software the public can obtain?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial, Craft (passed); clean-context Jim-waived for ADR-0016

## Status

Continue — Jim accepted ADR-0016 and authorized merge of PR #98 on 2026-08-31; complete final mechanical validation and final-head CI, then merge under that authorization.

Meaningful work-unit? Yes — the decision changes the durable public source-of-truth policy.
Review cadence: prior per-unit reviews completed; independent acceptance-record review, verification, and gauntlet checks precede merge
Unreviewed backlog: the acceptance-record update and final PR head; clean-context remains explicitly Jim-waived for ADR-0016

## What happened

Jim replaced the detailed proposal with a concise target decision: public documentation describes stable or general-availability software available through supported public routes. An explicit release baseline provides exact provenance; unreleased source cannot support default public claims; defects and unsupported tasks are represented honestly.

The ADR is 510 words including metadata and headings. Skill ownership, journey models, route truth tables, release comparison, manifest schemas, and implementation mechanics are outside its scope. It partially supersedes only ADR-0003, ADR-0004, and ADR-0006.

Jim's explicit human decision, supplied in chat on 2026-08-31, is to accept ADR-0016 via PR #98 and authorize it to be accepted and merged. Writing `Accepted` implements Jim's decision; it is not autonomous AI acceptance.

No implementation, rendered docs, skill, CI, test, harness, or other ADR changed. Implementation remains unauthorized without a separate approved spec, plan, and slice plus a fresh release audit. The introducing PR remains reviewable until merge; after ADR-0016 lands on the default branch, it is immutable and later changes require a superseding ADR.

## Evidence

CI arbiter / green of record:

- Location: PR #98, https://github.com/WithAutonomi/autonomi-developer-docs/pull/98 (open, non-draft)
- Rule: required checks on the current PR head are the green of record.
- Reviewed remediation head: `109101669908e7c7d86b3dc586a9b5b17933d2d6`; reviewed base: `42b5bfef3bde33ff785fa28cb03fb0e3038d05c3`.
- ADR Governance run `33376786646`, job `99439965340`: associated with the reviewed PR head and executed on clean synthetic PR merge ref `90806293682a5da7a3eeed72dfebd42f8f170f6e`; checkout, all 20 regression tests, and governance checks ran successfully.
- Prose run `33376786657`, job `99439965599`: successful scope-gate no-op (`not applicable`); main validation was skipped.
- Sweep run `33376786692`, job `99439965589`: successful scope-gate no-op (`not applicable`); main validation was skipped.
- Sweep SHA reachability run `33376786655`, job `99439965598`: successful scope-gate no-op (`not applicable`); main validation was skipped.
- GitBook status `GitBook`: passed.
- GitBook status `GitBook - docs.autonomi.com/developers/`: passed.
- Current PR required checks are the green of record. The final acceptance-record commit must receive green current-head checks before merge.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists.
- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20 tests.
- ant-sdk blob ref length check: passed, 31 refs checked and all are 40 characters.
- `git diff --check`: passed.
- Word count: 510.

Artifacts:

- `adr/ADR-0016-released-truth-for-public-developer-docs.md`
- `planning/released-antd-v0.11.2-audit.md`
- `planning/STATE.md`
- This checkpoint
- Exact-SHA reports matching `planning/adr-0016-*.md`

## Honesty Rules

- No-harness-modification: Pass. No gate, CI, test, build, or environment change.
- Baseline-diff for evidence: Pass. No failure was dismissed.
- Evidence reproducible-from-branch: Pass.
- Local vs CI consistency: Pass for the reviewed remediation. Merge is conditioned on final current-head green.

## Review Findings

Code review:

- Concise ADR review at `752099a`: passed with no findings.
- Focused evidence-wording review at `fc49173`: ADR passed; the old checkpoint had one MEDIUM consistency finding.
- Disposition: replaced the old accumulated checkpoint with this concise current record.
- Focused review of the replacement checkpoint at `dcf7c8c`: passed with no findings.
- Attended code review of `7b8b537`: HIGH evidence-reproducibility finding; two GitHub compare calls in the audit targeted local-only commit `2e11cdc908a04d31bc35a6d998211cdb7949ce93` and failed remotely. Commit `6e9f056` removed those commands; re-review and current-head CI were pending at that point and are completed below.
- Re-review of `6e9f056`: MEDIUM CI-scope record issue and LOW clean-context waiver-date record issue. Commit `1091016` records prose, sweep, and sweep SHA reachability as successful scope-gate no-ops with substantive validation skipped and dates the waiver from commit `f3f3bdc`; final review and CI evidence follow below.
- Final review of remediation head `109101669908e7c7d86b3dc586a9b5b17933d2d6` against base `42b5bfef3bde33ff785fa28cb03fb0e3038d05c3`: passed with no findings. Report: `planning/adr-0016-evidence-remediation-code-review-1091016.md`.

Goal verification:

- Final concise verification at `58545cd`: passed 12/12 with no gaps.
- Later ADR change: one validation line aligned with an already-authorized evidence path; focused code review passed it.
- Final remediation verification: passed 10/10 goals. It confirmed exact 40-character ant-sdk refs, reachable representative URLs, unlinked local-only docs commits, removal of unreachable compare commands, accurate PR/base/merge and CI-scope records, coherent Craft/waiver records, no readiness overclaim, an unchanged ADR tree, and only three in-scope planning-file changes. Report: `planning/adr-0016-evidence-remediation-verification-1091016.md`.

Adversarial review:

- Review at `d18a63b`: READY-WITH-NITS; no CRITICAL, HIGH, or MEDIUM findings.
- Deployed-network validation wording nit: corrected in `dfe2161` and passed focused review.
- Stale PR-body nit: corrected.
- Final remediation review: `READY-WITH-NITS`; no CRITICAL, HIGH, or MEDIUM findings. LOW: living records lagged completed review and CI; the PR body claimed the ADR was ready but repeatedly used stale `draft` language while live PR #98 was open and non-draft. NIT: `exact-head CI` wording needed to distinguish PR-head association from synthetic-merge-ref execution. This record update resolves the living-status and CI-wording findings; the orchestrator will remove the stale `draft` wording from the PR body after final CI. The reviewer used OpenAI GPT-5.6-sol, the same model as the earlier pass; the implementer provider is unrecorded, so model-independence evidence is weaker. Report: `planning/adr-0016-evidence-remediation-adversarial-1091016.md`.

Craft Review:

- Required: Yes.
- Result: Pass at `dcf7c8c`; no CONFORMANCE, SIMPLICITY, or NIT findings.
- Report: `planning/adr-0016-craft-dcf7c8c.md`.
- Final remediation result: PASS in fresh context; no CONFORMANCE, SIMPLICITY, or NIT findings. The reviewer used the same OpenAI GPT-5.6-sol model/provider as the earlier pass; the implementer provider is unrecorded, so independence evidence is weaker. Report: `planning/adr-0016-evidence-remediation-craft-1091016.md`.

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

No further acceptance or merge decision is pending. Jim accepted ADR-0016 and authorized merge of PR #98 on 2026-08-31. Final validation and required checks on the final PR head remain mechanical pre-merge conditions. This authorization does not authorize implementation.

PR / upstream action gate:

- PR status: already open and non-draft.
- Merge ready? Conditional on final validation and required final-head CI being green.
- Jim authorized merge? Yes — on 2026-08-31.

## Recommended Next Step

Run local validation, independent acceptance-record review, verification, and gauntlet checks, then obtain green required checks on the final PR head and merge PR #98 under Jim's authorization. Do not begin implementation.

## Handoff Note

The concise ADR and evidence remediation passed final code review, goal verification, adversarial review, and Craft Review. Clean-context remains explicitly Jim-waived for ADR-0016. Jim accepted ADR-0016 and authorized merge of PR #98 on 2026-08-31. Complete acceptance-record review and verification, final-head CI, and merge; do not begin implementation. Once merged, ADR-0016 is immutable and later changes require a superseding ADR.
