# ADR-0018: Retire the beta developer skill and its distribution

- **Status:** Proposed
- **Acceptance:** Pending human review; no acceptance recorded.
- **Date:** 2026-09-22
- **Decision owners:** Jim Collinson
- **Supersedes:** ADR-0012; ADR-0013; ADR-0014; ADR-0003 (skill metadata obligations and retirement-notice block requirement only); ADR-0004 (skill scanning and validation only); ADR-0006 (skill maintenance and release coherence only); ADR-0010 (retirement-notice verification-block requirement only)
- **Superseded by:** none
- **Related:** ADR-0017 (documentation information architecture and content design)

## Context

The beta developer skill and its plugin distribution are being retired. The separate general Autonomi skill is an external prototype, not a continuation of this repository's maintained developer-skill contract.

## Decision Drivers

- End obsolete distribution and maintenance obligations.
- Avoid a disproportionate compatibility service.
- Preserve documentation verification safeguards.

## Considered Options

1. Continue maintaining the beta skill: retains obsolete obligations.
2. Provide a versioned migration or forwarding manifest: creates continuing compatibility work.
3. Withdraw distribution and retain a short notice: chosen.

## Decision

Retire `skills/start/`, `.claude-plugin/`, and their skill-only registry, scanning, metadata, release, and maintenance obligations.

Withdraw the existing raw skill and manifest URLs without retaining the old manifest, issuing a major-version bump, or providing a compatibility service. This is retirement, not relocation or automatic migration.

Retain a short administrative notice at the existing developer-skill documentation URL, included in GitBook navigation. It records this decision without installation commands or technical product claims. Remove its obsolete ant-sdk verification stamp; no replacement ant-sdk SHA can verify retirement. This exception applies only to that notice.

The general skill's separate home is [WithAutonomi/skills](https://github.com/WithAutonomi/skills). Identify it as a distinct prototype, not a newly maintained product contract or an artifact automatically maintained by this repository's scanner.

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

Agents may draft this proposal but must not accept it. Supersession is recorded here; Accepted originals remain immutable.
