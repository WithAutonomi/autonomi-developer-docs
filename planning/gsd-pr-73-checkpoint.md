# GSD Checkpoint — PR 73 ADR corrections

Date: 2026-07-21
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
- On 2026-07-20, Jim resolved the ADR-0013/ADR-0014 metadata ambiguity: `verified_date` belongs only in `skills/start/SKILL.md`, while `skills/start/version.json` is the runtime version manifest and mirrors the fields needed for runtime and external inspection, including `version`, `verification_mode`, and `verified_commits`. Avoiding a duplicate review date removes unnecessary synchronization.
- Amended ADR-0013 and ADR-0014 within their introducing PR to state that contract consistently. ADR-0015 permits these review corrections before the records reach the default-branch immutability boundary. This amendment matches the existing explicit `skills/start/MAINTAINING.md` contract and creates no implementation debt.
- Rebased cleanly onto remote PR head `12806a9`. The pre-slice local commits are `f9350fc` and `c43e338`; the bounded correction commit containing this checkpoint remains local and unpushed.
- Aligned ordinary validation with David's team-standard changed-file scope: when a comparison base exists, format, status, required-section, and Acceptance-metadata checks apply only to current ADR files changed against that base; without a base, they apply to all current ADRs. Duplicate-number checking still covers all current ADRs, and every Accepted ADR on the base remains byte-for-byte immutable.
- Added focused push-event tests for a normal `GITHUB_EVENT_BEFORE` SHA and the all-zero initial-push fallback. Both prove that edits to an Accepted ADR on the selected base fail governance.
- Added the repo-root ADR governance instructions to `CLAUDE.md` and refreshed the implementation-conformance review date to 2026-07-20. Malformed ADR-prefix discovery remains an explicitly out-of-scope limitation of the shared standard.
- Retained workflow `permissions: contents: read` and checkout `persist-credentials: false` as ordinary least-privilege runner hygiene. They are not self-defending governance hardening; this correction adds no workflow self-inspection or action allowlists.
- Addressed the final ADR review's four findings in a separate local commit: made ADR-0014's targeted-foundational scope conditional on actual `feeds_skills` mappings; clarified ADR-0003's rendered-doc, skill-frontmatter, and runtime-manifest metadata schemas; separated default-branch merged truth from the installable/released constraint on installation and version surfaces; and recorded ADR-0013's missing bundled high-level post-quantum cryptography posture as implementation debt rather than adding skill content to PR 73.
- Addressed the follow-up code review by naming ADR-0003's model per-surface rather than per-claim and requiring the future post-quantum cryptography skill work to source-audit and wire its authoritative components through `feeds_skills` and `verified_commits` before adding bundled guidance.
- Completed the per-surface terminology correction throughout ADR-0003 after repeat review found three residual per-claim statements in its context, decision drivers, and consequences.
- The final ADR review has not rerun on those corrections. Final ADR, clean-context, adversarial, Craft, and panel review and exact-HEAD CI remain pending. No push is approved.

## Evidence

CI arbiter / green of record:

- Location: PR 73 GitHub checks.
- Status: Not run for this local correction set. The remote PR head before the local commits is `12806a9`; local commits `f9350fc`, `c43e338`, `c515299`, and the separate final ADR-review correction commit containing this checkpoint remain unpushed. Existing remote checks do not cover exact local HEAD.

Local fast gate / `.gsd/gate.sh`:

- Installed? N/A — no `.gsd/gate.sh` exists in this repo.
- Commands run:
  - `python3 -I -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
  - `python3 -I scripts/adr-governance.py`
  - `GITHUB_BASE_REF=main python3 -I scripts/adr-governance.py`
  - `GITHUB_EVENT_BEFORE="$(git rev-parse origin/main)" python3 -I scripts/adr-governance.py`
  - `python3 -m py_compile scripts/adr-governance.py scripts/tests/test_adr_governance.py`
  - `git diff --check`
- Result: Local checks pass after the final ADR-review correction: 20 focused integration tests passed; ordinary, pull-request, and push governance modes each validated 15 changed ADRs; compilation and diff checks passed. The push-event tests separately exercise Accepted-ADR immutability for both normal and all-zero `GITHUB_EVENT_BEFORE` paths. This is provisional local evidence, not final review or CI.

Files changed/artifacts produced:

- ADR-0002 through ADR-0014 corrections.
- Accepted ADR-0015.
- ADR README, template, and tooling guidance.
- ADR governance workflow, script, and integration tests.
- Remote routine policy/prompt and skill maintainer guidance.
- Skill open questions, implementation-conformance plan, work packet, and this checkpoint.
- Final bounded correction: `CLAUDE.md`, `scripts/adr-governance.py`, `scripts/tests/test_adr_governance.py`, `planning/adr-implementation-conformance.md`, and this checkpoint.
- Final ADR-review correction: ADR-0003, ADR-0014, `planning/adr-implementation-conformance.md`, and this checkpoint. The skill implementation is unchanged.

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
- Final pre-push correction status: implemented and locally verified, but no final ADR, clean-context, adversarial, Craft, or panel review has run on the bounded correction.

Final ADR review:

- Reviewer/tool: final ADR review completed against `c515299`; rerun on the correction commit is pending.
- Result: Four findings corrected in a separate local commit; dispositions await review confirmation.
- Findings and dispositions: ADR-0014 overstated targeted-foundational skill dependencies — restricted to components actually mapped through `feeds_skills`; ADR-0003 conflated the complete rendered-doc schema with intentionally split skill metadata — clarified each artifact contract; ADR-0003 conflated merged source truth with released truth for all pages — limited the installable/released constraint to installation, download, package, and version surfaces; ADR-0013 promised bundled high-level post-quantum cryptography guidance that the skill lacks — recorded the precise minimum follow-up in the conformance plan without changing the skill.
- Rerun status: Not run on the correction commit. This is a disposition record, not a claim of final review approval.

Follow-up code review:

- Reviewer/tool: code review completed against `8ff203a`; rerun on the follow-up correction commit is pending.
- Result: Two findings corrected locally; dispositions await review confirmation.
- Findings and dispositions: ADR-0003 used per-claim language for a per-surface model — corrected; the planned post-quantum cryptography guidance omitted the registry and verification-metadata work needed to keep it fresh — added source-audit, `feeds_skills`, and `verified_commits` prerequisites to the future conformance slice.
- Repeat review found residual per-claim wording at ADR-0003 lines 15, 22, and 52. All three statements now describe documented surfaces or verification records; rerun on the final correction commit is pending.

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
- Malformed ADR-prefix discovery is a known limitation of David's shared standard and is explicitly out of scope; no discovery logic or tests were added.
- Workflow read-only contents permission and disabled credential persistence are retained as ordinary runner hygiene, not treated as a governance security boundary. Workflow self-inspection and action allowlists remain out of scope.
- Model routing, docs-content lint, skill restructuring, registry-driven dependency discovery, and distribution publication remain future slices.
- The missing high-level post-quantum cryptography posture remains a tracked ADR-0013 conformance gap. PR 73 does not add or otherwise alter skill content.

## Open questions / decisions for Jim

- Resolved: Jim accepted ADR-0015 on 2026-07-16.
- Resolved: Jim directed the governance simplification on 2026-07-16 because broad self-hardening was overbuilding.
- Resolved: Jim decided on 2026-07-20 that `verified_date` lives only in `skills/start/SKILL.md`; `version.json` deliberately omits it and mirrors only the runtime/external manifest fields that need mirroring.
- Open: rerun final ADR review, then complete adversarial, Craft, and panel review plus CI evidence for the exact corrected HEAD.

PR / upstream action gate:

- PR ready to raise? Existing PR only; the local correction set is not CI-verified.
- Jim confirmed PR may be updated? No push action is approved for this step.
- Draft PR title/description prepared: Existing PR 73 description will need updating after approval.

## Recommended next step

Rerun the final ADR review on the separate correction commit, then run the pending adversarial, Craft, and panel reviews. Seek explicit approval before pushing, then confirm PR 73 CI on the pushed SHA.

## Handoff note

Jim's 2026-07-16 simplification decision supersedes stale readiness claims for the overbuilt checker. The 2026-07-20 local correction set addresses all three latest code-review findings and aligns ordinary validation with the shared checker's changed-file scope without expanding that deliberately small design. Jim's 2026-07-20 metadata decision is recorded consistently without changing the existing `MAINTAINING.md` contract. The separate 2026-07-21 local commit corrects the final four ADR-review findings without changing skill implementation. Remote PR head `12806a9` predates all local correction commits; exact local HEAD is unpushed. Final ADR review must rerun, and clean-context, adversarial, Craft, panel reviews and CI remain pending. The no-push gate remains in force.
