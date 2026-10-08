# Operator startup

1. Load the unpacked extension from `extension/`.
2. Open a plain ChatGPT tab at `https://chatgpt.com/` or `/c/...`.
3. Open GlassTTY side panel.
4. Select the supported ChatGPT tab.
5. Run `Write checkpoint + capture`.
6. Run `Check live gate`.
7. Run `Capture visible screenshot`.
8. Run `Submit checkpoint (gated)`.
9. Wait for `/c/...` and settled output.
10. Run `Read latest + capture`.
11. Run `Download proof JSON`.
12. Save JSON locally and run pack export/check commands.

Never use generic submit for proof. Never treat rehearsal output as live.


## Publish/support bundle and verifier gates

Use `glassttyd proof-publish-bundle` only after a live evidence pack passes `proof-check-pack --require-live --require-privacy-pass`. Rehearsal packs are expected to block and create no publish zip.


## Publish bundle verification

Run `glassttyd proof-status --pretty
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-publish-verify --bundle <publish-zip> --expected-sha256 <hash>` before sharing a support bundle. It extracts the zip safely, verifies manifest hashes, and reruns the live/privacy pack gate.

## Guided resume command

Use `glassttyd proof-autopilot --pretty` first. It reports the exact next operator action. Use `--execute-safe` to refresh offline preflight only, and `--execute-live --input <downloaded-json>` only after the side panel has downloaded a real proof JSON.


## rev0349 extension/side-panel readiness

Run this before live browser work or after changing extension code:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-extension-readiness --require-build --pretty
```

In the side panel, use `Run attempt readiness` before and after the major proof actions. Download proof JSON only after the side-panel readiness verdict is `proof-attempt-ready-to-download`.

After downloading a proof JSON, run `glassttyd proof-attempt-audit --input <json> --require-ready-to-download --pretty` before autopilot. Rev0350+ downloads should already contain the final readiness envelope.
