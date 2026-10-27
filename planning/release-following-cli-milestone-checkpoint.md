# GSD checkpoint — first working CLI release-following mechanism

Date: 2026-10-26
Project: Autonomi Developer Documentation
Slice: issue #103 CLI release-following mechanism, before baseline or documentation promotion
Status: Stop for commit, clean-context, CI, and PR authorization

## What exists

The local, uncommitted implementation discovers stable CLI releases from GitHub and npm, reconciles exact versions and source commits, observes both moving installers, maps affected pages, validates additive release baselines, and adds guarded metadata/prose promotion routes. It does not approve a release, modify the manifest or documentation, activate the hosted routine, commit, push, or publish.

Unit 1 implementation verification passed 10/10 goals and Craft passed. Unit 2 implementation verification passed 7/7 goals and Craft passed. No Craft CONFORMANCE findings remain.

## Evidence

- Release-following tests: 31/31 passed.
- Existing scanner tests: 11/11 passed.
- Documentation guard tests: 31/31 passed.
- Full repository suite: 93/93 passed.
- Isolated release-baseline validator: passed.
- ADR governance: passed.
- Whitespace check: passed.
- Fresh live scanner: exit 0, `status: ok`, no errors.
- Live candidate: CLI 0.3.12, tag `ant-cli-v0.3.12`, commit `6096b1c8caf6688d6825fcb9ff61fa1b590d984b`.
- Live installer evidence:
  - Linux/macOS: path commit `1a32bc6af3f3a8a3129f45d0fe3d60d5cdf76bb1`, blob `8da2f202afddbc39bdba6f3b52caba53f73de905`.
  - Windows: path commit `8658e16cbdaee8c2f2d7fb66d43498eb0f95c95a`, blob `d837fe3a90261ad1320b72e9d2d343979dda5251`.
- Full private live output outside the checkout: `/var/folders/f_/j942sskj6nx67b6gk3rqgsqm0000gn/T/opencode/release-following-live-20261026.json`; 47,366 bytes; SHA-256 `9a38daf69fd5193b6b25f0165264b38c56b21977ffd23010926c95ad9aada857`.

No archive, signature, or installer was downloaded or executed. No baseline was promoted.

## Review selection and timing

| Lane | Requirement and selection | Due point | Result |
|---|---|---|---|
| Craft | Required and Requested for each meaningful unit | Unit checkpoints | PASS for Units 1 and 2; no CONFORMANCE findings |
| Adversarial | Required and Requested | This milestone | NOT-READY; report summarized below |
| Clean-context | Required and Requested | This milestone, before PR readiness | Not run; required gate not discharged because the revision is uncommitted and cannot satisfy the clean committed-root precondition |
| CI | Green of record | Before PR readiness | Not run; commit and push remain unauthorized |

`clean-context deferred: configured lane unavailable or unverified for this uncommitted revision.` No preparation, authentication, or inference ran.

## Adversarial report

Reviewer: OpenAI GPT-5.6-sol. The implementer's provider is unknown, so cross-provider independence cannot be confirmed.

Verdict: **NOT-READY**

### Readiness blockers

1. **HIGH — Required shipped `ant-core` evidence can be omitted.** The specification requires the first `ant-cli/stable` baseline to include exact shipped `ant-core` evidence, but the validator currently makes all shipped dependencies optional.
2. **HIGH — Candidate discovery accepts unequal platform sets.** GitHub and npm can each be internally complete under different configurations while exposing five and four platforms respectively; reconciliation does not compare their target-key sets.

### Other finding for owner judgment

3. **MEDIUM — Automated promotion evidence is narrower than the phrase “fully audited promotion.”** CI checks that the promotion record exists, but not that it contains every authenticity result, and it does not reject a placeholder `verified_date`. The specification requires the evidence but does not define a detailed machine-readable record schema. Treat this as a human-review responsibility or separately approve a schema; do not grow one implicitly.

### Scope observations

- Keep the unrelated untracked GitBook cache-investigation note out of any release-following commit.
- The detailed authenticity helper is currently exercised by offline tests and described in the routine, not invoked automatically by the validator CLI. This is not one of the two named readiness blockers.

### Test-quality and proportionality notes

The reviewer reproduced all declared local checks and the live artifact hash. Provider mocks and disposable Git histories are substantive. Missing coverage corresponds to the two HIGH findings. Most implementation breadth follows the approved specification; no new dependency or unrelated framework was introduced.

## Decision recommendation

A taste review found the proportional choice **SETTLED**: fix only the two deterministic HIGH blockers. The recommendation follows the owner's preferences that machines carry precise, repeatable checks and that the implementation remain the minimum that earns its keep.

Do not add a promotion-record schema in this loop. Carry the MEDIUM finding as an explicit human-review limitation unless Jim separately chooses to mechanize it.

## Owner disposition and focused remediation

Jim approved the proportional recommendation: fix only the two deterministic HIGH blockers and leave the MEDIUM promotion-record concern as a visible human-review responsibility.

The focused remediation is complete:

- `ant-cli/stable` now requires exact shipped `ant-core` evidence; unrelated components retain the optional dependency rule.
- Candidate reconciliation now requires the exact specified five target keys on both GitHub and npm, with identical sets. Unequal or jointly reduced sets cannot emit a candidate.
- Release-following tests: 33/33 passed.
- Existing scanner tests: 11/11 passed.
- Documentation guard tests: 32/32 passed.
- Full repository suite: 96/96 passed.
- Independent focused verification: 4/4 goals passed.
- Focused Craft Review: PASS, with no findings.

The adversarial report was not rerun, in accordance with the milestone policy. Its original NOT-READY verdict and ranked findings remain the report Jim received; the two HIGH findings have documented post-report dispositions and independent evidence above. The MEDIUM finding remains carried, not silently dismissed.

## Authorization boundary

Commit, push, CI, clean-context dispatch, PR/issue creation, baseline promotion, documentation changes, hosted-routine activation, merge and publication remain unauthorized. The unrelated untracked GitBook cache-investigation note must not enter a release-following commit.
