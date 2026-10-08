# GlassTTY profile capture: lab

- captured_at: 2026-03-17T21:35:39Z
- profile_path: /mnt/data/GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling/validation/rev0100-focused/proof-home/profiles/lab
- attach_ready: False
- cdp_endpoint: http://127.0.0.1:9555
- reopen_launchable_now: True
- saved_browser_path: /usr/bin/chromium
- effective_browser_path: /usr/bin/chromium
- mv3_resume_proof_grade: strict_context_recovery
- mv3_resume_captured_at: 2026-03-17T21:32:00Z

## Recommended commands

- info: `./scripts/glasstty-profile.sh info lab --pretty`
- capture: `./scripts/glasstty-profile.sh capture lab --output-dir validation/latest/profile-capture-lab`
- reopen: `CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh lab --skip-extension --remote-debugging-port 9555 chrome://extensions/`
- reopen_portable: `./scripts/glasstty-profile.sh reopen lab --allow-discovered-browser-fallback`
- reopen_debug: `CHROMIUM_BIN=/usr/bin/chromium ./scripts/launch-chromium-profile.sh lab --skip-extension --remote-debugging-port auto chrome://extensions/`
- reopen_debug_portable: `./scripts/glasstty-profile.sh reopen lab --allow-discovered-browser-fallback --remote-debugging-port auto`
- resume_proof: `./scripts/glasstty-profile.sh resume-proof lab --output validation/latest/mv3-worker-resume-lab.json --timeout 25`

## Saved-browser native-host follow-up

- `./scripts/install-native-host.sh --target chromium --extension-id afmmlmjnbbcapinmhhhhbcoanfckdbfh --host-exe /mnt/data/GlassTTY-rev0100-2026.03.17.21.32-profilecapture-proofbundle-handofflane-sanderling/scripts/native-host-wrapper.sh`

## Bundle files

- `bundle-summary.json`
- `profile-info.json`
- `doctor.json`
- `native-host-current-browser.json`
- `native-host-saved-browser.json`
- `native-host-effective-browser.json`
- `profile-artifacts/`
