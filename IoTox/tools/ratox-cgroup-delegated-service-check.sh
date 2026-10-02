#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
test_binary=${1:-"$repo_root/build/iotox_terminal_cgroup_recovery_process_tests"}

if [[ ! -x "$test_binary" ]]; then
    printf 'missing executable: %s\n' "$test_binary" >&2
    printf 'build it with: nix develop -c cmake --build build -j2 --target iotox_terminal_cgroup_recovery_process_tests\n' >&2
    exit 2
fi

if ! command -v systemd-run >/dev/null 2>&1; then
    printf 'SKIP ratox delegated cgroup service check: systemd-run is unavailable\n'
    exit 77
fi

if ! systemctl --user --quiet is-active default.target >/dev/null 2>&1; then
    printf 'SKIP ratox delegated cgroup service check: user systemd manager is unavailable\n'
    exit 77
fi

passes=0
skips=0
failures=0
modes=(
    lifecycle
    memory-resource
    cpu-resource
    io-resource
    pressure-admission
)

for mode in "${modes[@]}"; do
    output=$(mktemp -t iotox-ratox-cgroup-check.XXXXXXXX)
    set +e
    systemd-run --user --collect --wait --pipe \
        --property=Delegate=yes \
        "$test_binary" "--$mode" >"$output" 2>&1
    status=$?
    set -e
    sed "s/^/[$mode] /" "$output"
    rm -f "$output"
    case "$status" in
        0)
            passes=$((passes + 1))
            ;;
        77)
            skips=$((skips + 1))
            ;;
        *)
            failures=$((failures + 1))
            ;;
    esac
done

printf 'ratox-cgroup-delegated-service-summary passes=%s skips=%s failures=%s\n' \
    "$passes" "$skips" "$failures"

if [[ "$failures" -ne 0 ]]; then
    exit 1
fi
if [[ "$passes" -eq 0 ]]; then
    exit 77
fi
exit 0
