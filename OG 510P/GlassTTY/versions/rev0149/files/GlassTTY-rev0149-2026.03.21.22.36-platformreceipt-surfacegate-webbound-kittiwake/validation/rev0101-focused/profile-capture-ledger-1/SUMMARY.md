# GlassTTY profile capture: ledger

- captured_at: 2026-03-17T22:05:09Z
- profile_path: /mnt/data/GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling/validation/rev0101-focused/sample-home/profiles/ledger
- attach_ready: False
- cdp_endpoint: http://127.0.0.1:9222
- reopen_launchable_now: True
- saved_browser_path: /usr/bin/chromium
- effective_browser_path: /usr/bin/chromium
- capture_history_count: 1

## Capture history

- ledger_path: `/mnt/data/GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling/validation/rev0101-focused/sample-home/profiles/ledger/glasstty-profile-captures.json`
- comparison_summary: no previous capture exists for this profile yet

## Recommended commands

- info: `./scripts/glasstty-profile.sh info ledger --pretty`
- captures: `./scripts/glasstty-profile.sh captures ledger --pretty`
- capture: `./scripts/glasstty-profile.sh capture ledger --output-dir validation/latest/profile-capture-ledger`
- reopen: `CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh ledger --skip-extension --remote-debugging-port 9222 chrome://extensions/`
- reopen_portable: `./scripts/glasstty-profile.sh reopen ledger --allow-discovered-browser-fallback`
- reopen_debug: `CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh ledger --skip-extension --remote-debugging-port auto chrome://extensions/`
- reopen_debug_portable: `./scripts/glasstty-profile.sh reopen ledger --allow-discovered-browser-fallback --remote-debugging-port auto`
- resume_proof: `./scripts/glasstty-profile.sh resume-proof ledger --output validation/latest/mv3-worker-resume-ledger.json --timeout 25`

## Saved-browser native-host follow-up

- `./scripts/install-native-host.sh --target chromium --extension-id afmmlmjnbbcapinmhhhhbcoanfckdbfh --host-exe /mnt/data/GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling/scripts/native-host-wrapper.sh`

## Bundle files

- `bundle-summary.json`
- `profile-info.json`
- `doctor.json`
- `native-host-current-browser.json`
- `capture-history.json`
- `capture-diff.json`
- `native-host-saved-browser.json`
- `native-host-effective-browser.json`
- `profile-artifacts/`
