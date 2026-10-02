#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
artifacts=${IOTOX_RETAINED_ARTIFACTS_DIR:-"$root/.sandwurm/retained-artifacts"}
revision=$(tr -d '[:space:]' < "$root/REVISION")
version=$(sed -n 's/.*kVersion = "\([^"]*\)".*/\1/p' "$root/include/iotox/version.hpp")
codename=$(sed -n 's/.*kCodename = "\([^"]*\)".*/\1/p' "$root/include/iotox/version.hpp")
if command -v rg >/dev/null 2>&1; then
    registered_checks=$(
        rg -n '^IOTOX_TEST\(' "$root/tests" -g '*.cpp' | wc -l | tr -d '[:space:]'
    )
else
    registered_checks=$(
        find "$root/tests" -type f -name '*.cpp' -exec grep -h '^IOTOX_TEST(' {} + |
            wc -l | tr -d '[:space:]'
    )
fi
if [[ -z "$revision" || -z "$version" || -z "$codename" || -z "$registered_checks" ]]; then
    printf '%s\n' 'unable to derive current revision metadata for retained artifacts' >&2
    exit 2
fi

for tool in install strip; do
    command -v "$tool" >/dev/null 2>&1 || {
        printf 'retained-artifact tool is missing: %s\n' "$tool" >&2
        exit 2
    }
done

install_runtime_binary() {
    local source=$1
    local destination=$2

    install -m 0755 "$source" "$destination"
    # Retained binaries are replay conveniences rather than debug-symbol
    # archives. Preserve the loadable program and dynamic symbol surface while
    # removing non-runtime sections that otherwise duplicate build-tree bulk in
    # every repository datacube.
    strip --strip-unneeded "$destination"
}

# A revision-owned evidence directory must identify an exact committed source
# tree. Artifact refresh now writes to an ignored evidence root by default so
# bulky binaries and logs do not re-enter the public source snapshot. Source,
# documentation, build logic, and tests must already be committed.
qualified_source_commit=$(git -C "$root" rev-parse HEAD)
qualified_source_tree=$(git -C "$root" rev-parse HEAD^{tree})
if ! git -C "$root" diff --quiet -- . ':(exclude)artifacts'; then
    printf '%s\n' 'refusing artifact refresh with uncommitted tracked source outside artifacts/' >&2
    exit 2
fi
if ! git -C "$root" diff --cached --quiet -- . ':(exclude)artifacts'; then
    printf '%s\n' 'refusing artifact refresh with staged source outside artifacts/' >&2
    exit 2
fi
unexpected_untracked=$(
    git -C "$root" ls-files --others --exclude-standard |
        grep -v '^artifacts/' || true
)
if [[ -n "$unexpected_untracked" ]]; then
    printf '%s\n' 'refusing artifact refresh with untracked source outside artifacts/:' >&2
    printf '  %s\n' "$unexpected_untracked" >&2
    exit 2
fi

mkdir -p "$root/build"
exec 9>"$root/build/.artifact-refresh.lock"
if ! flock -n 9; then
    printf '%s\n' "another IoTox artifact refresh already owns $root/build/.artifact-refresh.lock" >&2
    exit 75
fi

matrix_log=${1:-/mnt/data/iotox-${revision}-final-matrix.log}
matrix_exit=${IOTOX_MATRIX_EXIT_FILE:-/mnt/data/iotox-${revision}-final-matrix.exit}
standalone_attempt_log=${IOTOX_STANDALONE_ATTEMPT_LOG:-/mnt/data/iotox-${revision}-standalone-attempt.log}
standalone_attempt_exit=${IOTOX_STANDALONE_ATTEMPT_EXIT:-/mnt/data/iotox-${revision}-standalone-attempt.exit}
standalone_binary=${IOTOX_STANDALONE_BINARY:-"$root/dist/standalone/iotox"}
standalone_verification=${IOTOX_STANDALONE_VERIFICATION:-"$root/dist/standalone/verification.txt"}
standalone_build_info=${IOTOX_STANDALONE_BUILD_INFO:-"$root/dist/standalone/build-info.txt"}
fuzzer_log=${IOTOX_FUZZ_LOG:-/mnt/data/iotox-${revision}-fuzzer-smoke-final.log}
static_analyzer_log=${IOTOX_STATIC_ANALYZER_LOG:-/mnt/data/iotox-${revision}-focused-static-analysis-final.log}
agent_stress_log=${IOTOX_AGENT_STRESS_LOG:-/mnt/data/iotox-${revision}-agent-stress-final.log}
agent_stress_exit=${IOTOX_AGENT_STRESS_EXIT:-/mnt/data/iotox-${revision}-agent-stress-final.exit}
build_root=${IOTOX_ARTIFACT_BUILD_ROOT:-"$root/build"}
allow_partial=${IOTOX_ALLOW_PARTIAL_EVIDENCE:-0}

gcc_build="$build_root/gcc-debug"
release_build="$build_root/gcc-release"
clang_fuzz="$build_root/clang-fuzz"
linked_argon2="$build_root/gcc-linked-argon2"

required=(
    "$gcc_build/iotox"
    "$gcc_build/iotox_tests"
    "$gcc_build/iotox_cli_process_tests"
    "$gcc_build/libtoxcore-iotox-mock.so"
    "$gcc_build/libargon2-iotox-mock.so"
    "$release_build/iotox"
    "$matrix_log"
)
for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
        printf 'required retained-artifact input is missing: %s\n' "$path" >&2
        exit 2
    fi
done

configured_ctest_entries() {
    local build=$1
    local file file_count count=0
    while IFS= read -r -d '' file; do
        file_count=$(awk '/^add_test\(/ {++count} END {print count + 0}' "$file")
        count=$((count + file_count))
    done < <(find "$build" -type f -name CTestTestfile.cmake -print0)
    if (( count == 0 )); then
        printf 'unable to derive configured CTest entries from %s\n' "$build" >&2
        return 2
    fi
    printf '%s\n' "$count"
}

# Do not use `ctest -N` here: CTest rewrites Testing/Temporary/LastTest.log even
# for a show-only invocation, destroying the very transcript this tool retains.
gcc_debug_ctest_entries=$(configured_ctest_entries "$gcc_build")
gcc_release_ctest_entries=$(configured_ctest_entries "$release_build")
default_ctest_entries=$gcc_debug_ctest_entries
if [[ "$gcc_release_ctest_entries" != "$default_ctest_entries" ]]; then
    printf 'debug/release CTest topology differs: %s versus %s\n' \
        "$default_ctest_entries" "$gcc_release_ctest_entries" >&2
    exit 2
fi

declare -A ctest_entries=()
declare -A ctest_starts=()
declare -A ctest_skips=()
declare -A ctest_failures=()
ctest_entries[gcc-debug]=$gcc_debug_ctest_entries
ctest_entries[gcc-release]=$gcc_release_ctest_entries
for preset in clang-debug clang-asan-ubsan gcc-tsan gcc-linked-argon2 mutorr-preservation; do
    if [[ -f "$build_root/$preset/CTestTestfile.cmake" ]]; then
        ctest_entries[$preset]=$(configured_ctest_entries "$build_root/$preset")
    else
        ctest_entries[$preset]=0
    fi
done

# The preservation configuration adds exactly the two opt-in Mutorr tests to
# the default source suite. In partial mode the directory may be absent, so
# retain the configured expectation without describing it as executed.
mutorr_ctest_entries=${ctest_entries[mutorr-preservation]}
if (( mutorr_ctest_entries == 0 )); then
    mutorr_ctest_entries=$((default_ctest_entries + 2))
fi
ctest_entries[mutorr-preservation]=$mutorr_ctest_entries

fuzz_names=(
    iotox_frame_fuzzer
    iotox_session_fuzzer
    iotox_local_control_fuzzer
    iotox_terminal_protocol_fuzzer
    iotox_command_fuzzer
    iotox_terminal_profile_fuzzer
    iotox_terminal_cgroup_fuzzer
    iotox_update_bundle_fuzzer
    iotox_authority_fuzzer
    iotox_ratox_frame_fuzzer
    iotox_interactive_state_fuzzer
    iotox_interactive_service_fuzzer
)
fuzzer_count=${#fuzz_names[@]}
full_missing=()
for name in "${fuzz_names[@]}"; do
    [[ -f "$clang_fuzz/$name" ]] || full_missing+=("$clang_fuzz/$name")
done
[[ -f "$linked_argon2/iotox" ]] || full_missing+=("$linked_argon2/iotox")
for preset in \
    gcc-debug gcc-release clang-debug clang-asan-ubsan gcc-tsan \
    gcc-linked-argon2 mutorr-preservation; do
    ctest_log="$build_root/$preset/Testing/Temporary/LastTest.log"
    if [[ ! -f "$ctest_log" ]]; then
        full_missing+=("$ctest_log")
        continue
    fi
    observed_starts=$(grep -cE '^".*" start time:' "$ctest_log" || true)
    observed_skips=$(grep -cE '^SKIP ' "$ctest_log" || true)
    observed_failures=$(grep -cF 'Test Failed.' "$ctest_log" || true)
    ctest_starts[$preset]=$observed_starts
    ctest_skips[$preset]=$observed_skips
    ctest_failures[$preset]=$observed_failures
    expected_entries=${ctest_entries[$preset]:-0}
    if [[ "$observed_starts" != "$expected_entries" ]]; then
        full_missing+=("$ctest_log records $observed_starts/$expected_entries configured test starts")
    fi
    if (( observed_skips + observed_failures > observed_starts )); then
        full_missing+=("$ctest_log has impossible outcome counts: starts=$observed_starts skips=$observed_skips failures=$observed_failures")
    fi
    if [[ "$observed_failures" != 0 ]]; then
        full_missing+=("$ctest_log records $observed_failures failed tests")
    fi
    if ! grep -Fq 'End testing:' "$ctest_log"; then
        full_missing+=("$ctest_log lacks an End testing record")
    fi
done
[[ -f "$fuzzer_log" ]] || full_missing+=("$fuzzer_log")
[[ -f "$static_analyzer_log" ]] || full_missing+=("$static_analyzer_log")
[[ -f "$agent_stress_log" ]] || full_missing+=("$agent_stress_log")
[[ -f "$agent_stress_exit" ]] || full_missing+=("$agent_stress_exit")
if [[ -f "$agent_stress_exit" ]] && [[ "$(tr -d '[:space:]' < "$agent_stress_exit")" != 0 ]]; then
    full_missing+=("$agent_stress_exit does not record zero")
fi
agent_stress_runs=0
agent_stress_unique_runs=0
agent_stress_summary_count=0
agent_stress_summary=no
agent_stress_shard_index=unknown
agent_stress_registry_checks=0
if [[ -f "$agent_stress_log" ]]; then
    agent_stress_runs=$(grep -cE '^run=[0-9]{3} PASS ' "$agent_stress_log" || true)
    agent_stress_unique_runs=$(
        awk '/^run=[0-9][0-9][0-9] PASS / {sub(/^run=/, "", $1); print $1}' \
            "$agent_stress_log" | sort -u | wc -l | tr -d '[:space:]'
    )
    agent_stress_summary_count=$(grep -cE \
        '^agent-session-stress=100/100 passed shard=[0-9]+/[0-9]+$' \
        "$agent_stress_log" || true)
    if [[ "$agent_stress_runs" != 100 ]]; then
        full_missing+=("$agent_stress_log records $agent_stress_runs/100 passing Agent repetitions")
    fi
    if [[ "$agent_stress_unique_runs" != 100 ]] || \
       ! diff -u <(seq -w 1 100) \
           <(awk '/^run=[0-9][0-9][0-9] PASS / {sub(/^run=/, "", $1); print $1}' \
               "$agent_stress_log") >/dev/null; then
        full_missing+=("$agent_stress_log does not contain the ordered run sequence 001..100 exactly once")
    fi
    canonical_stress_summary=$(tail -n 1 "$agent_stress_log")
    if [[ "$canonical_stress_summary" =~ ^agent-session-stress=100/100\ passed\ shard=([0-9]+)/([0-9]+)$ ]]; then
        agent_stress_shard_index=${BASH_REMATCH[1]}
        agent_stress_registry_checks=${BASH_REMATCH[2]}
        if [[ "$agent_stress_registry_checks" != "$registered_checks" ]]; then
            full_missing+=("$agent_stress_log registry denominator $agent_stress_registry_checks does not match $registered_checks registered checks")
        elif (( 10#$agent_stress_registry_checks == 0 || \
                10#$agent_stress_shard_index >= 10#$agent_stress_registry_checks )); then
            full_missing+=("$agent_stress_log records invalid shard $agent_stress_shard_index/$agent_stress_registry_checks")
        elif [[ "$agent_stress_summary_count" == 1 ]]; then
            agent_stress_summary=yes
        fi
    fi
    if [[ "$agent_stress_summary" != yes ]]; then
        full_missing+=("$agent_stress_log must end with exactly one canonical summary for the current registry; count=$agent_stress_summary_count")
    fi
fi

static_analyzer_targets=(
    src/terminal_profile.cpp
    src/terminal_cgroup.cpp
    src/agent.cpp
    src/cli.cpp
    src/local/runtime_tree.cpp
    src/security/identity.cpp
    src/route_worker.cpp
    src/sync_service.cpp
    src/sync_subscriber.cpp
    src/sync_transfer.cpp
    src/sync_tree.cpp
    src/update_bundle.cpp
    src/update_state.cpp
)
static_analyzer_marker="focused-static-analysis=pass files=${#static_analyzer_targets[@]} diagnostics=0"
static_analyzer_passes=0
static_analyzer_summary=no
if [[ -f "$static_analyzer_log" ]]; then
    for target in "${static_analyzer_targets[@]}"; do
        count=$(grep -Fxc "PASS focused-static-analysis $target" \
            "$static_analyzer_log" || true)
        static_analyzer_passes=$((static_analyzer_passes + count))
        if [[ "$count" != 1 ]]; then
            full_missing+=("$static_analyzer_log records $count/1 clean result for $target")
        fi
    done
    static_analyzer_summary_count=$(grep -Fxc \
        "$static_analyzer_marker" "$static_analyzer_log" || true)
    static_analyzer_failure_count=$(grep -cE \
        '(^|[[:space:]])FAIL focused-static-analysis|focused-static-analysis=fail' \
        "$static_analyzer_log" || true)
    if [[ "$static_analyzer_summary_count" == 1 && \
          "$static_analyzer_failure_count" == 0 && \
          "$(tail -n 1 "$static_analyzer_log")" == \
              "$static_analyzer_marker" ]]; then
        static_analyzer_summary=yes
    else
        full_missing+=("$static_analyzer_log lacks one terminal clean summary or contains a failure")
    fi
fi

fuzzer_target_runs=0
fuzzer_done_runs=0
if [[ -f "$fuzzer_log" ]]; then
    for name in "${fuzz_names[@]}"; do
        count=$(grep -cF "==> $name runs=5000 " "$fuzzer_log" || true)
        fuzzer_target_runs=$((fuzzer_target_runs + count))
        if [[ "$count" != 1 ]]; then
            full_missing+=("$fuzzer_log records $count/1 starts for $name")
        fi
    done
    fuzzer_done_runs=$(grep -cE '^#5000[[:space:]]+DONE([[:space:]]|$)'         "$fuzzer_log" || true)
    if [[ "$fuzzer_target_runs" != "$fuzzer_count" ]]; then
        full_missing+=("$fuzzer_log records $fuzzer_target_runs/$fuzzer_count named 5000-run fuzzer starts")
    fi
    if [[ "$fuzzer_done_runs" != "$fuzzer_count" ]]; then
        full_missing+=("$fuzzer_log records $fuzzer_done_runs/$fuzzer_count completed 5000-run fuzzers")
    fi
fi

[[ -f "$matrix_exit" ]] || full_missing+=("$matrix_exit")
if [[ -f "$matrix_exit" ]] && [[ "$(tr -d '[:space:]' < "$matrix_exit")" != 0 ]]; then
    full_missing+=("$matrix_exit does not record zero")
fi
focused_static_analysis_marker=$static_analyzer_marker
focused_static_analysis_passes=$(grep -cFx "$focused_static_analysis_marker" "$matrix_log" || true)
focused_static_analysis_failures=$(grep -cE \
    '(^|[[:space:]])FAIL focused-static-analysis|focused-static-analysis=fail' \
    "$matrix_log" || true)
focused_static_analysis_status=incomplete
if [[ "$focused_static_analysis_passes" == 1 && "$focused_static_analysis_failures" == 0 ]]; then
    focused_static_analysis_status=pass
else
    full_missing+=("$matrix_log must contain exactly one clean focused-static-analysis marker; passes=$focused_static_analysis_passes failures=$focused_static_analysis_failures")
fi
matrix_passes=$(grep -cFx 'final-source-matrix=pass' "$matrix_log" || true)
if [[ "$matrix_passes" != 1 ]]; then
    full_missing+=("$matrix_log must contain exactly one final-source-matrix=pass marker; count=$matrix_passes")
elif [[ "$(tail -n 1 "$matrix_log")" != 'final-source-matrix=pass' ]]; then
    full_missing+=("$matrix_log does not end with final-source-matrix=pass")
fi
if (( ${#full_missing[@]} != 0 )) && [[ "$allow_partial" != 1 ]]; then
    printf '%s\n' 'full retained evidence is incomplete; either finish tools/build-matrix.sh or set IOTOX_ALLOW_PARTIAL_EVIDENCE=1 and retain the limit honestly:' >&2
    printf '  %s\n' "${full_missing[@]}" >&2
    exit 2
fi


matrix_mode=full
if (( ${#full_missing[@]} != 0 )); then
    matrix_mode=partial-final-source
fi
rm -rf \
    "$artifacts/linux-x86_64-gcc14" \
    "$artifacts/linux-x86_64-clang17" \
    "$artifacts/reports" \
    "$artifacts/$revision"
mkdir -p \
    "$artifacts/linux-x86_64-gcc14/bin" \
    "$artifacts/linux-x86_64-gcc14/test" \
    "$artifacts/linux-x86_64-clang17" \
    "$artifacts/reports/ctest"

install_runtime_binary "$gcc_build/iotox" \
    "$artifacts/linux-x86_64-gcc14/bin/iotox"
install_runtime_binary "$gcc_build/iotox_tests" \
    "$artifacts/linux-x86_64-gcc14/test/iotox_tests"
install_runtime_binary "$gcc_build/iotox_cli_process_tests" \
    "$artifacts/linux-x86_64-gcc14/test/iotox_cli_process_tests"
install_runtime_binary "$gcc_build/libtoxcore-iotox-mock.so" \
    "$artifacts/linux-x86_64-gcc14/test/libtoxcore-iotox-mock.so"
install_runtime_binary "$gcc_build/libargon2-iotox-mock.so" \
    "$artifacts/linux-x86_64-gcc14/test/libargon2-iotox-mock.so"

fuzz_complete=1
for name in "${fuzz_names[@]}"; do
    [[ -f "$clang_fuzz/$name" ]] || fuzz_complete=0
done
if [[ $fuzz_complete -eq 1 ]]; then
    mkdir -p "$artifacts/linux-x86_64-clang17/fuzz"
    for name in "${fuzz_names[@]}"; do
        install_runtime_binary "$clang_fuzz/$name" \
            "$artifacts/linux-x86_64-clang17/fuzz/$name"
    done
fi

if [[ "$matrix_mode" == full ]]; then
    cp "$matrix_log" "$artifacts/reports/build-matrix.log"
    if [[ -f "$matrix_exit" ]]; then
        cp "$matrix_exit" "$artifacts/reports/build-matrix.exit"
    else
        printf '%s\n' 'not-recorded' > "$artifacts/reports/build-matrix.exit"
    fi
else
    cp "$matrix_log" "$artifacts/reports/build-matrix-attempt.log"
    if [[ -f "$matrix_exit" ]]; then
        cp "$matrix_exit" "$artifacts/reports/build-matrix-attempt.exit"
    else
        printf '%s\n' 'tool-timeout-before-wrapper-could-record-exit' > "$artifacts/reports/build-matrix-attempt.exit"
    fi
fi

for preset in gcc-debug gcc-release clang-debug clang-asan-ubsan gcc-tsan gcc-linked-argon2 mutorr-preservation; do
    source_log="$build_root/$preset/Testing/Temporary/LastTest.log"
    if [[ -f "$source_log" ]]; then
        cp "$source_log" "$artifacts/reports/ctest/$preset-LastTest.log"
    fi
done
if [[ -f "$fuzzer_log" ]]; then
    cp "$fuzzer_log" "$artifacts/reports/fuzzer-smoke.log"
fi
if [[ -f "$static_analyzer_log" ]]; then
    cp "$static_analyzer_log" "$artifacts/reports/focused-static-analysis.log"
fi
if [[ -f "$agent_stress_log" ]]; then
    cp "$agent_stress_log" "$artifacts/reports/agent-session-stress.log"
fi
if [[ -f "$agent_stress_exit" ]]; then
    cp "$agent_stress_exit" "$artifacts/reports/agent-session-stress.exit"
fi

{
    printf 'project=IoTox\n'
    printf 'revision=%s\n' "$revision"
    printf 'version=%s\n' "$version"
    printf 'codename=%s\n' "$codename"
    printf 'retained-evidence-mode=%s\n' "$matrix_mode"
    printf 'generated-america-new-york=%s\n' "$(TZ=America/New_York date -Iseconds)"
    printf 'host-kernel=%s\n' "$(uname -srmo)"
    printf 'cmake=%s\n' "$(cmake --version | head -n1)"
    printf 'ninja=%s\n' "$(ninja --version)"
    printf 'gcc=%s\n' "$(g++ --version | head -n1)"
    printf 'clang=%s\n' "$(clang++ --version | head -n1)"
    printf 'strip=%s\n' "$(strip --version | head -n1)"
    printf 'retained-runtime-binary-strip=strip--strip-unneeded\n'
    printf 'registered-cpp-checks=%s\n' "$registered_checks"
    printf 'default-ctest-entries=%s\n' "$default_ctest_entries"
    printf 'agent-session-stress-runs=%s\n' "${agent_stress_runs:-0}"
    printf 'agent-session-stress-unique-runs=%s\n' "${agent_stress_unique_runs:-0}"
    printf 'agent-session-stress-shard-index=%s\n' "${agent_stress_shard_index:-unknown}"
    printf 'agent-session-stress-registry-checks=%s\n' "${agent_stress_registry_checks:-0}"
    printf 'agent-session-stress-summary=%s\n' "${agent_stress_summary:-no}"
    printf 'fuzzer-target-starts=%s\n' "${fuzzer_target_runs:-0}"
    printf 'fuzzer-target-completions=%s\n' "${fuzzer_done_runs:-0}"
    printf 'focused-static-analysis-passes=%s\n' "${static_analyzer_passes:-0}"
    printf 'focused-static-analysis-summary=%s\n' "${static_analyzer_summary:-no}"
    printf 'focused-static-analysis=%s\n' "$focused_static_analysis_status"
    printf 'focused-static-analysis-files=%s\n' "${#static_analyzer_targets[@]}"
    printf 'focused-static-analysis-diagnostics=%s\n' \
        "$([[ "$focused_static_analysis_status" == pass ]] && echo 0 || echo unknown)"
    printf 'public-installed-executables=1\n'
    for lane in \
        gcc-debug gcc-release clang-debug clang-asan-ubsan gcc-tsan \
        gcc-linked-argon2 mutorr-preservation; do
        printf 'configured-%s-ctest-entries=%s\n' \
            "$lane" "${ctest_entries[$lane]:-0}"
        printf 'retained-%s-ctest-starts=%s\n' \
            "$lane" "${ctest_starts[$lane]:-0}"
        printf 'retained-%s-ctest-skips=%s\n' \
            "$lane" "${ctest_skips[$lane]:-0}"
        printf 'retained-%s-ctest-failures=%s\n' \
            "$lane" "${ctest_failures[$lane]:-0}"
        printf 'retained-%s-ctest-log=%s\n' "$lane" \
            "$([[ -f "$build_root/$lane/Testing/Temporary/LastTest.log" ]] && echo yes || echo no)"
    done
    printf 'fresh-clang-fuzz-artifacts=%s\n' \
        "$([[ $fuzz_complete -eq 1 ]] && echo yes || echo no)"
    "$artifacts/linux-x86_64-gcc14/bin/iotox" --version
} > "$artifacts/reports/build-info.txt"

{
    printf 'IoTox %s retained artifact file types\n' "$revision"
    find "$artifacts/linux-x86_64-gcc14" "$artifacts/linux-x86_64-clang17" \
        -type f -print0 2>/dev/null | sort -z | xargs -0 -r file
} > "$artifacts/reports/file-types.txt"

{
    printf 'IoTox %s retained artifact dynamic dependencies\n' "$revision"
    while IFS= read -r -d '' binary; do
        printf '\n== %s ==\n' "${binary#$artifacts/}"
        ldd "$binary" || true
    done < <(find "$artifacts/linux-x86_64-gcc14" "$artifacts/linux-x86_64-clang17" \
        -type f -print0 2>/dev/null | sort -z)
} > "$artifacts/reports/runtime-dependencies.txt" 2>&1

{
    printf 'IoTox %s exact mock exported dynamic symbols\n' "$revision"
    nm -D --defined-only "$artifacts/linux-x86_64-gcc14/test/libtoxcore-iotox-mock.so"
} > "$artifacts/reports/mock-exported-symbols.txt"

{
    printf 'owned-cpp-lines='
    find "$root/include" "$root/src" "$root/tests" -type f \
        \( -name '*.cpp' -o -name '*.hpp' \) -print0 | xargs -0 cat | wc -l
    printf 'owned-cpp-files='
    find "$root/include" "$root/src" "$root/tests" -type f \
        \( -name '*.cpp' -o -name '*.hpp' \) | wc -l
    printf 'registered-cpp-checks=%s\n' "$registered_checks"
    printf 'default-ctest-entries=%s\n' "$default_ctest_entries"
} > "$artifacts/reports/source-tree-counts.txt"

(
    unit_work=$(mktemp -d)
    trap 'rm -rf "$unit_work"' EXIT
    cd "$unit_work"
    "$artifacts/linux-x86_64-gcc14/test/iotox_tests" \
        --mock-toxcore "$artifacts/linux-x86_64-gcc14/test/libtoxcore-iotox-mock.so" \
        --mock-argon2 "$artifacts/linux-x86_64-gcc14/test/libargon2-iotox-mock.so" \
        --wordlist "$root/third_party/eff_large_wordlist_2016-07-18.txt"
) > "$artifacts/reports/unit-tests-detail.log" 2>&1
[[ ! -e "$root/device.identity" && ! -e "$root/commands.store" && ! -e "$root/authority.ledger" ]]

"$artifacts/linux-x86_64-gcc14/test/iotox_cli_process_tests" \
    "$artifacts/linux-x86_64-gcc14/bin/iotox" \
    "$artifacts/linux-x86_64-gcc14/test/libtoxcore-iotox-mock.so" \
    > "$artifacts/reports/binary-process-lifecycle.log" 2>&1

IOTOX_SKIP_BUILD=1 IOTOX_BUILD_DIR="$gcc_build" \
    "$root/tools/run-mock-node.sh" gcc-debug \
    > "$artifacts/reports/mock-node-lifecycle.log" 2>&1

install_root=$(mktemp -d)
trap 'rm -rf "$install_root"' EXIT
cmake --install "$release_build" --prefix "$install_root" \
    > "$artifacts/reports/install-surface.log" 2>&1
{
    printf '\ninstalled-files:\n'
    find "$install_root" -type f -printf '%P\n' | sort
    printf '\ninstalled-executables:\n'
    find "$install_root/bin" -maxdepth 1 -type f -perm -u+x -printf '%f\n' | sort
} >> "$artifacts/reports/install-surface.log"

standalone_exit_value=not-recorded
if [[ -f "$standalone_attempt_exit" ]]; then
    standalone_exit_value=$(tr -d '[:space:]' < "$standalone_attempt_exit")
fi
standalone_success=0
standalone_sha256=not-recorded
if [[ "$standalone_exit_value" == 0 && -x "$standalone_binary" && \
      -f "$standalone_verification" && -f "$standalone_build_info" ]] && \
   grep -Fqx 'standalone-linked-toxcore-libsodium-argon2=pass' \
       "$standalone_verification" && \
   grep -Fqx "revision=$revision" "$standalone_build_info"; then
    standalone_success=1
    standalone_sha256=$(sha256sum "$standalone_binary" | awk '{print $1}')
fi
{
    if [[ $standalone_success -eq 1 ]]; then
        printf 'official-source-linked-c-toxcore=yes\n'
        printf 'official-source-linked-libsodium=yes\n'
        printf 'official-source-linked-argon2=yes\n'
        printf 'fully-source-linked-one-binary=yes\n'
        printf 'standalone-verification=pass\n'
        printf 'standalone-attempt-result=verified-source-linked-build\n'
        printf 'standalone-binary-sha256=%s\n' "$standalone_sha256"
    else
        printf 'official-source-linked-c-toxcore=not-verified\n'
        printf 'official-source-linked-libsodium=not-verified\n'
        printf 'official-source-linked-argon2=not-verified\n'
        printf 'fully-source-linked-one-binary=not-verified\n'
        printf 'standalone-verification=not-verified\n'
        printf 'standalone-attempt-result=not-verified; inspect retained attempt log\n'
        printf 'standalone-binary-sha256=not-recorded\n'
    fi
    printf 'genuine-tox-peer=not-executed\n'
    printf 'standalone-attempt-date-america-new-york=%s\n' \
        "$(TZ=America/New_York date +%Y-%m-%d)"
    printf 'standalone-attempt-exit=%s\n' "$standalone_exit_value"
    printf '%s\n' \
        'boundary=source linkage and local binary verification do not establish public-network operation, two-peer interoperability, portability, or production hardening'
    printf '%s\n' \
        'next=run two genuine pinned c-toxcore peers and drive Ratox OPEN, ATTACH, INPUT, replay, revocation, DETACH, CLOSE, and EXIT through real callbacks under loss, reconnect, and process failure'
} > "$artifacts/reports/real-toxcore-status.txt"

if [[ -f "$standalone_attempt_log" ]]; then
    cp "$standalone_attempt_log" "$artifacts/reports/standalone-attempt.log"
else
    printf '%s\n' 'No standalone attempt log was supplied.' > "$artifacts/reports/standalone-attempt.log"
fi
if [[ -f "$standalone_attempt_exit" ]]; then
    cp "$standalone_attempt_exit" "$artifacts/reports/standalone-attempt.exit"
else
    printf '%s\n' 'not-recorded' > "$artifacts/reports/standalone-attempt.exit"
fi

cat > "$artifacts/reports/external-sources.txt" <<SOURCES
Primary sources reviewed for ${revision}:
https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
https://github.com/TokTok/c-toxcore/security/advisories/GHSA-42vg-9mg3-399f
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://toktok.ltd/spec.html
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox_options.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.c
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.c
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://raw.githubusercontent.com/pranomostro/ratox/master/README
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.1
https://raw.githubusercontent.com/JFreegman/toxic/master/src/file_transfers.c
https://git.2f30.org/ratox/commit/99b652c0c07c6acf81b6a8cf36a107be76fbe98d.html
https://man7.org/linux/man-pages/man7/fifo.7.html
https://man7.org/linux/man-pages/man7/pipe.7.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
https://pubs.opengroup.org/onlinepubs/9699919799/functions/fpathconf.html
https://github.com/jedisct1/libsodium/releases/tag/1.0.22-RELEASE
https://github.com/P-H-C/phc-winner-argon2/releases/tag/20190702
https://www.rfc-editor.org/rfc/rfc9106.html
https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt
https://docs.kernel.org/admin-guide/cgroup-v2.html
https://docs.kernel.org/accounting/psi.html
https://github.com/torvalds/linux/blob/master/kernel/sched/psi.c
https://clang.llvm.org/docs/analyzer/user-docs/CommandLineUsage.html
https://clang.llvm.org/docs/analyzer/user-docs/Options.html
https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html
https://systemd.io/CGROUP_DELEGATION/
https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html
SOURCES

cat > "$artifacts/README.md" <<'README'
# Prebuilt @REVISION@ one-binary ratox-successor evidence

These Linux x86-64 convenience artifacts accompany **IoTox @REVISION@ — @CODENAME@**. They are
retained execution evidence and an offline smoke path, not a portable or production release. The
source tree remains authoritative.

## Current retained binaries

```text
linux-x86_64-gcc14/bin/iotox
linux-x86_64-gcc14/test/iotox_tests
linux-x86_64-gcc14/test/iotox_cli_process_tests
linux-x86_64-gcc14/test/libtoxcore-iotox-mock.so
linux-x86_64-gcc14/test/libargon2-iotox-mock.so
linux-x86_64-clang17/fuzz/iotox_frame_fuzzer
linux-x86_64-clang17/fuzz/iotox_session_fuzzer
linux-x86_64-clang17/fuzz/iotox_local_control_fuzzer
linux-x86_64-clang17/fuzz/iotox_terminal_protocol_fuzzer
linux-x86_64-clang17/fuzz/iotox_command_fuzzer
linux-x86_64-clang17/fuzz/iotox_terminal_profile_fuzzer
linux-x86_64-clang17/fuzz/iotox_terminal_cgroup_fuzzer
linux-x86_64-clang17/fuzz/iotox_authority_fuzzer
linux-x86_64-clang17/fuzz/iotox_ratox_frame_fuzzer
linux-x86_64-clang17/fuzz/iotox_interactive_state_fuzzer
linux-x86_64-clang17/fuzz/iotox_interactive_service_fuzzer
```

There is one public product executable: `iotox`. Test runners, exact provider doubles, and fuzzers
exist only to reproduce retained evidence. The artifact refresh copies each executable or shared
object and applies `strip --strip-unneeded` to that copy. Runtime loadable content and dynamic symbols
remain, while non-runtime debug and static-symbol bulk is intentionally not retained. The qualified
build trees and full source remain the debugging authority; these bounded copies are replay evidence.

The source tree configures the following evidence lanes. Execution outcomes are stated only in
`reports/validation-summary.txt`; the list below is topology, not a green claim:

```text
GCC 14 debug                         @GCC_DEBUG_CTEST_ENTRIES@ configured CTest entries
GCC 14 release                       @GCC_RELEASE_CTEST_ENTRIES@ configured CTest entries
Clang 17 debug                       @CLANG_DEBUG_CTEST_ENTRIES@ configured CTest entries
Clang path-sensitive static analysis 9 critical translation units
Clang 17 ASan + UBSan                @CLANG_ASAN_CTEST_ENTRIES@ configured CTest entries
GCC 14 ThreadSanitizer               @GCC_TSAN_CTEST_ENTRIES@ configured CTest entries
host-linked Argon2                   @LINKED_ARGON2_CTEST_ENTRIES@ configured CTest entries
Mutorr preservation                 @MUTORR_CTEST_ENTRIES@ configured CTest entries
Clang libFuzzer                      @FUZZER_TARGETS@ configured targets
exclusive Agent/session stress       100-run evidence gate
registered direct C++ checks         @REGISTERED_CHECKS@ configured checks
```

Exact retained results live in `reports/validation-summary.txt`. This prose cannot broaden them.

## Ratox-successor surface exercised

The separate-process fixture and exact c-toxcore ABI peer drive one `iotox` daemon through:

```text
friend request
    exact root request FIFO using a complete 38-byte Tox address
    outgoing request by structured local control
    live public-key request projection
    exact accept and reject FIFO decisions
    established peer removal bound to public key
    independent authority ledger remains unchanged

human text
    private per-peer message and action FIFOs
    exact byte framing and typed failure
    local send acceptance, incoming echo, and read receipt
    no hidden retry, durability, or machine authority

machine command
    private per-peer command FIFO
    signed durable device.describe before transport
    exact retry across injected toxcore SENDQ
    application receipt/result and stop/restart continuity

finite file
    private file-send, file-receive, and file-control FIFOs
    paused incoming offer and safe local destination admission
    exact chunk bytes and no-clobber publication
    independent local/peer pause truth and terminal convergence
```

FIFO write success is kernel evidence only. Bounded journals and live projections expose later local
semantics; Tox callbacks expose transport evidence; durable command records and published files
expose stronger state. Tox friendship never grants IoTox ownership, roles, capabilities, firmware
authority, or physical-effect authority.

From `.datacube/`:

```sh
./artifacts/run-prebuilt-tests.sh
```

## Evidence boundary

The exact toxcore mock validates the consumed C ABI and deterministic IoTox lifecycle/protocol
behavior. It does not implement Tox cryptography, DHT, NAT traversal, public bootstrap, real relays,
congestion, or hostile-network timing. The current source-linked standalone outcome and its exact
SHA-256 identity are recorded in `reports/real-toxcore-status.txt`; that local linkage evidence does
not establish a genuine two-peer or public-network Ratox session, portability, or production
hardening.

The permanent eight-word RecallRoot is intentionally reconstructible; offline guessing is possible
by contract, so generated phrase strength is structural. IoTox has no vendor reassignment key. The
signed authority and command stores are currently plaintext and rollbackable by restoring an older
valid snapshot.

Earlier revision evidence remains under `history/`; it cannot override or broaden a current-source
claim.

## Checksums

`SHA256SUMS` covers the retained artifact set except itself and the two reports produced while
checking or running that set:

```text
reports/checksum-verification.log
reports/prebuilt-smoke.log
```

Verify from the artifact directory:

```sh
cd .datacube/artifacts
sha256sum -c SHA256SUMS
```
README
sed -i \
    -e "s|@REVISION@|$revision|g" \
    -e "s|@CODENAME@|$codename|g" \
    -e "s|@REGISTERED_CHECKS@|$registered_checks|g" \
    -e "s|@GCC_DEBUG_CTEST_ENTRIES@|${ctest_entries[gcc-debug]}|g" \
    -e "s|@GCC_RELEASE_CTEST_ENTRIES@|${ctest_entries[gcc-release]}|g" \
    -e "s|@CLANG_DEBUG_CTEST_ENTRIES@|${ctest_entries[clang-debug]}|g" \
    -e "s|@CLANG_ASAN_CTEST_ENTRIES@|${ctest_entries[clang-asan-ubsan]}|g" \
    -e "s|@GCC_TSAN_CTEST_ENTRIES@|${ctest_entries[gcc-tsan]}|g" \
    -e "s|@LINKED_ARGON2_CTEST_ENTRIES@|${ctest_entries[gcc-linked-argon2]}|g" \
    -e "s|@MUTORR_CTEST_ENTRIES@|$mutorr_ctest_entries|g" \
    -e "s|@FUZZER_TARGETS@|$fuzzer_count|g" \
    "$artifacts/README.md"

cat > "$artifacts/run-prebuilt-tests.sh" <<'RUNNER'
#!/usr/bin/env bash
set -euo pipefail

artifact_root=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
repository_root=${IOTOX_REPOSITORY_ROOT:-"$(cd "$artifact_root/.." && pwd)"}
platform="$artifact_root/linux-x86_64-gcc14"
bin="$platform/bin/iotox"
test_dir="$platform/test"
unit_tests="$test_dir/iotox_tests"
process_tests="$test_dir/iotox_cli_process_tests"
mock_toxcore="$test_dir/libtoxcore-iotox-mock.so"
mock_argon2="$test_dir/libargon2-iotox-mock.so"
wordlist=${IOTOX_RECALL_WORDLIST:-"$repository_root/third_party/eff_large_wordlist_2016-07-18.txt"}
build_info="$artifact_root/reports/build-info.txt"
checksums="$artifact_root/SHA256SUMS"

required=(
    "$bin"
    "$unit_tests"
    "$process_tests"
    "$mock_toxcore"
    "$mock_argon2"
    "$wordlist"
    "$build_info"
    "$checksums"
)
for path in "${required[@]}"; do
    if [[ ! -f "$path" ]]; then
        printf 'prebuilt test input is missing: %s\n' "$path" >&2
        exit 2
    fi
done
for path in "$bin" "$unit_tests" "$process_tests"; do
    if [[ ! -x "$path" ]]; then
        printf 'prebuilt test executable is not executable: %s\n' "$path" >&2
        exit 2
    fi
done

revision=$(sed -n 's/^revision=//p' "$build_info")
registered_checks=$(sed -n 's/^registered-cpp-checks=//p' "$build_info")
if [[ ! "$revision" =~ ^rev[0-9]{4}$ ]] ||
   [[ ! "$registered_checks" =~ ^[1-9][0-9]*$ ]]; then
    printf '%s\n' 'retained build metadata is malformed' >&2
    exit 2
fi

# Authenticate every retained input before executing any of it. The checksum
# file deliberately excludes only itself and the two reports written by the
# checksum/smoke invocations.
(
    cd "$artifact_root"
    sha256sum -c SHA256SUMS
)

work=$(mktemp -d "${TMPDIR:-/tmp}/iotox-prebuilt.XXXXXX")
cleanup() {
    rm -rf "$work"
}
trap cleanup EXIT INT TERM HUP
chmod 0700 "$work"

export IOTOX_ARGON2_LIBRARY="$mock_argon2"
version_output=$(
    cd "$work"
    "$bin" --version
)
if [[ "$version_output" != *"$revision"* ]]; then
    printf 'prebuilt revision mismatch: expected %s, got %s\n' \
        "$revision" "$version_output" >&2
    exit 1
fi
printf '%s\n' "$version_output"

(
    cd "$work"
    "$unit_tests" \
        --mock-toxcore "$mock_toxcore" \
        --mock-argon2 "$mock_argon2" \
        --wordlist "$wordlist"
) | tee "$work/unit-tests.log"
expected_summary="tests=$registered_checks selected=$registered_checks shard=0/1 failures=0"
if [[ "$(tail -n 1 "$work/unit-tests.log")" != "$expected_summary" ]]; then
    printf 'prebuilt unit registry summary mismatch: expected %s\n' \
        "$expected_summary" >&2
    exit 1
fi

(
    cd "$work"
    "$process_tests" "$bin" "$mock_toxcore"
) | tee "$work/process-tests.log"

for forbidden in device.identity commands.store authority.ledger; do
    if [[ -e "$repository_root/$forbidden" ]]; then
        printf 'prebuilt test leaked state into repository root: %s\n' \
            "$forbidden" >&2
        exit 1
    fi
done

printf 'prebuilt-tests=pass revision=%s registered-checks=%s\n' \
    "$revision" "$registered_checks"
RUNNER
chmod 0755 "$artifacts/run-prebuilt-tests.sh"

print_ctest_summary() {
    local lane=$1
    local entries=${ctest_entries[$lane]:-0}
    local starts=${ctest_starts[$lane]:-0}
    local skips=${ctest_skips[$lane]:-0}
    local failures=${ctest_failures[$lane]:-0}
    local passes=$((starts - skips - failures))
    local log="$build_root/$lane/Testing/Temporary/LastTest.log"
    if [[ "$matrix_mode" == full ]]; then
        printf '%s=%s/%s CTest entries completed; passed=%s; capability-skipped=%s; failed=%s\n' \
            "$lane" "$starts" "$entries" "$passes" "$skips" "$failures"
    elif [[ -s "$log" ]]; then
        printf '%s=attempt-log-retained; configured-entries=%s; outcome=inspect-log\n' \
            "$lane" "$entries"
    else
        printf '%s=not-retained; configured-entries=%s\n' "$lane" "$entries"
    fi
}

{
    printf 'final-source-validation-summary\n'
    for lane in \
        gcc-debug gcc-release clang-debug clang-asan-ubsan gcc-tsan \
        gcc-linked-argon2 mutorr-preservation; do
        print_ctest_summary "$lane"
    done
    if [[ "$focused_static_analysis_status" == pass && \
          "${static_analyzer_passes:-0}" == \
              "${#static_analyzer_targets[@]}" && \
          "${static_analyzer_summary:-no}" == yes ]]; then
        printf 'focused-static-analysis=%s/%s critical translation units; matrix-marker=pass; retained-log=pass; diagnostics=0\n' \
            "$static_analyzer_passes" "${#static_analyzer_targets[@]}"
    else
        printf 'focused-static-analysis=incomplete; matrix-marker=%s; retained-log-passes=%s/%s; retained-log-summary=%s\n' \
            "$focused_static_analysis_status" "${static_analyzer_passes:-0}" \
            "${#static_analyzer_targets[@]}" "${static_analyzer_summary:-no}"
    fi
    if [[ "$fuzzer_target_runs" == "$fuzzer_count" && \
          "$fuzzer_done_runs" == "$fuzzer_count" ]]; then
        printf 'clang-libfuzzer=%s/%s targets completed 5000 units\n' \
            "$fuzzer_count" "$fuzzer_count"
    else
        printf 'clang-libfuzzer=%s/%s starts; %s/%s completions; outcome=incomplete\n' \
            "$fuzzer_target_runs" "$fuzzer_count" \
            "$fuzzer_done_runs" "$fuzzer_count"
    fi
    printf 'registered-cpp-checks=%s passed in retained direct run\n' "$registered_checks"
    printf 'literal-fifo-process-lifecycle=passed\n'
    printf 'one-binary-mock-node-lifecycle=passed\n'
    if [[ "${agent_stress_runs:-0}" == 100 && \
          "${agent_stress_unique_runs:-0}" == 100 && \
          "${agent_stress_summary:-no}" == yes ]]; then
        printf 'agent-session-stress=100/100 unique runs passed\n'
    else
        printf 'agent-session-stress=%s/100 lines; %s/100 unique; summary=%s\n' \
            "${agent_stress_runs:-0}" "${agent_stress_unique_runs:-0}" \
            "${agent_stress_summary:-no}"
    fi
    if [[ "$matrix_mode" == full ]]; then
        printf 'full-matrix=complete\n'
    else
        printf '%s\n' \
            'full-matrix=incomplete; inspect retained attempt and missing-evidence diagnostics'
        printf 'policy=no absent lane is described as green\n'
    fi
} > "$artifacts/reports/validation-summary.txt"

write_current_checksums() {
    (
        cd "$artifacts"
        find . -type f \
            ! -path './SHA256SUMS' \
            ! -path './reports/checksum-verification.log' \
            ! -path './reports/prebuilt-smoke.log' \
            -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS
        sha256sum -c SHA256SUMS > reports/checksum-verification.log
    )
}

# Authenticate the executable/current-report surface before running any retained
# binary. The prebuilt smoke transcript is deliberately excluded because the
# runner produces it only after this verification succeeds.
write_current_checksums
"$artifacts/run-prebuilt-tests.sh" > "$artifacts/reports/prebuilt-smoke.log" 2>&1

# Freeze a compact revision-owned evidence set after the prebuilt smoke passes.
# Keep executables only in the current platform directories: the revision
# directory is an immutable transcript/index layer, not a second binary payload.
revision_artifacts="$artifacts/$revision"
mkdir -p "$revision_artifacts"
cat > "$revision_artifacts/SOURCE_IDENTITY.txt" <<SOURCE_IDENTITY
project=IoTox
revision=$revision
version=$version
codename=$codename
source_commit=$qualified_source_commit
source_tree=$qualified_source_tree
retained_evidence_mode=$matrix_mode
SOURCE_IDENTITY
cat > "$revision_artifacts/README.txt" <<REVISION_README
This directory was generated by tools/refresh-retained-artifacts.sh for IoTox $revision
(version $version, codename "$codename") from exact committed source:

commit $qualified_source_commit
tree   $qualified_source_tree

It is a compact transcript and index layer. The authoritative execution outcomes are in
validation-summary.txt; configured topology in prose is not a pass claim, and a capability-skipped
route is never represented as positive enforcement. The retained evidence mode for this snapshot is
$matrix_mode.

The checksummed current executable, test, and fuzzer surfaces remain under artifacts/linux-x86_64-*
with artifacts/run-prebuilt-tests.sh. This revision directory intentionally duplicates reports, not
binary payloads, so a later repository handoff can retain exact evidence without multiplying large
executables.
REVISION_README

while IFS= read -r -d '' report; do
    relative=${report#"$artifacts/reports/"}
    destination="$revision_artifacts/$relative"
    mkdir -p "$(dirname "$destination")"
    cp "$report" "$destination"
done < <(find "$artifacts/reports" -type f \
    ! -path "$artifacts/reports/checksum-verification.log" -print0)

(
    cd "$revision_artifacts"
    find . -type f ! -path './SHA256SUMS' -print0 | \
        sort -z | xargs -0 sha256sum > SHA256SUMS
    sha256sum -c SHA256SUMS >/dev/null
)

# The revision snapshot was created after the first authenticated execution, so
# bind it into the final current-artifact checksum index and verify the complete
# delivered set once more.
write_current_checksums
printf 'retained-artifacts=refreshed mode=%s\n' "$matrix_mode"
