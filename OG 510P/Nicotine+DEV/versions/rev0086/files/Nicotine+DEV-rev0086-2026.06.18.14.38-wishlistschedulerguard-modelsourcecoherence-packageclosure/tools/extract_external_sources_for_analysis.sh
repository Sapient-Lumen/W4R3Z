#!/usr/bin/env bash
set -euo pipefail
bundle=${1:-Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z.zip}
out=${2:-/mnt/data/nicotine_dev_external_source_inventory}
mkdir -p "$out"
unzip -q "$bundle" 'Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees/*' 'Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/metadata/*' 'Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/logs/*' 'Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/SHA256SUMS' 'Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/README-FOR-REV0003.md' -d "$out"
find "$out/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees" -maxdepth 1 -mindepth 1 -type d -print
