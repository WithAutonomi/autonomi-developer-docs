# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: rerun Proposed ADR-0016 review after state correction
- Status: substantive corrections passed; code-review bookkeeping finding; attended checkpoint
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
- Independent code re-review: both substantive findings resolved; `issues_found` only because this state file still described the now-completed correction. This update corrects the handoff, but the code-review gate has not yet been rerun.
- Goal verification, adversarial re-review, and Craft re-review have not run on commit `57ec56c` because the code-review gate stopped on the stale-state finding.
- Clean-context gate: deferred because the Claude lane was unavailable due to expired OAuth. No substitute was used.
  - `models: unavailable (auth) · 0s`
- CI arbiter: no remote branch/PR exists; local evidence is weaker and must not be called CI-green.
- Freshness risk: the imported v0.11.2 audit is explicitly historical; `antd` v0.12.0 has since released and issue #233 has closed. A fresh candidate-release audit is required before implementation, regardless of ADR acceptance.

## Constraints

- Do not edit Accepted ADR-0003 or ADR-0004.
- Do not mark ADR-0016 Accepted autonomously.
- Do not implement manifest, tooling, policy, or rendered-documentation changes before the ADR decision gate.
- Do not open a PR without Jim's explicit confirmation.

## Next

- With Jim's attended approval, rerun code review now that the state record is accurate, then continue to goal verification, adversarial, Craft, and the deferred clean-context gate before returning for the human acceptance decision.
