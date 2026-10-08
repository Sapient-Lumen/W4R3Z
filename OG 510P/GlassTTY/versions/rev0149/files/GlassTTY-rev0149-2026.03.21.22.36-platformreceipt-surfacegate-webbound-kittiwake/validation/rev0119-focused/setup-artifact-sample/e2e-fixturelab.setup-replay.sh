#!/usr/bin/env bash
set -euo pipefail
cd /mnt/data/glasstty_rev0118_work/GlassTTY-rev0118-2026.03.19.00.27-setupledger-outputtails-replaystory-turnstone

# Replay the most relevant GlassTTY smoke setup commands.
# Commands that were only recommended or skipped stay commented out for operator review.

# playwright_channel_ready: executed-failed
# reason: cache drift forced a repair attempt
python scripts/playwright-browsers.py ensure-channel-ready

# native_host_install_chrome-for-testing: planned-only
# reason: Smoke installs native-host manifests for each required browser-family target before launching the bridge.
# ./scripts/install-native-host.sh --target chrome-for-testing --extension-id auto --host-exe ./scripts/native-host-wrapper.sh
