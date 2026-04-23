# Changelog - autonomi-developer skill

All notable changes to this skill are recorded here.

## [Unreleased]

## [0.1.0-draft] - 2026-04-22

### Added
- Initial in-repo `autonomi-developer` skill package.
- Operational path selector for SDK, CLI, Direct Rust, and MCP work.
- Exact golden flows for daemon health, SDK public data round-trip, CLI public file round-trip, and local devnet startup checks.
- Live reference table for the current docs site.
- Skill version manifest and maintenance guide.

### Changed
- Rebuilt the skill around the current docs and current upstream source artifacts instead of the earlier standalone draft.
- Reduced deep network internals so the skill stays focused on building and shipping applications.

### Verified Against
- ant-sdk: 2ed9b14bda42fbdc604a173cc1af27be0964908f
- ant-client: b0c501a163c1a95bdbfc703892b88a8a91f7e482
- ant-node: 5a5d7d4fed766cd56d0f97f337fcd5ff049bea6a
- self_encryption: 5f9d1646231da7ca2ce60e84d010acfb6d9c29d0
- evmlib: 82f2fccff243b48de0e04ceb71ccb2aa17d810af
