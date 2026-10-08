# GlassTTY ChatGPT-only proof cube

This working package is intentionally ChatGPT-only. The preserved archives are the place to recover old provider experiments; this tree keeps only what helps inspect, run, export, and review the ChatGPT checkpoint proof lane.

## Current target

```text
Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT
```

Expected reply:

```text
GLASSTTY-CHECKPOINT
```

## Active spine

```text
ChatGPT adapter
→ Tampermonkey surface oracle / active drift contract
→ side-panel live gate
→ visible-tab screenshot capture
→ downloadable side-panel proof JSON
→ proof-finalize-pack
→ proof-check-pack --require-live
→ ledger / schema / audit / evaluator / privacy review
→ proof-publish-bundle support/publication gate
→ proof-publish-verify post-transfer integrity gate
→ proof-status resumable operator state
```

## Operator commands

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd doctor --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-preflight --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-rehearse --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack --clean --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest --input <downloaded-json> --require-live-candidate --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-recovery-vault --input <downloaded-or-vault-json> --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-check-pack --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-privacy-review --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-bundle --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify --bundle validation/latest/chatgpt-proof-publish-bundle.zip --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-status --pretty
```

For a real live pack, the final check must be strict:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-check-pack \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --require-live \
  --pretty
```

## Side-panel live flow

1. Run `proof-extension-readiness --require-build` before loading/reloading the extension.
2. Select the supported ChatGPT tab.
3. Press `Run attempt readiness` to get the next side-panel step.
2. `Write checkpoint + capture`.
3. `Check live gate`.
4. `Capture visible screenshot`.
5. `Submit checkpoint (gated)`.
6. Wait for ChatGPT to settle on a `/c/...` conversation route.
7. `Read latest + capture`.
8. `Download proof JSON`.
9. Run `proof-ingest --input <downloaded-json> --require-live-candidate --pretty`.
10. Run `proof-finalize-pack --input validation/latest/chatgpt-first-proof-capture.json --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --clean --pretty`.
11. Run `proof-privacy-review --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --require-live --require-pass --reviewer <name> --decision pass --attest-screenshot-reviewed --attest-no-unrelated-content --attest-local-only --pretty`.
12. Run `proof-publish-bundle --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack --pretty` only after privacy review passes.
13. Run `proof-publish-verify --bundle validation/latest/chatgpt-proof-publish-bundle.zip --expected-sha256 <hash> --pretty` after transfer or before sharing.

The generic submit button is not a proof path.

## What is inside

- ChatGPT adapter and built extension.
- Native host / daemon substrate.
- Side-panel proof helper with live gate and visible screenshot capture.
- Tampermonkey surface oracle plus optional DevTools page-world restprobe.
- Surface report audit and drift-contract tooling.
- Offline proof rehearsal and preflight tooling.
- Proof JSON ingest/normalization, 30-slot evidence-pack exporter, checker, one-command finalizer, structured privacy review, and publish/support bundle and verifier gates.
- ChatGPT proof schema, bundle audit, artifact ledger, and evaluator.

## Active files

- Active surface contract: `validation/latest/chatgpt-live-surface-contract-rev0352-2026.06.13.json`
- Active preflight output: `validation/latest/chatgpt-proof-preflight.json`
- Latest ingest summary: `validation/latest/chatgpt-proof-ingest-summary.json`
- Latest privacy review summary: `validation/latest/chatgpt-proof-privacy-review.json`
- Operator state: `validation/latest/chatgpt-proof-operator-state.json`
- Rehearsal input: `validation/latest/chatgpt-proof-rehearsal.json`
- Rehearsal pack: `validation/latest/chatgpt-proof-rehearsal-evidence-pack/`

## Verify the cube

```bash
npm --prefix extension run typecheck
npm --prefix extension run build
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q
./scripts/smoke.sh
python scripts/verify-package.py
```

## Still missing

The live ChatGPT checkpoint proof has not been captured yet. The missing final deliverable is a real live 30-slot evidence pack with live screenshot, ledger, schema validation, bundle audit, evaluator output, and human privacy/redaction review.

## rev0346 focus

The operator path now has a conservative `proof-autopilot` command. It reports the current live-proof stage, can refresh safe offline preflight gates, and can advance a downloaded side-panel proof JSON through ingest/finalize/privacy/publish only when explicitly run with live execution flags. This is meant to reduce command-chain drift without hiding blockers.

## rev0352 focus

Added a static extension readiness gate (`proof-extension-readiness`) and a side-panel `Run attempt readiness` control. The live browser attempt now has a non-mutating checklist that records `proof.operator_readiness` evidence and tells the operator the next exact side-panel action before download/ingest.

- `glassttyd proof-attempt-audit --input <downloaded-json> --require-ready-to-download` verifies the side-panel proof steps happened in safe order before ingest/finalization.

## rev0352 focus

Rev0351 adds `proof-transfer-audit` as the first CLI check for a downloaded side-panel proof JSON. It verifies transfer/container integrity before the existing attempt-order audit and ingest path, and `proof-autopilot --execute-live --input <json>` now runs it automatically.

## Rev0352: evidence-pack integrity gate

The proof pack now has an internal integrity command:

```bash
glassttyd proof-pack-integrity --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack --refresh-ledger --write-pack-file --require-existing-match --require-ok --pretty
```

This refreshes `artifact-ledger.json` after mutable review files are finalized and writes `evidence-pack-integrity.json` into the pack. It prevents stale artifact hashes from surviving finalization.
