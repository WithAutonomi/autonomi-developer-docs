# ADR-0005: Subscription-billed daily scheduled routine as the interim trigger, over repository_dispatch webhooks and API-billed CI

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0004 (execution tiers); `planning/routines/upstream-sweep.md` §"Trigger shape" / §"Alignment with implementation-plan.md Section 8"; `planning/implementation-plan.md` §8; build commit `a6bce6be` (2026-05-04)

> Retrospective ADR. The scheduled-run architecture shipped 2026-05-04; execution-venue and billing details are folded in here.

## Context

`planning/implementation-plan.md` §8 describes the eventual "push" architecture: upstream repos install a `notify-docs.yml` workflow that fires a `repository_dispatch` at the docs repo on merge, which collates per-event and opens targeted PRs. That design depends on write access to every upstream repo to install the notifier — a cross-org dependency we do not control and cannot land quickly.

We needed drift handling working **now**, across upstream repos in orgs we do not own (e.g. `saorsa-labs`), without waiting on notifier installation anywhere. Two further constraints shaped the answer: the prose tier needs a frontier model (ADR-0004), and **there is no budget for API credits** — the automation has to run on the frontier-model access the team already pays for through ordinary subscriptions, not metered API billing.

## Decision Drivers

- Must work **without** installing anything in upstream repos.
- Must run **unattended on a schedule** with a bounded worst-case drift latency.
- Must run the prose tier on a **frontier model** (ADR-0004), which GitHub Actions runners cannot host.
- **No API-credit budget:** frontier-model work must run against **pre-existing subscription-backed access**, not metered API billing.
- Must be **forward-compatible** with the eventual `repository_dispatch` arm, not a throwaway.
- Prompt/behaviour must stay **version-controlled and reviewable**, not buried in a hosting UI.

## Considered Options

1. **Wait for `repository_dispatch` / `notify-docs.yml`.** Rejected as the *only* path: blocks all drift handling on cross-org installs we do not control.
2. **GitHub Actions cron, or the GitHub-installed Claude app, running the model in CI.** Rejected: Actions runners cannot host the frontier model, and the GitHub-app path is **API-billed** — materially more expensive, with no budget for it. It also couples the run to CI infrastructure and its secret/quota constraints.
3. **Subscription-billed hosted scheduled agent routine that polls daily**, calls the deterministic scanner, and runs the tiered model work under a team member's subscription-backed access. Chosen as the interim arm, sitting alongside (not replacing) the eventual push arm.

## Decision

We will run the sweep as a **scheduled agent routine that polls once per day using a team member's subscription-backed access** rather than metered API credits.

- **Cadence:** daily, off-peak (≈09:00 UTC), comfortably above the one-hour minimum interval for hosted routine schedules. Worst-case drift latency is ~24h; a missed slot is recovered by the next day's run.
- **Execution venue:** the sweep runs as a **Claude Code Remote routine** in a managed hosted environment under **Jim's Claude subscription/account**. It is scheduled remotely and executes in an ephemeral environment with a fresh repository clone. Durable outputs are written to GitHub as branches, pull requests, issues, and comments. GitHub access uses credentials available in the hosted routine environment, and `ANTHROPIC_API_KEY` is deliberately left **unset** so runs never silently fall through to API billing.
- **Billing model:** model execution uses subscription-backed access rather than metered API billing. This was chosen because the required frontier-model capability was available through an existing subscription, while viable automation alternatives at implementation time either required raw API expenditure or were not yet available.
- **Model tier is per ADR-0004:** the frontier model is spent only on prose; metadata sweeps can run on an efficient model. Concrete models are routine config, not repo config.
- **Prompt by reference, not paste:** the routine UI carries only a ~3-line bootstrap instructing the agent to read `planning/routines/upstream-sweep-prompt.md` from the cloned repo and follow it exactly. Prompt changes therefore ship via normal PR review — no routine edit.
- **Positioned as interim, not terminal:** this is the hosted-scheduled, polling equivalent of implementation-plan §8 Tiers 1+2. When `notify-docs.yml` rolls out upstream, the same routine can grow a webhook-receiver arm without invalidating the daily-poll v1.

## Consequences

### Positive

- Drift handling works immediately across upstreams in orgs we do not control, with zero upstream installation.
- Frontier-model prose runs at **no metered API cost** — it draws on subscription access the team already holds, which is what makes a daily cadence affordable.
- The frontier tier runs in a venue that supports it.
- Behaviour is version-controlled (prompt-by-reference), so the routine's logic is reviewable and auditable in git.
- No dependency on credentials stored on Jim's local machine; GitHub credentials live in the hosted routine environment.

### Negative / Trade-offs

- Up to ~24h latency versus a push architecture's near-real-time reaction.
- Polling re-scans the whole repo daily even when nothing changed (cheap, but not free).
- **Single-account dependency (bus factor):** the present routine depends on Jim's Claude subscription/account and its cloud-side routine configuration. If the account, schedule, selected model, or credentials become unavailable, runs stop or fail closed. Moving to shared ownership or diversifying across additional subscription-backed providers remains unresolved.
- Execution-venue config (schedule, model tiers, any secrets) lives **outside** the repo in the hosting UI, so it cannot be fully captured in version control — only the behaviour (the prompt) is.
- Dependence on hosted-routine availability and plan quota (a missed slot degrades to next-day recovery).

### Neutral / Operational

- Concrete model choices for the efficient/frontier tiers (ADR-0004) and the schedule are set in the routine config, not the repo; only the *requirement* is recorded in the prompt/policy.
- Credential precedence for the scanner's reads is documented in `upstream-sweep.md` (`GITHUB_TOKEN` → `gh auth token` → anonymous REST → `git ls-remote`). The hosted routine may use a configured token or connected app credentials; writes remain scoped to the docs repo.
- This decision does not bind the routine permanently to one provider. Future subscription-backed provider lanes, independent models, or multimodal capabilities can be considered without abandoning the core subscription-over-metered-API billing decision. Concrete providers and model versions remain operational configuration.

## Validation

- First-run check: inspect the hosted routine's run history after the scheduled trigger. A completed run may exit silently when it finds no drift; PRs or manual-review issues appear only when the outcome requires them. A missing run indicates an account or schedule problem, while a failed run or failure issue carries the execution diagnostic.
- Billing check: `ANTHROPIC_API_KEY` must remain unset in the routine environment so runs stay on subscription billing; a run that switches to API billing is a misconfiguration.
- Forward-compatibility check: the eventual `notify-docs.yml` arm must be addable without changing the daily-poll behaviour; if it forces a rewrite, revisit this ADR.
- Review trigger: adopting the `repository_dispatch` push arm as primary or moving from subscription-backed execution to metered API billing supersedes this ADR. Adding subscription-backed provider lanes or shared ownership does not supersede the core decision.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
