# Skill — open questions

Tracking notes for unresolved items on the Autonomi developer skill. Referenced from ADR-0012/0013/0014 (which record the *decisions*; this file holds the *open items* those decisions leave, so the ADRs stay durable and honest without becoming trackers). Resolving any of these that changes a recorded decision is done via a **superseding ADR**, not by editing the accepted one.

## 1. Canonical name vs on-disk name

- **Decision of record (ADR-0012):** the canonical name is `autonomi-developer` — vendor-neutral and self-describing.
- **Current repo state:** the skill ships as `skills/start/` (`name: start`, plugin `developer`, invocation `/developer:start`).
- **The gap:** commit `2b290ef` introduced `start` to produce the concise Claude-plugin slash form `/developer:start`; a vendor channel therefore shaped the current package identity, and `start` is opaque to non-Claude loaders. That channel-specific alias does not replace the canonical `autonomi-developer` identity recorded in ADR-0012.
- **To do:** decide whether to realign the on-disk name to `autonomi-developer` (keeping `/developer:start` only as a Claude-channel alias). Realigning the implementation with ADR-0012 needs no new ADR, but moving the stable raw URL requires a major version and migration under ADR-0013; choosing a different canonical identity does require a superseding ADR.

## 2. Possible migration to `WithAutonomi/skills`

- The user-facing `autonomi` skill (operate the network — nodes now; uploads/data management later) lives in `WithAutonomi/skills`. This developer skill currently lives beside the docs and is assembled by the same tooling/automation.
- **Open question:** whether this skill should migrate to `WithAutonomi/skills`, trading the "one PR updates skill + context" benefit of co-location for a dedicated skills home.
- **To do:** study the `autonomi` skill's distribution, naming, and conventions in that repo; reconcile them with ADR-0012/0013/0014 at migration time. A migration would supersede the location (and possibly naming) parts of ADR-0012 and the manifest-URL of ADR-0013.

## 3. Draft → stable promotion

- The skill sits at `0.1.x-draft`. The `-draft` suffix is held until a deliberate re-verification pass and a live-devnet exercise confirm the bundled commands/flows against a real network.
- **To do:** define and run that promotion gate, then cut a non-draft release.

## 4. Distribution channels beyond the repo

- Distribution is vendor-agnostic (ADR-0012). Compatible runtimes can consume the raw `SKILL.md` manually, while the only first-class packaged and documented distribution currently uses Claude-specific plugin conventions. `skills.sh`, an Anthropic skills directory, and other channels are anticipated.
- **To do:** decide which additional channels to publish through and in what priority.

---

_Resolved since genesis (kept out of the open list): `feeds_skills:` applied to `component-registry.yml`; `MAINTAINING.md` placed skill-local; real `verified_commits` SHAs replacing the initial placeholders._
