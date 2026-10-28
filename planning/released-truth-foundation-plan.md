# Released-truth rollout plan

Status: ADR-0019 accepted; local implementation, verification, and Craft Review passed. Clean-context review and CI remain pending. Later units require their named checkpoint.

## Milestone

Released truth becomes the safe repository default: authors cannot create or refresh public claims from moving branches, automation cannot propose moving-branch stamp updates, and the remaining migration is measurable.

## Unit 1 — policy and moving-source safety

Scope:

- Add the foundation packet, specification, plan, and `planning/released-truth-migration-inventory-2026-10-28.md`.
- Align `CLAUDE.md`, `README.md`, `CONTRIBUTING.md`, and `planning/verification-workflow.md`.
- Emit legacy blocks as `migration_backlog` without upstream lookup.
- Update scanner tests and routine instructions.

Done when:

- all legacy blocks are reported without GitHub branch resolution;
- released CLI discovery and Browser pins retain their existing behavior;
- full repository tests and required reviews pass;
- no page block, manifest baseline, `.github/workflows/**`, or validator changes.

## Unit 2 — CLI promotion

Re-resolve CLI publication evidence, audit the exact released candidate, and promote the two dedicated CLI pages through the existing mechanism. Shared pages remain migration debt until their other components are audited.

## Unit 3 — reusable profile and shared-page mechanism

Checkpoint before implementation: Jim reviews the common/profile boundary and shared-page rules from the foundation specification.

Scope:

- Define the common release-baseline record and profile dispatch.
- Add a non-CLI profile proving package/source flexibility.
- Permit reviewed page-scope growth.
- Permit grouped promotion where several changed profiles support one shared page.
- Freeze all unrelated legacy and released blocks in every promotion route.
- Add completeness checks for technical-page mappings.

Done when:

- the mechanism supports CLI, Browser, and one materially different component without profile-specific assumptions leaking into the common contract;
- same-repository and shared-page fixtures pass;
- no new verification mode or block field is required.

## Unit 4 — release inventory and component batches

Refresh issue #104 from the committed inventory, then migrate:

1. SDK/antd and language clients.
2. Native SDKs and Direct Rust.
3. Node and local-network tooling.
4. Foundational libraries.
5. Shared concepts, chooser pages, glossary, and source reference.

Each batch adds only the evidence profiles it needs. Automation is optional; released-truth policy is not.

## Unit 5 — routine activation

After the migration reaches zero unexplained legacy blocks:

- verify the hosted routine's actual configuration and permissions;
- run an authorized dry run;
- prove it emits release candidates or manual-review notices but never moving-branch proposals;
- request separate activation approval.

## Review gates

- Craft Review at every meaningful unit.
- Goal verification at every unit checkpoint.
- One adversarial review at the completed foundation milestone and before each PR-ready batch.
- Clean-context review when required by the full shared-repository profile.
- Jim explicitly authorizes every PR creation, merge, routine activation, and any required ADR acceptance.
