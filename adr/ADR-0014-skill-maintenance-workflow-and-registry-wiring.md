# ADR-0014: Skill maintenance — reuse the docs verification workflow, wired via `feeds_skills`

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification model), ADR-0005 (the routine now runs skill stamp refreshes), ADR-0006 (linked-release rule / guards enforce the skill envelope), ADR-0009 (path to automation), ADR-0010 (CLAUDE.md style contract), ADR-0012 (the skill), ADR-0013 (freshness the workflow keeps current); origin decision log Phases 8, 9, 10 + verification-metadata & style cross-cuts; `repo-registry.yml`, `component-registry.yml` (`feeds_skills`), `planning/verification-workflow.md`, `skills/start/MAINTAINING.md`

> Retrospective ADR reconstructed from the origin design sessions. At genesis this workflow was manual/agent-driven with automation deferred; the repo has since moved along exactly that trajectory (the daily routine now carries stamp refreshes) — noted where relevant.

## Context

The skill has to stay accurate as upstream code moves. The docs repo already owns the machinery for that: `repo-registry.yml` classifies each upstream repo by change impact (`broad-source`, `targeted-foundational`, `specialist`, `watchlist`, `excluded`, `tangential`) with an `on_change` behaviour; `component-registry.yml` maps each component to the pages it `feeds_pages:`; and `planning/verification-workflow.md` defines the `source audit → draft → verify` pass. The question is whether the skill gets its own maintenance machinery or reuses this.

## Decision Drivers

- **No fragmentation:** a docs verification pass and a skill verification pass should not be two disconnected chores that drift apart.
- **No premature automation:** upstream changes too fast for auto-open-PR-on-every-change; follow the docs project's own deliberate manual-then-automate trajectory (ADR-0009).
- **Machine-consumable dependency graph:** "when X changes, what re-verifies?" must be answerable from the registry alone, not by cross-reading artifacts.
- **Verification parity with pages** (real SHA per source of truth) without the pages' HTML-comment mechanics.

## Considered Options

**Maintenance workflow (Phase 8).**
1. *A new parallel workflow just for the skill.* Rejected: fragments maintenance; a docs pass and a skill pass fall out of sync.
2. *Full CI automation now* (watch upstreams, auto-open skill-bump PRs). Rejected as the v1 approach: too noisy given upstream velocity; the docs project itself introduces automation deliberately, and the skill should follow the same path.
3. *Reuse the existing docs verification workflow*, treating the skill as another artifact driven by the registries. Chosen.

**Registry wiring (Phase 9).**
1. *Option A — a new `feeds_skills:` field* on each component, parallel to `feeds_pages:`. Chosen.
2. *Option B — reuse `feeds_pages:`*, adding the skill path to the same list. Rejected: mixes two artifact types; any tool that opens each `feeds_pages:` entry as a Diátaxis-templated page breaks on the skill entry.
3. *Option C — the skill declares its own `depends_on:`* in frontmatter. Rejected: inverts the dependency graph — the registry should be the single source of "what updates when X changes."

**Verification metadata shape (cross-cut).**
1. *One block, first repo only.* Rejected: silent under-verification.
2. *Multiple HTML comment blocks* (as pages use). Rejected: awkward in a YAML frontmatter world.
3. *A frontmatter `verified_commits:` dict* (per-repo SHA) + single `verified_date`/`verification_mode`, mirrored in `version.json`. Chosen.

## Decision

- **Reuse the docs verification workflow.** The skill is a first-class artifact consuming both registries and following `source audit → draft → verify`. Re-verification scope keys off `repo-registry.yml`: a `broad-source` change (`ant-sdk`, `ant-client`, `ant-node`) triggers broad re-verification of every skill section touching those components; a `targeted-foundational` change (`saorsa-pqc`, `self_encryption`, `evmlib`, `ant-merkle`, `saorsa-transport`) triggers targeted re-verification of the named concept; `excluded`/`watchlist` changes only re-confirm the skill still says the repo is out of scope.
- **Wire the skill in via `feeds_skills:` (Option A)** in `component-registry.yml` — same YAML shape as `feeds_pages:`, new field name, on the components the skill actually covers (`antd`, `openapi`, `proto`, `ant-core`, `ant-cli`, `ant-node`, the documented language bindings, `self_encryption`, `evmlib`, `ant-protocol`, and the protocol-adjacent components), and *not* on components the skill doesn't teach. This keeps the registry the single machine-readable answer to "what re-verifies when X changes."
- **Verification metadata:** a frontmatter `verified_commits:` dict (real SHA per source repo) plus one `verified_date` and `verification_mode`, mirrored in `version.json` for external inspection. No published release may carry a placeholder SHA.
- **Releases move as a set, SemVer'd.** A verification pass produces a matched change to `SKILL.md`, `version.json`, and `CHANGELOG.md` in one commit. SemVer: **major** = skill-loading / manifest-shape breaks (including a manifest-URL move, per ADR-0013); **minor** = new paths, examples, or capabilities; **patch** = wording/pointer fixes or a re-verification that reflects an upstream change to a described surface. A pure `verified_commits` stamp refresh that touches no described surface is *not* a version bump — it moves only the SHA map (+ `verified_date`), which is the daily routine's normal gesture.
- **Style compliance:** the skill follows `CLAUDE.md`'s style contract (ADR-0010) as if it were a page, with two carve-outs — it may enumerate prohibited words (that's its terminology-mirror topic), and it may name its own repo (provenance about the skill itself is not provenance about docs content).
- **Maintainer doc placement:** resolved to **skill-local `MAINTAINING.md`** (`skills/start/MAINTAINING.md`). Alternatives considered (fold into `CLAUDE.md`; a repo-wide `skills/MAINTAINING.md`) remain open only if more skills co-locate here; the content is portable.

## Consequences

### Positive

- Zero new infrastructure and one workflow to learn; a docs pass and a skill pass are the same muscle.
- `feeds_skills:` keeps the "what re-verifies when X changes" answer in the registry, machine-consumable, without conflating pages and skills.
- The frontmatter `verified_commits` dict gives page-equivalent verification (real SHA per repo) that both the runtime freshness check (ADR-0013) and human/CI review consume.
- The trajectory matched the docs project's: the daily routine (ADR-0005) now performs the skill's stamp refreshes, and the linked-release rule is CI-enforced (ADR-0006) — the "automate later" the genesis session anticipated has largely arrived for the metadata half.

### Negative / Trade-offs

- Depends on `on_change` triggers actually being followed; if no one runs a pass after a `broad-source` change, the skill drifts silently and the runtime warning (ADR-0013) is the only user-side safety net — a human-paced fix rate.
- Skill and docs maintenance are coupled: a large docs PR can pull a skill re-verification along. Fine while docs volume is bounded; decouples if the skill migrates to `WithAutonomi/skills` (ADR-0012).
- **Two copies of the SHA map** (frontmatter + `version.json`) to keep in sync — a `MAINTAINING.md` checklist item.
- `feeds_skills:` adds a one-time teach-the-tooling cost (link validators / verification tooling must iterate the new field).

### Neutral / Operational

- `feeds_skills:` was drafted-then-deferred at genesis and has since been **applied** to `component-registry.yml`; the covered-component set tracks the skill's actual scope and evolves with it (e.g. `saorsa-pqc` out, `ant-protocol` in relative to the genesis draft).
- The manual/agent-driven maintenance path and the automated daily routine coexist: the routine handles metadata stamps and prose drafts; deliberate releases (version promotion out of `-draft`) remain a human gesture (ADR-0009).

## Validation

- `sweep-guard` / `prose-guard` (ADR-0006) enforce the skill's metadata-only vs linked-release envelopes; a mismatched release fails CI.
- `MAINTAINING.md` pre-merge checklist: `SKILL.md`/`version.json`/`CHANGELOG.md` agree on version; `verified_date`==`published_date`; every `verified_commits` entry is a real SHA; every live-docs URL resolves; no guessed SDK/CLI/MCP surface.
- Registry check: every component the skill covers carries `feeds_skills:`; components it doesn't teach do not.
- Review trigger: replacing the reuse-the-docs-workflow model, changing the registry wiring, or moving to full unattended auto-release supersedes this ADR (and interacts with ADR-0009).

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
