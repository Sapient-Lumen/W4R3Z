#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
build=false
include_cgroup=true

usage() {
    printf 'usage: %s [--build] [--skip-cgroup]\n' "$0" >&2
}

while (($# > 0)); do
    case "$1" in
        --build)
            build=true
            shift
            ;;
        --skip-cgroup)
            include_cgroup=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            usage
            exit 2
            ;;
    esac
done

cd "$repo_root"

if $build; then
    nix develop -c bash -lc \
        'cmake --build build -j2 --target iotox_tests iotox_terminal_posix_process_tests iotox_terminal_controller_process_tests iotox_ratox_restart_process_tests iotox_terminal_cgroup_recovery_process_tests'
fi

ratox_regex='^iotox\.(terminal-posix-process|terminal-controller-process|ratox-restart-fence-process|ratox-r7-analyzer|ratox-terminal-probe|ratox-cli-reconnect-probe)$'

nix develop -c bash -lc \
    "ctest --test-dir build -R '$ratox_regex' --output-on-failure"

if $include_cgroup; then
    ./tools/ratox-cgroup-delegated-service-check.sh
fi
