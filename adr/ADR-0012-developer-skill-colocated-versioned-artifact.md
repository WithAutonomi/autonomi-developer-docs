# ADR-0012: The Autonomi Developer skill — purpose, single-file format, in-repo location, and vendor-agnostic distribution

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (shared source-of-truth/verified_commits), ADR-0008 (dual audience — the skill is the agent-facing extreme), ADR-0011 (scope mirrors the SDK/CLI/Rust/MCP interface set), ADR-0013 (freshness & content tiering), ADR-0014 (maintenance & registry wiring); the reconstructed origin decision log (two Opus-4.7-era sessions, skill genesis); `skills/start/` (`SKILL.md`, `version.json`, `CHANGELOG.md`, `MAINTAINING.md`); `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`; `docs/developer-skill.md`; sibling repo `WithAutonomi/skills`

> Retrospective ADR reconstructed from the origin design sessions plus the current repo. Where origin intent and current repo state differ, both are recorded and the difference is called out (most sharply on naming, below). This ADR covers *what the skill is, how it is formatted, where it lives, and how it is distributed*; freshness is ADR-0013 and maintenance is ADR-0014.

## Context

### Why the skill exists

The skill's purpose is to **teach an AI agent to build on top of the Autonomi network** so the agent can begin and immediately see value, and gain the expertise to build applications, tools, and services on Autonomi — for itself and, by extension, its human operators. It is **developer knowledge**: developing, creating, and building *on top of* Autonomi's features, tools, and limitations.

Crucially, the value is **agent-side opinion**, not a second copy of the reference docs. Autonomi exposes four developer paths (SDK, MCP, CLI, Direct Rust) and the choice between them is meaningful; the network enforces strict terminology; and mainnet operations move real money. A skill can carry the opinion a raw doc fetch cannot: which path to recommend, which words are wrong, and what to warn about. That is the job.

### What it is and isn't (three-way boundary)

- **It is** — knowledge for **building on top of** Autonomi (SDK, daemon, CLI, Direct Rust, MCP).
- **It is not** — a skill for **using** the network as an **end user / operator** (running nodes, uploading/managing data as a consumer). That surface is a *separate* skill — the `autonomi` skill now living in the sibling `WithAutonomi/skills` repo (see Naming).
- **It is also not** — a skill for **developing the network itself** / contributing to the Autonomi codebase. Building *on* Autonomi is in scope; building *Autonomi* is not.

## Decision Drivers

- **Purpose first:** an agent must go from zero to *building on Autonomi with value* from the skill alone — carrying opinion (path choice, terminology, mainnet warnings), not just facts.
- **Cross-agent reach:** the artifact must be installable by anyone, across runtimes — not tied to one vendor.
- **One source of truth:** the skill must not drift from the docs it derives from, and must reuse their verification machinery rather than duplicate it.
- **Low-friction iteration** during the pre-1.0 verification-and-hardening phase.
- **Precedent/consistency** with the sibling `x0x` skill in the same problem space.
- **Bounded to "build on top of"** — no bleed into end-user/operator use or core contribution.

## Considered Options

**Should it exist (Phase 1).**
1. *Do nothing* — rely on agents fetching the live docs at query time. Rejected: no agent-side opinion about which of the four paths to pick, no terminology enforcement, no mainnet warnings, inconsistent results across agents.
2. *Ship a Claude Code plugin as the primary artifact.* Rejected as primary: locks the skill to one runtime; Autonomi wants OpenCode/Cursor/Windsurf/etc. reach. A plugin may still *wrap* the skill later.
3. *Ship a portable skill.* Chosen.

**Format (Phase 2).**
1. *Single `SKILL.md`* in a folder with `version.json` + `CHANGELOG.md`. Chosen.
2. *`.skill` archive* with `references/` + `scripts/` (progressive disclosure). Rejected: over-engineered for a bounded surface; the sibling `x0x` skill settled on single-file, and consistency beats theoretical elegance. Revisit only if the file grows past ~1500 lines.
3. *Plugin* wrapping either. Rejected as primary (see Phase 1).

**Location (Phase 5).**
1. *`docs/skills/…`* inside the GitBook-synced tree. Rejected: would publish an agent-instruction document to `docs.autonomi.com`, confuse human readers, and subject the skill to Diátaxis page-template + docs verification rules that don't fit it.
2. *Separate repo.* Rejected *at genesis*: fragments the source of truth — the skill mirrors `CLAUDE.md` terminology and depends on `repo-registry.yml` / `component-registry.yml`, so co-location lets one PR update skill and context together. (Note: this is now partially revisited — see Consequences — as a *future* migration target, not a genesis choice.)
3. *`skills/<name>/` at repo root.* Chosen.

## Decision

- **Ship a portable, single-file `SKILL.md`** (alongside `version.json` and `CHANGELOG.md`) as the canonical artifact, matching the `x0x` precedent. The skill carries agent-side opinion (path selection, terminology enforcement, mainnet/real-money warnings), not a duplicate of the reference docs.
- **Locate it at `skills/<name>/` at the repo root**, a sibling of `docs/`, `planning/`, `reference/` — co-located with the `CLAUDE.md` style guide and both registries it depends on, and **excluded from GitBook publish** (GitBook scope is `docs/` only) so public docs readers never land on agent instructions.
- **Distribute it vendor-agnostically from a canonical source, fanned out across channels.** The canonical artifact is the portable `SKILL.md` (plus its `version.json` manifest) at a stable raw URL. Channels include the Claude plugin/marketplace (currently realised via `.claude-plugin/` → marketplace `withautonomi`, plugin `developer`, giving `/developer:start`), **skills.sh**, **manual install** (fetch `SKILL.md` and drop it in), and future channels — with or without human intervention. The Claude marketplace is **one channel, not the definition of the artifact**; whether "plugin" is even the right framing is deliberately open.
- **Name (intended): `autonomi-developer`.** The canonical, vendor-neutral, self-describing name is `autonomi-developer` — accurate across all four paths (not just SDK), and distinct from a user-facing skill. This is what the ADR records as intended.

The genesis rationale: `autonomi-developer` is vendor-neutral, self-describing, correct across all four paths (not just SDK), and leaves a distinct name free for a future user-facing skill (rejected `autonomi` as too broad, `autonomi-sdk` as too narrow, `autonomi-development-skill` as clunky). That reserved user-facing slot has since been taken by the `autonomi` skill in the sibling `WithAutonomi/skills` repo, which confirms this one should keep the *developer* identity.

The repo currently ships the skill on-disk as `skills/start/` (`name: start`, plugin `developer`, `/developer:start`) — a form introduced to suit the Claude-plugin slash command rather than the vendor-neutral intent. This divergence, the unclear provenance of `start`, and the open question of a future migration to `WithAutonomi/skills` are tracked in `planning/skill-open-questions.md` and will be closed by a superseding ADR when resolved (see Validation). The automation ADRs (0005–0007) refer to the literal `skills/start/` path because that is what the routine touches today.

## Consequences

### Positive

- The skill carries opinion agents can't get from a raw doc fetch: path choice, terminology, real-money warnings.
- Single-file `SKILL.md` diffs and reviews cleanly in one PR, needs no build step, and any agent that reads Markdown can ingest it.
- Co-location keeps the skill honest against `CLAUDE.md` and the registries, and lets one PR move skill + context together.
- Vendor-agnostic distribution keeps reach broad (Claude marketplace, skills.sh, manual, future) and allows agent self-install.

### Negative / Trade-offs

- **Naming debt:** the on-disk name (`start`) reflects a vendor channel, not the canonical `autonomi-developer` intent — tracked in `planning/skill-open-questions.md`, to be closed by a superseding ADR.
- Single-file **size ceiling** (~1500 lines): if the surface outgrows it, revisit `.skill` with `references/` (partly mitigated by content tiering, ADR-0013).
- No place for bundled machine artifacts (helper scripts) in a single file — not needed today.
- Co-location couples skill release hygiene to the docs repo's PR flow; a future move to `WithAutonomi/skills` would decouple them but re-open the "one PR for skill + context" benefit.

### Neutral / Operational

- The repo doubles as a Claude marketplace (`.claude-plugin/`); that is one realised channel, not the artifact's definition.
- A future migration to `WithAutonomi/skills` is anticipated but not decided here; it would supersede the location and possibly the naming parts of this ADR.
- `MAINTAINING.md` (skill-local) and the registries carry the operational detail; ADR-0014 records the maintenance decision.

## Validation

- The canonical `SKILL.md` is installable across channels: the Claude path (`/plugin marketplace add …` → `/plugin install developer@withautonomi` → `/developer:start`) and the vendor-neutral path (fetch the raw `SKILL.md` and install it directly).
- Scope check (human today; the ADR-0009 panel later): reviewers reject material that teaches end-user/operator usage or core-codebase contribution.
- Naming/location review trigger: resolving the `start` vs `autonomi-developer` question, or migrating the skill to `WithAutonomi/skills`, supersedes the relevant parts of this ADR.
- Distribution review trigger: narrowing to a single vendor/channel supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
