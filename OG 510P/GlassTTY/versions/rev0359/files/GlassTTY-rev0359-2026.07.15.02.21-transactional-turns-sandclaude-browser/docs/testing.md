# Testing

The active tests cover the ChatGPT adapter policy, surface drift contract, userscript collector, side-panel live gate, visible screenshot capture source path, proof preflight, offline rehearsal, evidence-pack export/check, first-proof artifact ledger, schema validation, bundle audit, evaluator, proof kit, and native-host/runtime substrate.

Run:

```bash
npm --prefix extension run typecheck
npm --prefix extension run build
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q
```

Then run package checks:

```bash
node --check tools/chatgpt-surface-oracle.user.js
python -m py_compile scripts/*.py daemon/src/glassttyd/*.py
bash -n scripts/*.sh
./scripts/smoke.sh
python scripts/verify-package.py
```

The smoke script now exercises preflight, proof rehearsal, evidence-pack export,
evidence-pack check, and package hygiene. It creates a private short temp root under
`/tmp` because Linux AF_UNIX socket paths are limited to roughly 108 bytes and a
Nix shell's inherited `TMPDIR` may be much deeper. Override the parent only with
`GLASSTTY_SMOKE_TMP_ROOT`. Do not add non-ChatGPT provider tests to this working cube.

Relevant docs:

- `docs/chatgpt-sidepanel-live-gate.md`
- `docs/chatgpt-visible-screenshot-capture.md`
- `docs/chatgpt-proof-pack-exporter.md`
- `docs/chatgpt-proof-pack-check.md`


## Publish/support bundle and verifier gates

Use `glassttyd proof-publish-bundle` only after a live evidence pack passes `proof-check-pack --require-live --require-privacy-pass`. Rehearsal packs are expected to block and create no publish zip.


## Publish bundle verification

Run `glassttyd proof-publish-verify --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.


## Proof status

`proof-status --no-require-live` is part of smoke verification. It writes `validation/latest/chatgpt-proof-operator-state.json` and must remain non-publishing for checked-in rehearsal state.

## Autopilot smoke

`./scripts/smoke.sh` runs `chatgpt-proof-autopilot.py` in dry-run mode and requires `validation/latest/chatgpt-proof-autopilot-summary.json` to exist before packaging.


## rev0349 extension/side-panel readiness

Run this before live browser work or after changing extension code:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-extension-readiness --require-build --pretty
```

In the side panel, use `Run attempt readiness` before and after the major proof actions. Download proof JSON only after the side-panel readiness verdict is `proof-attempt-ready-to-download`.

`proof-attempt-audit` is covered by unit tests and should be used for downloaded side-panel proof captures before ingest/finalization.
