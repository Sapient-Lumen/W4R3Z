# Cube state

This cube is a ChatGPT-only proof product. Old provider ambitions are intentionally out of scope for the active working tree.

## Current spine

```text
ChatGPT adapter
→ surface oracle / active surface contract
→ side-panel live gate
→ visible screenshot capture
→ downloadable side-panel proof JSON
→ proof JSON ingest/normalization
→ evidence-pack finalizer
→ evidence-pack checker
→ evaluator / privacy review
→ publish/support bundle and verifier gates
```

## Current protection against UI drift

The active contract records the known-good ChatGPT proof surface. The side panel checks the critical live facts immediately before proof submit and blocks if the route, composer, strict send control, or known non-send control behavior drifted.

## Current protection against fake live proof

The rehearsal path exercises the proof shape, exporter, pack checker, and evaluator while live access is unavailable. Rehearsals return not-live verdicts and `proof-check-pack --require-live` blocks them.

## Current protection against weak evidence packs

The finalizer materializes all 30 expected artifacts, runs the pack checker, and writes an operator handoff. The checker verifies all slots, JSON parsing, nonempty content, evaluator verdict, screenshot metadata, placeholder status, and live/rehearsal safety.

## Missing live artifacts

The live ChatGPT checkpoint proof bundle has not been captured. The live evidence-pack artifacts, ledger, schema validation, bundle audit, evaluator output, and privacy review still need a real run.

## Current protection against proof-transfer loss

The side panel can download proof JSON, and `proof-ingest` validates the downloaded file before finalization. It writes a normalized full capture plus a redacted preview that removes embedded PNG base64 but preserves hashes and dimensions.

## Current protection against placeholder privacy review

`proof-privacy-review` writes a structured JSON sidecar plus markdown slot. Rehearsals stay `privacy-review-rehearsal-not-live`; live publication/support use requires explicit reviewer, pass decision, screenshot review attestation, no-unrelated-content attestation, and local-only attestation.

## Current protection against premature support bundles

`proof-publish-bundle` defaults to `--require-live` and `--require-privacy-pass`. It writes a blocked summary and creates no zip for rehearsal packs, placeholder screenshots, missing live evaluator verdicts, or missing privacy-pass attestations.


## rev0346 state addition

The cube now has a guided proof autopilot. It does not replace the individual gates; it orchestrates them and records which steps were attempted, skipped, or blocked. This reduces operator error while preserving explicit live/privacy/publish gates.

## rev0352 state addition

The side-panel proof helper now has a local recovery vault in `chrome.storage.local`. It stores the latest assembled proof JSON with a hash, redacted preview, and screenshot metadata when available. This is a local recovery guard only; support/publish output still requires downloaded proof JSON, ingest, finalization, privacy review, publish, and verify.


## rev0352 note

Added static extension readiness (`proof-extension-readiness`) plus side-panel attempt readiness evidence (`proof.operator_readiness`) so the live browser attempt is guided before any download/ingest step.

Rev0350 closes a transfer risk: proof JSON download is attempt-readiness gated and the new CLI audit verifies write → gate → screenshot → submit → read-latest → ready-to-download order.

## rev0352 state addition

The pipeline now has a transfer-integrity gate between side-panel download and attempt-order audit. This closes the gap where a malformed, preview-only, truncated, or mismatched proof JSON could reach ingest.

## Rev0352 state note

The pack directory is now self-auditing before publication: `artifact-ledger.json` is refreshed after mutable privacy/operator files, and `evidence-pack-integrity.json` records the final pre-publish file inventory.

## rev0353 state correction

This tree is no longer only a proof cube. The conversation lane is now the
product surface:

```text
shell -> glassttyd ask/chat/run
      -> conversation engine (send / settle / continue)
      -> broker -> native host -> extension -> ChatGPT adapter -> tab
```

The proof lane still exists, unchanged, alongside it and shares the same adapter,
broker, and protocol.

### Current protection against a silent partial answer

The engine treats "did the answer finish?" as a first-class question. It polls an
explicit generation lifecycle from the adapter; when that is unavailable it says
`detection: text-stability` rather than implying precision. Never-started,
never-settled, and stopped-at-a-continue-gate are all `ok: false` with a
`settle_reason`. Partial text is never returned as success.

### Current protection against needing a browser to develop

`glassttyd mock-tab` binds a real `BrokerServer` and plays the tab, including a
simulated streaming lifecycle. `ask` / `chat` / `run` cannot distinguish it from
the extension, so the whole stack is exercised in CI offline.
