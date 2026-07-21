# ADR-0013: Skill freshness — three-part staleness defence and content tiering

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification blocks/verified_commits), ADR-0012 (the skill this protects), ADR-0014 (maintenance closes the human-paced loop), ADR-0005 (the daily routine now carries stamp refreshes); origin decision log Phases 3, 6, 7; `skills/start/SKILL.md` frontmatter, `skills/start/version.json` (`canonical_skill_url`, `canonical_docs_url`)

> Retrospective ADR reconstructed from the origin design sessions. Freshness was identified there as "the load-bearing decision of the whole design": a skill that goes stale actively misleads users within weeks. This ADR records how staleness is defended against; ADR-0014 records how new versions are cut.

## Context

Autonomi's codebase changes almost daily, and a skill has **no runtime — it cannot self-update**. A shipped snapshot decays fast, and a stale skill is worse than none: it confidently gives wrong endpoints, flags, and commands. So freshness has to be *designed into* the artifact, defending against several distinct failure modes at once: the maintainer forgetting to re-verify, the user's agent not auto-updating, the agent being offline, and fast-moving API detail drifting between releases.

## Decision Drivers

- A stale skill must, at minimum, **know it is stale and say so**.
- The defence must **degrade gracefully** — no single point (a network call, a maintainer, a fetch) whose failure silently reintroduces stale answers.
- **Fast-moving detail must not live in the snapshot** — it should be fetched fresh at query time.
- **No new infrastructure** to run (no bespoke server, no subdomain) at this stage.

## Considered Options

**Freshness mechanism (Phase 3).**
1. *Static content, periodic re-release, no runtime check.* Rejected: Autonomi's velocity makes stale-harm certain.
2. *A dedicated skill-owned MCP server* serving live content. Rejected: over-engineering — infrastructure the docs team must run and the user must install, duplicating what `docs.autonomi.com` already serves.
3. *Rely on the existing `antd-mcp`.* Rejected: `antd-mcp` talks to a running daemon (network/wallet/upload state), not documentation — wrong tool.
4. *Rely solely on GitBook's `/~gitbook/mcp`.* Rejected as the sole mechanism: requires every consumer's agent to know about GitBook MCPs, isn't universally available, and doesn't help the skill notice *its own* staleness.
5. *Runtime freshness check + content tiering.* Chosen.

**Manifest hosting (Phase 6).**
1. *A `docs.autonomi.com/...` URL* (requires duplicating a copy into `docs/` for GitBook to sync). Rejected: re-publishes the manifest publicly and creates a two-copies divergence problem, inverting ADR-0012's location decision.
2. *A dedicated `skills.autonomi.com` subdomain.* Rejected as premature: no ops team, no second consumer yet to justify it.
3. *GitHub raw URL.* Chosen.
4. *GitHub Pages / CDN* in front of raw. Rejected as unnecessary for the current traffic (one read per activation).

**Content boundary (Phase 7).**
1. *Bundle everything* (full REST/CLI/binding surface pasted in). Rejected: 5000+ lines, blown context budgets, a new release on every trivial upstream change, and a two-copies problem with the docs.
2. *Pointer everything* (thin router). Rejected: strips the skill of its value-add — the opinion (path choice, terminology, warnings) is not in a REST reference.
3. *Tiered — bundle stable canon, point at fast-moving surfaces.* Chosen.

## Decision

We will defend skill freshness with a **three-part mechanism that degrades gracefully**, plus a **content-tiering rule** that keeps fast-moving detail out of the snapshot.

**1. Frontmatter fingerprint (passive).** Every release pins `version`, `verification_mode`, a per-repo `verified_commits` SHA map, and `verified_date` in the `SKILL.md` frontmatter. The runtime `version.json` manifest mirrors the fields needed for runtime and external inspection, including `version`, `verification_mode`, and `verified_commits`; it deliberately does not carry `verified_date`. That date describes when the skill content was reviewed and belongs only in `SKILL.md`. Even with no network, a maintainer can inspect the skill itself to see exactly what was verified, and when.

**2. Runtime version check (active).** The skill's first instruction to the loading agent is to fetch a stable-URL `version.json`, compare its `version` to the skill's own, and **warn the user if a newer version exists**. If the fetch fails (offline, blocked), the skill **continues silently** — the check never blocks use.

**3. Content tiering (structural).** Stable canon is **bundled**; fast-moving surfaces are **pointers** to the live docs, and the skill instructs the agent to *fetch the live page rather than fabricate*. So even if (1) and (2) are ignored or fail, drift in fast-moving areas causes a fresh fetch, not a wrong answer.

- **Bundled (changes on network-architecture cadence):** what Autonomi is; which developer path to pick and when; core concepts at high level (data types, keys/addresses/DataMaps, self-encryption, PQC, payment model); the terminology lockfile (mirrors `CLAUDE.md`); common errors/diagnostics; agent behaviour rules (don't invent APIs, warn on mainnet, silently correct terminology); the test/devnet/mainnet path at high level.
- **Pointered (changes on release cadence) → `docs.autonomi.com/developers/…`:** REST endpoints, gRPC services, daemon command reference, per-language binding APIs, CLI command reference, Rust library reference, install commands/versions, MCP tool list, wallet setup.
- **Boundary rule:** anything **regenerable from source** (endpoint shapes, signatures, flag lists) is fast-moving → pointer; anything describing **network-level design intent** (data model, payment concept, PQC posture) is stable → bundle.

**Manifest hosting.** The `version.json` is served from a **GitHub raw URL** on the docs repo (currently `raw.githubusercontent.com/WithAutonomi/autonomi-developer-docs/main/skills/start/…`), recorded in the skill via `canonical_skill_url` / `canonical_docs_url`. Zero new infrastructure. **Moving that URL (repo rename or path change) is a breaking change → major version bump**, and the base URL is treated as a stability contract.

## Consequences

### Positive

- The three parts fail independently: a missed re-verification is caught by the runtime warning; a failed/absent runtime check is caught by pointer-fetch-on-demand; an offline agent still gets correct path/terminology/warnings from the bundle.
- Skill releases track *conceptual* change, not routine API drift — far fewer releases, far less churn.
- No infrastructure to run; the manifest rides GitHub raw.

### Negative / Trade-offs

- The runtime check adds an on-activation HTTP request; airgapped/restricted agents skip it (acceptable — silent continue).
- Pointer content requires the agent to have **web-fetch** and requires `docs.autonomi.com` to stay up; a domain move breaks every pointer (same stability-contract mitigation as the manifest URL).
- Fields needed in both the skill frontmatter and runtime manifest — including `version`, `verification_mode`, and `verified_commits` — must be kept in sync (ADR-0014 checklist). `verified_date` is intentionally not duplicated, avoiding unnecessary date synchronization.
- The bundle/pointer boundary is a judgement call that must be applied consistently.

### Neutral / Operational

- The GitHub-raw path currently embeds `skills/start/`; if the skill is renamed or migrated (ADR-0012), the manifest URL changes and — by the rule above — that is a major bump.
- Since genesis, the daily upstream-sweep routine (ADR-0005) has taken over the *stamp-refresh* half of keeping `verified_commits` current, so part 1 is now machine-maintained rather than purely manual.

## Validation

- The runtime instruction is present in `SKILL.md` and points at a resolvable `version.json`; a stale install produces a user-visible warning, and a failed fetch produces silence, not an error.
- No published (non-draft) release may carry a placeholder SHA (`TBD-…`) in `verified_commits` (ADR-0014 gate).
- Content-boundary review: reviewers confirm regenerable-from-source detail is pointered, not bundled.
- Review trigger: changing the freshness mechanism, the manifest host, or the bundle/pointer boundary supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
