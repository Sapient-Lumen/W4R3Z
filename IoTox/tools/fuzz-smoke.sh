#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
build=${IOTOX_FUZZ_BUILD_DIR:-"$root/build/clang-fuzz"}
runs=${IOTOX_FUZZ_RUNS:-20000}
jobs=${IOTOX_FUZZ_JOBS:-2}
artifacts=${IOTOX_FUZZ_ARTIFACT_DIR:-"$build/artifacts"}
work_corpus=${IOTOX_FUZZ_CORPUS_DIR:-"$build/corpus"}

if [[ ! "$jobs" =~ ^[1-9][0-9]*$ ]]; then
    printf 'IOTOX_FUZZ_JOBS must be a positive integer: %s\n' "$jobs" >&2
    exit 2
fi

command -v clang >/dev/null 2>&1 || {
    printf '%s\n' 'fuzz smoke requires clang' >&2
    exit 2
}
command -v clang++ >/dev/null 2>&1 || {
    printf '%s\n' 'fuzz smoke requires clang++' >&2
    exit 2
}

hex_to_binary() {
    local source=$1
    local destination=$2

    if command -v xxd >/dev/null 2>&1; then
        xxd -r -p "$source" "$destination"
        return
    fi

    if command -v python3 >/dev/null 2>&1; then
        python3 - "$source" "$destination" <<'PY'
from pathlib import Path
import string
import sys

source = Path(sys.argv[1])
destination = Path(sys.argv[2])
text = "".join(source.read_text(encoding="ascii").split())
if len(text) % 2 != 0 or any(character not in string.hexdigits for character in text):
    raise SystemExit(f"invalid reviewed hexadecimal seed: {source}")
destination.write_bytes(bytes.fromhex(text))
PY
        return
    fi

    if command -v perl >/dev/null 2>&1; then
        perl -0777 -e '
            use strict;
            use warnings;
            my ($source, $destination) = @ARGV;
            open my $input, "<", $source or die "unable to read $source: $!\n";
            local $/;
            my $hex = <$input>;
            close $input or die "unable to close $source: $!\n";
            $hex =~ s/\s+//g;
            die "invalid reviewed hexadecimal seed: $source\n"
                if length($hex) % 2 != 0 || $hex =~ /[^0-9A-Fa-f]/;
            open my $output, ">", $destination
                or die "unable to write $destination: $!\n";
            binmode $output;
            print {$output} pack("H*", $hex)
                or die "unable to write $destination: $!\n";
            close $output or die "unable to close $destination: $!\n";
        ' "$source" "$destination"
        return
    fi

    printf '%s\n' \
        'fuzz smoke requires xxd, python3, or perl to decode reviewed binary seeds' >&2
    exit 2
}

cmake -S "$root" -B "$build" -G Ninja \
    -DCMAKE_BUILD_TYPE=Debug \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DBUILD_TESTING=ON \
    -DIOTOX_BUILD_FUZZER=ON \
    -DIOTOX_WARNINGS_AS_ERRORS=ON
cmake --build "$build" --parallel "$jobs" --target \
    iotox_frame_fuzzer \
    iotox_session_fuzzer \
    iotox_local_control_fuzzer \
    iotox_terminal_protocol_fuzzer \
    iotox_command_fuzzer \
    iotox_terminal_profile_fuzzer \
    iotox_terminal_cgroup_fuzzer \
    iotox_update_bundle_fuzzer \
    iotox_authority_fuzzer \
    iotox_ratox_frame_fuzzer \
    iotox_interactive_state_fuzzer \
    iotox_interactive_service_fuzzer

# libFuzzer minimizes and grows the corpus directory it receives. Never let a
# smoke run mutate the reviewed source seeds: copy them into build-local state.
rm -rf "$work_corpus"
mkdir -p \
    "$work_corpus/frame" \
    "$work_corpus/session" \
    "$work_corpus/local-control" \
    "$work_corpus/terminal-protocol" \
    "$work_corpus/command" \
    "$work_corpus/terminal-profile" \
    "$work_corpus/terminal-cgroup" \
    "$work_corpus/update" \
    "$work_corpus/authority" \
    "$work_corpus/ratox-frame" \
    "$work_corpus/interactive-state" \
    "$work_corpus/interactive-service" \
    "$artifacts/frame" \
    "$artifacts/session" \
    "$artifacts/local-control" \
    "$artifacts/terminal-protocol" \
    "$artifacts/command" \
    "$artifacts/terminal-profile" \
    "$artifacts/terminal-cgroup" \
    "$artifacts/update" \
    "$artifacts/authority" \
    "$artifacts/ratox-frame" \
    "$artifacts/interactive-state" \
    "$artifacts/interactive-service"
cp -a "$root/tests/corpus/frame/." "$work_corpus/frame/"
cp -a "$root/tests/corpus/session/." "$work_corpus/session/"
cp -a "$root/tests/corpus/local-control/." "$work_corpus/local-control/"
cp -a "$root/tests/corpus/terminal-protocol/." "$work_corpus/terminal-protocol/"
cp -a "$root/tests/corpus/command/." "$work_corpus/command/"
cp -a "$root/tests/corpus/terminal-profile/." "$work_corpus/terminal-profile/"
cp -a "$root/tests/corpus/terminal-cgroup/." "$work_corpus/terminal-cgroup/"
cp -a "$root/tests/corpus/update/." "$work_corpus/update/"
cp -a "$root/tests/corpus/authority/." "$work_corpus/authority/"
cp -a "$root/tests/corpus/ratox-frame/." "$work_corpus/ratox-frame/"
cp -a "$root/tests/corpus/interactive-state/." "$work_corpus/interactive-state/"
cp -a "$root/tests/corpus/interactive-service/." "$work_corpus/interactive-service/"
hex_to_binary "$work_corpus/ratox-frame/valid-input.hex" \
    "$work_corpus/ratox-frame/valid-input.bin"
rm -f -- "$work_corpus/ratox-frame/valid-input.hex"
hex_to_binary "$work_corpus/update/valid-manifest.hex" \
    "$work_corpus/update/valid-manifest.bin"
rm -f -- "$work_corpus/update/valid-manifest.hex"

run_one() {
    local executable=$1
    local corpus=$2
    local artifact_directory=$3
    local maximum_length=${4:-4096}
    printf '==> %s runs=%s corpus=%s max_len=%s\n' \
        "$(basename "$executable")" "$runs" "$corpus" "$maximum_length"
    ASAN_OPTIONS=${ASAN_OPTIONS:-detect_leaks=1:halt_on_error=1} \
    UBSAN_OPTIONS=${UBSAN_OPTIONS:-halt_on_error=1:print_stacktrace=1} \
        "$executable" \
            "$corpus" \
            -runs="$runs" \
            -max_len="$maximum_length" \
            -artifact_prefix="$artifact_directory/" \
            -print_final_stats=1
}

run_one "$build/iotox_frame_fuzzer" \
    "$work_corpus/frame" "$artifacts/frame"
run_one "$build/iotox_session_fuzzer" \
    "$work_corpus/session" "$artifacts/session"
run_one "$build/iotox_local_control_fuzzer" \
    "$work_corpus/local-control" "$artifacts/local-control"
run_one "$build/iotox_terminal_protocol_fuzzer" \
    "$work_corpus/terminal-protocol" "$artifacts/terminal-protocol" 16417
run_one "$build/iotox_command_fuzzer" \
    "$work_corpus/command" "$artifacts/command"
run_one "$build/iotox_terminal_profile_fuzzer" \
    "$work_corpus/terminal-profile" "$artifacts/terminal-profile" 65536
run_one "$build/iotox_terminal_cgroup_fuzzer" \
    "$work_corpus/terminal-cgroup" "$artifacts/terminal-cgroup" 65536
run_one "$build/iotox_update_bundle_fuzzer" \
    "$work_corpus/update" "$artifacts/update" 4096
run_one "$build/iotox_authority_fuzzer" \
    "$work_corpus/authority" "$artifacts/authority"
run_one "$build/iotox_ratox_frame_fuzzer" \
    "$work_corpus/ratox-frame" "$artifacts/ratox-frame"
run_one "$build/iotox_interactive_state_fuzzer" \
    "$work_corpus/interactive-state" "$artifacts/interactive-state"
run_one "$build/iotox_interactive_service_fuzzer" \
    "$work_corpus/interactive-service" "$artifacts/interactive-service"
