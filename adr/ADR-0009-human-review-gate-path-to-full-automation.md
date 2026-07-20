# ADR-0009: Human review gate now, with a path to full automation via AI-panel review and human escalation

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0005 (scheduled routine), ADR-0006 (PR tracks), ADR-0007 (fail-closed topology); `planning/routines/upstream-sweep.md` §"Out of scope" (auto-merge deferred to v1.5); `planning/implementation-plan.md` §8

> Retrospective ADR capturing both the current gate and the intended end-state. The current-state parts are settled; the end-state (AI-panel review, auto-merge) is **intent**, not yet built — called out as such below.

## Context

The **ultimate intention** is a fully automated pipeline: any change in an upstream repository is reflected in the documentation **without human intervention**, while maintaining very high, demonstrable, tested accuracy. That is the goal, and we have not reached it yet.

Two things stand between the current system and that goal. First, trust: the daily sweeps are reliable and the PRs are largely good, but prose PRs still occasionally contain inaccuracies, so a human must currently read them before merge. Second, mechanism: there is no automated reviewer that could stand in for that human with enough confidence to merge unattended. This ADR records how we gate today and the shape of the path to full automation, so the intent is not lost and the interim gate is not mistaken for the destination.

## Decision Drivers

- Accuracy is non-negotiable: wrong docs are worse than stale docs, so nothing merges unverified.
- The end goal is **no routine human intervention**, with accuracy maintained by construction and testing, not by a person eyeballing every PR.
- The routine already produces structurally-constrained, self-checked PRs (ADR-0006/0007), so the missing piece is trustworthy *review*, not trustworthy *generation*.
- Automation should be able to **escalate to a human** for the cases it cannot clear, rather than choosing between "merge blindly" and "block everything."

## Considered Options

1. **Auto-merge now.** Rejected: prose PRs still carry occasional inaccuracies; unattended merge would publish them.
2. **Permanent human review.** Rejected as the *end-state*: it caps throughput on human availability and contradicts the fully-automated goal, even though it is the correct *interim* gate.
3. **Human gate now; evolve to an AI review panel that can merge clean PRs and escalate uncertain ones to humans.** Chosen as the trajectory.

## Decision

We will keep a **human review gate as the current merge control**, while treating full automation as the explicit destination reached by strengthening *review*, not by loosening the gate.

- **Now (settled):** every routine PR is opened for human review; prose PRs are opened as drafts (ADR-0006) and a person promotes and merges them after reading. Ambiguity and failures are surfaced as issues, never merged (ADR-0007). Auto-merge is deferred (`upstream-sweep.md` §"Out of scope" marks it v1.5).
- **Assessment (current):** the metadata sweeps appear reliable enough to be candidates for full automation first; the prose track is close but not yet trustworthy for unattended merge because of residual inaccuracies. The sweep track and the prose track can therefore cross the automation threshold **independently**.
- **Intended end-state (not yet built):** replace the routine human read with an **AI review panel** — multiple independent agents reviewing each PR against the source-of-truth evidence and `CLAUDE.md` (ADR-0010) — that can approve and merge a clean PR and **escalate to human team members** when reviewers disagree or confidence is low. Provider diversity is desirable: reviews by both Anthropic and OpenAI frontier models, each run under its own subscription/OAuth (consistent with ADR-0005's no-API-budget constraint), so the reviewers are genuinely independent rather than one model checking itself.

## Consequences

### Positive

- Nothing inaccurate is published while the gate is human: accuracy is protected today.
- The end-state is written down, so the interim gate is understood as a stage, not the design's ceiling.
- Splitting the automation threshold by track lets the reliable sweep path advance without waiting on the prose path.
- Provider-diverse AI review reduces correlated blind spots and keeps escalation to humans as a safety valve.

### Negative / Trade-offs

- Human review is a throughput bottleneck and a standing time cost until the panel exists.
- An AI review panel is non-trivial to build and to trust; a panel that merges wrongly is worse than a slow human gate, so the bar for switching is high.
- Provider-diverse review adds operational surface (multiple subscriptions/OAuth sessions, multiple harnesses).

### Neutral / Operational

- The merge gate (human → AI-panel-with-escalation) is operational configuration; it does not alter ADR-0003's source-of-truth model or ADR-0006's envelopes.
- "Demonstrable, tested accuracy" implies a measurable accuracy signal (e.g. human-agreement rate on PRs) as the trigger for advancing a track — see Validation.

## Validation

- Current gate: no routine PR merges without human promotion; ambiguous/failed runs appear as issues, not merges (ADR-0007).
- Advancement criterion: a track moves to panel-gated auto-merge only when it clears an explicit, measured accuracy bar (e.g. sustained high reviewer/human agreement with no published inaccuracies over a defined window). The bar and window are set when the panel is specified.
- Review trigger: enabling any auto-merge, or standing up the AI review panel, is an architectural change that supersedes or extends this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
