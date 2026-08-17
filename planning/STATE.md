# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: remediate Proposed ADR-0016 review findings
- Status: code-review blockers; attended checkpoint
- Mode: attended
- Branch: `adr/released-and-usable-truth`
- Base: `origin/main` at `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Proposed ADR commits: initial `5716bbe539c352b7da880b3a0ad54dd3d475e546`; remediation `735091d7ed55db90eb48129c879796dc6ebfe963`
- Implementation: not started; ADR acceptance remains human-only

## Decision Intent

- Public rendered developer documentation and the published developer skill should describe released, publicly obtainable, compatible, capability-evidenced usable truth.
- Known released defects and safe alternatives are part of that truth.
- Moving default branches prepare the next release; they do not silently advance the public documentation.
- `target-manifest` remains pre-release/preview truth; `current-merged-truth` retires from the default public surface.

## Review State

- Remediation commit `735091d` addresses the first adversarial and Craft findings: ADR-0004 source-resolution/drift semantics, seven durable promotion-evidence groups, branch-local audit evidence, docs/skill capability consistency, explicit older-baseline guidance, Prospective Acceptance metadata, and American English.
- Structural validation after remediation: ADR governance passed with 1 ADR checked; 20 governance tests passed; `git diff --check origin/main...HEAD` passed; worktree was clean.
- Independent code review: `issues_found`.
  - HIGH: the retained-incumbent rule can preserve a release that has itself become withdrawn, insecure, network-incompatible, or baseline-noncompliant. Retention must require the incumbent still to pass applicable safety and baseline requirements; otherwise guidance must narrow or state that no supported baseline exists.
  - MEDIUM: the audit calls Python and Rust exact-source routes installable without clean-install commands/results. Add reproducible evidence or relabel them as identified but not runtime-verified.
- Goal verification, adversarial re-review, and Craft re-review have not run on remediation commit `735091d` because code review blocked advancement.
- Clean-context gate: deferred because the Claude lane was unavailable due to expired OAuth. No substitute was used.
  - `models: unavailable (auth) · 0s`
- CI arbiter: no remote branch/PR exists; local evidence is weaker and must not be called CI-green.

## Constraints

- Do not edit Accepted ADR-0003 or ADR-0004.
- Do not mark ADR-0016 Accepted autonomously.
- Do not implement manifest, tooling, policy, or rendered-documentation changes before the ADR decision gate.
- Do not open a PR without Jim's explicit confirmation.

## Next

- With Jim's attended approval, add the incumbent-disqualification invariant and correct the audit's Python/Rust installability evidence labels, then rerun code review, goal verification, adversarial, Craft, and the deferred clean-context gate before returning for the human acceptance decision.
