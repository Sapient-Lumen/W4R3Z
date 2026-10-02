#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
sandwurm_root=${IOTOX_SANDWURM_ROOT:-"$root/../sandwurm"}
sandwurm_root=$(cd "$sandwurm_root" && pwd -P)
sandwurm_bin=${SANDWURM_BIN:-/run/current-system/sw/bin/sandwurm}
state_root=${IOTOX_SANDWURM_STATE_DIR:-"$root/.sandwurm/lab"}
host_bin=/run/current-system/sw/bin
host_path="/run/wrappers/bin:$host_bin"
node_bin=$(command -v node || true)
if [[ -z "$node_bin" ]]; then
    sandwurm_real=$(readlink -f "$sandwurm_bin")
    sandwurm_prefix=$(cd "$(dirname "$sandwurm_real")/.." && pwd -P)
    if [[ -x "$sandwurm_prefix/libexec/sandwurm-host-tools/bin/node" ]]; then
        node_bin="$sandwurm_prefix/libexec/sandwurm-host-tools/bin/node"
    fi
fi
if [[ -z "$node_bin" ]]; then
    node_out=$("$host_bin/nix" eval --raw nixpkgs#nodejs.outPath)
    if [[ -x "$node_out/bin/node" ]]; then
        node_bin="$node_out/bin/node"
    fi
fi
if [[ -n "$node_bin" && -x "$node_bin" ]]; then
    host_path="$host_path:$(dirname "$node_bin")"
fi

usage() {
    printf '%s\n' \
        "usage: $0 preflight" \
        "       $0 build [client|device]" \
        "       $0 up [client|device]" \
        "       $0 up-three-writer [default|soak-smoke|soak-24h|near-ceiling-cap-1|near-ceiling-cap-4|near-ceiling-cap-8|near-ceiling-cap-16|near-ceiling-cap-32|near-ceiling-cap-64]" \
        "       $0 status-three-writer PROOF_ROOT" \
        "       $0 watch-three-writer PROOF_ROOT [watch args...]" \
        "       $0 verify-three-writer PROOF_ROOT" \
        "       $0 export-three-writer PROOF_ROOT" \
        "       $0 up-sync-metadata-corruption" \
        "       $0 verify-sync-metadata-corruption PROOF_ROOT" \
        "       $0 export-sync-metadata-corruption PROOF_ROOT" \
        "       $0 up-sync-projection-descriptor" \
        "       $0 verify-sync-projection-descriptor PROOF_ROOT" \
        "       $0 export-sync-projection-descriptor PROOF_ROOT" \
        "       $0 up-sync-power-cut [pre-exchange|post-exchange|receive-staging|cas-install|manifest-install|branch-record-install|branch-pointer-update|manifest-directory-fsync|branch-record-directory-fsync|branch-pointer-directory-fsync]" \
        "       $0 verify-sync-power-cut PROOF_ROOT" \
        "       $0 export-sync-power-cut PROOF_ROOT" \
        "       $0 up-sync-shadow" \
        "       $0 verify-sync-shadow PROOF_ROOT" \
        "       $0 export-sync-shadow PROOF_ROOT" \
        "       $0 up-pair direct-udp|forced-tcp|tox-tor [SCENARIO] [ACTUAL_TOR_NODE]" \
        "       $0 up-pair tox-i2p baseline NODE1 NODE2 NODE3" \
        "       $0 up-pair tox-i2p i2p-router-restart NODE1 NODE2 NODE3" \
        "       $0 up-pair tox-i2p i2p-service-restart NODE1 NODE2 NODE3" \
        "       $0 up-pair direct-udp sync-tree-route-private-actual-i2p-payload NODE1 NODE2 NODE3" \
        "       $0 up-pair direct-udp sync-tree-route-private-actual-i2p-loss NODE1 NODE2 NODE3" \
        "       $0 up-pair direct-udp sync-file-range-actual-i2p NODE1 NODE2 NODE3" \
        "       $0 up-pair direct-udp sync-file-range-actual-i2p-loss NODE1 NODE2 NODE3" \
        "       $0 verify-pair direct-udp|forced-tcp|tox-tor|tox-i2p|tox-i2p-construction PROOF_ROOT [SCENARIO]" \
        "       $0 export-pair PROOF_ROOT" \
        "       $0 export-provider-rolling PROOF_ROOT" \
        "       pair scenarios also include sync-content, sync-content-same-source-lanes," \
        "       sync-bidirectional, sync-automation," \
        "       sync-content-restart-cap-2, sync-content-restart-cap-4," \
        "       sync-content-lane-science, sync-content-lane-science-reverse," \
        "       sync-content-ratox-latency-science, sync-content-ratox-cap-2-sla," \
        "       sync-content-ratox-post-bulk-admission," \
        "       sync-content-route-private-actual-tor," \
        "       sync-content-same-source-multi-route-actual-tor," \
        "       sync-content-multi-route-actual-tor," \
        "       sync-content-multi-source," \
        "       sync-content-multi-source-loss and" \
        "       sync-content-multi-route-actual-tor-loss," \
        "       and sync-tree-route-throughput" \
        "       $0 status [client|device]" \
        "       $0 verify client|device PROOF_ROOT"
}

role_config() {
    case "${1:-device}" in
        client|device) printf 'iotox-sandwurm-%s\n' "${1:-device}" ;;
        *) printf 'invalid IoTox guest role: %s\n' "${1:-}" >&2; exit 2 ;;
    esac
}

require_substrate() {
    test -c /dev/kvm && test -w /dev/kvm
    test -c /dev/net/tun && test -w /dev/net/tun
    test -x "$sandwurm_bin"
    test -x "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"
    systemctl is-active --quiet sandwurm-direct-cloud-hypervisor-prepared-host.service
    systemctl is-active --quiet sandwurm-direct-cloud-hypervisor-runner-authority.service
}

run_chain() {
    local launch=$1
    local role=${2:-device}
    local config
    local proof_root
    config=$(role_config "$role")
    mkdir -p "$state_root/$role"
    proof_root=$(mktemp -d -p "$state_root/$role" "run.XXXXXXXX")
    printf 'proof-root=%s\n' "$proof_root"

    PATH="$host_path" \
    SANDWURM_BIN="$sandwurm_bin" \
    SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT="$proof_root" \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH="$launch" \
    SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS=1 \
    SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT=1 \
    SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN=1 \
    SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF="path:$sandwurm_root" \
    SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE=none \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY='size=2G,shared=on' \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS=2 \
    SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS=120 \
    SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT=/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json \
    SW_DIRECT_NIXOS_FLAKE_REF="git+file:$root" \
    SW_DIRECT_NIXOS_CONFIG="$config" \
      "$host_bin/bash" "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"
    if [[ "$launch" == 1 ]]; then
        "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
            "$proof_root" "$role"
    fi
}

run_three_writer() {
    local profile=${1:-default}
    local config
    local proof_subdir
    local receipt_timeout
    local proof_root
    case "$profile" in
        default|qualification)
            config=iotox-sandwurm-three-writer
            proof_subdir=three-writer
            receipt_timeout=1200
            ;;
        soak-smoke|short-soak)
            config=iotox-sandwurm-three-writer-soak-smoke
            proof_subdir=three-writer-soak-smoke
            receipt_timeout=1800
            ;;
        soak-24h|24h-soak)
            config=iotox-sandwurm-three-writer-soak-24h
            proof_subdir=three-writer-soak-24h
            # The guest-side 24h profile also enforces a 288-cycle minimum.
            # Long post-restart sparse windows can legitimately carry the run
            # past 26h, so keep the outer Sandwurm receipt wait well above the
            # nominal wall-clock target and let the guest harness's own
            # per-cycle correctness timeouts decide pass/reject.
            receipt_timeout=172800
            ;;
        near-ceiling-cap-1|near-ceiling-cap1|cap-1)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-1
            proof_subdir=three-writer-near-ceiling-cap-1
            receipt_timeout=2400
            ;;
        near-ceiling-cap-4|near-ceiling-cap4|cap-4)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-4
            proof_subdir=three-writer-near-ceiling-cap-4
            receipt_timeout=2400
            ;;
        near-ceiling-cap-8|near-ceiling-cap8|cap-8)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-8
            proof_subdir=three-writer-near-ceiling-cap-8
            receipt_timeout=2400
            ;;
        near-ceiling-cap-16|near-ceiling-cap16|cap-16)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-16
            proof_subdir=three-writer-near-ceiling-cap-16
            receipt_timeout=2400
            ;;
        near-ceiling-cap-32|near-ceiling-cap32|cap-32)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-32
            proof_subdir=three-writer-near-ceiling-cap-32
            receipt_timeout=2400
            ;;
        near-ceiling-cap-64|near-ceiling-cap64|cap-64)
            config=iotox-sandwurm-three-writer-near-ceiling-cap-64
            proof_subdir=three-writer-near-ceiling-cap-64
            receipt_timeout=2400
            ;;
        *)
            printf 'invalid three-writer profile: %s\n' "$profile" >&2
            exit 2
            ;;
    esac
    mkdir -p "$state_root/$proof_subdir"
    proof_root=$(mktemp -d -p "$state_root/$proof_subdir" "run.XXXXXXXX")
    printf 'profile=%s\n' "$profile"
    printf 'config=%s\n' "$config"
    printf 'proof-root=%s\n' "$proof_root"

    PATH="$host_path" \
    SANDWURM_BIN="$sandwurm_bin" \
    SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT="$proof_root" \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH=1 \
    SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS=1 \
    SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT=1 \
    SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN=1 \
    SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF="path:$sandwurm_root" \
    SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE=none \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY='size=2G,shared=on' \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS=2 \
    SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS="$receipt_timeout" \
    SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT=/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json \
    SW_DIRECT_NIXOS_FLAKE_REF="git+file:$root" \
    SW_DIRECT_NIXOS_CONFIG="$config" \
      "$host_bin/bash" "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"
    local sync_receipt
    sync_receipt="$proof_root/live/workspace-export/guest-receipts/iotox/sync-three-writer.json"
    if [[ ! -f "$sync_receipt" ]]; then
        local chain_status=missing
        local chain_receipt="$proof_root/direct-cloud-hypervisor-live-chain.json"
        if [[ -f "$chain_receipt" ]]; then
            chain_status=$("$host_bin/python3" -c \
                'import json, pathlib, sys; print(json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")).get("status", "unknown"))' \
                "$chain_receipt")
        fi
        printf 'three-writer-result=not-run chain-status=%s (proof retained at %s)\n' \
            "$chain_status" "$proof_root" >&2
        return 1
    fi
    "$host_bin/python3" \
        "$root/tools/verify-sync-three-writer-sandwurm.py" "$proof_root"
    local result
    result=$("$host_bin/python3" -c \
        'import json, pathlib, sys; print(json.loads((pathlib.Path(sys.argv[1]) / "live/workspace-export/guest-receipts/iotox/sync-three-writer.json").read_text(encoding="utf-8"))["status"])' \
        "$proof_root")
    if [[ "$result" == rejected ]]; then
        printf 'three-writer-result=rejected (proof retained and verified)\n' >&2
        return 1
    fi
    if [[ "$result" != passed ]]; then
        printf 'unexpected three-writer result: %s\n' "$result" >&2
        return 1
    fi
    "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
        "$proof_root" device
}

verify_three_writer() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'verify-three-writer requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/verify-sync-three-writer-sandwurm.py" "$1"
}

status_three_writer() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'status-three-writer requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/inspect-sync-three-writer-soak.py" "$1"
}

watch_three_writer() {
    if [[ $# -lt 1 || -z "$1" ]]; then
        printf 'watch-three-writer requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/watch-sync-three-writer-soak.py" "$@"
}

export_three_writer() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'export-three-writer requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/export-sync-three-writer-sandwurm.py" "$1"
}

run_sync_metadata_corruption() {
    local proof_root
    if [[ -n "$("$host_bin/git" -C "$root" status --porcelain=v1 \
        --untracked-files=all)" ]]; then
        printf 'metadata-corruption qualification requires a clean Git tree\n' >&2
        exit 1
    fi
    mkdir -p "$state_root/sync-metadata-corruption"
    proof_root=$(mktemp -d -p "$state_root/sync-metadata-corruption" \
        "run.XXXXXXXX")
    printf 'config=iotox-sandwurm-sync-metadata-corruption\n'
    printf 'proof-root=%s\n' "$proof_root"

    PATH="$host_path" \
    SANDWURM_BIN="$sandwurm_bin" \
    SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT="$proof_root" \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH=1 \
    SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS=1 \
    SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT=1 \
    SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN=1 \
    SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF="path:$sandwurm_root" \
    SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE=none \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY='size=2G,shared=on' \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS=2 \
    SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS=900 \
    SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT=/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json \
    SW_DIRECT_NIXOS_FLAKE_REF="git+file:$root" \
    SW_DIRECT_NIXOS_CONFIG=iotox-sandwurm-sync-metadata-corruption \
      "$host_bin/bash" "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"

    "$host_bin/python3" \
        "$root/tools/verify-sync-metadata-corruption-sandwurm.py" \
        "$proof_root"
    "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
        "$proof_root" device
}

verify_sync_metadata_corruption() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'verify-sync-metadata-corruption requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/verify-sync-metadata-corruption-sandwurm.py" "$1"
}

export_sync_metadata_corruption() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'export-sync-metadata-corruption requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/export-sync-metadata-corruption-sandwurm.py" "$1"
}

run_sync_projection_descriptor() {
    local proof_root
    if [[ -n "$("$host_bin/git" -C "$root" status --porcelain=v1 \
        --untracked-files=all)" ]]; then
        printf 'projection-descriptor qualification requires a clean Git tree\n' >&2
        exit 1
    fi
    mkdir -p "$state_root/sync-projection-descriptor"
    proof_root=$(mktemp -d -p "$state_root/sync-projection-descriptor" \
        "run.XXXXXXXX")
    printf 'config=iotox-sandwurm-sync-projection-descriptor\n'
    printf 'proof-root=%s\n' "$proof_root"

    PATH="$host_path" \
    SANDWURM_BIN="$sandwurm_bin" \
    SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT="$proof_root" \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH=1 \
    SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS=1 \
    SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT=1 \
    SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN=1 \
    SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF="path:$sandwurm_root" \
    SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE=none \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY='size=2G,shared=on' \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS=2 \
    SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS=1200 \
    SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT=/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json \
    SW_DIRECT_NIXOS_FLAKE_REF="git+file:$root" \
    SW_DIRECT_NIXOS_CONFIG=iotox-sandwurm-sync-projection-descriptor \
      "$host_bin/bash" "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"

    "$host_bin/python3" \
        "$root/tools/verify-sync-projection-descriptor-sandwurm.py" \
        "$proof_root"
    "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
        "$proof_root" device
}

verify_sync_projection_descriptor() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'verify-sync-projection-descriptor requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/verify-sync-projection-descriptor-sandwurm.py" "$1"
}

export_sync_projection_descriptor() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'export-sync-projection-descriptor requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/export-sync-projection-descriptor-sandwurm.py" "$1"
}

run_sync_power_cut() {
    local profile=${1:-pre-exchange}
    local config
    local boundary
    local proof_subdir
    case "$profile" in
        pre-exchange|pre)
            config=iotox-sandwurm-sync-power-cut
            boundary=pre-exchange-pending
            proof_subdir=sync-power-cut
            ;;
        post-exchange|post)
            config=iotox-sandwurm-sync-power-cut-post-exchange
            boundary=post-exchange-pending
            proof_subdir=sync-power-cut-post-exchange
            ;;
        receive-staging|receive)
            config=iotox-sandwurm-sync-power-cut-receive-staging
            boundary=receive-staging-partial
            proof_subdir=sync-power-cut-receive-staging
            ;;
        cas-install|cas)
            config=iotox-sandwurm-sync-power-cut-cas-install
            boundary=cas-install-temporary
            proof_subdir=sync-power-cut-cas-install
            ;;
        manifest-install|manifest)
            config=iotox-sandwurm-sync-power-cut-manifest-install
            boundary=manifest-install-temporary
            proof_subdir=sync-power-cut-manifest-install
            ;;
        branch-record-install|record)
            config=iotox-sandwurm-sync-power-cut-branch-record-install
            boundary=branch-record-install-temporary
            proof_subdir=sync-power-cut-branch-record-install
            ;;
        branch-pointer-update|pointer)
            config=iotox-sandwurm-sync-power-cut-branch-pointer-update
            boundary=branch-pointer-update-temporary
            proof_subdir=sync-power-cut-branch-pointer-update
            ;;
        manifest-directory-fsync|manifest-fsync)
            config=iotox-sandwurm-sync-power-cut-manifest-directory-fsync
            boundary=manifest-install-directory-fsync
            proof_subdir=sync-power-cut-manifest-directory-fsync
            ;;
        branch-record-directory-fsync|record-fsync)
            config=iotox-sandwurm-sync-power-cut-branch-record-directory-fsync
            boundary=branch-record-install-directory-fsync
            proof_subdir=sync-power-cut-branch-record-directory-fsync
            ;;
        branch-pointer-directory-fsync|pointer-fsync)
            config=iotox-sandwurm-sync-power-cut-branch-pointer-directory-fsync
            boundary=branch-pointer-update-directory-fsync
            proof_subdir=sync-power-cut-branch-pointer-directory-fsync
            ;;
        *)
            printf 'invalid sync power-cut profile: %s\n' "$profile" >&2
            exit 2
            ;;
    esac
    mkdir -p "$state_root/$proof_subdir"
    "$host_bin/python3" "$root/tools/run-sync-power-cut-sandwurm.py" \
        --repo-root "$root" \
        --sandwurm-root "$sandwurm_root" \
        --sandwurm-bin "$sandwurm_bin" \
        --host-bash "$host_bin/bash" \
        --host-path "$host_path" \
        --state-root "$state_root/$proof_subdir" \
        --verifier "$root/tools/verify-sync-power-cut-sandwurm.py" \
        --config "$config" \
        --cut-boundary "$boundary" \
        --prelaunch-timeout 3600 \
        --timeout 1200
}

verify_sync_power_cut() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'verify-sync-power-cut requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/verify-sync-power-cut-sandwurm.py" "$1"
}

export_sync_power_cut() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'export-sync-power-cut requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" \
        "$root/tools/export-sync-power-cut-sandwurm.py" "$1"
}

run_sync_shadow() {
    local proof_root
    mkdir -p "$state_root/sync-shadow"
    proof_root=$(mktemp -d -p "$state_root/sync-shadow" "run.XXXXXXXX")
    printf 'proof-root=%s\n' "$proof_root"

    PATH="$host_path" \
    SANDWURM_BIN="$sandwurm_bin" \
    SW_DIRECT_CH_LIVE_CHAIN_PROOF_ROOT="$proof_root" \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH=1 \
    SW_DIRECT_CH_LIVE_CHAIN_BUILD_ARTIFACTS=1 \
    SW_DIRECT_CH_LIVE_CHAIN_MATERIALIZE_ROOT=1 \
    SW_DIRECT_CH_LIVE_CHAIN_REALIZE_TOOLCHAIN=1 \
    SW_DIRECT_CH_LIVE_CHAIN_TOOLCHAIN_FLAKE_REF="path:$sandwurm_root" \
    SW_DIRECT_CH_LIVE_CHAIN_NETWORK_MODE=none \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_MEMORY='size=2G,shared=on' \
    SW_DIRECT_CH_LIVE_CHAIN_LAUNCH_VCPUS=2 \
    SW_DIRECT_CH_LIVE_CHAIN_GUEST_RECEIPT_TIMEOUT_SECONDS=9000 \
    SW_DIRECT_CH_PRELAUNCH_RUNNER_AUTHORITY_RECEIPT=/var/lib/sandwurm-direct-cloud-hypervisor/runner-authority-declaration.json \
    SW_DIRECT_NIXOS_FLAKE_REF="git+file:$root" \
    SW_DIRECT_NIXOS_CONFIG=iotox-sandwurm-sync-shadow \
      "$host_bin/bash" "$sandwurm_root/tests/probe-direct-cloud-hypervisor-live-chain.sh"
    "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
        "$proof_root" device
    "$host_bin/python3" "$root/tools/verify-sync-shadow-sandwurm.py" \
        "$proof_root"
}

verify_sync_shadow() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'verify-sync-shadow requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" "$root/tools/verify-sync-shadow-sandwurm.py" "$1"
}

export_sync_shadow() {
    if [[ $# != 1 || -z "$1" ]]; then
        printf 'export-sync-shadow requires one PROOF_ROOT\n' >&2
        exit 2
    fi
    "$host_bin/python3" "$root/tools/export-sync-shadow-sandwurm.py" "$1"
}

command=${1:-}
case "$command" in
    preflight)
        require_substrate
        "$host_bin/nix" flake check --no-build "git+file:$root" \
            --override-input sandwurm "path:$sandwurm_root"
        "$sandwurm_bin" doctor substrate --json
        ;;
    build)
        require_substrate
        run_chain 0 "${2:-device}"
        ;;
    up)
        require_substrate
        run_chain 1 "${2:-device}"
        ;;
    up-three-writer)
        require_substrate
        run_three_writer "${2:-default}"
        ;;
    status-three-writer)
        status_three_writer "${2:-}"
        ;;
    watch-three-writer)
        shift
        watch_three_writer "$@"
        ;;
    verify-three-writer)
        verify_three_writer "${2:-}"
        ;;
    export-three-writer)
        export_three_writer "${2:-}"
        ;;
    up-sync-metadata-corruption)
        require_substrate
        run_sync_metadata_corruption
        ;;
    verify-sync-metadata-corruption)
        verify_sync_metadata_corruption "${2:-}"
        ;;
    export-sync-metadata-corruption)
        export_sync_metadata_corruption "${2:-}"
        ;;
    up-sync-projection-descriptor)
        require_substrate
        run_sync_projection_descriptor
        ;;
    verify-sync-projection-descriptor)
        verify_sync_projection_descriptor "${2:-}"
        ;;
    export-sync-projection-descriptor)
        export_sync_projection_descriptor "${2:-}"
        ;;
    up-sync-power-cut)
        require_substrate
        run_sync_power_cut "${2:-pre-exchange}"
        ;;
    verify-sync-power-cut)
        verify_sync_power_cut "${2:-}"
        ;;
    export-sync-power-cut)
        export_sync_power_cut "${2:-}"
        ;;
    up-sync-shadow)
        require_substrate
        run_sync_shadow
        ;;
    verify-sync-shadow)
        verify_sync_shadow "${2:-}"
        ;;
    export-sync-shadow)
        export_sync_shadow "${2:-}"
        ;;
    up-pair)
        require_substrate
        case "${2:-}" in
            direct-udp|forced-tcp|tox-tor|tox-i2p|tox-i2p-construction) ;;
            *) usage >&2; exit 2 ;;
        esac
        scenario=${3:-baseline}
        case "$scenario" in
            sync-tree-route-throughput) ;;
            sync-content-ratox-latency-science) ;;
            sync-content-ratox-cap-2-sla) ;;
            sync-content-ratox-post-bulk-admission) ;;
            sync-content-restart-cap-2|sync-content-restart-cap-4) ;;
            sync-content-lane-science-reverse) ;;
            sync-file-range-actual-i2p|sync-file-range-actual-i2p-loss) ;;
baseline|relay-restart|proxy-restart|i2p-router-restart|i2p-service-restart|daemon-restart|link-interruption|packet-loss|provider-rolling|guest-restart|mutable-profile-status|signed-update|update-service|sync-bidirectional|sync-automation|sync-tree|sync-tree-admission|sync-tree-route-loss|sync-tree-route-loss-cancel|sync-tree-route-cancel-loss|sync-tree-route-cancel-race|sync-tree-route-cancel-race-loss-first|sync-tree-route-startup-order|sync-tree-route-private-mixed|sync-tree-route-private-actual-tor|sync-tree-route-private-actual-tor-payload|sync-tree-route-private-actual-i2p-payload|sync-tree-route-private-actual-i2p-loss|sync-tree-route-private-actual-tor-loss|sync-tree-route-balance|sync-tree-route-population|sync-tree-route-population-loss|sync-tree-route-loss-admission|sync-tree-route-startup-admission|sync-tree-route-concurrent-cancel|sync-tree-route-common-link-fairness|sync-tree-route-cancel|sync-tree-adversity|sync-tree-pressure|sync-tree-quota|sync-tree-object-quota|sync-tree-read-only|sync-tree-memory|sync-tree-source-corrupt|sync-tree-destination-corrupt|sync-tree-control-replay|sync-content|sync-content-same-source-lanes|sync-content-lane-science|sync-content-route-private-actual-tor|sync-content-same-source-multi-route-actual-tor|sync-content-multi-route-actual-tor|sync-content-multi-route-actual-tor-loss|sync-content-multi-source|sync-content-multi-source-loss|sync-file|sync-file-range|sync-file-corrupt-basis|sync-file-range-retry|sync-file-range-route-loss|sync-file-range-late-route-loss|sync-file-range-repeated-route-loss|sync-file-range-triple-route-loss|sync-file-range-restart-resume|sync-file-repair|sync-file-restart|sync-file-restart-resume|sync-file-guest-restart|sync-file-pause|sync-file-cancel|sync-file-disconnect|ratox-idle|ratox-route-impairment|ratox-route-loss|ratox-cli-reconnect|ratox-cli-reconnect-repeated|ratox-route-actual-tor-loss|ratox-route-actual-tor-soak|ratox-route-actual-tor-adversary|ratox-bulk-1|ratox-bulk-8|ratox-bulk-16|ratox-bulk-32|ratox-bulk-64|ratox-matrix-idle|ratox-matrix-bulk-1|ratox-matrix-bulk-8|ratox-matrix-bulk-16|ratox-matrix-bulk-32|ratox-matrix-bulk-64|ratox-stripe-32|ratox-stripe-40|ratox-stripe-48|ratox-stripe-56|ratox-stripe-64|ratox-stripe-recovery-32|ratox-stripe-live-loss-32|ratox-stripe-protected-live-loss-24) ;;
            *) usage >&2; exit 2 ;;
        esac
        if [[ "$scenario" == relay-restart && "$2" != forced-tcp ]]; then
            printf 'relay-restart requires forced-tcp\n' >&2
            exit 2
        fi
        if [[ "$scenario" == proxy-restart && "$2" != tox-tor ]]; then
            printf 'proxy-restart requires tox-tor\n' >&2
            exit 2
        fi
        i2p_route=false
        if [[ "$2" == tox-i2p || "$2" == tox-i2p-construction ]]; then
            i2p_route=true
        fi
        if $i2p_route && [[ "$scenario" != baseline && \
              "$scenario" != i2p-router-restart && \
              "$scenario" != i2p-service-restart ]]; then
            printf 'tox-i2p supports baseline or an I2P recovery gate\n' >&2
            exit 2
        fi
        if [[ "$scenario" == i2p-router-restart ]] && ! $i2p_route; then
            printf 'i2p-router-restart requires tox-i2p\n' >&2
            exit 2
        fi
        if [[ "$scenario" == i2p-service-restart ]] && ! $i2p_route; then
            printf 'i2p-service-restart requires tox-i2p\n' >&2
            exit 2
        fi
        if [[ "$scenario" == ratox-route-actual-tor-loss || \
              "$scenario" == ratox-route-actual-tor-soak || \
              "$scenario" == ratox-route-actual-tor-adversary ]] && \
           [[ "$2" != tox-tor ]]; then
            printf '%s requires tox-tor\n' "$scenario" >&2
            exit 2
        fi
        if [[ "$scenario" == sync-tree-route-private-mixed || \
              "$scenario" == sync-tree-route-private-actual-tor || \
              "$scenario" == sync-tree-route-private-actual-tor-payload || \
              "$scenario" == sync-tree-route-private-actual-i2p-payload || \
              "$scenario" == sync-tree-route-private-actual-i2p-loss || \
              "$scenario" == sync-file-range-actual-i2p || \
              "$scenario" == sync-file-range-actual-i2p-loss || \
              "$scenario" == sync-content-route-private-actual-tor || \
              "$scenario" == sync-content-same-source-multi-route-actual-tor || \
              "$scenario" == sync-content-multi-route-actual-tor || \
              "$scenario" == sync-content-multi-route-actual-tor-loss || \
              "$scenario" == sync-tree-route-private-actual-tor-loss ]] && \
           [[ "$2" != direct-udp ]]; then
            printf '%s requires direct-udp\n' "$scenario" >&2
            exit 2
        fi
        tor_args=()
        if [[ "$scenario" == sync-tree-route-private-actual-tor || \
              "$scenario" == sync-tree-route-private-actual-tor-payload || \
              "$scenario" == sync-tree-route-private-actual-tor-loss || \
              "$scenario" == sync-content-route-private-actual-tor || \
              "$scenario" == sync-content-same-source-multi-route-actual-tor || \
              "$scenario" == sync-content-multi-route-actual-tor || \
              "$scenario" == sync-content-multi-route-actual-tor-loss || \
              "$scenario" == ratox-route-actual-tor-loss || \
              "$scenario" == ratox-route-actual-tor-soak || \
              "$scenario" == ratox-route-actual-tor-adversary ]]; then
            tor_node=${4:-${IOTOX_PAIR_TOR_NODE:-}}
            test -n "$tor_node" || {
                printf 'actual-Tor scenario requires IPv4:PORT:64_HEX_KEY\n' >&2
                exit 2
            }
            tor_args=(--tor-node "$tor_node")
        fi
        i2p_args=()
        if $i2p_route || [[ \
              "$scenario" == sync-tree-route-private-actual-i2p-payload || \
              "$scenario" == sync-tree-route-private-actual-i2p-loss || \
              "$scenario" == sync-file-range-actual-i2p || \
              "$scenario" == sync-file-range-actual-i2p-loss ]]; then
            i2p_nodes=("${@:4}")
            if (( ${#i2p_nodes[@]} != 3 )); then
                printf 'tox-i2p requires exactly three IPv4:PORT:64_HEX_KEY nodes\n' >&2
                exit 2
            fi
            for i2p_node in "${i2p_nodes[@]}"; do
                i2p_args+=(--i2p-node "$i2p_node")
            done
        fi
        PATH="$host_path" \
        SANDWURM_BIN="$sandwurm_bin" \
        IOTOX_SANDWURM_ROOT="$sandwurm_root" \
        IOTOX_SANDWURM_STATE_DIR="$state_root" \
          "$host_bin/python3" "$root/tools/run-sandwurm-pair.py" \
            "$2" "$scenario" "${tor_args[@]}" "${i2p_args[@]}"
        ;;
    status)
        role=${2:-device}
        role_config "$role" >/dev/null
        latest=$(find "$state_root/$role" -mindepth 1 -maxdepth 1 -type d -name 'run.*' \
            -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -n 1 | cut -d' ' -f2-)
        test -n "$latest" || { printf 'no %s VM runs recorded\n' "$role" >&2; exit 1; }
        "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
            "$latest" "$role"
        ;;
    verify)
        role_config "${2:-}" >/dev/null
        test -n "${3:-}" || { usage >&2; exit 2; }
        "$host_bin/python3" "$root/tools/verify-sandwurm-vm-smoke.py" \
            "$3" "$2"
        ;;
    verify-pair)
        case "${2:-}" in
            direct-udp|forced-tcp|tox-tor|tox-i2p|tox-i2p-construction) ;;
            *) usage >&2; exit 2 ;;
        esac
        test -n "${3:-}" || { usage >&2; exit 2; }
        scenario=${4:-baseline}
        case "$scenario" in
            sync-tree-route-throughput) ;;
            sync-content-ratox-latency-science) ;;
            sync-content-ratox-cap-2-sla) ;;
            sync-content-ratox-post-bulk-admission) ;;
            sync-content-restart-cap-2|sync-content-restart-cap-4) ;;
            sync-content-lane-science-reverse) ;;
            sync-file-range-actual-i2p|sync-file-range-actual-i2p-loss) ;;
            sync-content-multi-route-actual-tor-loss) ;;
baseline|relay-restart|proxy-restart|i2p-router-restart|i2p-service-restart|daemon-restart|link-interruption|packet-loss|provider-rolling|guest-restart|mutable-profile-status|signed-update|update-service|sync-bidirectional|sync-automation|sync-tree|sync-tree-admission|sync-tree-route-loss|sync-tree-route-loss-cancel|sync-tree-route-cancel-loss|sync-tree-route-cancel-race|sync-tree-route-cancel-race-loss-first|sync-tree-route-startup-order|sync-tree-route-private-mixed|sync-tree-route-private-actual-tor|sync-tree-route-private-actual-tor-payload|sync-tree-route-private-actual-i2p-payload|sync-tree-route-private-actual-i2p-loss|sync-tree-route-private-actual-tor-loss|sync-tree-route-balance|sync-tree-route-population|sync-tree-route-population-loss|sync-tree-route-loss-admission|sync-tree-route-startup-admission|sync-tree-route-concurrent-cancel|sync-tree-route-common-link-fairness|sync-tree-route-cancel|sync-tree-adversity|sync-tree-pressure|sync-tree-quota|sync-tree-object-quota|sync-tree-read-only|sync-tree-memory|sync-tree-source-corrupt|sync-tree-destination-corrupt|sync-tree-control-replay|sync-content|sync-content-same-source-lanes|sync-content-lane-science|sync-content-multi-source|sync-content-multi-source-loss|sync-file|sync-file-range|sync-file-corrupt-basis|sync-file-range-retry|sync-file-range-route-loss|sync-file-range-late-route-loss|sync-file-range-repeated-route-loss|sync-file-range-triple-route-loss|sync-file-range-restart-resume|sync-file-repair|sync-file-restart|sync-file-restart-resume|sync-file-guest-restart|sync-file-pause|sync-file-cancel|sync-file-disconnect|ratox-idle|ratox-route-impairment|ratox-route-loss|ratox-cli-reconnect|ratox-cli-reconnect-repeated|ratox-route-actual-tor-loss|ratox-route-actual-tor-soak|ratox-route-actual-tor-adversary|ratox-bulk-1|ratox-bulk-8|ratox-bulk-16|ratox-bulk-32|ratox-bulk-64|ratox-matrix-idle|ratox-matrix-bulk-1|ratox-matrix-bulk-8|ratox-matrix-bulk-16|ratox-matrix-bulk-32|ratox-matrix-bulk-64|ratox-stripe-32|ratox-stripe-40|ratox-stripe-48|ratox-stripe-56|ratox-stripe-64|ratox-stripe-recovery-32|ratox-stripe-live-loss-32|ratox-stripe-protected-live-loss-24) ;;
            *) usage >&2; exit 2 ;;
        esac
        if [[ "$scenario" == sync-tree-route-private-mixed || \
              "$scenario" == sync-tree-route-private-actual-tor || \
              "$scenario" == sync-tree-route-private-actual-tor-payload || \
              "$scenario" == sync-tree-route-private-actual-i2p-payload || \
              "$scenario" == sync-tree-route-private-actual-i2p-loss || \
              "$scenario" == sync-file-range-actual-i2p || \
              "$scenario" == sync-file-range-actual-i2p-loss || \
              "$scenario" == sync-content-multi-route-actual-tor-loss || \
              "$scenario" == sync-tree-route-private-actual-tor-loss ]] && \
           [[ "$2" != direct-udp ]]; then
            printf '%s requires direct-udp\n' "$scenario" >&2
            exit 2
        fi
        if [[ "$scenario" == ratox-route-actual-tor-loss || \
              "$scenario" == ratox-route-actual-tor-soak || \
              "$scenario" == ratox-route-actual-tor-adversary ]] && \
           [[ "$2" != tox-tor ]]; then
            printf '%s requires tox-tor\n' "$scenario" >&2
            exit 2
        fi
        if [[ "$scenario" == provider-rolling ]]; then
            "$host_bin/python3" "$root/tools/verify-sandwurm-provider-rolling.py" \
                "$3" --route "$2"
        else
            "$host_bin/python3" "$root/tools/verify-sandwurm-pair.py" \
                "$3" --route "$2" --scenario "$scenario"
        fi
        ;;
    export-pair)
        test -n "${2:-}" || { usage >&2; exit 2; }
        "$host_bin/python3" "$root/tools/export-sandwurm-pair.py" "$2"
        ;;
    export-provider-rolling)
        test -n "${2:-}" || { usage >&2; exit 2; }
        "$host_bin/python3" "$root/tools/export-sandwurm-provider-rolling.py" "$2"
        ;;
    -h|--help|help) usage ;;
    *) usage >&2; exit 2 ;;
esac
