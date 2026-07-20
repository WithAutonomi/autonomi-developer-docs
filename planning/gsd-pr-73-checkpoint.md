# GSD Checkpoint — PR 73 ADR corrections

Date: 2026-07-20
Project: Autonomi Developer Documentation
Slice/question: Correct PR 73's retrospective ADRs and relocated governance
Prepared by: OpenCode orchestrator
Agents/tools used: OpenCode, local code reviewer; final ADR, adversarial, Craft, and panel reviewers pending

## Status

Continue — approved local correction set implemented; awaiting final review and CI

Meaningful work-unit? Yes — this changes ADR governance, immutable records, CI validation, and the durable account of prior architectural decisions.
Review cadence: latest local code review addressed; final ADR, adversarial, Craft, and panel review not yet run on the corrected implementation
Unreviewed backlog if deferred: complete corrected PR 73 work-unit

## What happened

- Repaired the `/adr` relocation across governance code, workflow paths, tooling guidance, and supersession metadata.
- Replaced implementation-ratification wording with owner-confirmed retrospective acceptance wording in ADR-0003 through ADR-0014.
- Corrected the Claude Code Remote routine, information-architecture authority, skill identity, vendor-neutral distribution, URL migration, release-date, and maintenance records agreed during review.
- Added `planning/adr-implementation-conformance.md` to separate intended decisions from implementation gaps.
- Drafted ADR-0015 to govern owner-confirmed retrospective acceptance and make the default branch the Accepted-record immutability boundary. Jim accepted it after review on 2026-07-16.
- On 2026-07-16, Jim decided the broad checker self-hardening was overbuilding. The governance implementation now follows David's established team-standard checker, adapted only for this repo's root-level `/adr` directory, the one-time `docs/adr` relocation, and ADR-0015 Acceptance metadata.
- Removed workflow self-inspection, action and command allowlists, symlink and execution-context threat-model machinery, and the adversarial tests dedicated to those mechanisms.
- Organization-wide validation from a trusted external checker remains a possible separate cross-repo follow-up. It is not required by PR 73.
- Addressed the latest local code review on 2026-07-20: local branch checks now compare against the merge base with `origin/main` (falling back to local `main`) instead of `HEAD^1`, while pull-request and push CI retain `GITHUB_BASE_REF` and `GITHUB_EVENT_BEFORE` handling.
- Added focused coverage proving an Accepted ADR introduced on a feature branch can be corrected across multiple commits before merge without weakening the default-branch immutability boundary.
- The checker now validates the current `.adr-kit.yaml` and fails when its `adr_directory` differs from the hard-coded `ADR_DIR`. Focused regression coverage protects the check.
- Restored executable mode on `scripts/adr-governance.py`.

## Evidence

CI arbiter / green of record:

- Location: PR 73 GitHub checks.
- Status: Not run for this local correction set. Existing PR green applies only to `bc79a09`; local evidence remains provisional until an approved push runs CI on the correction-set commit.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists in this repo.
- Commands run:
  - `python3 -I -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
  - `python3 -I scripts/adr-governance.py`
  - `GITHUB_BASE_REF=main python3 -I scripts/adr-governance.py`
  - `python3 -m py_compile scripts/adr-governance.py scripts/tests/test_adr_governance.py`
  - `git diff --check`
- Result: Local checks pass after the 2026-07-20 corrections: 16 focused integration tests passed; both governance modes validated all 15 ADRs; compilation and diff checks passed. This is provisional local evidence, not final review or CI.

Files changed/artifacts produced:

- ADR-0002 through ADR-0014 corrections.
- Accepted ADR-0015.
- ADR README, template, and tooling guidance.
- ADR governance workflow, script, and integration tests.
- Remote routine policy/prompt and skill maintainer guidance.
- Skill open questions, implementation-conformance plan, work packet, and this checkpoint.

## Honesty rules check

- No-harness-modification: Pass — governance workflow/test changes were explicitly in scope and reviewed as the subject of the slice.
- Baseline-diff for evidence: Pass — no failure was dismissed as environmental, flaky, or pre-existing.
- Evidence reproducible-from-branch: Pass for the approved correction-set commit — the checks use only files included in the commit, with no helper scripts or hidden environment state.
- Local vs CI consistency: Unknown until an approved push runs CI on the exact reviewed SHA.

## Review findings

Local code review:

- Reviewer/tool: latest local code review completed before the 2026-07-20 correction pass.
- Result: Findings addressed locally; final review remains pending.
- Findings: HIGH — replace `HEAD^1` fallback with the default-branch merge base and prove multi-commit introducing-PR corrections; MEDIUM — validate current `.adr-kit.yaml` against `ADR_DIR`; LOW — restore checker executable mode.
- Dispositions: All three fixes and both focused regressions are included in the correction set. The checker remains deliberately small; workflow self-inspection, action allowlists, broad symlink/execution hardening, and an external trusted validator were not reintroduced.

ADR governance review:

- Reviewer/tool: Pending.
- Result: Not run on the 2026-07-20 corrected implementation.
- Findings: Pending.

Clean-context test:

- Reviewer/tool: Not yet run on the simplified implementation.
- Result: Not run.
- Findings: Earlier review established the ADR-content corrections and Jim accepted ADR-0015; it does not establish readiness of the simplified checker.

Adversarial review:

- Reviewer/tool: fresh adversarial agents across repeated correction cycles.
- Required? Yes — governance and immutable records are meaningful shared work.
- Result: Not run on the simplified implementation.
- Findings: The earlier bypass-oriented review drove the overbuilding that Jim rejected on 2026-07-16. A focused review remains pending.

Craft Review:

- Reviewer/tool: fresh Craft reviewer.
- Required? Yes — shared governance and documentation changes.
- Verdict: Not run on the simplified implementation.
- CONFORMANCE findings and dispositions: Pending.
- SIMPLICITY / NIT findings carried: Pending.

Panel review:

- Reviewer/tool: Claude Opus panel lane.
- Result: Not run on the simplified implementation.
- Findings: Earlier panel findings remain relevant to ADR content, not checker readiness.

## Drift / scope concerns

- Jim determined that treating the repository-controlled workflow and checker as mutually self-defending security boundaries was overbuilding. PR 73 now preserves the established team-standard maintenance shape and only adds relocation and Acceptance-metadata behaviour required by this repo's Accepted decisions.
- A trusted external validator could address organization-wide self-modification concerns without making each repository checker self-inspecting. That is a separate design and rollout question, not PR 73 scope.
- Making ADR Governance a required branch-protection check remains out of scope and is tracked in `planning/adr-implementation-conformance.md`.
- Model routing, docs-content lint, skill restructuring, registry-driven dependency discovery, and distribution publication remain future slices.

## Open questions / decisions for Jim

- Resolved: Jim accepted ADR-0015 on 2026-07-16.
- Resolved: Jim directed the governance simplification on 2026-07-16 because broad self-hardening was overbuilding.
- Open: final ADR, adversarial, Craft, and panel review plus CI evidence for the corrected implementation.

PR / upstream action gate:

- PR ready to raise? Existing PR only; the local correction set is not CI-verified.
- Jim confirmed PR may be updated? No push action is approved for this step.
- Draft PR title/description prepared: Existing PR 73 description will need updating after approval.

## Recommended next step

Run the pending final ADR, adversarial, Craft, and panel reviews on the correction-set commit. Seek explicit approval before pushing, then confirm PR 73 CI on the pushed SHA.

## Handoff note

Jim's 2026-07-16 simplification decision supersedes stale readiness claims for the overbuilt checker. The 2026-07-20 local correction set addresses all three latest code-review findings without expanding that deliberately small design. Existing PR CI does not cover this state; final reviews and CI remain pending.
