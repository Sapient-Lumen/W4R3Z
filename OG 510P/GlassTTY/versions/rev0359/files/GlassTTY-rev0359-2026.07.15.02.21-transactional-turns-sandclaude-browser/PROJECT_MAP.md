# Project map

## Product lane

- `extension/src/adapters/chatgpt.ts` — ChatGPT DOM adapter.
- `extension/src/sidepanel/main.ts` — operator proof helper, live gate, screenshot capture, proof JSON assembly.
- `tools/chatgpt-surface-oracle.user.js` — Tampermonkey surface/drift oracle.
- `tools/chatgpt-pageworld-restprobe.js` — optional DevTools page-world gap probe.

## Proof tooling

- `scripts/chatgpt_proof_preflight.py` — static + drift + rehearsal gate.
- `scripts/chatgpt_proof_rehearsal.py` — offline proof-shaped rehearsal bundle.
- `scripts/chatgpt_proof_pack_exporter.py` — side-panel/rehearsal JSON to 30-slot evidence pack.
- `scripts/chatgpt_proof_recovery_vault.py` — classify/extract/ingest side-panel recovery-vault artifacts.
- `scripts/chatgpt_proof_pack_check.py` — evidence-pack completeness and live/rehearsal safety check.
- `scripts/chatgpt_proof_privacy_review.py` — structured privacy/redaction review and pass-attestation gate.
- `scripts/chatgpt_first_proof_evaluator.py` — final proof evaluator.
- `scripts/chatgpt_first_proof_artifact_ledger.py` — canonical 30-slot artifact registry/ledger.

## Active validation

- `validation/latest/chatgpt-live-surface-contract-rev0352-2026.06.13.json`
- `validation/latest/chatgpt-proof-preflight.json`
- `validation/latest/chatgpt-proof-rehearsal.json`
- `validation/latest/chatgpt-proof-rehearsal-evidence-pack/`

## Intentional exclusions

No non-ChatGPT adapters, no multi-provider support matrix, no broad host permissions, and no support claims beyond the ChatGPT proof path.


## Publish/support bundle and verifier gates

Use `glassttyd proof-publish-bundle` only after a live evidence pack passes `proof-check-pack --require-live --require-privacy-pass`. Rehearsal packs are expected to block and create no publish zip.


## Publish bundle verification

Run `glassttyd proof-publish-verify / proof-status --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.


## rev0346 operator flow

- `scripts/chatgpt_proof_autopilot.py` / `glassttyd proof-autopilot`: guided resumable operator flow.
- `validation/latest/chatgpt-proof-autopilot-summary.json`: latest autopilot state/step log.

## rev0352 recovery-vault path

- `extension/src/sidepanel/main.ts` — auto-save/restore/download/clear local recovery vault.
- `docs/chatgpt-sidepanel-recovery-vault.md` — operator notes for local recovery.
- `tests/test_chatgpt_sidepanel_recovery_vault.py` — static regression guard for the side-panel controls and storage calls.


## rev0352 note

Added static extension readiness (`proof-extension-readiness`) plus side-panel attempt readiness evidence (`proof.operator_readiness`) so the live browser attempt is guided before any download/ingest step.

- `scripts/chatgpt_proof_attempt_audit.py` — audits ordered side-panel proof events in downloaded captures before live ingest/finalization.

## rev0353 conversation lane

- `daemon/src/glassttyd/conversation.py` — broker client + turn engine
  (send → settle → auto-continue → return). The reusable brain behind the CLI.
- `daemon/src/glassttyd/mock_tab.py` — offline ChatGPT emulator on a real broker.
- `daemon/src/glassttyd/cli.py` — `ask`, `chat`, `run`, `mock-tab`.
- `extension/src/adapters/chatgpt.ts` — adds `generationSnapshot()` / `continueGeneration()`.
- `extension/src/content/main.ts` — adds `generation.state` and `prompt.continue` handlers.
- `docs/conversation-cli.md` — operator reference.
- `docs/queuer-to-commandline.md` — userscript-queuer parity map and migration.
- `tests/test_conversation_engine.py`, `tests/test_cli_conversation_commands.py`.

## rev0354 surface wing

- `extension/src/adapters/surface-probe.ts` — control inventory, role atlas, oddities.
- `extension/src/adapters/chatgpt.ts` — `surfaceProbe()` + runtime selector overrides.
- `daemon/src/glassttyd/surface.py` — snapshot / fingerprint / diff / triage / repair / history.
- `daemon/src/glassttyd/mock_tab.py` — drift scenarios (rehearse a UI change offline).
- `docs/surface-intelligence.md`, `docs/missing-features.md`.
- `tests/test_surface_intelligence.py`.

## rev0355 attachments

- `extension/src/adapters/chatgpt.ts` — `attachFiles()` (DataTransfer into the hidden
  file input), `attachmentWitness()`, `stopGeneration()`, `newChat()`.
- `extension/src/adapters/surface-probe.ts` — composer state, file-input detection,
  volatile-id blacklist, role atlas grounded in the live 2026-07-11 capture.
- `extension/src/content/main.ts` — chunked attach transfer (begin/chunk/commit/status).
- `daemon/src/glassttyd/conversation.py` — `attach()`, fileless-submit guard.
- `docs/attachments.md`, `docs/live-surface-findings-2026-07-11.md`.
- `tests/test_attachments_and_live_surface.py`.
