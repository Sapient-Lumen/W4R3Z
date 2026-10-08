# Tasks

## Highest-value next work

1. Run one live side-panel attempt when available and download the side-panel proof JSON.
2. Export that capture to `validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/`.
3. Run `proof-ingest --require-live-candidate` on the downloaded JSON, then finalize the normalized capture.
4. Improve side-panel export ergonomics if a real capture cannot finalize without manual surgery.
5. Keep pruning any generic-provider language that does not help the ChatGPT proof path.

## Non-live readiness loop

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-extension-readiness --require-build --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-status --no-require-live --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-preflight --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-rehearse --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-finalize-pack --clean --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-ingest --input validation/latest/chatgpt-proof-rehearsal.json --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-recovery-vault --input validation/latest/chatgpt-proof-rehearsal.json --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-check-pack --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-privacy-review --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-bundle --pack-dir validation/latest/chatgpt-proof-rehearsal-evidence-pack --pretty  # expected to block
python scripts/verify-package.py
```

Expected non-live verdicts:

```text
ready-for-live-operator-attempt-not-a-live-proof
rehearsal-harness-ok-not-live
rehearsal-evidence-pack-check-ok-not-live
```

## Live proof sequence once available

1. Load the unpacked extension from `extension/` in a clean browser profile.
2. Open `https://chatgpt.com/` or a plain `/c/...` ChatGPT conversation.
3. Use the side-panel proof flow: run attempt readiness → write → live gate → screenshot → gated submit → latest readback → run attempt readiness → download proof JSON.
4. Download the assembled JSON, then run `proof-ingest --input <downloaded-json> --require-live-candidate`.
5. Run `proof-finalize-pack --input validation/latest/chatgpt-first-proof-capture.json --require-live --clean`.
6. Run `proof-privacy-review --require-live --require-pass` before any publication/support use.
7. Run `proof-publish-bundle` to create the support/publication zip only after live and privacy gates pass.

## Drift response

If the side-panel gate or Tampermonkey drift verdict blocks: do not submit. Capture the Tampermonkey oracle report, update the ChatGPT adapter or active surface contract, and rerun `proof-preflight`.


## Publish bundle verification

Run `glassttyd proof-status --pretty` after every operator step. Run `glassttyd proof-publish-verify --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.


## Next high-risk tasks after rev0346

1. Exercise `proof-autopilot --execute-live` with a real downloaded side-panel proof JSON once live access is available.
2. Confirm the side-panel downloaded JSON plus screenshot satisfies ingest without manual edits.
3. Keep checking that rehearsals cannot produce publish bundles or live verdicts.

## Next high-risk tasks after rev0348

- Exercise the recovery vault against a real screenshot-sized proof JSON and verify browser storage quota behavior.
- Make `proof-autopilot` suggest recovery-vault restore/download when no downloaded proof JSON is present but the side panel reports a saved vault.
- Continue reducing manual live operator steps without allowing rehearsal artifacts to become support-ready.

## rev0348 task addition

If the side panel reloads or a capture is recovered from storage, run `glassttyd proof-recovery-vault --input <json> --require-full-document --require-integrity-match --pretty` before ingest/finalize.

## rev0352 task addition

Before live browser work, run `proof-extension-readiness --require-build`. In the side panel, press `Run attempt readiness` before and after each major proof action; do not download a proof JSON until the readiness verdict is `proof-attempt-ready-to-download`.

- Next live attempt: use Download proof JSON, then run `proof-attempt-audit --require-ready-to-download` before `proof-autopilot --execute-live`.

## rev0352 task addition

- Live operator: after Download proof JSON, `proof-autopilot --execute-live --input <json>` now runs `proof-transfer-audit` first; failures mean re-download the proof JSON or promote a full recovery-vault record before ingest.

## Rev0352 next tasks

- Run `proof-pack-integrity --require-existing-match` on every live pack after final privacy review.
- Keep `proof-publish-verify` as the final transferred-zip gate; pack integrity is the pre-zip directory gate.

## rev0353 tasks

### Done

1. Conversation engine (`daemon/src/glassttyd/conversation.py`): send → settle →
   auto-continue → return, with honest failure reasons.
2. Adapter generation lifecycle + `prompt.continue` (extension 0.1.117).
3. `glassttyd ask` / `chat` / `run` / `mock-tab`.
4. `run`: template vars, per-answer capture, `transcript.jsonl`, pacing, `--resume`.
5. Declared the missing `jsonschema` dependency; broker no longer tracebacks on
   client disconnect.

### Next

1. **File attachment** (`--attach PATH`). Adapter action on the composer file
   input + an upload-completion witness. Blocks everything below.
2. **Auto-recovery loop** (queuer T1/T2 parity): attach a package, wait for the
   answer, capture the returned archive, re-send. Needs a download witness.
3. **Model / tier / version pinning.** Use the queuer's v6.45 live menu capture
   as the spec.
4. `chat` niceties: `/attach`, `/retry`, `/save`.
5. Keep the proof lane green; it is unchanged but must not rot.

### Verification loop

```bash
glassttyd mock-tab &                                  # offline tab
glassttyd ask "hello"                                 # expect a settled answer
glassttyd run prompts.txt --out-dir ./out --resume    # expect per-answer files
PYTHONPATH=$PWD/daemon/src:$PWD/scripts python -m pytest -q   # expect 190 passed
```

## rev0354 tasks

### Done
- Surface probe (oddity hunter), snapshot history, diff, triage, repair, watch.
- `--diagnose` on ask/run. Runtime overrides. 8 drift rehearsal scenarios.

### Next
1. **File attachment** (`--attach`) + upload-completion witness + zero-byte guard.
2. Download-completion witness, then the auto-recovery loop.
3. Model/tier/version pinning (spec: queuer v6.45 menu capture).
4. Conversation control (`--new-chat`, `--conversation`), streaming, `--workers`.
5. Keep ROLE_ATLAS current as the surface wing reports unknown controls.

## rev0355 tasks

### Done
- File attachment: chunked transfer, zero-byte refusal, fileless-prompt guard,
  chip self-documentation. `ask --attach`, `run --attach`, `attach`.
- `stop`, `new-chat`, `--probe-with-draft`.
- Fixed: empty-composer false positive; volatile-id selectors; send scoring inverted.
- Closed the standing TASK_QUEUE item: "use the after-write strict send selector to
  finalize send scoring" — that is what `--probe-with-draft` does.

### Next
1. **Download-completion witness** → then `glassttyd loop` (the T1/T2 auto-recovery loop).
2. Model/effort pinning via the composer pill (class/text, never its volatile id).
3. `--conversation <id>`, `--stream`, `run --workers N`, rate-limit backoff.
4. When the first real attachment lands, read `added_controls` off the turn record
   and add the chip to ROLE_ATLAS.
