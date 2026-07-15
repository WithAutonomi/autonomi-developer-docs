# ADR-0005: Subscription-billed daily scheduled routine as the interim trigger, over repository_dispatch webhooks and API-billed CI

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0004 (execution tiers); `planning/routines/upstream-sweep.md` §"Trigger shape" / §"Alignment with implementation-plan.md Section 8"; `planning/implementation-plan.md` §8; deployment-venue notes in vault `Inbox/Untitled 43.md`; build commit `a6bce6be` (2026-05-04)

> Retrospective ADR. The scheduled-run architecture shipped 2026-05-04; execution-venue and billing details are folded in here.

## Context

`planning/implementation-plan.md` §8 describes the eventual "push" architecture: upstream repos install a `notify-docs.yml` workflow that fires a `repository_dispatch` at the docs repo on merge, which collates per-event and opens targeted PRs. That design depends on write access to every upstream repo to install the notifier — a cross-org dependency we do not control and cannot land quickly.

We needed drift handling working **now**, across upstream repos in orgs we do not own (e.g. `saorsa-labs`), without waiting on notifier installation anywhere. Two further constraints shaped the answer: the prose tier needs a frontier model (ADR-0004), and **there is no budget for API credits** — the automation has to run on the frontier-model access the team already pays for through ordinary subscriptions, not metered API billing.

## Decision Drivers

- Must work **without** installing anything in upstream repos.
- Must run **unattended on a schedule** with a bounded worst-case drift latency.
- Must run the prose tier on a **frontier model** (ADR-0004), which GitHub Actions runners cannot host.
- **No API-credit budget:** frontier-model work must run against a **pre-existing team subscription via OAuth**, not metered API billing.
- Must be **forward-compatible** with the eventual `repository_dispatch` arm, not a throwaway.
- Prompt/behaviour must stay **version-controlled and reviewable**, not buried in a hosting UI.

## Considered Options

1. **Wait for `repository_dispatch` / `notify-docs.yml`.** Rejected as the *only* path: blocks all drift handling on cross-org installs we do not control.
2. **GitHub Actions cron, or the GitHub-installed Claude app, running the model in CI.** Rejected: Actions runners cannot host the frontier model, and the GitHub-app path is **API-billed** — materially more expensive, with no budget for it. It also couples the run to CI infrastructure and its secret/quota constraints.
3. **Subscription-billed hosted scheduled agent routine that polls daily**, calls the deterministic scanner, and runs the tiered model work under a team member's OAuth session. Chosen as the interim arm, sitting alongside (not replacing) the eventual push arm.

## Decision

We will run the sweep as a **scheduled agent routine that polls once per day, billed to a team member's subscription via OAuth** rather than metered API credits.

- **Cadence:** daily, off-peak (≈09:00 UTC), comfortably above the one-hour minimum interval for hosted routine schedules. Worst-case drift latency is ~24h; a missed slot is recovered by the next day's run.
- **Execution venue:** the routine currently runs as a **Claude Code scheduled routine from Jim's desktop**, under **Jim's Claude subscription (OAuth)** — so it depends on that account and setup. GitHub access rides the connected **Claude GitHub App** (no `GITHUB_TOKEN`/PAT required; PRs attributed to the user's GitHub identity), and `ANTHROPIC_API_KEY` is deliberately left **unset** so runs never silently fall through to API billing. (A Claude Code *web* routine at `claude.ai/code/routines` is an equivalent surface for the same design, explored in `Inbox/Untitled 43.md`; the billing and auth model are the same.)
- **Model tier is per ADR-0004:** the frontier model is spent only on prose; metadata sweeps can run on an efficient model. Concrete models are routine config, not repo config.
- **Prompt by reference, not paste:** the routine UI carries only a ~3-line bootstrap instructing the agent to read `planning/routines/upstream-sweep-prompt.md` from the cloned repo and follow it exactly. Prompt changes therefore ship via normal PR review — no routine edit.
- **Positioned as interim, not terminal:** this is the hosted-scheduled, polling equivalent of implementation-plan §8 Tiers 1+2. When `notify-docs.yml` rolls out upstream, the same routine can grow a webhook-receiver arm without invalidating the daily-poll v1.

## Consequences

### Positive

- Drift handling works immediately across upstreams in orgs we do not control, with zero upstream installation.
- Frontier-model prose runs at **no metered API cost** — it draws on subscription access the team already holds, which is what makes a daily cadence affordable.
- The frontier tier runs in a venue that supports it.
- Behaviour is version-controlled (prompt-by-reference), so the routine's logic is reviewable and auditable in git.
- No long-lived PAT to store or rotate; auth rides the GitHub App.

### Negative / Trade-offs

- Up to ~24h latency versus a push architecture's near-real-time reaction.
- Polling re-scans the whole repo daily even when nothing changed (cheap, but not free).
- **Single-account dependency (bus factor):** the routine runs under Jim's subscription and desktop setup, so it is tied to that account being active and in good standing. Moving it to a shared or service identity is unresolved and is the main fragility of this arrangement.
- Execution-venue config (schedule, model tiers, any secrets) lives **outside** the repo in the hosting UI, so it cannot be fully captured in version control — only the behaviour (the prompt) is.
- Dependence on hosted-routine availability and plan quota (a missed slot degrades to next-day recovery).

### Neutral / Operational

- Concrete model choices for the efficient/frontier tiers (ADR-0004) and the schedule are set in the routine config, not the repo; only the *requirement* is recorded in the prompt/policy.
- Credential precedence for the scanner's reads is documented in `upstream-sweep.md` (GITHUB_TOKEN → `gh auth token` → anonymous REST → `git ls-remote`); the current path relies on the GitHub App and needs none of it.

## Validation

- First-run check: within ~10 minutes of the trigger, expect either a silent no-drift exit, up to two PRs, and/or manual-review issues; nothing appearing means the routine did not fire (GitHub App scope or schedule misconfig), per `Inbox/Untitled 43.md`.
- Billing check: `ANTHROPIC_API_KEY` must remain unset in the routine environment so runs stay on subscription billing; a run that switches to API billing is a misconfiguration.
- Forward-compatibility check: the eventual `notify-docs.yml` arm must be addable without changing the daily-poll behaviour; if it forces a rewrite, revisit this ADR.
- Review trigger: adopting the `repository_dispatch` push arm as primary, moving off subscription/OAuth billing, or moving the routine off a personal account to a shared identity supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
