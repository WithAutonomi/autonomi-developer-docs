# GSD Checkpoint — Proposed ADR-0016 review

Date: 2026-08-20
Project: Autonomi Developer Documentation
Slice/question: Should released truth replace moving merged truth as the default public documentation source?
Prepared by: orchestrator
Agents/tools used: operative, codereviewer, verifier; adversarial, Craft, and clean-context pending

## Status

Continue through remaining review gates; not yet ready for the human acceptance decision.

Meaningful work-unit? Yes — this proposal changes the repository's durable public source-of-truth and drift semantics.
Review cadence: per-unit in progress
Unreviewed backlog if deferred: none; remaining gates are pending for this unit

## What happened

Proposed ADR-0016 makes released, publicly obtainable, compatible, capability-evidenced truth the default for public rendered developer documentation and the published developer skill. It preserves moving default branches as next-release watch inputs, retains `target-manifest` for isolated pre-release previews, defines promotion and honest fallback evidence, and supersedes only the relevant portions of ADR-0003 and ADR-0004.

The branch also carries the dated v0.11.2 motivating audit as inspectable evidence. The audit explicitly distinguishes historical policy from current authority, records evidence gaps, and notes that Python and Rust source-install routes were identified but not clean-install or runtime verified.

No implementation, rendered documentation, skill, manifest, automation, CI, test, or Accepted ADR changed. ADR-0016 remains Proposed.

## Evidence

CI arbiter / green of record:

- Location: none; no remote branch, PR, or repository CI workflow exists for this work-unit.
- Status: no CI arbiter exists; evidence is weaker.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — the repository has no `.gsd/gate.sh`.
- Commands run: ADR governance, governance unit tests, and `git diff --check`.
- Result: passed.

Files changed/artifacts produced:

- `adr/ADR-0016-released-truth-for-public-developer-docs.md`
- `planning/released-antd-v0.11.2-audit.md`
- `planning/STATE.md`
- `planning/gsd-adr-0016-checkpoint.md`

Checks run:

- `python3 -I scripts/adr-governance.py`
- `python3 -I -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
- `git diff --check origin/main...HEAD`
- Independent code review of the complete diff.
- Goal-backward verification against the approved decision intent and Accepted ADR boundaries.

Results:

- ADR governance: passed, 1 ADR checked.
- Governance tests: 20 passed.
- Diff check: passed.
- Code review: passed, no findings.
- Goal verification: passed, 7/7 goals verified.
- Accepted ADRs: byte-identical to the base.

## Honesty rules check

- No-harness-modification: Pass
  - No test, harness, daemon, build, environment, gate, or CI change.
- Baseline-diff for evidence: Pass
  - No failure or skip was dismissed as environmental, flaky, or pre-existing.
- Evidence reproducible-from-branch: Pass
  - The motivating audit and representative commands are committed on this branch; no uncommitted wrapper or environment variable is required.
- Local vs CI consistency: N/A — no CI arbiter exists; local evidence is explicitly weaker.

## Ledger / forks

Not applicable; attended run. No forks or split decisions were created.

## Review findings

Clean-context test:

- Reviewer/tool: panel Claude lane
- Result: Not run for the corrected proposal
- Findings: a prior attempt was deferred because authentication was unavailable (`models: unavailable (auth) · 0s`); a fresh attempt remains pending.

Adversarial review:

- Reviewer/tool: adversarial
- Required? Yes — architecture and public documentation policy.
- Result: Not run on the corrected proposal
- If Not run: pending before the acceptance checkpoint.
- Findings: none yet.

Craft Review:

- Reviewer/tool: craft
- Required? Yes — repository-governance and maintainer-conformance work.
- Verdict: Not run on the corrected proposal
- If Not run: pending before the acceptance checkpoint.
- CONFORMANCE findings and dispositions: none yet.
- SIMPLICITY / NIT findings carried: none yet.

## Drift / scope concerns

The v0.11.2 audit is historical evidence. `antd` v0.12.0 has since released and issue #233 has closed. A fresh candidate-release audit is required before implementation; ADR acceptance does not promote v0.11.2 or authorize documentation changes.

## Open questions / decisions for Jim

After the remaining review gates: accept, reject, or request changes to Proposed ADR-0016.

PR / upstream action gate, if applicable:

- PR ready to raise? No
- Jim confirmed PR may be opened? No
- Draft PR title/description prepared: No

## Recommended next step

Run adversarial, Craft, and clean-context gates. If they pass, return to Jim for the ADR acceptance decision. Do not begin implementation.

## Handoff note

The proposal is code-reviewed and goal-verified but is not Accepted and has not completed its gauntlet. No implementation is authorized.
