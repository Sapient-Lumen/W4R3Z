# GlassTTY smoke setup summary

- report_phase: playwright_channel_prepare_failed
- report_timestamp: 2026-03-19T00:43:39Z
- setup_action_count: 2
- executed_setup_action_count: 1
- failed_setup_action_count: 1
- skipped_setup_action_count: 0
- setup_replay_script: `validation/rev0119-focused/setup-artifact-sample/e2e-fixturelab.setup-replay.sh`
- setup_ledger_json: `validation/rev0119-focused/setup-artifact-sample/e2e-fixturelab.setup-ledger.json`

## Environment fingerprint

- browser_mode_requested: auto
- playwright_channel_policy: if-needed
- playwright_launch_strategy: bundled-executable
- playwright_channel_ready: False
- playwright_cache_alignment_status: cache-install-name-drift
- playwright_root: validation/rev0119-focused/setup-artifact-sample/pw-cache
- profile_dir: validation/rev0119-focused/setup-artifact-sample/tmp-root/profile
- native_host_install_targets: `["chromium", "chrome-for-testing"]`
- default_browser: `{"browser_family": "chrome-for-testing", "native_messaging_primary_target": "chrome-for-testing", "native_messaging_targets": ["chrome-for-testing"], "path": "/tmp/cft/chrome", "source": "chrome-for-testing", "version": "146.0.7390.7"}`
- playwright_browser: `{"browser_family": "chromium", "native_messaging_primary_target": "chromium", "native_messaging_targets": ["chromium"], "path": "/tmp/pw/chromium", "source": "playwright-cache"}`

## Recommended next action

- summary: Repair or inspect Playwright cache alignment before rerunning fixture-lab smoke.
- command: `python scripts/playwright-browsers.py ensure-channel-ready`
- reason: cache drift forced a repair attempt
- source_action: `playwright_channel_ready`

## Actions

- `playwright_channel_ready` — executed-failed
  - reason: cache drift forced a repair attempt
  - command: `python scripts/playwright-browsers.py ensure-channel-ready`
  - environment_fingerprint: `{"browser_mode_requested": "auto", "default_browser": {"browser_family": "chrome-for-testing", "native_messaging_primary_target": "chrome-for-testing", "native_messaging_targets": ["chrome-for-testing"], "path": "/tmp/cft/chrome", "source": "chrome-for-testing", "version": "146.0.7390.7"}, "native_host_install_targets": ["chromium", "chrome-for-testing"], "playwright_browser": {"browser_family": "chromium", "native_messaging_primary_target": "chromium", "native_messaging_targets": ["chromium"], "path": "/tmp/pw/chromium", "source": "playwright-cache"}, "playwright_cache_alignment_reason_before": "cached browser does not match expected package", "playwright_cache_alignment_status_before": "cache-install-name-drift", "playwright_channel_policy": "if-needed", "playwright_channel_ready_before": false, "playwright_root": "validation/rev0119-focused/setup-artifact-sample/pw-cache", "profile_dir": "validation/rev0119-focused/setup-artifact-sample/tmp-root/profile"}`
  - stdout_tail:

    ```text
    audit before
    audit after
    ```
  - stderr_tail:

    ```text
    cache-install-name-drift
    registry link missing
    ```
- `native_host_install_chrome-for-testing` — planned-only
  - reason: Smoke installs native-host manifests for each required browser-family target before launching the bridge.
  - command: `./scripts/install-native-host.sh --target chrome-for-testing --extension-id auto --host-exe ./scripts/native-host-wrapper.sh`
  - environment_fingerprint: `{"browser_mode_requested": "auto", "default_browser": {"browser_family": "chrome-for-testing", "native_messaging_primary_target": "chrome-for-testing", "native_messaging_targets": ["chrome-for-testing"], "path": "/tmp/cft/chrome", "source": "chrome-for-testing", "version": "146.0.7390.7"}, "native_host_install_targets": ["chromium", "chrome-for-testing"], "native_host_target": "chrome-for-testing", "playwright_browser": {"browser_family": "chromium", "native_messaging_primary_target": "chromium", "native_messaging_targets": ["chromium"], "path": "/tmp/pw/chromium", "source": "playwright-cache"}, "playwright_channel_policy": "if-needed", "playwright_root": "validation/rev0119-focused/setup-artifact-sample/pw-cache", "profile_dir": "validation/rev0119-focused/setup-artifact-sample/tmp-root/profile"}`
