# Browser SDK documentation — work packet

Updated: 2026-10-16
Stage: Implementation — source audit, isolated browser exercise, guide and checks
Role: Coordinator / documentation planner
Status: [Draft PR #106](https://github.com/WithAutonomi/autonomi-developer-docs/pull/106) open. Implementation CI passed all 53 tests and GitBook generated a preview; required fresh-context review remains blocked. Not merge-ready.
Unattended mode: No
Repository base: `295695745e38c4b17d619ed8f7c5fea17f0cefb1`
Working branch: `docs/browser-sdk-guides`

## Draft PR authorization — 2026-10-16

Jim explicitly authorized committing and pushing this browser-documentation change and opening one draft PR in the documentation repository. This includes the overview, tutorial, SDK navigation corrections, source records and approved component-map test adjustment. It excludes the separate release-updater plan. No merge, publication, scheduler activation or ADR acceptance is authorized.

The required fresh-context lane is now due for the review candidate. Launcher verification was blocked by denied access to the GSD repository before preparation, authentication or inference. Record `clean-context deferred: configured lane unavailable or unverified`; no substitute, retry through another access route, or pass is inferred. The authorized draft may be opened with this outstanding requirement, but is not merge-ready.

Writing the additional temporary failure/retry browser check was also denied in this session. That scenario remains unexecuted. Do not substitute successful earlier reads for this missing exercise or retry the denied access through another tool/path.

## Goal and reason

Explain browser applications as one use of the Autonomi SDKs, then provide a separate, working public-retrieval tutorial. Browser documentation is a near-term content need, independent of the CLI release-updater pilot.

## Live implementation scope

Jim requested the browser guide with its intended long-term title and IA placement, and an information banner at the top identifying its experimental status. This authorizes the bounded guide implementation, source enrollment/component mapping and isolated free browser-read validation. The distinct guide and explicit banner preserve the separation required by ADR-0016; no stable-support claim or ADR change is authorized.

Jim's subsequent editorial direction separates explanation from instruction and avoids presenting browser development as an alternative to SDK use. Use `docs/sdk/build-in-browser.md`, titled `Browser SDK`, as an explanatory child of `Build with the SDKs`. Put the existing tested example in `docs/sdk/how-to-guides/retrieve-data-in-browser.md`, titled `Retrieve Data in the Browser`, under SDK How-To Guides. Add the browser choice to the SDK connection table and reconcile directly related SDK index/reference text.

Jim then approved giving all three overview choices equal standing: `Native SDKs`, `Browser SDK` and `Local-Daemon Clients` are children of `Build with the SDKs`. The existing native/local-daemon overview files keep their paths, receive the agreed titles and move out of the Reference navigation group. Related link labels and chooser order match. This follow-up changes navigation/titles only, not technical instructions, code examples or source records.

Use the existing `target-manifest` mode for the two browser pages and the browser-source blocks added to shared SDK landing pages. The manual pin covers browser claims only; existing non-browser verification blocks remain unchanged. This is not the repository-wide mechanism in issue #103, and existing automation does not validate the manifest.

Jim separately approved changing the historical component-map regression test to retain checks on every existing entry while allowing newly enrolled components. This is an explicitly authorized test-expectation change, to be called out in review; do not weaken checks on the existing entries or alter the scanner/guards.

Allowed changes: browser overview and retrieval tutorial; their navigation, chooser and directly related SDK index/reference text; source/component registration; the scoped target manifest; the single previously approved regression-test adjustment; this packet, source/runtime evidence and the current-state note. The overview may explain source-backed streaming, private reads and uploads without adding untested runnable examples or claiming runtime verification of those features. Commit/push and one draft PR are authorized above; personal-environment installations, paid uploads and publication remain forbidden.

## Source and policy boundary

- [ADR-0016: Public documentation describes obtainable releases — documentation repository](../adr/ADR-0016-released-truth-for-public-developer-docs.md) permits stable/general-availability software in default public documentation and requires clearly separate treatment for pre-release documentation.
- `CLAUDE.md` prohibits verifying against repositories absent from `repo-registry.yml`.
- `repo-registry.yml`, `component-registry.yml`, `docs/SUMMARY.md`, `docs/sdk/install.md`, `docs/sdk/native/nodejs.md`, `docs/sdk/reference/native-sdks.md`, and `docs/rust/embed-a-node-in-your-application.md` define the current scope and coverage.

The planning discovery identified a separate browser SDK publication, rather than browser support in the existing native Node.js package or antd JavaScript client. Jim then requested a bounded read-only investigation of its documentation, source, publication and recorded browser evidence before asking its maintainer. The October 14 follow-up established public publication and an explicit experimental designation. This is support/enrollment research, not a completed guide audit, runtime verification or declaration of stable support.

Unapproved enrollment leads from that October 14 investigation, retained so the next reader can identify the proposed source without reconstructing the conversation:

- Package: `@withautonomi/ant-browser-sdk`, candidate version `0.1.2`; [exact npm metadata locator](https://registry.npmjs.org/@withautonomi/ant-browser-sdk/0.1.2).
- Candidate source: [WithAutonomi/ant-browser-sdk](https://github.com/WithAutonomi/ant-browser-sdk), reported release `v0.1.2` at `a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0`; [release locator](https://github.com/WithAutonomi/ant-browser-sdk/releases/tag/v0.1.2).
- Reported experimental wording: [README at the candidate commit](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/README.md).
- Maintainer contact is not established. Do not assume ownership from Chris's or Nic's release-tool responsibilities. The initial maturity question is answered by the published documentation below; no contact is required to repeat it.

The browser source was enrolled as part of Jim's subsequent guide-implementation request, before the formal guide audit. The earlier discovery did not itself waive the registry rule. The scoped manifest and component mapping are now present for the new page.

## Support answer from the sources — 2026-10-14

The [released README](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/README.md#autonomi-browser-sdk) says:

> This SDK and the direct-browser protocol are experimental. Pin the SDK version and test it against the exact `ant-node` version used by your deployment.

That warning also remains at main revision `1d572a2b5496595f034e4fb5155e7ac4e3bef199`; the [release-to-main changes](https://github.com/WithAutonomi/ant-browser-sdk/compare/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0...1d572a2b5496595f034e4fb5155e7ac4e3bef199) do not announce graduation to stable support.

- Publication: [release run 37335676124](https://github.com/WithAutonomi/ant-browser-sdk/actions/runs/37335676124) succeeded at the exact `v0.1.2` source commit. The [release workflow](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/.github/workflows/release.yml) checks tag/version agreement, WASM provenance, source tests and example builds before publishing the packaged artifact to npm and GitHub. Its `latest` versus beta/rc routing follows the version suffix; it does not override the experimental warning or constitute a supported-browser guarantee.
- Developer documentation exists in the [README](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/README.md) and [five example applications](https://github.com/WithAutonomi/ant-browser-sdk/tree/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/examples). The `docs/` directory contains decisions and audit records rather than a separate guide collection.
- Read-only onboarding: the README describes `AutonomiClient.connect()` with bundled mainnet seeds and `download()` without a wallet or payment RPC. Its explicit-address quick start still contains placeholders. A complete docs example must supply a real file and fresh runtime proof rather than copy those placeholders.
- Browser evidence: the [October 5 audit](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/docs/audits/2026-10-05-webkit-connection-fixes.md) reports Chromium and Playwright WebKit checks on one macOS machine. Retained logs identify Chromium `151.0.7922.34` and Playwright WebKit `26.5`; these are historically exercised versions, not supported minimums. Playwright WebKit is not shipping Safari, and the audit explicitly excludes iOS Safari. No successful Firefox evidence or formal browser support matrix was found in the inspected sources.
- Evidence identity: the October 5 candidate core revision and WASM hash match the [released source record](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/wasm/source.json). That ties the recorded checks to the shipped core, not to a newly executed test of npm 0.1.2; one retained verification log still identifies the pre-version-bump package as 0.1.1.
- Runtime boundaries: [capability checks](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/capabilities.ts) distinguish basic reading from upload workers/storage and media service workers. Do not impose media-only requirements on a basic read or turn API presence into a promise of working network access. Node.js 20.19+ is installation/build tooling, not a requirement for the person using the finished browser application.

No package, browser, probe script, build or test suite was executed in this follow-up. Recorded product checks are attributed to their authors. Neither a release job nor a historical browser audit is a fresh success for the proposed guide.

## Current implementation checkpoint — 2026-10-16

Jim retained a normal title/navigation and a prominent experimental information banner, then asked for a separate explanation and how-to. Both pages now have concise status banners. The overview explains capabilities and browser architecture; the tutorial retains the complete tested image example. Browser links and the SDK chooser preserve the experimental distinction without declaring stable support. The browser is explicitly another SDK option, and both browser and native libraries are described as direct connections.

The approved disposable browser exercise succeeded against the published package on mainnet, in both Vite development and production-preview builds. It required no wallet or payment provider. Exact source, browser, content-hash and command evidence is in [browser-sdk-guide-verification.md](browser-sdk-guide-verification.md). Those results do not promise support for untested browsers or a particular self-hosted node deployment.

The version-specific setup remains in the tutorial, with a short explanation that exact versions make its APIs reproducible. The banner no longer tells a public-network reader to test their own node deployment. This does not change Jim's ordinary CLI installation preference. No maintainer question is pending for the read-only example; ask only if a later task needs a support promise absent from the published sources. No Accepted ADR, scanner, guard, schedule or public website was changed.

## Approved first content unit

The implementation follows these bounded steps:

1. Audit the exact published package, its source identity, bundled WASM identity, browser assets and connection requirements. Use shipped dependencies rather than whichever source is newest.
2. Build a disposable, minimal browser example that retrieves a known public file without a wallet. Verify the returned bytes against an independently known expected value. Record actual browser/version, operating system, package, network and serving conditions.
3. Verify initialization and asset paths, connection failure reporting, cleanup, and repeatability from the documented instructions. Do not infer browser support from a Node.js test or successful package download.
4. Explain what browser applications can do in a source-backed overview, then provide the tested retrieval tutorial with imports, setup, error handling and expected output. Use normal titles and explicit experimental banners.
5. Keep native Node.js-only claims accurate and link to the separate browser package instead of erasing the distinction.
6. Add its approved source/component mappings and truthful verification records. No source stamp may imply a browser runtime test that did not occur.

Public files changed: the browser overview and retrieval tutorial; `docs/sdk/install.md`'s chooser and browser explanation; SDK How-To/Reference landing pages and the reference overview; the Node.js cross-link; SDK navigation. Registry mappings and the scoped manifest follow these browser additions. Existing source blocks remain unchanged; new browser blocks cover only the new browser claims.

## Relationship to release tracking

The browser guide must not wait for automatic release detection. It may use a directly audited release and an approved fixed-source record once the minimum baseline rules exist. Do not invent a third verification mode or stamp moving-main evidence as released truth to bypass that dependency.

Only the small shared decision about recording a directly audited release is a prerequisite. It can be reviewed before the CLI detector, candidate reports, guards or hosted routine are implemented. The browser guide does not depend on those automation deliverables.

The separate release-following work under [issue #103](https://github.com/WithAutonomi/autonomi-developer-docs/issues/103) treats the CLI as the first automation unit, not the only product that can receive documentation changes. Its local planning packet is deliberately excluded from this browser PR. Add browser release tracking later as a bounded publication source once its identity and support status are established.

## Out of scope and stop conditions

- Paid uploads, wallet configuration, production keys, network writes, node deployment and server changes.
- Runnable media-streaming/upload examples, service-worker playback tests, broad browser matrices or a complete browser API reference. The requested conceptual overview describes these source-backed capabilities without claiming they were exercised.
- Changes to native SDKs, antd, Inventory, pricing or release tooling.
- Global installations, personal browser profiles, or hidden local setup needed to make the example work.
- Merge, publication, deployment, scheduler activation, additional PRs or autonomous ADR acceptance. Only the commit/push and single draft PR named above are authorized.

Stop if public-read verification requires paid operations, product fixes, unavailable infrastructure, an unapproved package/dependency, or a policy exception. Record the blocker rather than broadening the example or weakening the checks.

## Verification and reviews

Source identification and a successful example are separate requirements. The approved browser exercise checked real public retrieval, expected bytes and image rendering. All 53 repository tests passed locally with the declared dependency in a disposable Python 3.12 environment and independently in [implementation CI](https://github.com/WithAutonomi/autonomi-developer-docs/actions/runs/38904119556). Jim approved the local setup after baseline reproductions of prerequisite failures. CI remains the authoritative automated result; consult the draft PR for checks on subsequent planning-only commits.

| Review | Requirement and selection | Due point | Disposition at packet creation |
|---|---|---|---|
| Craft | Required; requested | Packet and meaningful content checkpoints | Overview/tutorial split PASS, session `ses_ebba50fa6ffepJwY7YFkhsxURI`; earlier single-guide verdict retained in evidence |
| Adversarial | Required; requested | Completed local content milestone | Split READY-WITH-NITS, session `ses_ebba50f65ffeSk3cMsJ5s28Ilr`; two LOW observations addressed afterward; no second pass |
| Clean-context | Required for public onboarding; requested | Due for the committed review candidate before merge-readiness | Not run: launcher verification denied before preparation/authentication/inference. Requirement retained; unavailable lane is not an approved waiver. |

The earlier packet checkpoint had no product-runtime evidence. The evidence file records the actual browser exercises and implementation CI separately; clean-context is blocked as recorded above. The candidate is not publication-ready. Prior permission limits below describe the historical planning stage, not the current draft-PR authorization.

### Planning review checkpoint

Fresh Craft session `ses_ec5d6f814ffe03xTSRv70y01VH` reported PASS with no findings. Fresh adversarial session `ses_ec5d6f7fbffeILIAnrC8G9Crfj` reported READY-WITH-NITS with no planning blockers: make the browser lead identifiable (MEDIUM) and separate the small recording prerequisite from completion of CLI automation (LOW). The additions above address those two handoff concerns; no second adversarial pass was run. Cross-model independence is not established. Those packets were uncommitted at the planning checkpoint; this browser packet and its evidence are now included in the draft PR.

The subsequent source-answer update was not covered by those earlier planning reviews. It records read-only findings and a narrower open question; no implementation or publication approval is inferred.

## Required handoff

Return the cited support statement, proposed source enrollment, approved documentation placement, exact audited identities, actual runtime evidence and limits, scoped content diff and review outcomes. Seek a maintainer answer only for a specific remaining gap. If blocked, return the missing prerequisite; keep the CLI work moving independently.
