# ADR implementation conformance

**Status:** Active planning record
**Last reviewed:** 2026-07-16

## Purpose

The retrospective ADRs record decisions made before this repo adopted ADR governance. They are normative records of intended invariants, not claims that every part of the present implementation conforms.

This file tracks known or suspected implementation gaps separately so correcting an implementation does not rewrite the historical decision. A gap is closed by bringing the implementation into conformance. A superseding ADR is required only when the decision itself changes.

## Confirmed gaps

| ADR | Intended invariant | Present implementation | Required follow-up |
|---|---|---|---|
| ADR-0001 / ADR-0002 | ADR format and Accepted-record immutability are enforced by CI at the repo-root `/adr` location. | The corrected script and workflow validate `/adr`, but the ADR Governance check is not a required branch-protection check and path-filtered execution cannot detect an architectural PR that omits an ADR. | Make ADR Governance a required check and define the human-review mechanism for identifying architectural changes that require a Proposed ADR. |
| ADR-0003 | Every documented surface carries complete, machine-checkable verification provenance. | The scanner validates discovered records but does not prove that every page contains a record, and its required-field validation does not cover the full declared schema. | Specify and implement repository-wide verification-presence and schema checks without moving source audit or verification judgement into the scanner. |
| ADR-0004 | Deterministic detection, efficient-model metadata audits, and frontier-model prose audits run as separate capability tiers. | Detection is deterministic, but the committed routine requires a frontier model end-to-end for both metadata and prose audits. | Add model routing after classification while preserving deterministic detection and fail-closed escalation. |
| ADR-0010 | The mechanically checkable parts of `CLAUDE.md` are enforced by CI. | `prose-guard` enforces the automated prose branch's file and release envelope, not terminology, prohibited wording, page templates, or verification-block presence. | Add a separate docs-content lint that runs after prose is written and on any PR that changes rendered docs or skill prose. The routine may invoke the same lint before opening a PR; CI remains the enforcement boundary. |
| ADR-0012 | `autonomi-developer` is a vendor-neutral portable skill distributed through multiple compatible channels. | The raw `SKILL.md` is manually consumable by compatible runtimes, but the first-class packaged and documented distribution is shaped around the Claude plugin aliases `developer`, `start`, and `/developer:start`. | Improve non-Claude installation and discoverability, evaluate skills.sh and other registries, and decide whether to realign the path or move the canonical artifact to `WithAutonomi/skills`. Preserve one canonical artifact and identity; treat any stable raw URL move as a major version migration under ADR-0013. |
| ADR-0013 | Stable canon is bundled; regenerable, fast-moving interface detail is fetched from live docs. Runtime freshness checks, pinned provenance, and stable manifest URLs provide independent staleness defences. | The skill bundles endpoint lists, constructors, command flags, method names, and installation details. Its runtime check compares release versions, so a metadata-only verification refresh with no version bump is not detected by an installed copy. Commit `2b290ef` also moved the stable raw URL without applying the required major-version migration. | Re-audit the bundle/pointer boundary, specify how runtime freshness detects verification movement without making activation noisy or brittle, and apply the major-version migration rule to the next stable raw URL move. |
| ADR-0014 | The component registry is the machine-readable dependency graph for skill re-verification. | `feeds_skills` records the intended graph, but the scanner discovers skill dependencies from fixed `verified_commits` maps. Adding a registry edge alone does not add a watched skill dependency. | Make registry wiring and verification metadata agree, then have the scanner derive or validate skill dependency coverage from `feeds_skills`. |

## Gaps requiring design confirmation

| ADR | Question to resolve before implementation |
|---|---|
| ADR-0007 | Define the exact guarantee when issue, PR, or backlink creation fails after an earlier GitHub artifact has already been created. Decide whether compensation, reconciliation, or explicit partial-state reporting is the intended fail-closed behaviour. |
| ADR-0009 | Define the evidence threshold and review protocol for moving metadata and prose tracks independently from human merge control to panel-gated automation. The intended sequence is metadata sweeps first, followed by prose once its accuracy is demonstrably high enough. |

## Proposed implementation slices

### 1. Governance enforcement

- Make the ADR Governance check required after the corrected workflow is green on the PR branch.
- Keep Accepted records immutable once merged to the default branch while allowing the introducing PR to remain reviewable until merge.
- Define how human review identifies architectural changes that omitted a required Proposed ADR.

### 2. Verification completeness

- Specify verification-presence and full-schema rules for docs pages and the developer skill.
- Add deterministic checks for missing records, missing fields, invalid modes, placeholder SHAs, and inconsistent skill metadata.
- Keep claim-level source audit and judgement outside the scanner.

### 3. Model-tier routing

- Keep `scripts/sweep_poll.py` deterministic and model-free.
- Route metadata-only audit work to an efficient subscription-backed model.
- Route prose audit, writing, and verification to a frontier subscription-backed model.
- Fail closed to human review when classification or routing is ambiguous.
- Keep concrete providers and model versions in operational configuration.

### 4. Docs-content enforcement

- Build a content lint separate from `prose-guard`.
- Run it after prose generation and on human-authored documentation PRs.
- Enforce terminology, prohibited wording, required page structure, and verification-record presence.
- Keep `prose-guard` focused on the automated branch's allowed-change envelope.

### 5. Skill identity, freshness, and distribution

- Re-audit bundled content against ADR-0013's stable-versus-volatile boundary.
- Preserve `autonomi-developer` as the canonical identity while treating `developer`, `start`, and `/developer:start` as Claude-channel aliases.
- Evaluate skills.sh and a multi-channel distribution workflow.
- Evaluate a move to `WithAutonomi/skills`; if chosen, draft a superseding ADR for location and apply ADR-0013's major-version treatment to stable manifest URLs.
- Improve freshness signalling so verification movement can be detected independently of release-version changes.

### 6. Registry-driven skill maintenance

- Define the consistency rule between `feeds_skills` and `verified_commits`.
- Make tooling detect missing or extra dependency edges.
- Use the registry to determine re-verification scope without conflating skills with Diátaxis pages.

### 7. Fail-closed artifact reconciliation

- Specify outcome semantics for partial GitHub writes.
- Make failure issues report durable partial state precisely.
- Add idempotent reconciliation where it reduces duplicate or stranded artifacts without hiding failures.

## Verification principle

Each follow-up slice must verify implementation against the governing ADR. If a slice discovers that the intended invariant is no longer wanted, stop and propose a superseding ADR rather than changing the implementation and silently redefining the decision.
