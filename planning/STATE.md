# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: rerun adversarial review of Proposed ADR-0016
- Status: code review and goal verification passed; adversarial pending
- Mode: attended
- Branch: `adr/released-and-usable-truth`
- Base: `origin/main` at `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Proposed ADR commits: initial `5716bbe539c352b7da880b3a0ad54dd3d475e546`; first remediation `735091d7ed55db90eb48129c879796dc6ebfe963`; second correction `57ec56cb90db89583603f4cf075c9f7d272a9b87`; adversarial remediation `fb67648a8ac0a874ea94a1e1c3e208490a052a8c`; lifecycle correction `9c2f1da15de685e54fdb0ef8eceeedfa2692f153`; pointer-security correction `4873f368feec5183b7a69c493c86d2beb6efe8b5`
- Implementation: not started; ADR acceptance remains human-only

## Decision Intent

- Public rendered developer documentation and the published developer skill should describe released, publicly obtainable, compatible, capability-evidenced usable truth.
- Known released defects and safe alternatives are part of that truth.
- Moving default branches prepare the next release; they do not silently advance the public documentation.
- `target-manifest` remains pre-release/preview truth; `current-merged-truth` retires from the default public surface.

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
- Clean-context gate: deferred because the Claude lane was unavailable due to expired OAuth. No substitute was used.
  - `models: unavailable (auth) · 0s`
- CI arbiter: `.github/workflows/adr-governance.yml`, triggered for ADR-changing pull requests. No remote branch/PR or exact-SHA CI run exists; local evidence is weaker and must not be called CI-green.
- Freshness risk: the imported v0.11.2 audit is explicitly historical; `antd` v0.12.0 has since released and issue #233 has closed. A fresh candidate-release audit is required before implementation, regardless of ADR acceptance.

## Constraints

- Do not edit Accepted ADR-0003 or ADR-0004.
- Do not mark ADR-0016 Accepted autonomously.
- Do not implement manifest, tooling, policy, or rendered-documentation changes before the ADR decision gate.
- Do not open a PR without Jim's explicit confirmation.

## Next

- Rerun adversarial against the proposal and branch-local review evidence. If it passes, run Craft and clean-context. CI green will later require Jim's explicit authorization for the exact PR action. Do not begin implementation.
