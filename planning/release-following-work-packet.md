# Release-following documentation — work packet

Date: 2026-10-14
Stage: Planning
Role: Coordinator / planner
Status: Proposed execution scope; temporary direct release checking approved by Jim in conversation
Unattended mode: No
Repository base: `295695745e38c4b17d619ed8f7c5fea17f0cefb1`
Working branch: `plan/released-truth-next`

## Goal and reason

Make a public software release trigger a documentation review, without treating unreleased code as a product update. Begin with the CLI so the complete process can be exercised before adding more publication channels.

Jim approved temporary direct publication checks in the documentation updater while Inventory's release feed is unfinished. This is a limited implementation inside the existing process, not a second general release catalogue. Future Inventory input should replace discovery without replacing page verification or review.

## Sources and authority

- [Issue #103 — adopt released truth in rules and tooling](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103).
- [Issue #104 — verify pages and replace their old records](https://github.com/WithAutonomi/autonomi-developer-docs/issues/104).
- [ADR-0016: Public documentation describes obtainable releases — documentation repository](../adr/ADR-0016-released-truth-for-public-developer-docs.md): Accepted; controls public source selection despite older authoring instructions.
- [ADR-0003: Verification-block source-of-truth model — documentation repository](../adr/ADR-0003-verification-block-source-of-truth.md): preserve the existing block fields and modes unless a superseding decision is approved.
- [ADR-0004: Tiered execution — documentation repository](../adr/ADR-0004-deterministic-scanner-model-audit-loop.md), [ADR-0006: Separate metadata and prose update tracks — documentation repository](../adr/ADR-0006-separate-metadata-and-prose-update-tracks.md), and [ADR-0007: Fail-closed operation and the GitHub artifact topology — documentation repository](../adr/ADR-0007-fail-closed-and-github-artifact-topology.md).
- `CLAUDE.md`, `planning/verification-workflow.md`, both `planning/routines/upstream-sweep*` documents, `scripts/sweep_poll.py`, `repo-registry.yml`, `component-registry.yml`, the three sweep/prose guard workflows, and `scripts/tests/` at the base above.

## What is true at the planning checkpoint

- The published content has had release-based updates, but the rules and automation still implement merged-source tracking. Issue #104 records 108 old verification blocks and six missing page mappings/blocks.
- The scanner resolves declared refs and skips `target-manifest` blocks. It does not load or validate a release manifest. Existing guards prohibit routine edits to those pins.
- Component-to-page mappings exist and guide the audit; the scanner does not itself select affected pages through that map.
- The external Claude routine is recorded as paused on 2026-09-25. Its live enabled state has not been inspected. Committed schedule instructions and the issue describe different times; reconcile the actual setting before activation.
- The current local root checkout is an older branch. This worktree was created from fetched `origin/main`; earlier worktrees and untracked work were preserved.
- Inventory's current main has pricing publication but no consumable general release feed. Neither Inventory completion nor pricing changes are prerequisites for this first unit.

## First working unit

Observe the CLI's GitHub release track and npm distribution, compare with the documented version, identify affected CLI pages, and prepare a reviewed update with evidence. Never merge or publish automatically.

Primary pages: `docs/cli/use-the-cli.md` and `docs/cli/command-reference.md`. Inspect CLI-specific statements in `docs/reference/source-repositories.md` and the other pages mapped to `ant-cli` for contradictions. Shared pages must not be certified in full from a CLI-only check.

The October 14 discovery reported documented CLI 0.3.8 and published CLI 0.3.10 as a candidate. Re-resolve publication and source identities during the implementation audit; this packet approves neither version nor a documentation update. `ant-core` is a separate release track, even though it shares a repository.

Preserve Jim's existing preference for ordinary unversioned installation commands. Record exact versions used for verification and check what the advertised installers actually select. A fixed audit record does not freeze a moving installer. Any proposal to change public install defaults needs a separate owner decision.

## Immediate output: short specification and decision check

Before code changes, write the bounded specification under issue #103. It must settle:

1. The minimal `target-manifest.yml` shape: product/context, exact source identity, public distribution evidence, and shipped dependency/pairing evidence needed by the affected claims. Several products or contexts may use different commits from one repository.
2. How existing page blocks and component mappings match the selected entries, without adding a parallel page map unnecessarily.
3. GitHub/npm release selection and cross-channel disagreement handling. Package availability, source identity and working examples are separate evidence; tags alone are insufficient.
4. The candidate report and permitted metadata/prose changes. Preserve mechanically distinct update tracks and stronger review for rendered changes. A new branch name must not bypass pin protection.
5. Failure, duplicate-proposal and staged-migration behavior. Unmigrated pages remain an explicit backlog; no automatic fallback to merged-source advancement and no invented verification status or renewed date.
6. How later Inventory input replaces direct discovery, without assuming an unpublished Inventory schema or endpoint.

Inspect the accepted operational decisions against the proposed contract. Draft a narrowly scoped Proposed successor if outcome handling, fallbacks, collision rules or fingerprints change. Do not edit Accepted ADRs or reopen the released-truth policy. Exact branch names and report fields belong in the specification, not this packet.

## Proposed implementation sequence

1. Review the specification and any necessary Proposed decision; obtain approval for the bounded scanner, test and workflow changes.
2. Implement publication detection and baseline validation using offline fixtures, then verify bounded read-only discovery against the real providers.
3. Audit the selected CLI release and affected instructions. Replace page records only after the corresponding checks, preserving explicit runtime/platform limitations.
4. Demonstrate an unpublished source change producing no release proposal, a published release producing the correct candidate, and failed/disagreeing evidence preventing a misleading update.
5. Review the first complete CLI update and its checks before publication. Expand to daemon, bindings and remaining pages as separate bounded units.
6. Separately verify the external routine's configuration and permissions, run an authorized hosted trial, and seek activation approval. Other pages must remain protected during partial rollout.

The browser-documentation work in [its packet](browser-sdk-docs-work-packet.md) is an independent priority. It need not wait for completion of the updater.

## Verification and reviews

The existing Repository Tests workflow and applicable PR checks are the CI authority. New production checks must cover the actual promotion branches, not report success through an unrelated scope skip. No CI result exists for this planning branch.

Existing implementation checks, to run from the eventual implementation branch:

```bash
python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'
python3 -I scripts/adr-governance.py
git diff --check
```

Specify the new validator command and focused tests before implementation. Necessary coverage includes publication versus tag/branch changes, stable versus prerelease selection, multiple same-repository identities, provider disagreement/failure, moved source identity, changed manifests, pin mutation and unchanged legacy-page records. Tests and workflows may change only within the expressly approved mechanism slice; retain the protections whose implementation changes.

| Review | Requirement and selection | Due point | Disposition at packet creation |
|---|---|---|---|
| Craft | Required for this shared-repository planning unit; requested | Packet checkpoint, then each meaningful implementation unit | PASS on initial packet text; no conformance findings |
| Adversarial | Required at milestone; requested for this packet milestone | Challenge scope/policy at packet checkpoint; implementation readiness at the working CLI milestone | READY-WITH-NITS for planning only; see joint checkpoint in the browser packet |
| Clean-context | Required under the production-bound profile | First working CLI milestone, before PR/merge readiness | Not run; not yet due. No waiver or approved deferral. |

No implementation unit is being marked Done or silently deferred. The later specification must name the clean-context execution route; prior feature-specific waivers do not carry over.

Planning checks: tracked-diff whitespace check and explicit new-file whitespace checks passed. No code tests were run for these text-only changes. Fresh review results and their limits are recorded in the [joint planning checkpoint](browser-sdk-docs-work-packet.md#planning-review-checkpoint); they do not establish implementation readiness. These uncommitted packets are not yet reproducible from a branch checkout alone.

## Boundaries and stop conditions

Current output is planning only. Scanner, guard, registry, metadata, external routine, release baseline and public content changes require the next approved slice. No commit, push, PR, merge, publication, schedule activation, paid operation or production-network write is authorized by this packet. Read-only checks and later isolated free-download tests must not alter personal configuration.

Stop for a required decision change, unsupported public claim, unavailable required runtime evidence, new dependency or unrelated mechanism change. Missing checks stay missing. Do not infer a passing clean-context review or public release from local checks.

## Required handoff

Return the specification, precise decision amendments if needed, approved-versus-proposed scope, commands and real results, review outcomes and remaining evidence gaps. The first implementation approval should be for a working CLI update process, not the entire documentation estate.
