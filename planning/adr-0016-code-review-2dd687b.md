# ADR-0016 code review — 2dd687b

- Date: 2026-08-20
- Reviewed commit: `2dd687bdd4a958694a53049014791ede0b67c0be`
- Base: `af6d0e9da96dd9b7d31105accbeb9b6a181aaf37`
- Reviewer: codereviewer — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Result: `issues_found`

## Checks

- ADR governance: passed, 1 ADR checked.
- Governance tests: passed, 20 tests.
- `git diff --check origin/main...HEAD`: passed.
- Full diff inspected: five added files, 706 insertions.
- Content commit `9c2f1da15de685e54fdb0ef8eceeedfa2692f153`: inspected in full.
- Accepted ADR-0003 through ADR-0007 and ADR-0012 through ADR-0015: byte-identical to base.
- ADR-0016 remained Proposed with human-only acceptance.
- CI: not run; local evidence is not CI-green.
- Worktree: clean at review time.

## Findings

### HIGH — Pointer parity lacks an untrusted-content boundary

Anchors: `adr/ADR-0016-released-truth-for-public-developer-docs.md:101-103` and `skills/start/SKILL.md:81-83` at the reviewed commit.

Pointer parity requires agents to ingest fetched documentation before answering release-sensitive detail but does not require fetched pages to be treated as untrusted factual data. It does not prevent embedded instructions from overriding the skill or user request, require content delimiting, or require independent validation before actions are taken from fetched material. The historical audit mentions this safeguard, but the audit is explicitly not current authority.

Required disposition: add a durable prompt-injection boundary for pointered content.

### MEDIUM — Mutable-alias policy is internally inconsistent

Anchors: `ADR-0016:57,82,155,166` at the reviewed commit.

The ADR requires every default or recommended command to use an immutable selector while also allowing a mutable alias to continue to be recommended after requalification.

Required disposition: mutable aliases may only appear as explicitly unsupported conveniences and can never be default or recommended commands.

## Previous-finding dispositions

- Deterministic fallback across all eligible sets: resolved.
- Requalification on every qualification-input change: resolved.
- Immutable default selectors: resolved, but mutable-alias recommendation language remains inconsistent as described above.

## Remaining risks

- Applicable pull-request CI has not run.
- Goal verification, adversarial re-review, Craft, and clean-context remain outstanding.
- The v0.11.2 audit is historical; a fresh candidate audit is required before implementation.
- Implementer provider is unrecorded; cross-provider independence is unconfirmed.
