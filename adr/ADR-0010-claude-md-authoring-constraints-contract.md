# ADR-0010: CLAUDE.md as the enforced authoring-constraints contract

- **Status:** Accepted
- **Acceptance:** Retrospective — this ADR records a decision made before the ADR process existed. The original decision owner confirms it as a faithful account; current implementation gaps are tracked separately.
- **Date:** 2026-07-14
- **Decision owners:** Jim Collinson
- **Supersedes:** none
- **Superseded by:** none
- **Related:** ADR-0003 (verification model — CLAUDE.md restates it), ADR-0006 (prose track that must satisfy this contract), ADR-0008 (dual audience), ADR-0009 (AI panel reviews against it), ADR-0011 (the IA/content design this contract enforces operationally); `CLAUDE.md` (repo root); terminology lint / `prose-guard`

> Retrospective ADR. `CLAUDE.md` has governed authoring since the repo baseline (2026-04-02); this records its role as a binding contract rather than advisory notes.

## Context

The docs are written and reviewed mostly by AI agents on a daily cadence (ADR-0005/0006). Agents are fluent but not automatically consistent: left unconstrained they drift in voice, invent plausible-but-wrong terminology, reach for banned filler ("simply", "just", "leverage"), leak provenance language ("upstream", "the README says", "current merged truth") into rendered prose, or restructure pages ad hoc. For a corpus that must read as one coherent product **and** be reliably parsed by other LLMs (ADR-0008), that variance is a correctness problem, not a style preference. The constraints therefore need to live in one authoritative, machine-loadable file that every authoring and reviewing agent reads — and parts of it need to be **mechanically enforced**, not merely requested.

## Decision Drivers

- One **authoritative, version-controlled** source of authoring rules, loadable by any agent (Claude Code, OpenCode, reviewers) and by CI.
- Terminology and prohibited-word rules must be **machine-checkable**, because human review will not catch every slip at daily volume.
- Rules must cover **voice, terminology, structure, code examples, refusal, and audience priority** — the full surface that keeps the corpus coherent and machine-parseable.
- Must bind **both writing and review**, so the panel in ADR-0009 checks against the same contract the author used.

## Considered Options

1. **Informal style notes** in a wiki or README section. Rejected: advisory, unenforced, drifts, and not reliably loaded by agents.
2. **Per-page or per-agent prompt conventions.** Rejected: inconsistent, unversioned, impossible to audit or lint against.
3. **A single root `CLAUDE.md` as a binding contract, with its terminology/word rules enforced by CI.** Chosen.

## Decision

We will treat **`CLAUDE.md` at the repo root as the binding authoring-constraints contract** that every authoring and reviewing agent must follow, and enforce its mechanical parts in CI. Its scope is:

- **Repository purpose & scope** — source of truth for `docs.autonomi.com/developers`; Autonomi 2.0 only; explicit exclusions (Autonomi 1.0/MaidSafe, `ant-quic`); in-scope repos governed by `repo-registry.yml` / `component-registry.yml`.
- **Audience & priority hierarchy** — dual human + LLM audience (ADR-0008); practical usage ("what can I do?") outranks internals ("how does it work?").
- **Source-of-truth restatement** — the two verification modes and the `source audit → draft → verify` workflow (the authoring-facing face of ADR-0003), plus refusal rules (no `source_commit: TBD`, no inferred endpoints/types, historical memos are not authoritative).
- **Voice & tone** — second person, present tense, active voice; explain "why" before "how"; lead with the user task, not repo/implementation names; keep provenance language (`upstream`, `current-merged-truth`, "the README says") out of rendered prose.
- **Prohibited words/phrases** — e.g. "simply", "just", "easy", "leverage", "utilize", "in order to", "we", "please", "it should be noted that".
- **Terminology lockfile** — canonical terms with prohibited alternatives and definitions (e.g. `DataMap`, `antd`, `Autonomi Network Token (ANT)`, `ML-DSA-65`), explicitly "used by both agents (when writing) and CI (when linting)."
- **Page templates** — required structure per Diátaxis page type (Getting Started / Core Concept / How-to / Reference / Language Binding), including the mandatory verification block.
- **Code-example rules** — complete and runnable; `{% tabs %}` with cURL first; language-tagged fences.
- **Drafting & review procedures** — new-page, update-page, and reviewer checklists (the reviewer checklist is the seed of ADR-0009's panel).

The mechanically-checkable parts (terminology lockfile, prohibited words, template/verification-block presence) are enforced by the terminology lint / `prose-guard` layer; the judgement parts (voice, structure, priority) bind agents and reviewers by contract.

## Consequences

### Positive

- The corpus reads as one product and stays reliably machine-parseable, regardless of which agent wrote a given page.
- Terminology and banned-word violations are caught by CI at daily volume, not left to human vigilance.
- Authors and the ADR-0009 review panel are held to the **same** contract, so review is objective rather than taste-based.
- New agents/harnesses onboard by reading one file.

### Negative / Trade-offs

- `CLAUDE.md` is large and must be kept current; a stale rule silently mis-shapes every page written against it.
- Hard terminology/word rules can produce false positives (a legitimately-quoted banned word), needing occasional escaping or rule refinement.
- Centralisation makes `CLAUDE.md` itself a high-value change surface — edits to it are effectively edits to every future page.

### Neutral / Operational

- `CLAUDE.md` restates parts of the source-of-truth model (ADR-0003) for the author's convenience; the ADR remains the decision of record and the two must not diverge.
- The terminology lockfile is a living list; adding a term is routine, but changing the *enforcement contract* (what CI blocks) is an authoring-policy change worth noting here.

## Validation

- CI (terminology lint / `prose-guard`) fails a PR that violates the lockfile, uses a prohibited word, or omits a required verification block.
- Reviewers (human today, panel in ADR-0009) check voice, structure, template conformance, and prohibited phrasing against `CLAUDE.md`.
- Review trigger: a material change to the authoring contract — new prohibited/terminology rules that CI enforces, or a change to the template set or audience priority — should be reflected here (and may warrant a superseding ADR if it changes the enforcement model itself).

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
