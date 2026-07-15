# ADR-0004: Tiered execution — deterministic detection, efficient-model metadata sweeps, frontier-model prose

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification blocks); `scripts/sweep_poll.py`; `planning/routines/upstream-sweep.md` §"Opus audit/write/verify loop"; build commit `a6bce6be` (2026-05-04); hardening commits `ddeb45a` (2026-05-09), `8c541eb` (2026-05-09), `f447f78`/`1ce7ef9`/`8348c72` (2026-05-11, session `019cz1M7pXuXFQykMZxfdXHm`)

> Retrospective ADR. Implemented 2026-05-04 and hardened through 2026-05-11.

## Context

The pipeline actually contains three kinds of work, each with a different cost/capability profile, and treating them as one wastes money and trust:

1. **Drift detection** — for each verification block, resolve upstream HEAD and compare SHAs. A pure, repeatable computation. No model judgement at all.
2. **Metadata-only sweeps** — when a drifted upstream change has no developer-facing impact, the work is to audit the diff, confirm it is genuinely metadata-only, and re-stamp the SHA (see ADR-0006's `claude/sweep-*` track). This needs light judgement, but not deep source comprehension or authoring.
3. **Prose sweeps** — when a change alters real behaviour, the work is to read the upstream diff and source, judge developer-facing impact, and write correct, voice-consistent documentation (ADR-0006's `claude/prose-*` track). This needs a frontier model.

Conflating these produces a system that is neither trustworthy (an LLM "detecting" drift is non-reproducible) nor efficient (running frontier-model inference to re-stamp a SHA that changed nothing a developer sees is pure cost). We also learned during hardening that a "detector" which silently swallows edge cases (missing token, an org that refuses fine-grained PATs, a null value in a map) is dangerous: it reports "no drift" when it actually failed to look. The detector therefore has to be strict and fail-closed, which is far easier to guarantee in deterministic code than in a model prompt.

## Decision Drivers

- Drift detection must be **deterministic and reproducible** — the same inputs give the same report every run.
- Detection must **fail closed**, never fail silent, on auth/network/parse/shape errors.
- Prose audit, rewriting, and verification need **frontier-model judgement** and cannot be scripted.
- Cheaper work must not pay frontier-model prices: **match the execution tier to the job**.
- Each tier should be independently testable and independently hardenable.

## Considered Options

1. **Model does everything**, including "notice what looks out of date." Rejected: non-reproducible, no audit trail, easy to hallucinate freshness, expensive to run over the whole repo.
2. **Script does everything**, including regenerating prose via templates. Rejected: cannot judge developer-facing impact or write correct, voice-consistent prose from an upstream diff.
3. **One frontier model for all model work** (detection stays scripted, but a single frontier model handles both metadata sweeps and prose). This is what the routine ran at build time. Retained as workable, but rejected as the target: it pays frontier prices to re-stamp SHAs that change nothing developer-facing.
4. **Tiered execution: deterministic detection, an efficient model for metadata sweeps, a frontier model for prose.** Chosen.

## Decision

We will run the pipeline in **three tiers, matching cost and capability to the work**:

- **Detection — `scripts/sweep_poll.py`, deterministic, no model.** It walks every verification block in `docs/**/*.md`, `version.json`, and `SKILL.md` frontmatter; resolves `(repo, ref)` via `repo-registry.yml` + GitHub default branch; and emits a per-record JSON drift report. It **fails closed** on auth, network, parse, shape, and unknown-mode errors (see ADR-0007), deliberately skips `target-manifest` blocks into a separate array, and never writes docs. Its report is a **candidate list, not a directive** — SHAs are bumped only after a per-page audit succeeds.
- **Metadata-only sweeps — an efficient model is sufficient.** Auditing a diff, confirming it carries no developer-facing change, and re-stamping the SHA (the `claude/sweep-*` track, ADR-0006) does not require a frontier model; an efficient model (Sonnet-class) is an appropriate floor.
- **Prose sweeps — a frontier model is required.** Reading upstream source, judging developer-facing impact, and writing/verifying documentation prose (the `claude/prose-*` track, ADR-0006) requires a frontier model, provider-agnostic (a Claude Opus-class or GPT-5.x-class model). There is no subagent layer for this work.
- **Model names are deliberately de-versioned in this decision.** The requirement is the *tier* ("efficient" vs "frontier"), not a specific model. For provenance: at build time the prose floor was specified as Opus 4.7+ (or GPT-5.5/5.6+), raised to Opus 4.8+ on 2026-06-18 (session `011PdDcd7X5C1aSz7sYqjSnz`); the current frontier is a later generation again. The floor should track "the current frontier," not a frozen version string.

## Consequences

### Positive

- Detection is reproducible and cheap; a human can re-run the scanner and get the identical drift report.
- Fail-closed detection means "no drift" genuinely means "looked, found nothing," not "failed to look."
- Prose quality is owned by a frontier model competent to write it, gated by audit and verification.
- Cost tracks value: the common case (no-drift and metadata-only re-stamps) never pays frontier-model prices; frontier inference is spent only where prose is actually rewritten.
- The tiers harden independently — most of the May 9–11 fixes were scanner shape/HTTP robustness with zero change to the prose loop.

### Negative / Trade-offs

- Frontier-model prose is the expensive tier, with cost and availability implications on any run that rewrites prose.
- Tiering adds routing complexity: the metadata-vs-prose classification must be reliable, or a prose-impacting change could be handled by the cheaper tier. Classification is the routine's job (see the page-batching rule) and ambiguous records fail closed to human review (ADR-0007), which bounds this risk.
- Multiple artifacts to maintain (scanner code + routine prompt), and potentially more than one model configured.

### Neutral / Operational

- The scanner's JSON output schema (`status`, `records`, `errors`, `target_manifest_skipped`, `notices`) is a contract consumed by the routine; additive fields are safe, shape changes are not.
- Which concrete models fill the "efficient" and "frontier" tiers is routine config (see ADR-0005), not a repo change; only the *tier requirement* is recorded in the prompt and policy.

## Validation

- Re-running `scripts/sweep_poll.py` must return `status: "ok"` and a reproducible `records` list; the routine re-runs it as a post-write check.
- Scanner unit behaviour is exercised by the shape/type guards added in `ddeb45a` and `8c541eb` (non-string SHA, null/empty `verified_commits`, empty frontmatter all fail closed).
- Review trigger: any move of audit/verification responsibility into the scanner, or of detection into the model, supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
