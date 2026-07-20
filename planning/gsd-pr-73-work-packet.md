# GSD Work Packet — PR 73 ADR corrections

Date: 2026-07-15
Prepared by: OpenCode orchestrator
Requested agent/tool: OpenCode with independent ADR, adversarial, Craft, and panel review
Role requested: Coordinator / Implementer / Verifier
Review mode: ADR governance review, Adversarial review, Craft review, and multi-model panel

## Project / workspace

Project: Autonomi Developer Documentation
Repo/path: `WithAutonomi/autonomi-developer-docs`
Current source of truth: PR 73 branch `adr/relocate-and-retrospective-records` plus the decisions confirmed by Jim in the review discussion

## Owner-confirmed decisions

- Retrospective ADRs enter as Accepted records because Jim, the original decision owner, confirms that they faithfully capture decisions made before ADR governance existed. Their introducing PR remains reviewable until merge; immutability applies to the Accepted content on the default branch.
- ADR-0004 and ADR-0010 record intended invariants even where implementation currently diverges. Those divergences belong in planning, not in replacement ADRs unless the intended decision changes.
- The scheduled sweep is a Claude Code Remote routine using subscription-backed execution rather than metered API billing. The present implementation depends on Jim's Claude account, but the decision does not foreclose future subscription-backed providers, independent models, multimodal capabilities, or shared ownership.
- ADR-0011 itself is the information-architecture authority. Navigation and planning files are implementations or historical context, not alternative sources of the decision.
- `autonomi-developer` is the canonical vendor-neutral skill identity. Claude's `developer`, `start`, and `/developer:start` names are channel-specific packaging. Compatible runtimes can consume the raw artifact manually, and future multi-channel distribution may include skills.sh or a move to `WithAutonomi/skills`.

## Goal

Correct PR 73 so the relocated ADR governance works, the retrospective records accurately distinguish decisions from implementation conformance, and known implementation gaps are tracked outside the immutable ADRs.

## Read first

- `CLAUDE.md`
- `adr/ADR-0001-adopt-architecture-decision-records.md`
- `adr/ADR-0002-adrs-live-at-repo-root-not-docs.md`
- `adr/ADR-0003-verification-block-source-of-truth.md` through `adr/ADR-0014-skill-maintenance-workflow-and-registry-wiring.md`
- `adr/TEMPLATE.md`
- `adr/TOOLING.md`
- `.adr-kit.yaml`
- `scripts/adr-governance.py`
- `.github/workflows/adr-governance.yml`
- `planning/routines/upstream-sweep.md`
- `planning/routines/upstream-sweep-prompt.md`
- `skills/start/`

## Stage

Implementation and verification

## Approved slice

- Repair every stale `docs/adr` assumption in the relocated governance implementation and guidance.
- Add regression coverage proving `/adr` records are validated and Accepted records remain immutable.
- Keep ADR-0002 Accepted and make it supersede ADR-0001's location clause only.
- Replace ADR-0003 through ADR-0014's retrospective acceptance wording with the owner-confirmed wording agreed in review.
- Correct factual reconstruction where agreed: the Claude Code Remote routine, the site-wide `llms.txt`, ADR-0011 as the information-architecture authority, and the known provenance of `skills/start`.
- Make ADR-0012 unambiguous that `autonomi-developer` is the canonical vendor-neutral identity; Claude packaging is one current adapter, while compatible runtimes can consume the portable artifact manually.
- Add a planning artifact for current implementation-conformance gaps.
- Show Jim the complete local diff before any commit or push.

## Relevant artifacts

PR: `https://github.com/WithAutonomi/autonomi-developer-docs/pull/73`
ADR governance: ADR-0001 and `.adr-kit.yaml`
Plan/state: this packet and the conformance-gap artifact produced by the slice
Previous review: PR 73 review discussion in the active session

## Scope

- ADR governance script, test, workflow, and tooling guidance.
- ADR metadata and narrowly agreed factual wording.
- Planning documentation for implementation debt.

## Out of scope

- Implementing efficient/frontier model routing.
- Building terminology, prohibited-word, template, or verification-presence lint.
- Reworking the skill's bundled-versus-pointered content.
- Publishing to skills.sh or moving the skill to `WithAutonomi/skills`.
- Wiring `feeds_skills` into scanner dependency discovery.
- Changing repository branch-protection settings.
- Committing, pushing, merging, or publishing.

## Constraints / forbidden actions

- Do not change a retrospective decision merely to match a nonconforming implementation.
- Do not add fictional historical reviewers or acceptance ceremonies.
- Do not mark any new ADR Accepted autonomously.
- Do not edit `.gsd/gate.sh`, CI outside the explicitly in-scope ADR workflow, test harnesses outside the new governance regression coverage, or environment setup.
- Do not commit or push without Jim's explicit approval after diff review.

## Unattended mode / rigor profile

Unattended mode: No

Rigor profile:

- Meaningful governance and documentation work-unit.
- Run local governance and regression checks.
- Run fresh ADR, adversarial, Craft, and panel reviews before checkpoint.
- CI is the green of record, but no push is approved in this slice; report local evidence as provisional and state that PR CI has not run on the local changes.

## Verification required

- `python3 -m unittest discover -s scripts/tests -p 'test_adr_governance.py'`
- `python3 scripts/adr-governance.py`
- `GITHUB_BASE_REF=main python3 scripts/adr-governance.py`
- `git diff --check`
- Search for stale operational `docs/adr` references.
- Inspect the full diff against `origin/main` and the local incremental diff.
- Independent ADR governance review.
- Independent adversarial review.
- Independent Craft review.
- Independent panel review.

## Stop conditions

Stop and report if:

- the governance repair requires weakening Accepted-ADR immutability;
- a proposed wording change alters a confirmed historical decision rather than clarifying its record;
- implementation requires model-routing, broad docs lint, skill redesign, distribution publication, or branch-protection changes;
- a readiness claim would depend on uncommitted helper scripts or hidden environment state;
- local evidence conflicts with PR CI after any later approved push;
- any commit, push, merge, or publication is requested implicitly rather than explicitly approved.

## Required output

Return:

- sources read;
- files changed;
- exact verification evidence;
- independent review findings and dispositions;
- remaining risks and implementation gaps;
- the complete uncommitted diff summary for Jim's review;
- no commit or push.
