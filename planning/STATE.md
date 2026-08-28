# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: reconcile concise ADR checkpoint before final gates
- Status: ADR passed focused review; checkpoint contradiction found; attended checkpoint
- Mode: attended
- Branch: `adr/released-and-usable-truth`
- Draft PR: https://github.com/WithAutonomi/autonomi-developer-docs/pull/98
- Branch point: `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Current draft-PR base: `origin/main` at `49e202c818bab1be780b81c28e5d0718cfb89b1c`
- Current concise ADR content: redraft `afdaa07ec909475f69fff16229952559b1e415ee`; tightening `f326e0c3f65de0646495da02d6eb74b70dac966f`; evidence-alignment correction `dfe2161`
- Implementation: not started; ADR acceptance remains human-only

## Decision Intent

- Public documentation describes stable or general-availability software available through supported public routes.
- An explicit release baseline provides exact provenance for released components, shipped dependencies, and relevant deployed-network behavior.
- Unreleased source may prepare future documentation but cannot support default public claims.
- Known defects and unsupported tasks are represented honestly; pre-release documentation remains separate.
- A separate developer skill is outside this decision.

## Review State

- First remediation commit `735091d` addresses the initial adversarial and Craft findings: ADR-0004 source-resolution/drift semantics, seven durable promotion-evidence groups, branch-local audit evidence, docs/skill capability consistency, explicit older-baseline guidance, Prospective Acceptance metadata, and American English.
- Second correction commit `57ec56c` disqualifies withdrawn, insecure, incompatible, or baseline-noncompliant incumbents and relabels Python/Rust source-install routes as metadata-identified but not clean-install/runtime verified.
- Structural validation after the second correction: ADR governance passed with 1 ADR checked; 20 governance tests passed; `git diff --check origin/main...HEAD` passed; worktree was clean.
- Final independent code review at `5dbecd5`: passed with no findings. ADR governance passed; 20 governance tests passed; `git diff --check origin/main...HEAD` passed; Accepted ADRs remained byte-identical.
- Goal verification at `5dbecd5`: passed, 7/7 goals verified. No scope gaps or unauthorized implementation found.
- Adversarial re-review at `ff9761a`: `NOT-READY` with four HIGH and three MEDIUM findings.
  - HIGH: candidate admission does not explicitly exclude draft/pre-release artifacts or apply symmetric safety/security qualification.
  - HIGH: deterministic newest-candidate discovery/ordering and continuing incumbent requalification across releases, artifacts, advisories, and deployed-network changes are not durable invariants.
  - HIGH: supersession is incomplete because released-only provenance conflicts with Accepted ADR-0006 and ADR-0014, with an impact on ADR-0013's stamp-refresh mechanism.
  - HIGH: the repository has an applicable PR-triggered CI arbiter at `.github/workflows/adr-governance.yml`; no CI run exists for this unpushed branch.
  - MEDIUM: docs/skill capability parity is ambiguous against ADR-0013's pointer-based skill model.
  - MEDIUM: public release identity requirements do not distinguish distributable artifacts from exact transitive dependency refs without their own release.
  - MEDIUM: code-review and goal-verification claims covered commit `5dbecd5`, not the later checkpoint/state-only HEAD, and their detailed reports were not branch-local.
- Adversarial reviewer: OpenAI GPT-5.6-sol; implementer provider was not recorded, so cross-provider independence cannot be confirmed and evidence is weaker.
- ADR governance review confirmed that the policy corrections belong in existing Proposed ADR-0016 and require no new ADR.
- Adversarial remediation commit `fb67648` addresses the policy findings by adding stable/general-availability eligibility, symmetric security qualification, deterministic release discovery/ordering, continuing incumbent requalification, precise ADR-0003/0004/0006/0013/0014 supersession, pointer-compatible skill parity, and separate distributable/dependency identity contracts.
- Independent code review at `e3df509` returned `issues_found`; the exact report is committed at `planning/adr-0016-code-review-e3df509.md`.
  - HIGH: candidate selection is undefined if maximal eligible sets fail qualification while a dominated older set could pass.
  - HIGH: continuing incumbent requalification omits provenance-integrity changes, mandatory-baseline changes, and newly discovered non-security runtime/capability evidence.
  - MEDIUM: mutable installation aliases can move to an unqualified release after a point-in-time clean-install check.
- Goal verification did not run because code review blocked advancement. Adversarial re-review, Craft, and fresh clean-context remain pending.
- Lifecycle correction commit `9c2f1da` defines deterministic newest-first evaluation across all eligible sets, requalification on every qualification-input change, immutable default install selectors, and alias-target requalification. Local ADR governance, 20 governance tests, and `git diff --check` passed.
- Independent code review at `2dd687b` resolved the two previous HIGH lifecycle findings and found two remaining issues; the exact report is `planning/adr-0016-code-review-2dd687b.md`.
  - HIGH: skill pointers require fetched released docs but lack a durable untrusted-content/prompt-injection boundary.
  - MEDIUM: mutable aliases are prohibited as default/recommended selectors but later language allows them to continue being recommended after requalification.
- Goal verification did not run because code review blocked advancement.
- Pointer-security correction commit `4873f36` makes fetched docs untrusted factual input that cannot override instructions or gates, and prohibits mutable aliases from ever being default, supported, or recommended install commands. Local ADR governance, 20 governance tests, and `git diff --check` passed.
- Final independent code review at `481ca8c`: passed with no findings. The exact report is committed at `planning/adr-0016-code-review-481ca8c.md`.
- Exact-HEAD goal verification at `9bd4f6f`: passed, 10/10 decision-contract goals verified with no gaps. The report is committed at `planning/adr-0016-verification-9bd4f6f.md`.
- Exact-head adversarial re-review at `dfd14da`: `NOT-READY`. The report is committed at `planning/adr-0016-adversarial-dfd14da.md`.
  - HIGH: the ADR simultaneously makes mandatory-baseline qualification global to one coherent release set and permits journey-local retention/withdrawal. One unit of qualification and fallback must be chosen.
  - LOW: state/checkpoint must distinguish the historical branch point from the current PR base and describe scope-gated CI checks honestly.
- Craft and clean-context did not run because adversarial blocked advancement.
- Jim chose option 2 on 2026-08-20: one active coherent release set with journey-local support status, no mixed versions or per-journey old-release fallback, and global no-supported-baseline only when no eligible set supplies complete routes for every mandatory core outcome.
- Journey-local amendment `fb00f10` formalizes that decision, including same-interface complete routes, global set selection/fallback, atomic optional-journey regression disclosure, journey-keyed manifest/docs/skill parity, and the minimum end-to-end store-and-retrieve outcome. Local ADR governance and 20 tests passed; exact-head draft-PR CI and GitBook checks are green.
- Exact-head adversarial re-review remained pending after the journey-local amendment.
- Exact-head code review at `b1e4846`: passed with no findings and all qualification truth-table scenarios passed. Report: `planning/adr-0016-code-review-b1e4846.md`.
- Exact-head goal verification at `39e2cdf`: passed, 10/10 goals and all required truth-table scenarios verified with no gaps. Report: `planning/adr-0016-verification-39e2cdf.md`.
- Exact-head adversarial re-review at `ef646b9`: `NOT-READY`. Report: `planning/adr-0016-adversarial-ef646b9.md`.
  - HIGH: top-level `SDK` continuity still permits incompatible bindings/transports to be combined into a false complete route.
  - HIGH: allowing CLI to become the only recommended complete route changes ADR-0011's unconditional SDK-primary stance, so ADR-0011 must be precisely superseded rather than called intact.
  - MEDIUM: branch-local truth-table evidence must include concrete binding, transport, installation, runtime/configuration, and carried-state identities.
  - LOW: state/checkpoint/PR evidence was stale, and the historical v0.11.2 defect sentence needs past-tense scoping.
- Craft and clean-context did not run because adversarial blocked advancement.
- Jim then directed a scope reset: ADR-0016 should state only the durable rule that public documentation covers stable software the public can obtain. Skill ownership, journey models, route truth tables, comparison algorithms, and implementation mechanics moved out of the ADR.
- Concise content commit `afdaa07` replaced the detailed proposal; `f326e0c` tightened it to 477 words including metadata and headings. It now supersedes only the public source-selection/provenance clauses in ADR-0003, ADR-0004, and ADR-0006 and explicitly leaves any separate developer skill out of scope.
- Exact-head ADR Governance, 20 local governance tests, diff check, and draft-PR CI passed for `f326e0c`. The earlier route-continuity and ADR-0011 findings applied to removed decisions and require fresh review rather than mechanical remediation.
- Fresh code review at `752099a`: passed with no findings. The 477-word ADR, template, American English, partial supersession, target-architecture scope, Accepted-ADR immutability, and exact-head CI all passed. Report: `planning/adr-0016-code-review-752099a.md`.
- Goal verification at `85fde83`: ADR content passed all 11 applicable decision goals; the twelfth state/PR accuracy goal found two bookkeeping gaps. Report: `planning/adr-0016-verification-85fde83.md`.
  - `STATE.md` still described removed skill/mode intent.
  - PR #98 still called the completed fresh code review pending.
- Reverification at `d09520e`: ADR content and the first bookkeeping corrections passed; two further checkpoint accuracy gaps and the invalid recorded `f326e0c` full SHA remained. These are corrected in the current state/checkpoint update.
- Final exact-head reverification at `58545cd`: passed 12/12 with no gaps. Report: `planning/adr-0016-verification-58545cd.md`.
- Fresh adversarial review at `d18a63b`: `READY-WITH-NITS`, with no CRITICAL, HIGH, or MEDIUM findings. Report: `planning/adr-0016-adversarial-d18a63b.md`.
  - LOW: validation wording should preserve the deployed-network evidence path. Corrected in `dfe2161`.
  - LOW: PR body lagged final verification. Corrected after review.
- Focused code review at `fc49173`: ADR content passed with no findings; one MEDIUM checkpoint-consistency issue remained. Report: `planning/adr-0016-code-review-fc49173.md`.
  - The accumulated checkpoint mixed current READY-WITH-NITS status with historical blocker/pending language. It is replaced by a concise current checkpoint; detailed history remains in the review reports.
- Clean-context gate: deferred because the Claude lane was unavailable due to expired OAuth. No substitute was used.
  - `models: unavailable (auth) · 0s`
- CI arbiter: draft PR #98. Exact reverification head `d09520e` passed ADR Governance run `33189218449` and both GitBook checks. Prose/sweep checks returned success as scope-gate no-ops, not substantive coverage.
- Freshness risk: the imported v0.11.2 audit is explicitly historical; `antd` v0.12.0 has since released and issue #233 has closed. A fresh candidate-release audit is required before implementation, regardless of ADR acceptance.

## Constraints

- Do not edit Accepted ADR-0003 or ADR-0004.
- Do not mark ADR-0016 Accepted autonomously.
- Do not implement manifest, tooling, policy, or rendered-documentation changes before the ADR decision gate.
- Do not open a PR without Jim's explicit confirmation.

## Next

- With Jim's attended approval, rerun focused exact-head review of the concise checkpoint, then run Craft and clean-context. Do not merge, accept the ADR, or begin implementation.
