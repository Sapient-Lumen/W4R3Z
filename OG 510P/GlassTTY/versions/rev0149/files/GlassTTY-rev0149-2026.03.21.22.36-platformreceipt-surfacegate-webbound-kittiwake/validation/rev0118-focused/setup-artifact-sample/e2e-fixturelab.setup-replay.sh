#!/usr/bin/env bash
set -euo pipefail
cd /mnt/data/glasswork/GlassTTY-rev0117-2026.03.19.00.03-setupreplay-fixtureledger-channelprep-oystercatcher

# Replay the most relevant GlassTTY smoke setup commands.
# Commands that were only recommended or skipped stay commented out for operator review.

# playwright_channel_ready: executed-failed
# reason: synthetic cache drift proof
python scripts/playwright-browsers.py ensure-channel-ready

# native_host_install_chromium: executed-ok
# reason: install host manifest for chromium lane
./scripts/install-native-host.sh --target chromium --extension-id auto --host-exe ./scripts/native-host-wrapper.sh
