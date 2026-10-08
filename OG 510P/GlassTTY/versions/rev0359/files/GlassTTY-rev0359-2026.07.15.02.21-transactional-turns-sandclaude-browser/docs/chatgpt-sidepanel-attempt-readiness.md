# ChatGPT side-panel attempt readiness

The side panel now has a non-mutating operator check:

```text
Run attempt readiness
```

This check does not submit anything. It inspects the selected ChatGPT tab, receiver state, current proof-log evidence, screenshot state, live-gate state, latest-turn readback, and local recovery vault. It then prints the exact next side-panel action.

Typical sequence:

1. Open `https://chatgpt.com/`.
2. Open the GlassTTY side panel.
3. Select the supported ChatGPT tab.
4. Press `Run attempt readiness`.
5. Follow the reported `next_action` until it says to download proof JSON.

The readiness check emits a local proof-log envelope:

```text
proof.operator_readiness
```

That envelope is included in the downloaded proof JSON so reviewers can see the operator-facing readiness state that existed before and during the attempt.

Readiness stages are intentionally practical:

- `select-chatgpt-tab`
- `write-checkpoint`
- `check-live-gate`
- `capture-visible-screenshot`
- `submit-checkpoint`
- `read-latest`
- `download-proof-json`

A capture is not ready to leave the browser until the verdict is:

```text
proof-attempt-ready-to-download
```

This is still not a live proof verdict. The downloaded JSON must still pass:

```bash
glassttyd proof-autopilot --execute-live --input <downloaded-json> --clean --pretty
```
