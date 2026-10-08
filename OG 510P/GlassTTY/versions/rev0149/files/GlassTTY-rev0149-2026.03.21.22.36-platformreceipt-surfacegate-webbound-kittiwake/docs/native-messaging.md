# Native messaging notes

GlassTTY uses a Chrome native-messaging host named `com.glasstty.bridge`.

## Current model

- background service worker opens a long-lived native port
- native host speaks Chrome's length-prefixed JSON protocol on stdin/stdout
- native host also exposes a local UNIX socket for CLI access
- content scripts do not talk to the native host directly; the background coordinates that path

## Host manifest

Template: `native-host/com.glasstty.bridge.template.json`

Fields to fill:
- `path`
- `allowed_origins`

## User-level install defaults now handled by the helper

### Linux

- Chromium: `~/.config/chromium/NativeMessagingHosts/`
- Google Chrome: `~/.config/google-chrome/NativeMessagingHosts/`
- Chrome for Testing: `~/.config/google-chrome-for-testing/NativeMessagingHosts/`
- **version nuance:** current Chrome docs note that Chrome for Testing used the Google Chrome locations until Chrome 146, so current stable CfT builds may still need the `google-chrome` target instead of `chrome-for-testing`

### macOS

- Chromium: `~/Library/Application Support/Chromium/NativeMessagingHosts/`
- Google Chrome: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
- Chrome for Testing: `~/Library/Application Support/Google/ChromeForTesting/NativeMessagingHosts/`
- **version nuance:** current Chrome docs note that Chrome for Testing used the Google Chrome locations until Chrome 146, so current stable CfT builds may still need the `chrome` target instead of `chrome-for-testing`

## Practical notes

- the extension ID must be the real unpacked ID or packaged ID that Chromium assigns
- the host executable path must be executable by Chromium
- the broker socket lives under `GLASSTTY_HOME/run/daemon.sock`
- GlassTTY now treats Chrome's 1 MB host→extension ceiling as a runtime safety rail instead of a fatal crash: if an outbound message is too large, the full payload is spilled under `GLASSTTY_HOME/state/fixtures/oversized-host-outbound-*.json`, a summary is mirrored to `GLASSTTY_HOME/state/latest/oversized-host-outbound.json`, and the browser receives a compact `error.report` pointing at that artifact
- `./scripts/install-native-host.sh` now defaults to `--target auto`, which follows the current browser-aware recommendation instead of assuming `chromium`
- use `--target playwright` when you want only the Playwright persistent extension lane target(s)
- use `--target combined` when you want the merged Playwright + raw-browser matrix target set in one command
- add `--all-recommended` when you want GlassTTY to install every target the detected browser family/version may need
- `python scripts/native-host-report.py --pretty` audits installed manifests, allowed extension IDs, and wrapper-path mismatches before you blame the browser loop
- `python scripts/doctor.py --pretty` now surfaces manifest parse/match status for each standard target directory instead of only checking for file presence
- `python -m glassttyd.cli overflow-report` summarizes the latest oversized spill artifact without printing the full preserved message unless you pass `--include-message`
- `python -m glassttyd.cli overflow-prune` can dry-run or apply a retention plan for accumulated `oversized-host-outbound-*.json` artifacts (`--keep`, `--max-age-days`, `--max-disk-bytes`) without deleting the current latest linked artifact by default
- the extension now mirrors native-host overflow notices as `lastOversizedHostMessage`, so bridge-status / side-panel sessions can show that the host downgraded a reply on purpose instead of only recording a generic last error
- `bridge.status` and `bridge.probe` can now refresh a compact one-shot native-host status snapshot over `sendNativeMessage()`, which means browser-visible diagnostics can see local overflow inventory counts and recent artifact summaries without turning the long-lived `connectNative()` lane into another oversized payload risk
- because Chrome still launches a fresh host process for each `sendNativeMessage()` request, GlassTTY now guards the broker socket with an ownership lease **and** defers broker startup until the first browser message declares intent: persistent-port health pings are owner candidates, while one-shot `bridge.status` / probe helper calls stay `secondary_only` and report local state without creating a transient broker socket

## Why long-lived native port

Using a long-lived native port helps keep the service worker alive while the host is connected and gives a stable path for broker-driven round trips.

- `python scripts/native-host-report.py --browser-bin /path/to/browser --pretty` can anchor the audit to the exact browser binary you intend to launch instead of the ambient default.
- `./scripts/glasstty-profile.sh open ...` now saves that browser-aware audit as `glasstty-native-host.json` inside the profile directory before Chromium starts.
