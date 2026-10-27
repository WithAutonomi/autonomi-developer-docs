# Release baseline maintenance

`target-manifest.yml` records the released software that selected public pages have been checked against. It is a reviewed pin, not a release feed, a list of the newest repository commits, or permission to update pages from `main`.

## How the pieces fit

- `repo-registry.yml` identifies trusted source repositories.
- `component-registry.yml` maps each component to the pages it can support and, where available, defines release discovery.
- `target-manifest.yml` records an exact reviewed source. The Browser SDK uses the fixed manual `sources.ant-browser-sdk` record. The CLI uses structured `release_baselines.entries` records.
- Each scoped page has one matching `target-manifest` verification block with the same repository, release tag and commit.
- `planning/sweeps/YYYY-MM-DD.md` records the audit and promotion. Its date matches the branch and the pages' new `verified_date`.

These files move together. A manifest edit alone does not promote documentation.

## Promotion workflow

1. **Source audit:** confirm that the release is publicly obtainable. Record the exact tag and peeled commit, distribution metadata, integrity values, shipped dependencies, support status and known limits required by the profile.
2. **Atomic promotion:** update the one manifest source or baseline, every scoped page block, and one new dated promotion record in the same branch. Update rendered documentation in that branch when behavior changed.
3. **Validation:** run the commands below. Do not bypass a failing guard or move a pin to a branch such as `main`.
4. **Review:** have a maintainer review the evidence and complete diff. Merge is the promotion action; validation alone does not approve it.

Use `claude/sweep-YYYY-MM-DD` or `claude/sweep-YYYY-MM-DD-<slug>` when only metadata changes. Use `claude/prose-YYYY-MM-DD-<slug>` when any rendered documentation changes.

```bash
python3 -I scripts/validate_release_baselines.py
python3 -B -m unittest discover -s scripts/tests -p 'test_doc_guards.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_release_following.py' -v
python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'
python3 -I scripts/adr-governance.py
git diff --check
```

CI runs the same validator and the branch-specific prose, sweep and SHA-reachability guards. The reachability guard loads repository coordinates from the base branch's registry and confirms that each promoted tag peels to the recorded commit.

## Manual pin and automated adapter

The Browser SDK is the manual example. Its existing `scope.pages` contains six mapped pages, and `sources.ant-browser-sdk` records the release, npm package and shipped WebAssembly (WASM) evidence. A promotion advances that source record and all six blocks without adding a `release_baselines` entry. The package remains `experimental`; a version change cannot alter that classification.

The CLI is the automated-adapter example. `scripts/sweep_poll.py` uses the `ant-cli` release-discovery configuration to prepare evidence for a version-1 `release_baselines.entries.ant-cli/stable` record. That larger record captures GitHub assets, npm platform packages, installers and shipped `ant-core` evidence. Discovery prepares a candidate; it does not approve or merge a promotion.

## Add another component

1. Add the trusted repository and component-to-page mapping through a separately reviewed registry change.
2. Choose a bounded source profile. Add release discovery only when a reliable adapter is useful; a universal adapter is not required.
3. Add strict validation for the profile before promoting its first release. The profile must identify an obtainable release, exact source commit, required distribution evidence, scoped pages and promotion record.
4. Audit the release, then promote it through the atomic workflow above.

If no reviewed profile or released artifact exists, leave the pages unpromoted. Do not fall back to `main`, weaken a guard, or activate a routine to work around missing evidence. Routine activation is a separate operational decision, not part of normal baseline maintenance.
