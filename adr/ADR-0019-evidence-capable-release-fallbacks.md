# ADR-0019: Require complete release evidence and isolate legacy records

- **Status:** Accepted
- **Acceptance:** Prospective — accepted by Jim Collinson as decision owner after review on 2026-10-28
- **Date:** 2026-10-28
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0007 (scanner read ladder, its `git ls-remote` diagnostic requirement, and no-drift meaning for legacy blocks only); ADR-0005 (scanner credential-precedence sentence only); ADR-0004 (moving-ref detection and no-drift meaning for legacy blocks only)
- **Superseded by:** none
- **Related:** ADR-0016; issues [#103](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103) and [#104](https://github.com/WithAutonomi/autonomi-developer-docs/issues/104); `planning/released-truth-foundation-spec.md`

## Context

The documentation scanner previously checked the latest code on each project's main development branch. If GitHub's normal web service refused a request, the scanner could ask Git directly for the latest code reference using `git ls-remote`.

ADR-0016 changed the source of truth. Public documentation must now describe software that people can obtain as a release, not the latest development code. Proving a release can require downloadable files, package-registry records, installers, source tags, and details of included dependencies. A Git lookup can confirm a source tag, but it cannot prove that the downloadable release, packages, and installers exist and agree with each other.

This matters because the documentation is a promise about what a developer can install and use. A source tag can exist while packages are missing, installers select another version, or release files are incomplete. Treating the tag as sufficient could make the docs look freshly verified while their instructions fail. Stopping creates work for maintainers, but it is safer than giving developers false confidence.

The repository also contains older verification records based on development branches. Continuing to update them would make their claims look fresh without proving an obtainable release. They must remain visible until migrated, but they must not keep advancing against changing branches.

## Decision Drivers

- Documentation must describe software developers can obtain.
- Missing evidence must never be mistaken for a valid release.
- Failures must be visible and useful without creating unnecessary issues.
- Existing human review and safety checks should remain in place.

## Considered Options

1. Keep the Git lookup as the final backup. Rejected because it cannot provide all the evidence needed to prove a release.
2. Stop after the first failed request. Rejected because GitHub may reject an access token while allowing the same public information to be read without one.
3. Allow a backup source only when it can provide the same complete and trustworthy evidence. Chosen.

## Decision

A backup source may be used only when it provides the same required information, authority, identity, freshness, and failure behavior as the original source.

If GitHub rejects an authenticated request with HTTP 403, the scanner may retry the same public request without authentication. If the provider remains unreachable or returns an invalid response, the scanner stops and reports an error rather than guessing. This is called failing closed.

If the providers respond correctly but the release information is incomplete or contradictory, the scanner creates no release candidate and sends the affected records for manual review. It does not substitute development-branch code, a Git lookup, or partial evidence.

Older `current-merged-truth` records receive no branch lookup. The scanner lists each one in `migration_backlog`. A run containing only this backlog creates no new GitHub issue or pull request, and it does not claim that these older records were checked for changes. Issue #104 remains the migration ledger.

This decision does not change the later audit of exact source commits. Existing failure issues, manual-review issues, pull-request collision handling, fingerprints, labels, write restrictions, and human approval remain unchanged.

## Consequences

### Positive

- Partial source information cannot be presented as proof of a complete release.
- Older records stay visible without driving unsafe automatic updates.
- Existing review and approval safeguards remain in place.

### Negative / Trade-offs

- A provider outage can stop a scan even when the source code remains reachable through Git.
- Older records receive no change monitoring until they are migrated.
- Adding more evidence providers gives a scan more possible points of failure.

### Neutral / Operational

- Incomplete or conflicting release information creates manual-review work.
- Scanner diagnostics record the attempts actually made; they no longer promise a Git lookup.

## Validation

- Tests prove older records cause no provider, branch, or Git lookup.
- Tests prove the authenticated-to-public retry and structured error reporting.
- Provider failures produce an error with empty results.
- Incomplete or conflicting evidence produces manual review and no release candidate.
- Complete, agreeing evidence still produces deterministic release candidates.
- Changing these boundaries requires another superseding ADR.

## Notes for AI-assisted work

AI tools may help draft this ADR, but **must not mark it Accepted without human review**. Accepted ADRs are immutable: create a new superseding ADR rather than editing an Accepted ADR.
