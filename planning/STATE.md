# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: remediate Proposed ADR-0016 adversarial findings
- Status: adversarial NOT-READY; attended checkpoint
- Mode: attended
- Branch: `adr/released-and-usable-truth`
- Base: `origin/main` at `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Proposed ADR commits: initial `5716bbe539c352b7da880b3a0ad54dd3d475e546`; first remediation `735091d7ed55db90eb48129c879796dc6ebfe963`; second correction `57ec56cb90db89583603f4cf075c9f7d272a9b87`
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
- Craft re-review and fresh clean-context were not run because the adversarial gate blocked advancement.
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

- With Jim's attended approval, remediate the adversarial policy, supersession, skill-parity, dependency-identity, and evidence-record findings; rerun code review and goal verification against the resulting HEAD; then rerun adversarial before Craft and clean-context. CI green will later require Jim's explicit authorization for the exact PR action. Do not begin implementation.
