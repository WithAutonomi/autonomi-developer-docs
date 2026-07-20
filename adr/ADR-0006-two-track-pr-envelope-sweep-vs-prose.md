# ADR-0006: Two-track PR envelope — metadata "sweeps" vs prose "pro sweeps" — enforced by branch-scoped CI guards

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification blocks), ADR-0004 (execution tiers — the two tracks map onto the efficient/frontier model tiers), ADR-0010 (CLAUDE.md authoring contract the prose track must satisfy), ADR-0014 (the skill release lifecycle the linked-release rule governs); `.github/workflows/sweep-guard.yml`, `prose-guard.yml`, `sweep-sha-reachability.yml`; `planning/routines/upstream-sweep.md` §"Sweep/Prose PR envelope", §"Page batching rule"; commits `e5869c5` (2026-05-05, prose-guard + v1.1), `7b23c92` (2026-05-08), `ddeb45a` (2026-05-09)

> Retrospective ADR. The metadata sweep track shipped 2026-05-04; the prose ("pro sweep") track and `prose-guard` were added 2026-05-05 and hardened through 2026-05-09.

## Context

Drift comes in two very different shapes. Sometimes an upstream commit changes nothing a developer sees — only the pinned SHA needs re-stamping (a **metadata-only** refresh). Sometimes it changes real behaviour — an endpoint, a flag, a type — and the rendered prose must be rewritten (a **prose-impacting** change). These carry very different review risk: a SHA re-stamp is near-mechanical and safe to skim; a prose rewrite must be read word-for-word by a human before it ships.

If both kinds land in one undifferentiated PR, a reviewer cannot trust *any* PR without a full read, and a prose change can hide inside a "just re-stamping" PR (or vice versa). We needed the two kinds to be **structurally separable and independently trustworthy**, and we needed that separation **machine-enforced**, because the author is an automated routine.

## Decision Drivers

- A metadata re-stamp must be reviewable in seconds; a prose change must be flagged for a full read.
- The routine is automated, so the envelope must be **enforced by CI**, not by author discipline.
- A prose change to the skill must move its **release metadata in lockstep** (or the skill's version lies).
- Verification-block integrity must be protected: a "metadata" PR must not smuggle prose, and a prose PR must not silently edit a deferred/ambiguous verification block.

## Considered Options

1. **One PR type for all drift.** Rejected: no PR is trustworthy without a full read; hides prose in metadata noise.
2. **Human labels each PR by type after the fact.** Rejected: the author is a routine; labels are best-effort and can be missing; not enforceable pre-merge.
3. **Two branch-namespaced PR tracks with per-track CI guards** that green-skip on the other track. Chosen.

## Decision

We will split routine output into **two mutually exclusive PR tracks**, distinguished by branch prefix and each policed by a required CI check:

- **Metadata sweep — `claude/sweep-*`, policed by `sweep-guard`.** Allowed: verification-block `source_commit`/`verified_date` lines in `docs/**`, the `verified_commits` maps in `version.json` and `SKILL.md` frontmatter (key sets **locked** — values may refresh, keys may not add/remove), and exactly one new `planning/sweeps/<date>.md`. Forbidden: any prose, any `SKILL.md` body change, `version`/`published_date`/`CHANGELOG` changes, and any change to `scripts/**`, `.github/**`, `repo-registry.yml`, `component-registry.yml`.
- **Prose sweep ("pro sweep") — `claude/prose-*` (opened as draft), policed by `prose-guard`.** Allowed: `docs/**` prose, `SKILL.md` body/frontmatter, and — only as part of a **linked release** — `version`, `published_date`, and `CHANGELOG`. Draft status forces a human to promote to ready only after reading the prose.
- **Linked-release rule (both directions):** if the `SKILL.md` body changes, the same PR must bump `version` (patch), update `published_date`, match frontmatter `version:`, update `verified_date:`, and add one `CHANGELOG` entry. If the body is byte-identical, release fields (`version`, `published_date`, frontmatter `version:`, and `CHANGELOG`) stay unchanged; `verified_commits` and `verified_date` may move as a pure stamp refresh. `prose-guard` enforces both directions on the routine branch namespaces.
- **The two tracks never touch the same page.** A page's classification (via the five-case page-batching rule in `upstream-sweep.md`) sends it to exactly one track; a prose PR that touches a page with a deferred ambiguous record must leave that record's verification block **byte-identical** to base (routine-side deferred-record self-check, since the guards cannot know which records were deferred).
- Guards run **only** on their own branch prefix and green-skip elsewhere, using a real gate step plus an `if:` on every later step (exit-0 from an early step does not skip later steps in Actions). `sweep-sha-reachability` runs on **both** tracks and validates every changed SHA against upstream.

## Consequences

### Positive

- A `claude/sweep-*` PR is trustworthy at a glance: CI guarantees it changed nothing but pinned SHAs and a run summary.
- A `claude/prose-*` PR is always a draft and always flags a human read; prose can never hide in a "metadata" PR.
- The skill's published version can never silently diverge from its body.
- Enforcement is mechanical, so it holds regardless of author (routine or human).

### Negative / Trade-offs

- Two guard workflows plus a reachability check to maintain; their envelopes are intricate and were the source of most early defects (`7b23c92`, `ddeb45a`).
- The page-batching rule that keeps the tracks disjoint is non-trivial and lives in the routine prompt, not in CI — CI enforces the envelope, not the classification.
- A single upstream change touching one page's prose and another page's metadata produces two PRs.

### Neutral / Operational

- Branch prefixes (`claude/sweep-*`, `claude/prose-*`) and the guard `name:` strings become required-check contracts in branch protection.
- `planning/sweeps/<date>.md` summary files accumulate as a per-run audit trail.

## Validation

- `sweep-guard`, `prose-guard`, and `sweep-sha-reachability` are required checks on `main`; a PR that violates its envelope fails CI and cannot merge.
- Synthetic verification PRs (branch slugs) exercise individual envelope rules; the 2026-05-09 pass (`ddeb45a`, `8c541eb`) added shape/type and rename-diff coverage after five defects were found this way.
- Review trigger: any change to what a track may touch, or to the linked-release rule, supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
