# ChatGPT side-panel recovery vault

The live proof handoff now has a local recovery vault in the extension side panel. Its purpose is narrow: prevent losing a nearly complete `GLASSTTY-CHECKPOINT` proof capture if the operator forgets to download the proof JSON immediately or the side panel reloads.

The primary transfer path is still **Download proof JSON**. The vault is a local recovery backstop, not the publication artifact.

## What is saved

The side panel auto-saves the latest assembled proof document to `chrome.storage.local` under:

```text
glasstty.chatgpt.firstProof.recoveryVault.v1
```

The record includes:

```text
attempt_id
envelope_count
document_bytes
document_hash
screenshot hash/dimensions when present
redacted preview
full proof document when browser storage quota allows it
```

If the full proof document is too large for browser local storage, the side panel records a fallback metadata entry and warns the operator to download the proof JSON immediately.

## Buttons

The ChatGPT first-proof card now has:

```text
Save recovery vault
Restore recovery vault
Download recovery JSON
Clear recovery vault
```

`Restore recovery vault` rebuilds the side-panel in-memory proof log from the saved `raw_envelopes` when available. `Download recovery JSON` writes the saved full proof JSON to disk. `Clear proof log` only clears memory; it does not delete the vault. Use `Clear recovery vault` for that.

## Privacy posture

The vault is local extension storage. It may contain the full proof JSON, including the embedded visible-tab screenshot data URL. Treat it as sensitive local evidence until privacy review passes. It is intentionally not copied into the evidence pack or publish bundle by itself; downloaded/ingested proof JSON is still the operator handoff source of truth.

## Failure mode covered

This feature covers the case where a live run reaches screenshot/readback capture but the operator loses the side-panel state before finalization. The next safe action is:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-autopilot --pretty
```

Then restore or download the recovery JSON from the side panel and continue with `proof-ingest` or `proof-autopilot --execute-live --input <json>`.
