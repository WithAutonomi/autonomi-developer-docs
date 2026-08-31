# ADR-0016 adversarial review — ef646b9

- Date: 2026-08-20
- Reviewed commit: `ef646b9f7d360a5ef2597d3b77cfc08cedb5fd61`
- Current PR base: `487866a249fcb5ad7d8dd7829c017ed63d421343`
- Draft PR: https://github.com/WithAutonomi/autonomi-developer-docs/pull/98
- Reviewer: adversarial — OpenAI GPT-5.6-sol (`openai/gpt-5.6-sol`)
- Result: `NOT-READY`
- Independence: same model/provider as prior lanes; implementer provider unrecorded, so evidence remains weaker

## Findings

### HIGH — Same-interface wording permits a non-existent composite SDK route

Anchors: `adr/ADR-0016-released-truth-for-public-developer-docs.md:77,80`, `CLAUDE.md:139,142`, and the binding/transport differences in `planning/released-antd-v0.11.2-audit.md:98-114` at the reviewed commit.

The ADR forbids combining different top-level interfaces, but both Python REST store and Go gRPC retrieve can be labeled SDK. Without route continuity below the top-level interface, incompatible bindings or transports could be combined to fabricate a complete route.

Required disposition: every dependent step in a complete route must use one concrete binding, transport, installation identity, runtime/configuration, and carried state where applicable. Detailed identifier schema remains specification work.

### HIGH — ADR-0011's unconditional SDK-primary stance is changed but not superseded

Anchors: `adr/ADR-0011-information-architecture-and-content-design.md:47,50,79` and `ADR-0016:106,132,159` at the reviewed commit.

ADR-0016 permits SDK journeys to become unavailable while CLI remains the only recommended complete route, but it says ADR-0011 remains intact and omits ADR-0011 from `Supersedes`.

Required disposition: precisely supersede ADR-0011's unconditional primary-interface stance and replace it with an evidence-conditioned rule. Preserve the rest of ADR-0011.

### MEDIUM — Truth-table evidence omitted concrete within-SDK continuity

The branch-local code-review and verification reports list scenario names but do not provide concrete route identities and missed the cross-binding/transport case.

Required disposition: commit an explicit truth table with concrete binding, transport, installation, runtime/configuration, state-continuity inputs, expected results, actual clause derivation, and ADR-0011 consequence.

### LOW — State, checkpoint, and PR evidence were stale

Records still named older reviews and CI heads, and the PR body called pre-amendment reports final. Reconcile them with the current exact head and distinguish scope-gated no-op checks.

### LOW — Historical v0.11.2 defect used present tense

Scope the gRPC issue sentence explicitly to v0.11.2 and use past tense because current base includes the fix and issue #233 is closed.

## Truth-table challenge

All reviewed scenarios passed except:

- Python SDK store plus a different SDK binding/transport retrieve: ambiguous and could falsely pass.
- SDK unavailable while CLI is recommended: allowed by ADR-0016 but conflicts with Accepted ADR-0011.

## Evidence integrity

- Exact local/remote head and clean worktree confirmed.
- Exact-head ADR Governance and GitBook checks passed.
- Prose/sweep checks were scope-gate no-ops.
- No implementation, mechanism, skill, docs, manifest, or Accepted ADR changed.
- Historical audit limitations remained explicit.
- Craft and clean-context remained pending.

## Single most important correction

Define complete-route continuity below the four top-level interface labels so incompatible SDK bindings or transports cannot fabricate an end-to-end route.
