# Browser overview and tutorial — source and runtime evidence

Date: 2026-10-16
Scope: `docs/sdk/build-in-browser.md`, `docs/sdk/how-to-guides/retrieve-data-in-browser.md`, SDK chooser/index links, source enrollment and scoped browser release pins.
Status: [Draft PR #106](https://github.com/WithAutonomi/autonomi-developer-docs/pull/106) open; implementation CI passed 53 tests and GitBook preview succeeded. Earlier browser exercises and scoped reviews are retained below. Required clean-context review and additional failure/retry exercise are blocked by current tool permissions; no merge-readiness or publication claim.

## Approved scope and policy

Jim first requested a distinct guide with its long-term title/navigation and a prominent experimental information banner, then requested an explanatory page and separate how-to. `Browser SDK` is now a child of `Build with the SDKs`; `Retrieve Data in the Browser` sits under SDK How-To Guides. Linked descriptions preserve the experimental distinction. This keeps the interface-specific explanation within SDK rather than tool-neutral Core Concepts, consistent with [ADR-0016: Public documentation describes obtainable releases — documentation repository](../adr/ADR-0016-released-truth-for-public-developer-docs.md) and [ADR-0017: Documentation information architecture and content design — documentation repository](../adr/ADR-0017-interface-accurate-documentation-design.md). No Accepted ADR changed.

The task activates `target-manifest` for browser-sourced content only. `target-manifest.yml` pins the two browser pages and the new browser blocks on shared SDK landing pages; it does not implement issue #103 or assert that existing automation validates the manifest. Existing non-browser verification blocks are not promoted.

Jim explicitly approved the test-expectation correction in `test_registry_retains_all_non_skill_fields`: retain exact checks on every historical component and other top-level fields, while allowing newly enrolled components. No historical entry was edited. No scanner, workflow or test-runner behavior changed.

## Canonical sources

- [Released README](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/README.md): experimental warning, default mainnet connection, read-only behavior, deployment and cleanup.
- [Package manifest](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/package.json), [public npm metadata](https://registry.npmjs.org/@withautonomi/ant-browser-sdk/0.1.2), and [release](https://github.com/WithAutonomi/ant-browser-sdk/releases/tag/v0.1.2): package/version and obtainability.
- [Client](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/client.ts), [types](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/types.ts), [capabilities](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/capabilities.ts), and [runtime](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/internal/runtime.ts): actual call shapes, returned `bytes`, feature checks, signal handling and asset loading.
- [Shipped WASM source record](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/wasm/source.json): ant-client `9858af5dbbb2caf090e20db67ac62aa4bd100c81`; the installed binary's independently calculated SHA-256 was `ab58bd3e331436d22acfe3d08b384992be9addec52145fa0325468c27b6da70a`, matching the record.
- Overview follow-up: [exports](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/index.ts), [file reader](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/file-reader.ts), [media bridge](https://github.com/WithAutonomi/ant-browser-sdk/blob/a29a87cf8d8f696ae5e8b22d6ee4f91d4e7bfbb0/src/internal/media.ts), and the released README support range reads, media/service-worker requirements, private DataMaps and payment-provider uploads. These were source-checked, not runtime-tested here. Book readers, galleries and data viewers are explicitly illustrative application patterns; no built-in ebook renderer or general browser compatibility is claimed.

Source-code inspection and runtime observations are separate evidence. The SDK computes a whole-file hash; comparing two returned copies of that hash would not establish independent expected content. The test below instead checks a fixed SHA-256 previously recorded from a separate CLI retrieval of the same public file. That historical CLI run was not repeated here.

Historical checksum locator: `/Users/jimcollinson/code/autonomi-developer-docs/.worktrees/adr-0016-overnight-refresh/planning/release-evidence-2026-09-02.md:93`, inspected during this handoff. It records a 2026-09-03 macOS ARM64 `ant 0.3.5` run of `ant file download 711c7e20006ff3e0ac6c1f3063286a0c1a3e4c409642e8c526173fa60bb7078a -o lucky-recheck.jpg` and SHA-256 `98f657d987d339c302295e79907e7a4abc1564bd6b42300ea8d59ccd2148fd17`. That earlier local record is not included in this branch; the exact address/hash and attribution are retained here rather than inventing a public evidence URL.

## Local environment and actual results

- macOS ARM64, Node.js 22.22.3, npm 10.9.8.
- Published browser SDK 0.1.2 and Vite 8.2.0 installed through the guide's npm commands in a disposable directory.
- Playwright 1.64.1, fresh Chromium 156.0.8078.4; no personal browser profile, wallet, payment provider, local daemon or custom network profile.
- Development server: `vite --host 127.0.0.1 --port 5179 --strictPort`.
- Production check: `vite build`, then `vite preview --host 127.0.0.1 --port 5180 --strictPort`.
- Both browser runs returned `Downloaded 138931 bytes.`; the image decoded to 782 by 1600 pixels. Both returned SHA-256 `98f657d987d339c302295e79907e7a4abc1564bd6b42300ea8d59ccd2148fd17`; both had zero uncaught page errors and restored the download button.
- Development WASM request returned HTTP 200 from the package asset path. Production WASM returned HTTP 200 from the generated `dist/assets/ant_core_bg-CePe0MQN.wasm` path. No Vite plugin, custom bootstrap override or special response header was needed.
- The production bundle includes JavaScript, the WASM binary and an upload-worker asset; this example does not invoke the upload worker.
- Correctness review noticed npm's default caret range in `package.json`. The install instructions now include `--save-exact` for both the SDK and Vite. Both commands were run against the disposable project; the installed SDK/version and guide HTML/JS remain unchanged. No new browser success is inferred from changing the saved dependency constraint.

Temporary exercise directory: `/var/folders/f_/j942sskj6nx67b6gk3rqgsqm0000gn/T/opencode/browser-sdk-guide.umgG3C`. Its HTML and JavaScript are the tutorial's complete code blocks; the split did not change those blocks. Local screenshots are supporting evidence, not committed or required to reproduce the exercise.

## Reproduce the browser check

Follow [Retrieve Data in the Browser](../docs/sdk/how-to-guides/retrieve-data-in-browser.md) in a new directory and keep the development or preview server running. For automated verification, install `@playwright/test@1.64.1` into a separate `qa/` directory and install its Chromium with `playwright install chromium`. The original run set `PLAYWRIGHT_BROWSERS_PATH` to the disposable `qa/browsers` directory; use the same setting for installation and execution if isolating the browser files.

Save this as `qa/check.mjs`. Run `node qa/check.mjs http://127.0.0.1:5179/`, then repeat with `http://127.0.0.1:5180/` after building and starting the preview. A failed run must be reported, not replaced by these historical results.

```javascript
import assert from "node:assert/strict";
import { chromium } from "@playwright/test";

const browser = await chromium.launch();
try {
  console.log(JSON.stringify({ browser: browser.version(), platform: process.platform, arch: process.arch }));
  const page = await browser.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  page.on("console", (message) => {
    if (["error", "warning"].includes(message.type())) console.log(message.type(), message.text());
  });
  page.on("response", (response) => {
    if (response.url().includes(".wasm")) console.log("wasm", response.status(), response.url());
  });
  await page.goto(process.argv[2] ?? "http://127.0.0.1:5179/");
  await page.locator("#download").click();
  await page.waitForFunction(() => /^(Downloaded|Download failed:)/.test(document.querySelector("#status").textContent), null, { timeout: 195_000 });
  const status = await page.locator("#status").textContent();
  console.log("status", status);
  console.log("pageErrors", JSON.stringify(errors));
  assert.match(status, /^Downloaded \d+ bytes\.$/);
  await page.waitForFunction(() => document.querySelector("#preview").naturalWidth > 0);
  const result = await page.locator("#preview").evaluate(async (image) => {
    const bytes = await (await fetch(image.src)).arrayBuffer();
    const digest = await crypto.subtle.digest("SHA-256", bytes);
    return {
      length: bytes.byteLength,
      sha256: [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join(""),
      width: image.naturalWidth,
      height: image.naturalHeight,
    };
  });
  console.log(JSON.stringify(result));
  assert.equal(result.sha256, "98f657d987d339c302295e79907e7a4abc1564bd6b42300ea8d59ccd2148fd17");
  assert.equal(await page.locator("#download").isEnabled(), true);
  assert.deepEqual(errors, []);
  await page.screenshot({ path: new URL("./result.png", import.meta.url).pathname, fullPage: true });
} finally {
  await browser.close();
}
```

## Repository checks and review

- `python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'` initially ran under macOS Python 3.9.6, below the guard tests' documented minimum 3.10. The unchanged base `2956957` guard module reproduced the same `setUpClass` rejection. The available Python 3.12 and 3.13 interpreters lacked PyYAML; original base guard/scanner modules reproduced the missing-import failure under 3.12. No code failure was dismissed as environmental without that comparison.
- Jim approved a disposable Python 3.12 environment. Using the already installed Python 3.12.12, created a virtual environment under the scratch directory and installed only the repository/CI's existing `PyYAML>=6,<7` requirement (resolved 6.0.3). The complete suite then passed: **53 tests, zero failures/skips**. No global Python default, system package or test invocation inside the repository was changed.
- Reproduction on a machine with the declared dependencies: `python3.12 -B -m unittest discover -s scripts/tests -p 'test_*.py'`. For isolated setup, use `python3.12 -m venv <temporary-directory>` and `<temporary-directory>/bin/python -m pip install 'PyYAML>=6,<7'`, then run the same suite with that interpreter.
- `python3 -I scripts/adr-governance.py`: passed, zero ADR files changed/checked. This is not approval of the scoped manifest or proof of runtime behavior.
- Guide HTML and JavaScript were compared byte-for-byte with the exercised temporary files. The page's source ref/commit, scoped manifest and component mapping agree.
- Craft: PASS, fresh session `ses_ebbe16c0bffeUD4oZQzT6WUibm`; no actionable conformance, simplicity or nit findings. Source/spec review: no blocking defect, session `ses_ebbe16bf5ffelI6FGENG3HK2Xy`; exact npm-save and stale handoff concerns corrected afterward. Neither review reran the browser. Cross-model independence is not established.
- Relative links: 98 local file targets across the guide and three changed navigation/discovery pages resolve. Existing verification blocks on those pages are byte-identical to the base. The GitBook information banner is balanced and precedes the prerequisites. Whitespace checks pass.
- Final adversarial review: READY-WITH-NITS for this local milestone, session `ses_ebbd7aef0ffes6Jm35sakiupR0`; no CRITICAL/HIGH blocker. LOW findings: no recorded failure-and-retry browser exercise, and no locator for the historical CLI checksum. The locator is now supplied above; failure/retry/transport cleanup remain source-reviewed, not browser-exercised. Carry that focused exercise to the required fresh-reader review without adding a new framework. The reviewer independently checked published identities but could not inspect the temporary exercise directory; runtime/test results remain attributed to the implementer. No repeat adversarial pass was run.
- Clean-context runtime review: required before publication readiness, not run. Jim subsequently authorized a fixed commit/push and one draft PR, but launcher verification was denied before preparation/authentication/inference. No attempt was made through a substitute route. Earlier planning-review verdicts are not product-readiness evidence.

## Remaining boundaries

No Safari/iOS/Firefox or cross-platform support claim, paid upload, self-hosted-node pairing, live HTTPS deployment or browser-wide certification. The actual public nodes' software versions were not independently inventoried. Both successful reads used the package's bundled mainnet defaults. The guide remains explicitly experimental.

No clean-context launch has run; implementation CI evidence is recorded below. The code examples, pin and this evidence are included together in the review candidate. Existing metadata debt remains tracked in issues #103/#104; targeted discovery links do not restamp the older pages.

## Owner-requested overview/tutorial split — 2026-10-16

- `Browser SDK` explains capabilities, WASM/WebRTC and application responsibilities beneath `Build with the SDKs`; `Retrieve Data in the Browser` is a separate SDK How-To Guide. Both have a concise experimental information banner. The overview is interface-specific, so it stays within SDK rather than tool-neutral Core Concepts.
- The SDK chooser has native-direct, local-daemon and browser-direct options. Related SDK overview/reference text no longer treats every direct connection as a native library. Existing ant-sdk verification blocks are unchanged; new ant-browser-sdk blocks cover the browser additions only.
- Removed the unexplained node-deployment/version warning from both banners. The tutorial explains exact package versions beside the installation commands. Its complete HTML/JavaScript are byte-identical to the already exercised example, verified after the move; no new runtime claim or repeat network test was needed.
- Ran the full existing suite with the approved temporary Python environment: **53 tests passed**. Checked **156 relative file targets**, manifest-to-page/source consistency, component mapping, and preservation of all old verification blocks on edited pages. Whitespace and ADR governance pass; no ADR files changed.
- Fresh Chromium preview check confirmed the overview's title/banner, its nesting under the SDK chooser, the link to the tutorial, the tutorial's JavaScript block, and all three chooser rows. This exercised the documentation preview, not the SDK again.
- Craft PASS: `ses_ebba50fa6ffepJwY7YFkhsxURI`, no actionable findings. Advisory READY-WITH-NITS: `ses_ebba50f65ffeSk3cMsJ5s28Ilr`, no blocking content or page-move defect. LOW observations were stale current-state wording and optionally making the 1 GB media ceiling visible; both were addressed afterward without rerunning the review. Cross-model independence is not established.
- Streaming/upload explanations are source-checked only; those operations were not run. The existing fresh-reader failure/retry exercise and CI remain outstanding before publication readiness.

## Draft PR preparation — 2026-10-16

Jim authorized commit, push and one draft browser-docs PR, not merge or publication. The separate release-updater planning file is excluded. The final navigation includes all three SDK overviews beneath the chooser and all seven SDK task guides beneath How-To Guides; a later introduction-copy correction changes no technical instruction.

The controlled fresh-context lane could not verify its launcher revision because access to the GSD repository was denied. No preparation, authentication, inference or review lease was created. Disposition: `clean-context deferred: configured lane unavailable or unverified`; the requirement remains binding before merge-readiness.

The planned failure/retry exercise would block the first WASM response, check the visible error and restored button, then restore the response and retry the real download in the same browser page. Creating that temporary check was denied, so it was not executed or counted as a pass. Prior successful reads remain historical observations from this work, not a replacement for the missing check.

Final source/link checks passed on the complete review candidate: 12 changed public Markdown files, 212 relative file targets, unchanged pre-existing verification blocks, six consistent browser-source pins/component mappings, unique navigation targets and clean whitespace. ADR governance passed with zero ADR files changed. The 53-test local pass remains the earlier documented run; CI must independently exercise the committed candidate after the draft PR opens.

## Draft PR and CI evidence

- Browser implementation commit: `0e8516fbb984b966341dd41a0e5a6e4a1f8dd0c5`; [draft PR #106](https://github.com/WithAutonomi/autonomi-developer-docs/pull/106), base `295695745e38c4b17d619ed8f7c5fea17f0cefb1`.
- [Repository Tests run 38904119556](https://github.com/WithAutonomi/autonomi-developer-docs/actions/runs/38904119556) is associated with that implementation head and executed on clean synthetic PR merge commit `91a47b45afabad63c1bddf04a0f481f39963fd57`. Python 3.12.15/PyYAML 6.0.3; all **53 tests passed**, with setup and the full suite executed. This is CI evidence, not another local run.
- ADR Governance passed. The three branch-scoped prose/sweep/SHA guards passed their scope gates but skipped substantive validation on this ordinary documentation branch; their green statuses are not additional source-verification evidence.
- Both GitBook statuses passed and produced a [documentation preview](https://docs.autonomi.com/developers/~/revisions/mdSGBOYtLgsOlHuA2LPg/). Preview generation does not verify example runtime or authorize publication to the default site.
- Recording this handoff changes planning records only after the implementation commit. The [PR checks](https://github.com/WithAutonomi/autonomi-developer-docs/pull/106/checks) are the authority for its latest head. Fresh-context and failure/retry requirements remain outstanding; keep the PR draft.
