# ADR-0016 adversarial review — dfd14da

- Date: 2026-08-20
- Reviewed commit: `dfd14dabcbec4706449ae6af1270328ed6dc26af`
- Current PR base: `487866a249fcb5ad7d8dd7829c017ed63d421343`
- Draft PR: https://github.com/WithAutonomi/autonomi-developer-docs/pull/98
- Reviewer: adversarial — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Result: `NOT-READY`
- Independence: same model/provider as prior review lanes; implementer provider unrecorded, so evidence is weaker

## Blocker

### HIGH — Qualification is ambiguously global to the release set and local to individual journeys

Anchors at the reviewed commit: `adr/ADR-0016-released-truth-for-public-developer-docs.md:43,73,87,89,99,180`.

The ADR selects one coherent release set and requires its mandatory baseline to pass across every default or recommended interface. Elsewhere, it allows an incumbent to remain supported only for qualifying journeys and says affected guidance can withdraw one journey.

Those rules permit conflicting outcomes. If one active set supports recommended SDK and CLI journeys and the SDK store journey later fails, the whole set can be disqualified by the mandatory baseline, while the journey-local clauses allow only SDK guidance to be withdrawn and CLI support to remain.

Required decision: make qualification and fallback unambiguously either global to the coherent release set or journey-local with per-journey incumbents reconciled against the one-manifest/one-coherent-set invariant. Then align mandatory-baseline, incumbent, no-baseline, validation, and verification language.

## Low finding

The committed state/checkpoint described exact-head CI as pending after it had passed and still called the historical branch point `origin/main`. Final records must distinguish branch point from current PR base and state that prose/sweep checks succeeded as scope-gate no-ops rather than substantive coverage.

## Evidence integrity

- Local and remote head matched `dfd14da`; worktree was clean.
- Current PR base was `487866a`; PR was mergeable but behind base, with no conflicts in the eight changed files.
- Exact-head ADR Governance, GitBook, and preview checks were green.
- `prose-guard`, `sweep-guard`, and `sweep-sha-reachability` succeeded but their substantive steps were skipped because the branch name was outside their prose/sweep scopes.
- No branch commit changed CI, tests, scripts, gates, rendered docs, skill content, registries, manifests, or Accepted ADRs.
- ADR content had not changed since `4873f36`; later commits were review/state evidence.
- The v0.11.2 audit remained explicitly historical and was not used as v0.12.0 implementation evidence.
- Craft and clean-context remained pending.

## Test-quality note

ADR governance and 20 governance tests passed but exercise structure and Accepted-ADR immutability, not qualification granularity. The 10/10 goal verification did not exercise the conflicting mandatory-baseline scenario and must be updated after the decision.

## Single required decision

Define one qualification and fallback unit—global release set or per journey—and make all related clauses agree.
