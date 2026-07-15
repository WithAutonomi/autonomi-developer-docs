# ADR-0008: GitBook + GitHub as the docs platform, serving a dual human and LLM audience

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification blocks), ADR-0006 (PR tracks), ADR-0010 (CLAUDE.md contract), ADR-0011 (IA & content design carried on this platform); `CLAUDE.md` §"Audience and objectives" and §"Repository purpose"; `.gitbook.yaml`; `docs/SUMMARY.md`; publishes to `docs.autonomi.com/developers`

> Retrospective ADR. This platform choice predates and underlies the automation; it is recorded here because everything else (source-of-truth model, sweeps, prose PRs) assumes it.

## Context

The developer documentation has **two first-class audiences at once**, and the platform has to serve both without forking the content:

- **Humans** — developers from indie hackers to enterprise teams — who need readable, navigable, usable docs with a familiar information architecture.
- **AI agents / LLMs** — which need the same content in a form they can ingest, parse, and act on programmatically, and which increasingly are the thing reading docs on a developer's behalf.

`CLAUDE.md` already encodes this dual mandate explicitly: the audience is "Human developers building applications" **and** "AI agents consuming documentation via llms.txt to interact with the network programmatically." We needed a delivery platform that treats machine-readability as a primary output, not an afterthought, while not forcing us to build and maintain a documentation web app of our own.

## Decision Drivers

- Content must be **first-class for both humans and LLMs** from a single source — no separate machine copy to drift.
- Source format must be **LLM-native** and diff-friendly so both people and agents can contribute auditably.
- Contribution and change control must run through **GitHub** (branches, PRs, review) — the substrate the automation in ADR-0005/0006 already depends on.
- Must expose the **whole corpus to machines** (an `llms.txt`, per-page Markdown renderings, SEO-aware structure) while keeping a human IA/navigation.
- Should let the team **focus on content, not on building an interface**, using tooling that already works today.

## Considered Options

1. **Bespoke docs web app** (custom-built site over the Markdown). Rejected for now: forces us to build and maintain an interface alongside the content, for capabilities GitBook already provides; revisitable later.
2. **Plain static-site generator** (e.g. a generic SSG) on GitHub Pages. Rejected: we would have to assemble `llms.txt`, per-page Markdown endpoints, and SEO structure ourselves, and re-solve navigation/IA.
3. **GitBook synced to GitHub via Git Sync.** Chosen. Markdown source in Git; GitBook renders the human site and the machine surfaces.

## Decision

We will publish the docs through **GitBook, Git-synced to the GitHub repository**, with Markdown as the single source of truth. This choice is made for the following properties, all of which serve the dual audience:

1. **Markdown source** — natively ingestible by LLMs and human-readable, and the format the whole verification/sweep model (ADR-0003/0006) operates on.
2. **Already in place and functional** on the website — no migration cost to start.
3. **Contribution via GitHub** — team members *and* agents contribute reliably and auditably through branches and PRs, which is exactly what the automation relies on.
4. **Machine surfaces are generated for us** — LLM-tuned per-page Markdown renderings, and automatically assembled SEO-aware structures including `llms.txt`, so the corpus is discoverable and ingestible by models.
5. **Dual access shape** — a human-familiar IA and navigation for people, while machines can grab the entire corpus via `llms.txt`, the GitHub repo, and the per-page Markdown renderings.
6. **Content focus** — pre-existing tooling means the team maintains documentation, not a documentation interface.

We may in future move to a native or custom-designed UI; GitBook's GitHub integration is sufficient for all of the above **now**, and a later UI change does not invalidate the Markdown-in-Git source model.

## Consequences

### Positive

- One Markdown source serves humans and LLMs; no separate machine copy to keep in sync.
- The GitHub-centric flow is what makes agent contribution (ADR-0005/0006) and auditable review possible at all.
- `llms.txt` + per-page Markdown make the corpus first-class for model ingestion without extra engineering.
- No interface to build or run; effort goes into content and accuracy.

### Negative / Trade-offs

- A dependency on GitBook's product and its Git Sync semantics (e.g. GitBook-specific `{% tabs %}` syntax in the Markdown, per `CLAUDE.md`).
- Some presentation is owned by GitBook, not us, until/unless we move to a custom UI.
- Machine surfaces (`llms.txt`, SEO structure) are generated by the platform, so their exact shape is partly outside our control.

### Neutral / Operational

- The Diátaxis IA (Getting Started → Core Concepts → How-to → Reference) and `SUMMARY.md` navigation are maintained for humans; `CLAUDE.md` requires each page to be self-contained so it stands alone when an agent pulls it via `llms.txt`.
- A future custom UI is an open option, not a commitment; this ADR would be superseded if we adopt one.

## Validation

- The published site at `docs.autonomi.com/developers` serves both the human pages and the machine surfaces (`llms.txt`, per-page Markdown).
- Self-containment is enforced by review against `CLAUDE.md` (no "see above" cross-references), so a single page pulled by an agent is intelligible alone.
- Review trigger: adopting a custom/native UI, or moving off GitBook/Git Sync, supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
