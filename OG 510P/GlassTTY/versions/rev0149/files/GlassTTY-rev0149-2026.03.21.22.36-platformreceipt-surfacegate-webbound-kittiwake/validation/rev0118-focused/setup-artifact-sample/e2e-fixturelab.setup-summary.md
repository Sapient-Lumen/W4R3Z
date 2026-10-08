# GlassTTY smoke setup summary

- report_phase: native_host_ready
- report_timestamp: 2026-03-19T00:27:00Z
- setup_action_count: 2
- executed_setup_action_count: 2
- failed_setup_action_count: 1
- skipped_setup_action_count: 0
- setup_replay_script: `/mnt/data/glasswork/GlassTTY-rev0117-2026.03.19.00.03-setupreplay-fixtureledger-channelprep-oystercatcher/validation/rev0118-focused/setup-artifact-sample/e2e-fixturelab.setup-replay.sh`
- setup_ledger_json: `/mnt/data/glasswork/GlassTTY-rev0117-2026.03.19.00.03-setupreplay-fixtureledger-channelprep-oystercatcher/validation/rev0118-focused/setup-artifact-sample/e2e-fixturelab.setup-ledger.json`

## Actions

- `playwright_channel_ready` — executed-failed
  - reason: synthetic cache drift proof
  - command: `python scripts/playwright-browsers.py ensure-channel-ready`
  - stdout_tail:

    ```text
    repairing cache
    retrying sync
    ```
  - stderr_tail:

    ```text
    [… trimmed …]
    stderr-line-5
    stderr-line-6
    stderr-line-7
    stderr-line-8
    stderr-line-9
    stderr-line-10
    stderr-line-11
    stderr-line-12
    stderr-line-13
    stderr-line-14
    stderr-line-15
    stderr-line-16
    stderr-line-17
    stderr-line-18
    stderr-line-19
    stderr-line-20
    stderr-line-21
    stderr-line-22
    stderr-line-23
    stderr-line-24
    ```
- `native_host_install_chromium` — executed-ok
  - reason: install host manifest for chromium lane
  - command: `./scripts/install-native-host.sh --target chromium --extension-id auto --host-exe ./scripts/native-host-wrapper.sh`
  - stdout_tail:

    ```text
    installed manifest
    ```
