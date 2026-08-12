# GSD State

## Current Position

- Phase: released-truth source-of-truth decision
- Plan: supersede ADR-0003 before documentation remediation
- Task: review Proposed ADR-0016
- Status: adversarial blockers; attended remediation checkpoint
- Mode: attended
- Branch: `adr/released-and-usable-truth`
- Base: `origin/main` at `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Proposed ADR commit: `5716bbe539c352b7da880b3a0ad54dd3d475e546`
- Implementation: not started; ADR acceptance remains human-only

## Decision Intent

- Public rendered developer documentation and the published developer skill should describe released, publicly obtainable, compatible, capability-evidenced usable truth.
- Known released defects and safe alternatives are part of that truth.
- Moving default branches prepare the next release; they do not silently advance the public documentation.
- `target-manifest` remains pre-release/preview truth; `current-merged-truth` retires from the default public surface.

## Review State

- Repo-local ADR review: valid after the first correction pass.
- Goal verification: passed; commit adds only one Proposed ADR and changes no Accepted ADR or implementation.
- Structural validation: ADR governance passed with 1 ADR checked; 20 governance tests passed; `git diff --check` passed.
- Adversarial review: `NOT-READY`.
  - HIGH: ADR-0004 supersession must cover default-branch detector/source-resolution semantics for released records, not only restamping.
  - HIGH: release promotion needs durable minimum evidence semantics for release identity, clean obtainability, capability/runtime evidence, deployed-network identity, and retaining an older baseline.
  - HIGH: the motivating v0.11.2 audit is not reproducible from this branch or an immutable link.
  - MEDIUM: skill capability/defect consistency needs explicit validation, not only matching refs.
  - MEDIUM: rendered installation/version guidance must identify an older supported baseline when a newer public release is unsuitable.
- Craft Review: concerns.
  - CONFORMANCE: add template-aligned prospective Acceptance metadata.
  - CONFORMANCE: replace the informal audit reference with an inspectable immutable artifact.
  - CONFORMANCE: replace British spellings with repo-required American English.
- Clean-context gate: deferred because the Claude lane was unavailable due to expired OAuth. No substitute was used.
  - `models: unavailable (auth) · 0s`
- CI arbiter: no remote branch/PR exists; local evidence is weaker and must not be called CI-green.

## Constraints

- Do not edit Accepted ADR-0003 or ADR-0004.
- Do not mark ADR-0016 Accepted autonomously.
- Do not implement manifest, tooling, policy, or rendered-documentation changes before the ADR decision gate.
- Do not open a PR without Jim's explicit confirmation.

## Next

- Remediate the Proposed ADR and evidence reproducibility findings, rerun ADR review, verification, adversarial, Craft, and the deferred clean-context gate, then return to Jim for the human acceptance decision.
