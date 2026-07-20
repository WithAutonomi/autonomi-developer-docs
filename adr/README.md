# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for this repository.

## Rules

1. Use `ADR-NNNN-short-title.md` names with four-digit numbers.
2. New ADRs start as `Proposed`.
3. `Accepted` ADRs are immutable. If the decision changes, create a new ADR and mark the old ADR as superseded by reference, not by editing its accepted content.
4. Architectural PRs must add or update an ADR before merge.
5. Reviews must check ADR correctness, evidence, trade-offs, and compliance — not just presence.

Immutability begins when an Accepted ADR lands on the default branch. Its introducing PR remains reviewable until merge so the decision owner can confirm the final record. Retrospective ADRs may enter as Accepted when the original decision owner confirms that they faithfully record a decision made before ADR governance existed.

Supersession never requires editing an Accepted record. The new ADR's `Supersedes` field is the authoritative forward link; the older record remains byte-identical. Use `Superseded by` only when that metadata can be populated before the older ADR becomes Accepted.

## Template

Use [`TEMPLATE.md`](./TEMPLATE.md).

## Tooling

See [`TOOLING.md`](./TOOLING.md) for `adrs`, `adr-kit`, and AI harness setup.
