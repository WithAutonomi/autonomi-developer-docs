# ADR-0016 clean-context dispatch — 50f4462

- Date: 2026-08-28
- Requested commit: `50f4462`
- Requested reviewer: controlled Claude Fable panel lane
- Result: `Blocked before inference`

Milestone A activation was present in `planning/STATE.md`, but the required caller-owned `brief.md` did not exist under the exact disposable panel root. The orchestrator's outer filesystem permission refused creation of that root and brief. Chat text cannot substitute for the required regular stdin file.

The panel could not create or attest the caller-owned brief. Claude CLI and inference were not invoked. No session, provider/model attribution, findings, or persisted output exists.

Required next action: explicitly authorize creation of one disposable root and regular `brief.md` under the named `/var/.../opencode/gsd-panel-<UUID>` path, then issue a fresh dispatch with all fields.

models: provider=not-observed · model=not-resolved · duration=unknown

claude=blocked-before-inference (caller-owned brief missing) · provider=not-observed · model=not-resolved
