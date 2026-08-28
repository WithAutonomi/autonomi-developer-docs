# GSD Checkpoint — Proposed ADR-0016 review

Date: 2026-08-20
Project: Autonomi Developer Documentation
Slice/question: Should released truth replace moving merged truth as the default public documentation source?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier, adversarial; Craft and clean-context not run after adversarial blocker

## Status

Continue — the 477-word concise ADR passed fresh code review; goal verification is pending.

Meaningful work-unit? Yes — this proposal changes the repository's durable public source-of-truth and drift semantics.
Review cadence: per-unit fresh review after scope reset
Unreviewed backlog if deferred: Craft and clean-context remain unrun until the concise ADR passes adversarial review

## What happened

Jim approved a scope reset for Proposed ADR-0016. The ADR now states one durable target invariant: public documentation describes stable software the public can obtain, using an explicit released baseline with exact provenance. Unreleased source may prepare future documentation but cannot support default public claims. Known defects must be represented honestly.

Skill ownership, journey models, route truth tables, release comparison, manifest schemas, and implementation mechanics are outside this ADR. The proposal now partially supersedes only ADR-0003, ADR-0004, and ADR-0006. A separate developer skill is explicitly out of scope.

The branch also carries the dated v0.11.2 motivating audit as inspectable evidence. The audit explicitly distinguishes historical policy from current authority, records evidence gaps, and notes that Python and Rust source-install routes were identified but not clean-install or runtime verified.

No implementation, rendered documentation, skill, manifest, automation, CI, test, or Accepted ADR changed. ADR-0016 remains Proposed.

## Evidence

CI arbiter / green of record:

- Location: `.github/workflows/adr-governance.yml`, triggered by pull requests that change `adr/**`.
- Status: draft PR #98 is open. Exact concise head `f326e0c` passed ADR Governance run `33188143434` and both GitBook checks. Prose/sweep checks returned success as branch-scope no-ops, not substantive coverage.

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
- `planning/adr-0016-code-review-481ca8c.md`
- `planning/adr-0016-verification-9bd4f6f.md`
- `planning/adr-0016-adversarial-dfd14da.md`
- `planning/adr-0016-code-review-b1e4846.md`
- `planning/adr-0016-verification-39e2cdf.md`
- `planning/adr-0016-adversarial-ef646b9.md`
- `planning/adr-0016-code-review-752099a.md`

Checks run:

- `python3 -I scripts/adr-governance.py`
- `python3 -I -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
- `git diff --check origin/main...HEAD`
- Independent code review through commit `5dbecd5`, before the later state/checkpoint-only commit.
- Goal-backward verification through commit `5dbecd5` against the approved decision intent and Accepted ADR boundaries.
- Final code review through `481ca8c` and goal verification through `9bd4f6f`, with branch-local reports.

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
- Pointer-security local validation at `4873f36`: ADR governance passed, 20 governance tests passed, and `git diff --check` passed.
- Code review at exact commit `481ca8cb653b32823851d38b2bcc36b4007ddf7a`: passed with no findings. Full report: `planning/adr-0016-code-review-481ca8c.md`.
- Goal verification at exact commit `9bd4f6f0780d3a431a134214f9abaa3fddb45ea4`: passed, 10/10 decision-contract goals verified with no gaps. Full report: `planning/adr-0016-verification-9bd4f6f.md`.
- Journey-local content amendment `fb00f10`: local ADR governance and 20 tests passed; exact-head ADR Governance and GitBook checks passed on draft PR #98.
- Journey-local code review at `b1e4846`: passed with no findings; all global/journey truth-table scenarios passed. Report: `planning/adr-0016-code-review-b1e4846.md`.
- Journey-local goal verification at `39e2cdf`: passed, 10/10 goals and all required truth-table scenarios verified with no gaps. Report: `planning/adr-0016-verification-39e2cdf.md`.
- Concise redraft `afdaa07` replaced the detailed decision; tightening commit `f326e0c` reduced the complete ADR to 477 words. ADR governance, 20 tests, diff check, and exact-head CI passed.
- Fresh concise-ADR code review at `752099a`: passed with no findings. Report: `planning/adr-0016-code-review-752099a.md`.

## Honesty rules check

- No-harness-modification: Pass
  - No test, harness, daemon, build, environment, gate, or CI change.
- Baseline-diff for evidence: Pass
  - No failure or skip was dismissed as environmental, flaky, or pre-existing.
- Evidence reproducible-from-branch: Pass for local review evidence
  - The motivating audit, representative commands, latest passing exact-SHA code-review report, 10/10 goal-verification report, and adversarial report are committed and require no uncommitted wrapper or environment variable.
- Local vs CI consistency: no conflict observed; exact reviewed head `dfd14da` was green.

## Ledger / forks

Not applicable; attended run. No forks or split decisions were created.

## Review findings

Independent code review:

- Reviewer/tool: codereviewer — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Reviewed commit: latest passing review `481ca8cb653b32823851d38b2bcc36b4007ddf7a`; prior issue rounds `e3df509` and `2dd687b`
- Result: Passed after two recorded remediation rounds
- Findings:
  - HIGH: define deterministic behavior when maximal eligible sets fail but a dominated older eligible set might qualify.
  - HIGH: incumbent requalification must trigger whenever any qualification input changes, not only availability, security, or network evidence.
  - MEDIUM: default install routes must pin immutable versions/digests or alias-target movement must trigger requalification.
- Disposition: all three were remediated in `9c2f1da` and re-reviewed at `2dd687b`.
- Re-review disposition at `2dd687b`: deterministic fallback and complete requalification passed; immutable defaults passed, but alias recommendation language remained inconsistent. A new HIGH pointer-security finding was added.
- Disposition: pointer-security and alias-consistency findings were remediated in `4873f36` and re-reviewed at `481ca8c`.
- Re-review disposition at `481ca8c`: both findings resolved; code-review gate passed.
- Reports: `planning/adr-0016-code-review-e3df509.md`, `planning/adr-0016-code-review-2dd687b.md`, and `planning/adr-0016-code-review-481ca8c.md`

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
  - MEDIUM: review/verification evidence and exact reviewed SHA were overstated. Claims were narrowed and exact-SHA code-review/verification reports are now branch-local; adversarial re-review pending.
- Re-review at `dfd14da`: `NOT-READY`.
  - HIGH: qualification is ambiguous between one global coherent release set and journey-local support/withdrawal.
  - LOW: checkpoint/base/CI wording was stale; corrected in this post-review record.
- Report: `planning/adr-0016-adversarial-dfd14da.md`
- Owner disposition: Jim chose journey-local support within one active coherent release set. Amendment `fb00f10` resolves the ambiguity; adversarial re-review pending.
- Independent code-review disposition at `b1e4846`: ambiguity resolved with no new findings.
- Re-review at `ef646b9`: `NOT-READY`.
  - HIGH: a top-level SDK route can still combine incompatible bindings or transports.
  - HIGH: ADR-0016 changes ADR-0011's unconditional SDK-primary stance but does not supersede it.
  - MEDIUM: truth-table evidence lacks concrete route-continuity identities and clause derivations.
  - LOW: state/checkpoint/PR evidence and the v0.11.2 present-tense sentence need correction.
- Report: `planning/adr-0016-adversarial-ef646b9.md`
- Scope-reset disposition: the journey, route, skill, and ADR-0011 decisions reviewed at `ef646b9` were removed from ADR-0016. Fresh review of the concise target decision is pending.

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

No owner decision is pending until the concise ADR completes fresh review. The redraft does not authorize merge or ADR acceptance.

PR / upstream action gate, if applicable:

- PR ready to raise? Yes — as a draft CI/review vehicle only; not acceptance-ready or merge-ready
- Jim confirmed PR may be opened? Yes — exact draft PR action authorized in chat on 2026-08-20
- Draft PR title/description prepared: Yes
  - Title: `docs(adr): adopt released truth for public documentation`
  - Description: proposes ADR-0016, carries its dated motivating audit and branch-local review evidence, states that no implementation is included, and requests ADR Governance CI plus review before the human acceptance decision.

## Recommended next step

Run fresh goal verification against the concise ADR, persist the exact-SHA report, and rerun adversarial. Craft and clean-context follow only after adversarial passes. Do not merge, accept ADR-0016, or begin implementation.

## Handoff note

Jim replaced the detailed journey-local proposal with a 477-word target-architecture decision at `f326e0c`. Exact-head CI and fresh code review are green. Goal verification, adversarial, Craft, and clean-context remain. No implementation is authorized.
