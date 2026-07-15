# ADR-0011: Documentation information architecture and content design — route-first navigation with Diátaxis, dual-audience pages

- **Status:** Accepted
- **Acceptance:** Retrospective — predates the ADR process; ratified by the implementation built on it and by this review pass, not by prospective pre-implementation review.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification trails per page), ADR-0008 (platform & dual audience), ADR-0010 (CLAUDE.md enforces this design operationally); `planning/information-architecture.md` (v4 — detailed IA, per-page briefs, design principles); `docs/SUMMARY.md`; the route-first IA arc (2026-04-17 → 04-21, PR #9 `ia/route-first-docs`)

> Retrospective ADR. The IA and content-design decisions were made and iterated across late March → April 2026. This records the durable design of record; `planning/information-architecture.md` holds the page-by-page detail and remains the working reference for specifics.

## Context

Publishing platform (ADR-0008) and authoring mechanics (ADR-0010) do not decide the *shape and quality* of the documentation: how it is organised, how a reader moves through it, and what makes a page good. That is a distinct design decision, and it was deliberated in its own right — the site was first laid out Diátaxis-section-first (`getting-started/`, `core-concepts/`, `how-to-guides/`, `sdk-reference/`, `cli-reference/`) and then deliberately reorganised into a **route-first** tree (`docs/sdk/`, `docs/mcp/`, `docs/cli/`, `docs/rust/`, `docs/guides/`, `docs/reference/`) with Diátaxis expressed *inside* each interface.

The design has to satisfy two readers with different consumption modes at once (the same dual audience as ADR-0008, but here it constrains *page and tree design*, not platform):

- **Humans** read sequentially and learn a journey — from "Hello World" to production — jumping to reference as needed.
- **AI agents** fetch specific pages by semantic search via `llms.txt` and need each page to stand alone, with no "see the previous chapter" dependencies.

A developer also arrives already committed to an interface (SDK, MCP, CLI, or Direct Rust); organising primarily by Diátaxis type forces them to hop between top-level sections to follow one interface's story.

## Decision Drivers

- Serve both a **human learning journey** and **agent page-level fetch** from one tree.
- Match the reader's real entry point: they pick an **interface** first, then a task type.
- Keep the taxonomy **proven and predictable** (Diátaxis) rather than bespoke.
- Make each page **self-contained** and single-topic so LLM ingestion and hyperlinking stay clean.
- Foreground **practical usage** over internals; ship **correct** pages over comprehensive-but-speculative ones.

## Considered Options

1. **Diátaxis-section-first** (top-level Getting Started / Core Concepts / How-to / Reference, interfaces mixed within). The original layout. Rejected: a reader committed to one interface must hop across top-level sections to follow its thread; interface material gets diluted.
2. **Reference-only / API dump.** Rejected: serves neither the human learning journey nor conceptual understanding; agents get endpoints but no task or concept framing.
3. **Route-first (by interface) with Diátaxis expressed within each interface**, plus shared `guides/` and `reference/` areas and tool-neutral Core Concepts. Chosen.

## Decision

We will structure and write the docs to the following design, which is the standard the docs must keep meeting:

- **Taxonomy: Diátaxis.** Getting Started → Core Concepts → How-to Guides → Reference is the documentation-type framework.
- **Navigation: route-first.** The tree is organised primarily by the four developer interfaces — **SDK, MCP, CLI, Direct Rust** — with Diátaxis types expressed *within* each interface, plus shared `guides/` and `reference/` areas. Landing pages sit first in a section with child pages nested beneath; navigation stays **hierarchical but flat** (max ~3 levels; every page a distinct URL).
- **Interface purity.** A page covers one interface unless it is explicitly a comparison/chooser page. **Core Concepts stay tool-neutral.** Getting Started and How-to pages state which interface/route they cover, why you'd choose it, and where the alternatives live.
- **Page design for dual consumption.** **One concept per page**, and every page is **self-contained** — no "as discussed above"; related pages are linked at the end, not relied on inline. An agent pulling a single page via `llms.txt` must understand it alone.
- **Content priority.** **Practical usage ("what can I do?") outranks internals ("how does it work?")**; internals appear as "under the hood" context or dedicated concept pages, never as the primary framing of a task page.
- **Interface stance.** **ant-sdk is the primary interface**; ant-client (Rust/CLI) is the advanced/direct alternative. The **REST API reference is the canonical shared surface** that all language bindings wrap ("learn one, know them all").
- **Quality bar: correctness over coverage.** Better to ship fewer verified, accurate pages than many speculative ones; every page carries its verification trail (ADR-0003).

`planning/information-architecture.md` holds the concrete expression of this design (directory tree, `SUMMARY.md`, per-page briefs, launch priorities). That file is the working reference; this ADR is the decision and its invariants.

## Consequences

### Positive

- A developer follows one interface's full story (concept → how-to → reference) without leaving its section.
- Self-contained, single-topic pages serve agent fetch and human scanning equally, and keep `llms.txt` ingestion clean.
- Diátaxis gives writers (human and AI) a predictable slot for every page, reducing structural drift.
- Practical-first framing and correctness-over-coverage keep the corpus useful and trustworthy rather than exhaustive and speculative.

### Negative / Trade-offs

- Route-first duplicates some Diátaxis scaffolding across interfaces (each interface has its own getting-started/how-to shape), which is more surface to keep parallel.
- Interface purity requires chooser/comparison pages to route readers who haven't picked an interface yet.
- Self-containment means some deliberate repetition across pages rather than cross-references.
- A shared canonical REST reference must stay accurate for *all* bindings at once; drift there is high-blast-radius (mitigated by ADR-0003/0006).

### Neutral / Operational

- Many of these principles are enforced operationally by `CLAUDE.md` (ADR-0010): per-Diátaxis-type page templates, interface-purity and tool-neutral-concepts rules, self-containment, and the practical-first hierarchy. This ADR is the design of record; CLAUDE.md is its enforcement, and the two must not diverge.
- The concrete tree and page set evolve (pages added/retired post-launch); such changes follow this design without needing a new ADR unless they change the design itself.
- A future custom UI (ADR-0008) would render this IA differently but does not change the taxonomy or page-design invariants.

## Validation

- `docs/SUMMARY.md` and the `docs/{sdk,mcp,cli,rust,guides,reference}/` tree reflect the route-first-with-Diátaxis layout.
- Review (human today; the ADR-0009 panel later) checks each page for interface purity, single-topic self-containment, correct Diátaxis slot, and practical-first framing — against `CLAUDE.md`.
- Correctness-over-coverage is observable: pages ship verified (ADR-0003) rather than speculative; unverifiable pages are deferred or stubbed, not guessed.
- Review trigger: changing the taxonomy (away from Diátaxis), the navigation model (away from route-first), the interface set, the primary-interface stance, or the canonical-REST-reference model supersedes this ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
