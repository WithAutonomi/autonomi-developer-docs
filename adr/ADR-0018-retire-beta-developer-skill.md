# ADR-0018: Retire the beta developer skill and its distribution

- **Status:** Accepted
- **Acceptance:** Prospective — accepted by Jim Collinson as decision owner after review of PR #102 on 2026-09-25.
- **Date:** 2026-09-22
- **Decision owners:** Jim Collinson
- **Reviewers:** Jim Collinson
- **Supersedes:** ADR-0012; ADR-0013; ADR-0014; ADR-0003 (skill metadata obligations and retirement-notice block requirement only); ADR-0004 (skill scanning and validation only); ADR-0006 (skill maintenance and release coherence only); ADR-0010 (retirement-notice verification-block requirement only)
- **Superseded by:** none
- **Related:** ADR-0017 (documentation information architecture and content design)

## Context

The beta developer skill and its plugin distribution are being retired in favor of a single, more general Autonomi skill and its supporting processes in the skills repository.

## Decision Drivers

- Give agents and users one general skill, with more flexibility and a better experience than several skills in different locations.
- House this and future skills in one findable location that supports their distribution and installation.
- End obsolete distribution and maintenance obligations.
- Avoid a disproportionate compatibility service.
- Preserve documentation verification safeguards.

## Considered Options

1. Continue maintaining the beta skill: retains obsolete obligations.
2. Provide a versioned migration or forwarding manifest: creates continuing compatibility work.
3. Retire it in favor of the general skill in the skills repository, retaining a short notice: chosen.

## Decision

Retire `skills/start/`, `.claude-plugin/`, and their skill-only registry, scanning, metadata, release, and maintenance obligations.

Withdraw the existing raw skill and manifest URLs without retaining the old manifest, issuing a major-version bump, or providing a compatibility service. This is retirement, not relocation or automatic migration.

Retain a short notice at the existing developer-skill documentation URL, included in GitBook navigation. It records the deprecation and links to the general skill, without installation commands. Remove its obsolete ant-sdk verification stamp; no replacement ant-sdk SHA can verify retirement. This exception applies only to that notice.

The general skill and its supporting processes live in [WithAutonomi/skills](https://github.com/WithAutonomi/skills), which also houses future skills. That repository maintains them; this repository's scanner and verification rules do not apply to it.

All other public-documentation verification, released-source boundaries, target-manifest protections, update-track enforcement, infrastructure, and fail-closed behavior remain unchanged.

## Consequences

### Positive

- Removes obsolete distribution and maintenance dependencies.

### Negative / Trade-offs

- Old raw URLs stop serving the retired artifacts after publication.
- Installed or cached copies remain; retirement neither uninstalls nor automatically migrates them.

### Neutral / Operational

- Accepted historical records remain unchanged.

## Validation

Confirm withdrawn distribution, notice continuity, absence of skill-only maintenance dependencies, and unchanged documentation safeguards through governance checks, regression tests, and review.

## Notes for AI-assisted work

AI tools helped draft this ADR. Jim Collinson accepted it through PR #102 on 2026-09-25. Supersession is recorded here; Accepted originals remain immutable, and later changes require a superseding ADR.
