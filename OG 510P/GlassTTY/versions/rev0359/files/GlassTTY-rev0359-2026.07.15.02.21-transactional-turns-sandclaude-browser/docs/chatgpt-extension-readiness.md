# ChatGPT extension readiness

`glassttyd proof-extension-readiness` checks whether the unpacked browser extension is statically ready for a live ChatGPT first-proof attempt.

It checks the risky pieces before an operator opens ChatGPT:

- Manifest V3 is in use.
- `host_permissions` and content-script matches are exactly `https://chatgpt.com/*`.
- The side panel is registered at `sidepanel/index.html`.
- Required browser permissions for the proof UI are present.
- Side-panel proof controls exist, including attempt readiness, live gate, screenshot, download, and recovery-vault controls.
- The side-panel source contains the live-gate, attempt-readiness, recovery-vault, screenshot, and download markers.
- The extension build outputs exist when `--require-build` is used.

Run:

```bash
PYTHONPATH=$PWD/daemon/src:$PWD/scripts glassttyd proof-extension-readiness --require-build --pretty
```

Expected passing verdict:

```text
extension-readiness-ok
```

A failure here is pre-browser failure. Fix it before a live proof attempt; do not move on to side-panel capture or ChatGPT submission.
