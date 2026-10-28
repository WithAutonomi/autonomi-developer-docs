# Released-truth migration inventory — 2026-10-28

This is the structural snapshot for foundation Unit 1. It records verification and mapping debt in the repository after Browser SDK 0.1.4 promotion. It is not the release/artifact inventory required before component migration; that later inventory must resolve obtainable versions, package identities, exact source commits, compatibility, and runtime gaps.

## Verification-block snapshot

- Total verification blocks: 114.
- `target-manifest` blocks: 6, all for Browser SDK claims.
- `current-merged-truth` blocks: 108, frozen as migration debt.
- Pages containing legacy blocks: 54.
- Multi-component pages containing legacy blocks: 22.
- Legacy blocks on those multi-component pages: 74.

The six Browser blocks remain authoritative only for their Browser SDK claims. Four shared SDK pages contain both Browser released evidence and legacy evidence for other components, so those pages are not fully migrated.

## Known unmapped technical pages

Issue [#104](https://github.com/WithAutonomi/autonomi-developer-docs/issues/104) identifies six technical pages without a verification block or complete component mapping:

- `docs/sdk/native/README.md`
- `docs/sdk/native/csharp.md`
- `docs/sdk/native/nodejs.md`
- `docs/sdk/native/python.md`
- `docs/sdk/reference/native-sdks.md`
- `docs/sdk/use-antd.md`

These pages must be mapped, release-audited, and stamped or explicitly deferred during their component batch. They must not receive inferred baseline records in Unit 1.

For Unit 1 acceptance criteria, see [Released-truth foundation specification](released-truth-foundation-spec.md). For sequencing and later release-inventory requirements, see [Released-truth rollout plan](released-truth-foundation-plan.md).
