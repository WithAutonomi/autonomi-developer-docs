# Maintaining the `autonomi-developer` skill

This skill lives in `skills/autonomi-developer/` and follows the same source-of-truth model as the rest of the docs repo.

## Files that move together

Every release or re-verification pass updates these files together:

- `SKILL.md`
- `version.json`
- `CHANGELOG.md`

## Current scope

This skill is intentionally practical. It covers:

- SDK and daemon workflows
- CLI workflows
- Direct Rust with `ant-core`
- MCP setup rules
- read-only versus upload-enabled architecture
- local devnet testing
- wallet and payment basics needed to build safely

It does not try to teach the deeper routing, transport, or cryptography internals in detail. If the skill grows into those areas later, update the component mapping first.

## Verification inputs

Use the same workflow the docs use:

1. Source audit
2. Draft
3. Verify

Read these repo files before changing the skill:

- `CLAUDE.md`
- `planning/verification-workflow.md`
- `repo-registry.yml`
- `component-registry.yml`

## Components that currently feed this skill

The skill is mapped through `feeds_skills:` in `component-registry.yml`.

Current component coverage:

- `antd`, `openapi`, `proto`, and the documented `antd-*` language bindings
- `ant-core`
- `ant-cli`
- `ant-node`
- `ant-devnet`
- `self_encryption`
- `evmlib`

That means these repos trigger re-verification today:

- `ant-sdk`
- `ant-client`
- `ant-node`
- `self_encryption`
- `evmlib`

## When to re-verify

Run a skill verification pass when:

- one of the mapped repos changes in a way that can affect the skill
- a docs page URL baked into `SKILL.md` changes
- a golden flow in the skill stops matching the current docs or source artifacts
- the skill adds or removes path coverage

## What to verify

### SDK path

Check current daemon defaults and exact route names against the active `ant-sdk` source artifacts.

Use these artifacts first:

- `antd/openapi.yaml`
- `antd/proto/`
- `antd-mcp/README.md` when MCP setup rules are in scope

### CLI path

Check command names, global-flag placement, and quickstart flows against the active `ant-client` sources.

Use these artifacts first:

- `README.md`
- current help output if you have the repo checked out locally

### Direct Rust path

Check named `ant-core` surfaces against the active `ant-client` sources.

Use these artifacts first:

- `README.md`
- public Rust API docs or examples in `ant-core`

### Concepts and safety rules

Check these against the relevant docs pages and source repos:

- public versus private data
- wallet key versus public address versus `DataMap`
- self-encryption behavior
- payment and wallet handling
- local devnet workflow

## Update order

1. Update `SKILL.md`.
2. Update `version.json` with the same version, date, and verified commits.
3. Add a matching entry to `CHANGELOG.md`.

## Versioning

Use Semantic Versioning with these rules:

- major: breaking changes to skill loading or manifest shape
- minor: new paths, new verified examples, or new operational capabilities
- patch: wording fixes, pointer fixes, or re-verification-only updates

Keep the `-draft` suffix until the skill has gone through at least one deliberate re-verification pass after landing in the repo.

## Pre-merge checklist

- [ ] `SKILL.md`, `version.json`, and `CHANGELOG.md` agree on the version.
- [ ] `verified_date` and `published_date` match.
- [ ] every `verified_commits` entry is a real SHA
- [ ] every live-docs URL in `SKILL.md` resolves
- [ ] no hard-coded detail was added without a matching verification source
- [ ] the skill still avoids guessed SDK methods, CLI flags, and MCP tool names
