# ADR-0007: Fail-closed operation and the GitHub artifact topology

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0004 (scanner/model split), ADR-0006 (PR envelopes); `scripts/sweep_poll.py`; `planning/routines/upstream-sweep.md` §"GitHub artifacts the routine produces" / §"Fail-closed semantics" / §"Open-PR collision handling" / §"Manual-review issue de-duplication"; commits `a6bce6be` (2026-05-04), `f447f78`/`1ce7ef9`/`8348c72` (2026-05-11, session `019cz1M7pXuXFQykMZxfdXHm`)

> Retrospective ADR. Shipped 2026-05-04 and materially hardened on 2026-05-11 after live HEAD-resolution failures against `saorsa-labs` repos.

## Context

An unattended daily routine (ADR-0005) with write access to the docs repo will, over time, hit every failure mode: rate limits, an org that refuses fine-grained PATs, a garbage-collected SHA, a force-push, a malformed block, a network blip. Two failure behaviours are unacceptable: (1) **failing silent** — reporting "no drift" when it actually failed to look, which lets real drift rot undetected; and (2) **flooding** — opening duplicate PRs/issues every day for the same unresolved condition. We also had a concrete incident: the scanner could not read public `saorsa-labs` repos via the authenticated REST path (org-level FG-PAT refusal) *or* the anonymous retry (shared-sandbox-IP quota), and earlier diagnostics misreported public repos as private.

The routine needed a disciplined, predictable relationship between run outcomes and the GitHub artifacts it produces, and a strict fail-closed posture with diagnostics good enough to triage from the issue body alone.

## Decision Drivers

- Never fail silent: an error must **abort and surface**, never masquerade as "no drift."
- Never flood routine output: open-PR collisions and unresolved per-record manual reviews must **deduplicate**, not re-open daily. Whole-run failure issues are the deliberate exception because each failed run is a separate observation requiring triage.
- Issues are for **things a human must act on**; healthy runs should leave no noise.
- Diagnostics must distinguish rate-limit vs policy-refusal vs transient outage **from the issue body alone**.
- Reads must degrade through fallbacks before giving up; writes stay scoped to the docs repo only.

## Considered Options

1. **Fail-open / best-effort scanning** (skip unreadable repos, continue). Rejected: this is exactly the silent-failure mode; the skip path was fail-open and was removed in `1ce7ef9`.
2. **Emit an artifact for every run** (including no-drift status comments). Rejected: daily noise trains reviewers to ignore the routine; healthy runs should be silent.
3. **Strict fail-closed scanner + a fixed outcome→artifact topology with fingerprint dedup and serial-cadence collision handling.** Chosen.

## Decision

We will operate the routine **fail-closed**, with a fixed mapping from run outcome to GitHub artifact.

- **Scanner fail-closed (whole run aborts):** GitHub 4xx/5xx after fallbacks exhausted, network timeout, malformed verification block, unknown/missing `verification_mode`, unparseable registry/frontmatter, or unknown `source_repo` → the routine opens **one fresh `upstream-sweep-failure` issue** carrying the JSON diagnostic (response body, rate-limit state, `x-github-request-id`, `retry-after`, and the `git ls-remote` fallback outcome) and opens **no PR**. Failure issues are **not** auto-closed and **not** deduplicated — each is a discrete observation a human triages and closes deliberately.
- **Read fallback ladder** (before any fail-close): `GITHUB_TOKEN` → `gh auth token` → anonymous REST (with an authenticated-403→anonymous retry) → unauthenticated `git ls-remote` against the public clone URL (a separate code path that bypasses both org FG-PAT policy and REST anonymous limits for public repos). Writes use `gh` and target **only** `withautonomi/autonomi-developer-docs`.
- **Per-record fail-closed (one page deferred, run continues):** if both SHA fetches *and* the compare API fail for a record → that page is held back as a **`upstream-sweep-manual-review`** issue; the rest of the run proceeds. Manual-review issues also cover audit ambiguity (page-batching cases 3/4/5 from ADR-0006).
- **Outcome → artifact topology:** no drift → **nothing** (silent exit; the run log is the only trace). Drift, all clean → sweep PR (+ prose draft PR if prose changed); the PR bodies are the run summary. Drift + ambiguity → PRs plus one manual-review issue per deferred record. Scanner/step error → one failure issue, no PR.
- **Serial cadence via open-PR collision:** before opening anything, list open PRs (`--limit 1000`, client-side prefix filter on `claude/sweep-*`/`claude/prose-*`) and **exit silently if any are open** — the open PR is itself the signal; drift is re-detected next run. This forces one-PR-at-a-time and prevents accumulation.
- **Fingerprint dedup for manual-review issues:** a deterministic `Fingerprint:` line (record location + `recorded_sha..head_sha`) is matched client-side across all open issues (no label filter, because labels are best-effort); an unmoved record **reuses** its existing issue (adding a run-trail comment) instead of opening a duplicate; a moved `head_sha` is a new event with a new issue.
- **Best-effort labels:** the routine attempts `upstream-sweep-failure` / `upstream-sweep-manual-review` labels but falls back to an unlabeled issue (with an in-body note) rather than aborting on label-write permission gaps. Only a real issue-creation failure (auth/network/permission) aborts.

## Consequences

### Positive

- "No drift" is trustworthy — it can only mean the scanner looked and found nothing.
- Reviewers get **zero noise on healthy days** and a precise, self-contained diagnostic on failures.
- No PR/issue floods: collision handling serializes PRs; fingerprinting serializes manual-review issues.
- The `git ls-remote` fallback resolves the real `saorsa-labs` incident that motivated the hardening.

### Negative / Trade-offs

- Strictness can abort a whole run on a single transient error; recovery is next-day (acceptable given ~24h latency, ADR-0005).
- Failure issues are intentionally *not* deduplicated, so a persistent fault produces one issue per day until a human fixes and closes them.
- Serial cadence means a long-open PR blocks new drift detection surfacing until it merges/closes.

### Neutral / Operational

- Two distinct issue classes (`-failure` aborts the run; `-manual-review` is per-record and non-blocking) with different lifecycles a human must understand.
- The scanner's diagnostic schema and the fingerprint format become contracts; changing them affects dedup correctness.

## Validation

- The scanner returns a non-zero exit / `status: "error"` on every fail-closed condition; the routine treats any non-`ok` status as abort-and-open-failure-issue.
- The `git ls-remote` fallback was **verified live** against `saorsa-labs/saorsa-core` from the routine sandbox (`8348c72`).
- Dedup is checkable: a record whose `head_sha` has not advanced must not spawn a second open manual-review issue across consecutive runs.
- Review trigger: changing the outcome→artifact topology, the fallback ladder, the collision rule, or the fingerprint format supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
