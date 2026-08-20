# ADR-0016 code review — e3df509

- Date: 2026-08-20
- Reviewed commit: `e3df50957d2691b8661c503bfd6f34cc960aece9`
- Base: `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Reviewer: codereviewer — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Result: `issues_found`

## Checks

- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20 tests.
- `git diff --check origin/main...HEAD`: passed.
- Full diff inspected: four added files, 627 insertions.
- Content commit `fb67648a8ac0a874ea94a1e1c3e208490a052a8c`: inspected in full.
- Accepted ADR-0003 through ADR-0007 and ADR-0012 through ADR-0015: byte-identical to base.
- ADR-0016 remained Proposed with human-only acceptance.
- CI: not run. The pull-request-triggered arbiter exists; local results are not CI-green.
- Worktree: clean at review time.

## Findings

### HIGH — Candidate selection after qualification failure is undefined

Anchors: `adr/ADR-0016-released-truth-for-public-developer-docs.md:43,65-71,83-85` at the reviewed commit.

The ADR promises the newest release set that passes, but computes maximal sets from eligibility before qualification. If every maximal eligible set fails while a dominated older set would pass, it does not say whether to evaluate that set, retain an incumbent, or declare no baseline. Different conforming specifications could produce different outcomes.

Required disposition: define selection over qualified sets, deterministic iterative fallback through eligible sets, or an explicit no-fallback invariant.

### HIGH — Continuing incumbent requalification omits qualification-changing events

Anchors: `ADR-0016:67,83-85,158-168` at the reviewed commit.

Outside promotion decisions, requalification is triggered only by artifact availability, safety/security evidence, and deployed-network changes. It omits provenance-integrity changes, mandatory-baseline changes, and newly discovered non-security runtime or capability defects. An incumbent could remain supported after a mandatory journey is proven broken when no new candidate exists.

Required disposition: trigger requalification whenever any qualification input changes.

### MEDIUM — Mutable installation aliases can bypass immutable released identity

Anchors: `ADR-0016:57,67,78` at the reviewed commit.

Mutable aliases are rejected only when they lack an immutable underlying identity. A point-in-time clean-install check could approve a documented `latest`-style route that later resolves to an unqualified release without triggering incumbent requalification.

Required disposition: require default installation routes to pin immutable versions or digests, or make alias-target movement a mandatory requalification event.

## Remaining risks

- Applicable CI has not run and requires an authorized pull request.
- Goal verification, adversarial re-review, Craft, and clean-context remain outstanding after remediation.
- The v0.11.2 audit is historical; a fresh candidate audit is required before implementation.
- Implementer provider is unrecorded, so cross-provider independence cannot be confirmed.
