# Verification Workflow

This document defines the repeatable workflow for writing, updating, and re-verifying documentation in this repo.

## Purpose

The repo follows a strict source-of-truth model. Pages must describe the active source of truth for the repos they depend on, not the expected future product shape.

Use this workflow for:
- new pages
- rewrites of inaccurate pages
- updates after public releases
- migration of legacy verification records

## Active mode

The repo retains two verification mode names during migration.

### `target-manifest`

This is the authoritative mode for public technical documentation.

Meaning:
- use a reviewed public release profile and exact refs pinned in `target-manifest.yml`
- include the public distribution, shipped dependency, and deployed-network evidence required by the affected claims
- advance the manifest, scoped page blocks, and dated promotion record atomically

If no reviewed profile supports the claim, defer the technical update or prepare the missing profile. Never fall back to a moving branch.

### `current-merged-truth`

Existing blocks in this mode are historical records of the previous source-selection rule. They are frozen migration debt, not authority for a new or refreshed public claim.

A pure editorial change may leave such a block byte-identical. Work that touches its technical claim must migrate that claim through a reviewed release promotion or defer it.

## Required workflow

Every documentation task follows these stages:

1. Source audit
2. Draft
3. Verify

Do not skip or reorder these stages.

## 1. Source audit

Before writing or editing a page:

1. Identify the page type.
2. Identify the source repos for the page.
3. Identify the reviewed `target-manifest` profile for every affected claim and any legacy blocks that must remain untouched.
4. Resolve the exact public release refs, commit SHAs, and distribution evidence.
5. Collect the canonical source artifacts for the page.
6. Extract the facts, commands, types, and examples the page is allowed to describe.

### Source repo selection

Use these repo files to determine scope:
- `repo-registry.yml`
- `component-registry.yml`

Start with the broad product repos:
- `ant-sdk`
- `ant-client`
- `ant-node`

Add foundational repos only when the topic requires them.

### Canonical source artifacts by page type

#### Reference pages

Use the canonical interface artifacts first:
- OpenAPI specs
- gRPC proto files
- CLI `--help` output
- exported request/response models
- package metadata and published install instructions

If the interface is not present in these artifacts in the reviewed release, do not document it as available.

#### Getting Started and How-to pages

Use:
- runnable examples from the active source repos
- actual daemon defaults and current commands
- published install or download paths

These pages must reflect what a developer can do now.

They must also make the user path explicit:
- say what tool or path the page covers
- explain why a developer would choose that path
- link to alternative supported paths when they exist

#### Language binding pages

Use:
- package metadata
- exported constructors and models
- upstream README examples
- transport/discovery defaults from the binding source

Do not assume every binding shares the same shape unless the source artifacts show that it does.

#### Concept pages

Use:
- code-backed facts from the active source repos

Concept pages can explain the system, but they still must reflect the active source of truth.

Historical notes, research memos, and prior synthesis documents are not authoritative. They may help you locate likely code paths, but every technical claim must still be grounded in the active source repos.

## 2. Draft

Write only from the audited evidence.

Rules:
- Keep the existing information architecture unless the content itself is wrong for the current source of truth.
- Prefer the smallest correct rewrite.
- Preserve structure that is still accurate.
- Use the page template that matches the page type.
- Use only terminology allowed by `CLAUDE.md`.
- Do not put source-audit or verification language into rendered body text.
- Explain a tool or interface before telling the reader to install or run it.
- When a task can be done through multiple supported paths, be explicit about which path the page covers and link the alternatives.

If evidence is missing:
- do not infer the missing details
- do not write a future-state page as if it were current
- either defer the page, leave a thin placeholder, or reframe it conceptually

## 3. Verify

After drafting, verify the page against the audited sources.

### Verification checklist

#### Reference pages

Verify that every:
- endpoint
- method
- command
- flag
- type
- field
- example payload

exists in the active source of truth at the recorded commit.

#### Getting Started and How-to pages

Verify that every:
- install instruction
- command
- code example
- default port or URL
- expected response

matches the active source of truth and is runnable in principle.

#### Concept pages

Verify that every technical claim can be traced to:
- code in the active source repos, or
- a confirmed technical decision

### Verification metadata

Only after verification is complete:

1. Add a verification block for each source repo used.
2. Record the repo, ref, exact commit SHA, verified date, and verification mode.
3. Use multiple verification blocks for multi-repo pages.

Never use `source_commit: TBD` on a page presented as verified.

## Page states

Pages move through these states:

1. `source-audited`
2. `drafted`
3. `verified`
4. `publishable`

Meaning:
- `source-audited`: source repos, refs, SHAs, and canonical artifacts identified
- `drafted`: content written from audited evidence
- `verified`: claims checked and verification metadata populated with real SHAs
- `publishable`: verified and ready to push once repo publishing is set up

## Special rules

### Installation and downloads

Pages about installation, binaries, packages, and versions must point to artifacts users can actually download or install now. These pages are not allowed to get ahead of published artifacts.

### Default branches and previews

Default branches and feature branches can inform future documentation, but they are not public release evidence. Future or pre-release material must remain separate from default-public documentation and cannot advance its verification records.

### Legacy verification blocks

Do not renew a `current-merged-truth` block. Preserve it byte-for-byte during unrelated editorial work. If the work changes a claim it supported, migrate that claim to the active release set or defer the change.

A page containing both modes is a temporary migration state, not a fully verified page. Do not combine the two modes to support one claim or complete developer journey.

## Automation

Automation must follow the same workflow:

1. observe public releases for enrolled component profiles
2. reconcile release channels and exact source identity
3. map release candidates to affected pages
4. re-run source audit -> draft -> verify
5. promote the manifest and verification blocks only after re-verification and human review succeed

Automation reports legacy blocks as migration debt and never compares them with moving branch heads. It does not approve or merge a release promotion.
