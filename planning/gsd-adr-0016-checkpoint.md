# GSD Checkpoint — Proposed ADR-0016 review

Date: 2026-08-20
Project: Autonomi Developer Documentation
Slice/question: Should released truth replace moving merged truth as the default public documentation source?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial; Craft and clean-context not run after adversarial blocker

## Status

Revise — lifecycle fallback/requalification passed re-review, but pointer security and mutable-alias consistency remain.

Meaningful work-unit? Yes — this proposal changes the repository's durable public source-of-truth and drift semantics.
Review cadence: per-unit blocked at code review
Unreviewed backlog if deferred: Craft and clean-context remain unrun until adversarial passes

## What happened

Proposed ADR-0016 makes released, publicly obtainable, compatible, capability-evidenced truth the default for public rendered developer documentation and the published developer skill. It preserves moving default branches as next-release watch inputs, retains `target-manifest` for isolated pre-release previews, and defines promotion and honest fallback evidence. Remediation commit `fb67648` adds stable/general-availability candidate rules, symmetric candidate/incumbent safety, deterministic release-set discovery and ordering, continuing incumbent requalification, pointer-compatible skill parity, separate distributable/dependency identities, and precise partial supersession of ADR-0003, ADR-0004, ADR-0006, ADR-0013, and ADR-0014.

The branch also carries the dated v0.11.2 motivating audit as inspectable evidence. The audit explicitly distinguishes historical policy from current authority, records evidence gaps, and notes that Python and Rust source-install routes were identified but not clean-install or runtime verified.

No implementation, rendered documentation, skill, manifest, automation, CI, test, or Accepted ADR changed. ADR-0016 remains Proposed.

## Evidence

CI arbiter / green of record:

- Location: `.github/workflows/adr-governance.yml`, triggered by pull requests that change `adr/**`.
- Status: the CI arbiter exists, but no remote branch, pull request, or exact-SHA CI run exists. Local evidence is weaker and is not CI-green.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — the repository has no `.gsd/gate.sh`.
- Commands run: ADR governance, governance unit tests, and `git diff --check`.
- Result: passed.

Files changed/artifacts produced:

- `adr/ADR-0016-released-truth-for-public-developer-docs.md`
- `planning/released-antd-v0.11.2-audit.md`
- `planning/STATE.md`
- `planning/gsd-adr-0016-checkpoint.md`
- `planning/adr-0016-code-review-e3df509.md`
- `planning/adr-0016-code-review-2dd687b.md`

Checks run:

- `python3 -I scripts/adr-governance.py`
- `python3 -I -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
- `git diff --check origin/main...HEAD`
- Independent code review through commit `5dbecd5`, before the later state/checkpoint-only commit.
- Goal-backward verification through commit `5dbecd5` against the approved decision intent and Accepted ADR boundaries.

Results:

- ADR governance: passed, 1 ADR checked.
- Governance tests: 20 passed.
- Diff check: passed.
- Code review through `5dbecd5`: passed, no findings; detailed reviewer output was session-local rather than a committed report.
- Goal verification through `5dbecd5`: passed, 7/7 goals verified; detailed verifier output was session-local rather than a committed report.
- Accepted ADRs: byte-identical to the base.
- Adversarial-remediation local validation at `fb67648`: ADR governance passed, 20 governance tests passed, and `git diff --check` passed.
- Code review at exact commit `e3df50957d2691b8661c503bfd6f34cc960aece9`: `issues_found`; two HIGH and one MEDIUM finding. Full report: `planning/adr-0016-code-review-e3df509.md`.
- Lifecycle-correction local validation at `9c2f1da`: ADR governance passed, 20 governance tests passed, and `git diff --check` passed.
- Code review at exact commit `2dd687bdd4a958694a53049014791ede0b67c0be`: `issues_found`; previous lifecycle HIGH findings resolved, with one new HIGH and one MEDIUM finding. Full report: `planning/adr-0016-code-review-2dd687b.md`.

## Honesty rules check

- No-harness-modification: Pass
  - No test, harness, daemon, build, environment, gate, or CI change.
- Baseline-diff for evidence: Pass
  - No failure or skip was dismissed as environmental, flaky, or pre-existing.
- Evidence reproducible-from-branch: Concern
  - The motivating audit, representative commands, and latest exact-SHA code-review report are committed and require no uncommitted wrapper or environment variable. The earlier verifier report was session-local; a new exact-SHA verification remains pending after remediation.
- Local vs CI consistency: no conflict observed, but the applicable CI arbiter has not run.

## Ledger / forks

Not applicable; attended run. No forks or split decisions were created.

## Review findings

Independent code review:

- Reviewer/tool: codereviewer — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Reviewed commit: `e3df50957d2691b8661c503bfd6f34cc960aece9`
- Result: Issues found
- Findings:
  - HIGH: define deterministic behavior when maximal eligible sets fail but a dominated older eligible set might qualify.
  - HIGH: incumbent requalification must trigger whenever any qualification input changes, not only availability, security, or network evidence.
  - MEDIUM: default install routes must pin immutable versions/digests or alias-target movement must trigger requalification.
- Disposition: all three were remediated in `9c2f1da` and re-reviewed at `2dd687b`.
- Re-review disposition at `2dd687b`: deterministic fallback and complete requalification passed; immutable defaults passed, but alias recommendation language remained inconsistent. A new HIGH pointer-security finding was added.
- Report: `planning/adr-0016-code-review-e3df509.md`

Clean-context test:

- Reviewer/tool: panel Claude lane
- Result: Not run for the corrected proposal
- Findings: a prior attempt was deferred because authentication was unavailable (`models: unavailable (auth) · 0s`); no fresh attempt ran because adversarial review blocked advancement.

Adversarial review:

- Reviewer/tool: adversarial — OpenAI GPT-5.6-sol; implementer provider unrecorded, so cross-provider independence is unconfirmed
- Required? Yes — architecture and public documentation policy.
- Result: Blockers
- Findings:
  - HIGH: candidate eligibility must explicitly require stable/general-availability status and symmetric candidate safety/security qualification. Remediated at `fb67648`; re-review pending.
  - HIGH: deterministic newest-candidate discovery/ordering and continuing incumbent requalification are missing. Remediated at `fb67648`; re-review pending.
  - HIGH: supersession conflicts with ADR-0006 and ADR-0014, with an ADR-0013 stamp-refresh impact. Remediated at `fb67648`; re-review pending.
  - HIGH: applicable PR-triggered ADR Governance CI exists but has not run.
  - MEDIUM: skill parity is ambiguous under the pointer-based skill model. Remediated at `fb67648`; re-review pending.
  - MEDIUM: distributable release identity and transitive dependency identity are conflated. Remediated at `fb67648`; re-review pending.
  - MEDIUM: review/verification evidence and exact reviewed SHA were overstated. Claims remain narrowed; exact-SHA re-review evidence is pending.

Craft Review:

- Reviewer/tool: craft
- Required? Yes — repository-governance and maintainer-conformance work.
- Verdict: Not run
- If Not run: adversarial NOT-READY blocked advancement; rerun after remediation.
- CONFORMANCE findings and dispositions: none yet.
- SIMPLICITY / NIT findings carried: none yet.

## Drift / scope concerns

The v0.11.2 audit is historical evidence. `antd` v0.12.0 has since released and issue #233 has closed. A fresh candidate-release audit is required before implementation; ADR acceptance does not promote v0.11.2 or authorize documentation changes.

## Open questions / decisions for Jim

Approve or decline the pointer-security and alias-consistency remediation. ADR acceptance is not yet ready for decision.

PR / upstream action gate, if applicable:

- PR ready to raise? No
- Jim confirmed PR may be opened? No
- Draft PR title/description prepared: No

## Recommended next step

Add a durable untrusted-content boundary for fetched skill pointers and prohibit mutable aliases from ever being default or recommended commands. Then rerun code review and goal verification before adversarial. Craft and clean-context follow only after adversarial passes. Obtaining CI green will require Jim's explicit authorization for the exact pull-request action. Do not begin implementation.

## Handoff note

Adversarial review of `ff9761a` returned NOT-READY. The first policy findings were remediated in `fb67648`; lifecycle fallback and requalification were remediated in `9c2f1da` and passed re-review. Pointer security and alias consistency still block code review. The proposal still needs goal verification, adversarial re-review, Craft, clean-context, and CI. No implementation is authorized.
