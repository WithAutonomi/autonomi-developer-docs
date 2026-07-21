# ADR-0002: Architecture Decision Records live at repo-root `/adr`, not `docs/adr`

- **Status:** Accepted
- **Acceptance:** Prospective — confirmed by Jim Collinson as decision owner during review of PR 73.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0001 (location clause only; ADR governance remains in force)
- **Superseded by:** none
- **Related:** ADR-0001 (adopt ADRs — its governance decision remains in force while this ADR supersedes its location clause), ADR-0008 (GitBook platform — why `docs/` is the published product), ADR-0012 (the developer skill kept out of `docs/` for the same reason); `.gitbook.yaml` (`root: ./docs/`), `.adr-kit.yaml` (`adr_directory`), `scripts/adr-governance.py` (`ADR_DIR`), `.github/workflows/adr-governance.yml`

> Current (prospective) decision — made while adopting ADRs in this repo, not a retrospective reconstruction. It re-points the team standard's default ADR location for this repo's specific circumstances; the standard's mechanics are untouched.

## Context

The team ADR standard (ADR-0001, shipped via PR #56) defaults ADRs to `docs/adr/` — correct in a typical repo where `docs/` holds internal documentation. This repo is different: `.gitbook.yaml` sets `root: ./docs/`, so the **entire `docs/` tree is the published developer-documentation product**, synced to GitBook at `docs.autonomi.com/developers`. Placing ADRs under `docs/adr/` puts internal architecture records inside that published product tree.

## Decision Drivers

- Internal architecture records must not publish to, or surface on, the public developer-docs site — nav, search, or the auto-generated `llms.txt`.
- ADRs must stay out of the docs' machinery: the upstream-sweep scanner walks `docs/**/*.md` for verification blocks, and doc tooling (Diátaxis templates, terminology lint, link-checking) globs the same tree.
- A contributor browsing `docs/` as "the documentation" should not find architecture decisions mixed in with product pages.
- The team standard should still be honoured — its own `.adr-kit.yaml` `adr_directory` knob exists precisely so a repo can relocate the instance.
- Consistency with the existing decision to keep the developer skill at `skills/`, not `docs/skills/` (ADR-0012), for exactly this reason.

## Considered Options

1. **Keep ADRs at `docs/adr/`** (the team default). Rejected here: `docs/` is the published GitBook root, so ADRs would sit inside the product tree, risk leaking to the public site / `llms.txt`, and be swept by doc tooling.
2. **Keep `docs/adr/` but exclude it from GitBook** (SUMMARY omission or a `.gitbook.yaml` rule). Rejected: fragile — `root: ./docs/` keeps the files in scope, so it relies on GitBook silently ignoring unlisted files, and the conceptual mixing remains.
3. **Relocate ADRs to repo-root `/adr`.** Chosen. (`planning/adr/` was also considered and rejected: ADRs are formal, ratified decisions, distinct from the loose-thinking design docs that live in `planning/`.)

## Decision

Architecture Decision Records live at repo-root **`/adr`** in this repo. This is a repo-local *configuration* of the team standard, not a fork of it:

- `.adr-kit.yaml` → `adr_directory: adr`.
- `scripts/adr-governance.py` → `ADR_DIR = Path("adr")`.
- `.github/workflows/adr-governance.yml` → path filters point at `adr/**`.
- Move the standard's own files (`TEMPLATE.md`, `TOOLING.md`, `README.md`, and `ADR-0001`) from `docs/adr/` to `/adr`.

`/adr` is chosen over `planning/adr/` because ADRs are formal, ratified decisions — distinct from the loose-thinking design material (`implementation-plan.md`, `verification-workflow.md`, `routines/`, `sweeps/`) that already lives in `planning/`.

## Consequences

### Positive

- Architecture records stay entirely out of the published product tree and its tooling.
- Mirrors the skill's out-of-`docs/` placement (ADR-0012): one consistent rule — product content in `docs/`, internal artifacts at the repo root.
- Still fully governed — the gate validates ADRs at `/adr` once `ADR_DIR` is re-pointed.

### Negative / Trade-offs

- Diverges from the team-standard default (`docs/adr`), so a contributor arriving from another WithAutonomi/Saorsa repo must notice the repo-local location — this ADR is the signpost, and `docs/adr/` is left empty/removed so nothing looks half-moved.
- Requires the three config points (`adr_directory`, `ADR_DIR`, workflow paths) to stay in agreement. The governance script fails closed when they diverge, but the workflow must still become a required check to prevent bypass at merge time.

### Neutral / Operational

- The change is small and repo-local; the shared standard's mechanics (template, lifecycle, immutability) are unchanged — only the configurable location differs.
- Decided as too minor to route through the standard's owner; recorded here so the deviation is explicit and auditable.

## Validation

- `scripts/adr-governance.py` (with `ADR_DIR=adr`) is the validation entrypoint for the `/adr` set; `docs/adr/` no longer exists. Making its workflow a required check is tracked as an implementation-conformance gap.
- Spot-check after the move: no ADR path appears in the GitBook nav, site search, or `llms.txt`.
- Review trigger: a change to `.gitbook.yaml`'s `root`, or a move to a different docs platform, may reopen the location question.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
