# validation/latest

This directory is the staging area for the next ChatGPT-only proof run. It does not carry historical multi-provider validation output.

Current non-live artifacts:

- `chatgpt-live-surface-contract-rev0352-2026.06.13.json` — active known-good ChatGPT UI drift contract.
- `chatgpt-live-surface-contract-fixture-rev0352.json` — minimal contract-check fixture.
- `chatgpt-proof-preflight.json` — static/drift/rehearsal preflight output.
- `chatgpt-proof-rehearsal.json` — synthetic offline proof rehearsal payload; not a live proof.
- `chatgpt-proof-rehearsal-evidence-pack/` — exported 30-slot rehearsal evidence pack; not live evidence.
- `chatgpt-proof-pack-export-summary.json` and `chatgpt-proof-pack-check-summary.json` — exporter/checker summaries for the rehearsal pack.
- `chatgpt-proof-privacy-review.json` — structured rehearsal privacy status; not live.

Expected live staging once execution is available:

- `chatgpt-first-proof-capture.json` — copied side-panel proof JSON from a real run.
- `../live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/` — live exported evidence pack.


## Publish/support bundle and verifier gates

Use `glassttyd proof-publish-bundle` only after a live evidence pack passes `proof-check-pack --require-live --require-privacy-pass`. Rehearsal packs are expected to block and create no publish zip.


## Publish bundle verification

Run `glassttyd proof-publish-verify --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.

- `chatgpt-proof-operator-state.json`: resumable status file written by `glassttyd proof-status`.

## rev0346

`chatgpt-proof-autopilot-summary.json` is the latest guided pipeline state. It is safe to regenerate with `glassttyd proof-autopilot --pretty`; it does not make rehearsal material live.

- `chatgpt-proof-recovery-vault-summary.json` — latest recovery-vault/proof-json classification and extraction summary.


## rev0352 extension/side-panel readiness

Run this before live browser work or after changing extension code:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-extension-readiness --require-build --pretty
```

In the side panel, use `Run attempt readiness` before and after the major proof actions. Download proof JSON only after the side-panel readiness verdict is `proof-attempt-ready-to-download`.

Rev0350 adds `chatgpt-proof-attempt-audit.json` as the summary for downloaded proof event-order audits.

## rev0352 transfer audit

`chatgpt-proof-transfer-audit.json` is the summary for the downloaded-proof transfer gate. The checked-in rehearsal summary is expected to block because rehearsals do not carry the full side-panel raw envelope/download container.
