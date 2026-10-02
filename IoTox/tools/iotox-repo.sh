#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

die() {
    printf 'iotox-repo: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage:
  tools/iotox-repo.sh help
  tools/iotox-repo.sh doctor
  tools/iotox-repo.sh build
  tools/iotox-repo.sh test quick
  tools/iotox-repo.sh test full [CMAKE_PRESET]
  tools/iotox-repo.sh sync-recovery-drill [drill options] BACKUP_ROOT RESTORED_ROOT
  tools/iotox-repo.sh sync-loopback-custody-drill [loopback drill options]
  tools/iotox-repo.sh sync-dishonest-storage-drill [drill options]
  tools/iotox-repo.sh sync-dishonest-storage-matrix [matrix options]
  tools/iotox-repo.sh sync-log-writes-prefix-replay [prefix options]
  tools/iotox-repo.sh sync-production-prefix-replay [prefix options]
  tools/iotox-repo.sh sync-backup-custody-verify RECEIPT_OR_RUN_DIR
  tools/iotox-repo.sh sync-precious-data-gates-plan [plan options]
  tools/iotox-repo.sh storage-readiness [readiness options]
  tools/iotox-repo.sh current-sync-long-soak-receipt --out PATH
  tools/iotox-repo.sh witness-custody [drill options] SERVICE_ROOT CHECKPOINT SERVICE_PUBLIC_KEY_HEX
  tools/iotox-repo.sh stable-evidence-plan
  tools/iotox-repo.sh current-stable-evidence
  tools/iotox-repo.sh release-plan [founder-preview|stable]
  tools/iotox-repo.sh release-check [founder-preview|stable] [--iotox PATH] [--evidence-manifest PATH] [--allow-dirty]
  tools/iotox-repo.sh datacube [--seed|--public|--conversation|--upload] [datacube options] [OUTPUT_DIRECTORY]
  tools/iotox-repo.sh clean [clean-workspace options]

Safe repository companion for IoTox. This script is intentionally small:
it guides and launches existing build/test/evidence/datacube/cleanup tools, but
it does not create device authority, sync namespaces, terminal profiles, sudo
policy, or host services.
EOF
}

have() {
    command -v "$1" >/dev/null 2>&1
}

print_cmd() {
    printf '  '
    printf '%q ' "$@"
    printf '\n'
}

shell_command() {
    local rendered=''
    local token
    local quoted
    for token in "$@"; do
        printf -v quoted '%q' "$token"
        rendered+="${rendered:+ }$quoted"
    done
    printf '%s' "$rendered"
}

default_sodium_library() {
    if [[ -n "${IOTOX_SODIUM_LIBRARY:-}" && -f "${IOTOX_SODIUM_LIBRARY:-}" ]]; then
        printf '%s' "$IOTOX_SODIUM_LIBRARY"
        return 0
    fi
    local candidate
    for candidate in \
        /nix/store/*-libsodium-*/lib/libsodium.so.* \
        /nix/store/*-libsodium-*/lib/libsodium.so \
        /run/current-system/sw/lib/libsodium.so.* \
        /run/current-system/sw/lib/libsodium.so; do
        if [[ -f "$candidate" ]]; then
            printf '%s' "$candidate"
            return 0
        fi
    done
    return 0
}

ensure_iotox_provider_env() {
    if [[ -z "${IOTOX_SODIUM_LIBRARY:-}" ]]; then
        local sodium
        sodium=$(default_sodium_library)
        if [[ -n "$sodium" ]]; then
            export IOTOX_SODIUM_LIBRARY="$sodium"
        fi
    fi
}

iotox_shell_command() {
    local iotox=$1
    shift
    local sodium
    sodium=$(default_sodium_library)
    if [[ -n "$sodium" ]]; then
        shell_command env "IOTOX_SODIUM_LIBRARY=$sodium" "$iotox" "$@"
    else
        shell_command "$iotox" "$@"
    fi
}

exec_cmd() {
    printf 'iotox-repo: executing\n'
    print_cmd "$@"
    exec "$@"
}

run_cmd() {
    printf 'iotox-repo: executing\n'
    print_cmd "$@"
    "$@"
}

show_tool() {
    local name=$1
    if have "$name"; then
        printf '%-18s %s\n' "$name" "$(command -v "$name")"
    else
        printf '%-18s missing\n' "$name"
    fi
}

cmd_doctor() {
    cd "$root"
    printf 'root              %s\n' "$root"
    if [[ -f REVISION ]]; then
        printf 'revision          %s\n' "$(tr -d '\n' < REVISION)"
    fi
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        printf 'git-commit        %s\n' "$(git rev-parse --short=12 HEAD)"
        printf 'git-branch        %s\n' "$(git symbolic-ref --short -q HEAD || printf detached)"
        local dirty
        dirty=$(git status --porcelain=v1 --untracked-files=all | wc -l | tr -d ' ')
        printf 'git-dirty-lines   %s\n' "$dirty"
    else
        printf 'git               not-a-worktree\n'
    fi

    printf '\nrequired tools\n'
    show_tool bash
    show_tool git
    show_tool nix
    show_tool cmake
    show_tool ctest
    show_tool g++
    show_tool ninja
    show_tool python3
    show_tool zip
    show_tool unzip

    printf '\nlocal evidence helpers\n'
    [[ -x tools/make-repository-datacube.sh ]] &&
        printf '%-18s present\n' datacube ||
        printf '%-18s missing\n' datacube
    [[ -f tools/clean-workspace.py ]] &&
        printf '%-18s present\n' clean-workspace ||
        printf '%-18s missing\n' clean-workspace
    [[ -x build/iotox ]] &&
        printf '%-18s %s\n' built-iotox "$(build/iotox --version 2>/dev/null | head -n 1)" ||
        printf '%-18s not-built\n' built-iotox

    printf '\nnearby labs\n'
    local sandwurm_root=${IOTOX_SANDWURM_ROOT:-"$root/../sandwurm"}
    local monsternix_root=${IOTOX_MONSTERNIX_ROOT:-"$root/../monsternix"}
    [[ -d "$sandwurm_root" ]] &&
        printf '%-18s %s\n' sandwurm "$(cd "$sandwurm_root" && pwd -P)" ||
        printf '%-18s missing\n' sandwurm
    [[ -d "$monsternix_root" ]] &&
        printf '%-18s %s\n' monsternix "$(cd "$monsternix_root" && pwd -P)" ||
        printf '%-18s missing\n' monsternix
}

cmd_build() {
    cd "$root"
    have nix || die "nix is required for build"
    exec_cmd nix build .#iotox-source-linked
}

cmd_test_quick() {
    cd "$root"
    if have g++; then
        have cmake || die "cmake is required for quick test"
        have ctest || die "ctest is required for quick test"
        printf 'iotox-repo: executing quick gcc-debug build/test gate\n'
        run_cmd cmake --preset gcc-debug
        run_cmd cmake --build --preset gcc-debug --parallel --target iotox iotox_tests
        run_cmd ctest --preset gcc-debug -R '^(iotox.unit-and-integration|iotox.client-help)$'
    elif have nix; then
        exec_cmd nix develop --command bash -lc \
            'cmake --preset gcc-debug && cmake --build --preset gcc-debug --parallel --target iotox iotox_tests && ctest --preset gcc-debug -R "^(iotox.unit-and-integration|iotox.client-help)$"'
    else
        die "quick test requires g++/cmake/ctest or nix develop"
    fi
}

cmd_test_full() {
    local preset=${1:-gcc-debug}
    cd "$root"
    [[ -x tools/test.sh ]] || die "tools/test.sh is missing or not executable"
    if have g++; then
        exec_cmd tools/test.sh "$preset"
    elif have nix; then
        exec_cmd nix develop --command tools/test.sh "$preset"
    else
        die "full test requires g++/cmake/ctest or nix develop"
    fi
}

cmd_datacube() {
    cd "$root"
    [[ -x tools/make-repository-datacube.sh ]] ||
        die "tools/make-repository-datacube.sh is missing or not executable"
    exec_cmd tools/make-repository-datacube.sh "$@"
}

cmd_clean() {
    cd "$root"
    [[ -f tools/clean-workspace.py ]] || die "tools/clean-workspace.py is missing"
    exec_cmd python3 tools/clean-workspace.py "$@"
}

cmd_sync_recovery_drill() {
    cd "$root"
    [[ -f tools/run-sync-retained-recovery-drill.py ]] ||
        die "tools/run-sync-retained-recovery-drill.py is missing"
    exec_cmd python3 tools/run-sync-retained-recovery-drill.py "$@"
}

cmd_sync_loopback_custody_drill() {
    cd "$root"
    [[ -f tools/run-sync-loopback-custody-drill.py ]] ||
        die "tools/run-sync-loopback-custody-drill.py is missing"
    exec_cmd python3 tools/run-sync-loopback-custody-drill.py "$@"
}

cmd_sync_dishonest_storage_drill() {
    cd "$root"
    [[ -f tools/run-sync-dishonest-storage-drill.py ]] ||
        die "tools/run-sync-dishonest-storage-drill.py is missing"
    exec_cmd python3 tools/run-sync-dishonest-storage-drill.py "$@"
}

cmd_sync_dishonest_storage_matrix() {
    cd "$root"
    [[ -f tools/run-sync-dishonest-storage-matrix.py ]] ||
        die "tools/run-sync-dishonest-storage-matrix.py is missing"
    exec_cmd python3 tools/run-sync-dishonest-storage-matrix.py "$@"
}

cmd_sync_log_writes_prefix_replay() {
    cd "$root"
    [[ -f tools/run-sync-log-writes-prefix-replay.py ]] ||
        die "tools/run-sync-log-writes-prefix-replay.py is missing"
    exec_cmd python3 tools/run-sync-log-writes-prefix-replay.py "$@"
}

cmd_sync_production_prefix_replay() {
    cd "$root"
    [[ -f tools/run-sync-production-prefix-replay.py ]] ||
        die "tools/run-sync-production-prefix-replay.py is missing"
    if [[ -z "${IN_NIX_SHELL:-}" ]] && have nix; then
        exec_cmd nix develop --command python3 tools/run-sync-production-prefix-replay.py "$@"
    fi
    exec_cmd python3 tools/run-sync-production-prefix-replay.py "$@"
}

cmd_storage_readiness() {
    cd "$root"
    [[ -f tools/qualify-storage-readiness.py ]] ||
        die "tools/qualify-storage-readiness.py is missing"
    exec_cmd python3 tools/qualify-storage-readiness.py "$@"
}

cmd_sync_backup_custody_verify() {
    cd "$root"
    [[ -f tools/verify-sync-backup-custody.py ]] ||
        die "tools/verify-sync-backup-custody.py is missing"
    exec_cmd python3 tools/verify-sync-backup-custody.py "$@"
}

cmd_sync_precious_data_gates_plan() {
    cd "$root"
    [[ -f tools/plan-sync-precious-data-gates.py ]] ||
        die "tools/plan-sync-precious-data-gates.py is missing"
    exec python3 tools/plan-sync-precious-data-gates.py "$@"
}

cmd_witness_custody() {
    cd "$root"
    [[ -f tools/run-witness-checkpoint-custody-drill.py ]] ||
        die "tools/run-witness-checkpoint-custody-drill.py is missing"
    exec_cmd python3 tools/run-witness-checkpoint-custody-drill.py "$@"
}

cmd_current_sync_long_soak_receipt() {
    [[ $# -eq 2 && "${1:-}" == "--out" ]] ||
        die "current-sync-long-soak-receipt requires --out PATH"
    local output=$2
    case "$output" in
        /*) ;;
        *) die "current-sync-long-soak-receipt --out must be absolute" ;;
    esac
    cd "$root"
    local proof=".sandwurm/exports/three-writer/run.2nPKtCoX"
    [[ -d "$proof" ]] ||
        die "current accepted sync long-soak proof is missing: $proof"
    [[ -f tools/verify-sync-three-writer-sandwurm.py ]] ||
        die "tools/verify-sync-three-writer-sandwurm.py is missing"
    local output_dir
    output_dir=$(dirname "$output")
    mkdir -p "$output_dir"
    local output_base
    output_base=$(basename "$output")
    local temporary
    temporary=$(mktemp -p "$output_dir" ".${output_base}.part.XXXXXXXX")
    if ! python3 tools/verify-sync-three-writer-sandwurm.py "$proof" >"$temporary"; then
        rm -f "$temporary"
        die "current sync long-soak verifier failed"
    fi
    chmod 600 "$temporary"
    mv -f "$temporary" "$output"
    local digest
    digest=$(python3 - "$output" <<'PY'
import hashlib
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
digest = hashlib.sha256()
with path.open("rb") as source:
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        digest.update(chunk)
print(digest.hexdigest())
PY
)
    cat <<EOF
iotox-current-sync-long-soak-receipt-v1
proof=$proof
receipt=$output
receipt-sha256=$digest
stable-evidence-key=sync.long-soak
mutated=1
EOF
}

cmd_stable_evidence_plan() {
    [[ $# -eq 0 ]] || die "stable-evidence-plan takes no arguments"
    cd "$root"
    cat <<'EOF'
iotox-stable-evidence-plan-v1
schema-line=schema=iotox.stable-evidence.v1
precious-data-gates-plan-command=tools/iotox-repo.sh sync-precious-data-gates-plan --dataset PATH --write-templates PATH
storage-readiness-command=tools/iotox-repo.sh storage-readiness --backup-custody-proof PATH
sync-long-soak-command=tools/iotox-sandwurm-lab.sh up-three-writer soak-24h
current-sync-long-soak-proof=.sandwurm/exports/three-writer/run.2nPKtCoX
current-sync-long-soak-receipt-command=tools/iotox-repo.sh current-sync-long-soak-receipt --out /PROOF/long-soak.json
current-sync-long-soak-verifier-receipt-sha256=6e88a2efcf33b268ff82cf0fdaaa99e8c45be612f50c9e77dc0714ab2d6759a0
current-sync-long-soak-guest-receipt=.sandwurm/exports/three-writer/run.2nPKtCoX/live/workspace-export/guest-receipts/iotox/sync-three-writer.json
current-sync-long-soak-guest-receipt-sha256=687b4ace878465ba733399a722d009a8d99afc616fe244ad7f2721443263356b
current-sync-long-soak-manifest-sha256=e7e42344883152e5dde264c3b6fab0c0df5e601a56334e2c2e344754d30318f9
backup-custody-verify-command=tools/iotox-repo.sh sync-backup-custody-verify PATH
native-backup-plan-command=iotox sync backup plan PATH read-write 30
native-backup-receipt-command=iotox sync backup receipt PATH read-write 30 backup-root=/BACKUP/PATH restored-root=/RESTORE/PATH backup-system=borg backup-generation=gen001 live-failure-domain=live.host backup-failure-domain=same-host.versioned restored-failure-domain=restore.drill restore-provenance=restore.drill custody-class=same-host-versioned immutable-or-versioned=1 operator-rehearsal-repeatable=1 --out /PROOF/sync-backup
native-runbook-plan-command=iotox sync runbook plan PATH read-write 30
native-runbook-receipt-command=iotox sync runbook receipt PATH read-write 30 --runbook /PROOF/recovery-runbook.md --reviewer owner --accept-reviewed-runbook --out /PROOF/recovery-runbook.receipt
native-runbook-status-command=iotox sync runbook status --receipt /PROOF/recovery-runbook.receipt
native-retention-command=iotox sync retention set NAMESPACE --keep-days 90 --min-revisions 8 --delete-grace-days 14 --out /PROOF/sync-retention-policy.receipt
native-evidence-collect-command=iotox evidence collect sync PATH read-write 30 --out /PROOF/sync --storage-readiness /PROOF/storage-readiness.json --long-soak /PROOF/long-soak.json --backup-custody /PROOF/sync-backup/backup-custody.json --restore-drill /PROOF/sync-backup/restore-drill.json --recovery-runbook /PROOF/recovery-runbook.receipt --retention-policy /PROOF/sync-retention-policy.receipt
native-precious-status-command=iotox sync precious-status PATH read-write 30 --evidence-dir /PROOF/sync
native-precious-signoff-command=iotox sync precious-signoff PATH read-write 30 --evidence-dir /PROOF/sync --reviewer owner --accept-operator-responsibility --out /PROOF/precious-signoff.receipt
sync-graduation-command=iotox sync graduation-check PATH read-write 30 --evidence local-preflight=doctor --evidence storage-readiness=repo.storage --evidence recovery-custody=backup.receipt --evidence restore-drill=restore.drill --evidence recovery-runbook=runbook.review
sync-local-preflight-shape=iotox-sync-doctor-v3-or-v4 decision=ready
sync-storage-readiness-shape=json schema=iotox.storage-readiness.v1 status=ready ready_for_precious_data=true contains_secrets=false
sync-long-soak-shape=json schema=iotox.sync-three-writer-sandwurm-verification.v1 status=passed soak_campaign=true soak_elapsed_ms>=86400000 contains_secrets=false
sync-recovery-custody-shape=json schema=iotox.sync-backup-custody.v1 status=passed custody_class=same-host-versioned|sync-external-versioned|off-host-versioned|offline-or-remote-versioned immutable_or_versioned=true restore_verified=true contains_secrets=false scope=not-disk-loss-host-compromise-or-filesystem-wide-corruption
sync-restore-drill-shape=json schema=iotox.sync-retained-recovery-drill.v1 status=passed decision=match local_requirements_satisfied=true contains_secrets=false
sync-recovery-runbook-shape=line schema=iotox.sync-recovery-runbook-review.v1 status=reviewed content-free=1 operator-runbook=present reviewer-label=LABEL dataset-selector-sha256=HEX runbook-sha256=HEX runbook-bytes>0 accepted-reviewed-runbook=1 coverage-flags=all not-content-custody=1
terminal-long-soak-command=iotox terminal soak-plan --root PATH --peer PEER
terminal-graduation-command=iotox terminal graduation-check --root PATH --peer PEER --evidence daily-control=local.gate --evidence profile-freshness=profile.check --evidence service-supervision=systemd.user --evidence reconnect-continuity=cli.reconnect --evidence cgroup-delegation=nixos.cgroup --evidence route-loss=tox.loss --evidence long-soak=soak.24h --evidence tor-route-loss=tor.operator --evidence i2p-route-loss=i2p.fronts --evidence sudo-policy=host.sudo --evidence security-review=review --evidence activation-decision=owner
resident-service-status-plan-command=iotox service status-plan --target all --root PATH --manager systemd-user --unit-prefix iotox-self --binary /usr/bin/iotox
resident-service-reality-command=iotox service status-receipt --target all --root PATH --manager systemd-user --unit-prefix iotox-self --binary /usr/bin/iotox --service-manager-state active --enabled-state enabled --log-state reviewed --health-state passed --upgrade-state passed --accept-operator-responsibility --out /PROOF/terminal-service-supervision.receipt
native-terminal-evidence-collect-command=iotox evidence collect terminal --root PATH --peer PEER --out /PROOF/stable --service-reality /PROOF/terminal-service-supervision.receipt --long-soak /PROOF/terminal-24h.receipt --evidence daily-control=local.gate --evidence profile-freshness=profile.check --evidence reconnect-continuity=cli.reconnect --evidence cgroup-delegation=nixos.cgroup --evidence route-loss=tox.loss --evidence tor-route-loss=tor.operator --evidence i2p-route-loss=i2p.fronts --evidence sudo-policy=host.sudo --evidence security-review=owner.review --evidence activation-decision=owner.decree
native-terminal-evidence-shape=line schema=iotox.terminal-stable-evidence.v1 status=operator-attested gate=terminal.NAME label=LABEL root-sha256=HEX peer-sha256=HEX content-free=1 repo-certified=0; terminal.service-supervision prefers schema=iotox.service-reality.v1 status=accepted service-manager-state=active enabled-state=enabled|static|managed log-state=reviewed health-state=passed upgrade-state=passed
native-evidence-manifest-command=iotox evidence manifest /PROOF/stable --out /PROOF/stable-evidence.manifest --scope auto
required-gate=sync.local-preflight
required-gate=sync.storage-readiness
required-gate=sync.long-soak
required-gate=sync.recovery-custody
required-gate=sync.restore-drill
required-gate=sync.recovery-runbook
required-gate=terminal.daily-control
required-gate=terminal.profile-freshness
required-gate=terminal.service-supervision
required-gate=terminal.reconnect-continuity
required-gate=terminal.cgroup-delegation
required-gate=terminal.route-loss
required-gate=terminal.long-soak
required-gate=terminal.tor-route-loss
required-gate=terminal.i2p-route-loss
required-gate=terminal.sudo-policy
required-gate=terminal.security-review
required-gate=terminal.activation-decision
manifest-rule=each required gate needs gate=accepted, gate.receipt-path=PATH, and gate.receipt-sha256=<64 lowercase hex of that bounded receipt file>
sync-manifest-rule=sync gate receipts are also native shape-checked; placeholder prose is rejected
stable-check-command=iotox ship-check all stable --evidence-manifest stable-evidence.manifest
release-check-command=tools/iotox-repo.sh release-check stable --iotox /path/to/iotox --evidence-manifest stable-evidence.manifest
mutated=0
boundary=manifest-paths-and-hashes-bind-content-free-receipts-or-review-records; sync receipt shapes reject placeholders; this plan does not create evidence
EOF
}

sha256_file() {
    local path=$1
    python3 - "$path" <<'PY'
import hashlib
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
digest = hashlib.sha256()
with path.open("rb") as source:
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        digest.update(chunk)
print(digest.hexdigest())
PY
}

cmd_current_stable_evidence() {
    [[ $# -eq 0 ]] || die "current-stable-evidence takes no arguments"
    cd "$root"
    local manifest=".sandwurm/exports/terminal-soak/run.OjbHRv/all-stable-evidence.service-reality.XOlEdI/stable-evidence.manifest"
    local expected_sha="1dfef328a55c91259d479134d71606d78f8bcf7f05a40ef136c7b0eb810d9006"
    local iotox
    iotox=$(default_iotox_executable)
    printf 'iotox-current-stable-evidence-v1\n'
    printf 'manifest=%s\n' "$manifest"
    printf 'expected-sha256=%s\n' "$expected_sha"
    if [[ -f "$manifest" ]]; then
        local observed
        observed=$(sha256_file "$manifest")
        printf 'present=1\n'
        printf 'observed-sha256=%s\n' "$observed"
        if [[ "$observed" == "$expected_sha" ]]; then
            printf 'status=accepted-local-dossier\n'
        else
            printf 'status=manifest-drifted\n'
        fi
    else
        printf 'present=0\n'
        printf 'observed-sha256=absent\n'
        printf 'status=missing\n'
    fi
    printf 'ship-check-command=%s\n' \
        "$(iotox_shell_command "$iotox" ship-check all stable --evidence-manifest "$manifest")"
    printf 'release-check-command=%s\n' \
        "$(shell_command tools/iotox-repo.sh release-check stable --iotox "$iotox" --evidence-manifest "$manifest")"
    printf 'seed-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --seed)"
    printf 'public-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --public)"
    printf 'datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --seed)"
    printf 'upload-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --upload)"
    printf 'conversation-datacube-command=%s\n' \
        "$(shell_command tools/iotox-repo.sh datacube --conversation)"
    printf 'docs=docs/stable-release-evidence.md,docs/ship-readiness.md\n'
    printf 'mutated=0\n'
    printf 'boundary=local-accepted-dossier-pointer; release-owner-must-keep-receipts-with-the-built-binary-and-not-reuse-across-scope\n'
}

normalize_release_channel() {
    local channel=${1:-founder-preview}
    case "$channel" in
        founder-preview|stable)
            printf '%s' "$channel"
            ;;
        *)
            die "release channel must be founder-preview or stable: $channel"
            ;;
    esac
}

default_iotox_executable() {
    local candidate
    for candidate in \
        "$root/build/iotox" \
        "$root/build/iotox-nix-debug/iotox" \
        "$root/build/gcc-debug/iotox" \
        "$root/build/gcc-release/iotox"; do
        if [[ -x "$candidate" ]]; then
            printf '%s' "$candidate"
            return
        fi
    done
    if have iotox; then
        command -v iotox
        return
    fi
    printf 'iotox'
}

require_iotox_executable() {
    local executable=$1
    if [[ "$executable" == */* ]]; then
        [[ -x "$executable" ]] || die "iotox executable is not executable: $executable"
    else
        have "$executable" || die "iotox executable is not on PATH: $executable"
    fi
}

cmd_release_plan() {
    local channel
    channel=$(normalize_release_channel "${1:-founder-preview}")
    [[ $# -le 1 ]] || die "release-plan takes at most one release channel"
    cd "$root"
    local iotox
    iotox=$(default_iotox_executable)
    local release_doc='docs/founder-preview-release.md'
    if [[ "$channel" == stable ]]; then
        release_doc='docs/ship-readiness.md'
    fi
    printf 'iotox-release-plan-v1\n'
    printf 'channel=%s\n' "$channel"
    printf 'repo-doctor-command=%s\n' "$(shell_command tools/iotox-repo.sh doctor)"
    printf 'build-command=%s\n' "$(shell_command tools/iotox-repo.sh build)"
    printf 'quick-test-command=%s\n' "$(shell_command tools/iotox-repo.sh test quick)"
    printf 'full-test-command=%s\n' "$(shell_command tools/iotox-repo.sh test full gcc-debug)"
    if [[ "$channel" == stable ]]; then
        printf 'ship-check-command=%s\n' \
            "$(iotox_shell_command "$iotox" ship-check all stable --evidence-manifest stable-evidence.manifest)"
        printf 'stable-evidence-plan-command=%s\n' \
            "$(shell_command tools/iotox-repo.sh stable-evidence-plan)"
        printf 'stable-ship-check-command=%s\n' \
            "$(iotox_shell_command "$iotox" ship-check all stable --evidence-manifest stable-evidence.manifest)"
    else
        printf 'ship-check-command=%s\n' "$(iotox_shell_command "$iotox" ship-check all "$channel")"
        printf 'stable-brake-command=%s\n' "$(iotox_shell_command "$iotox" ship-check all stable)"
    fi
    if [[ "$channel" == stable ]]; then
        printf 'release-check-command=%s\n' \
            "$(shell_command tools/iotox-repo.sh release-check "$channel" --iotox "$iotox" --evidence-manifest stable-evidence.manifest)"
    else
        printf 'release-check-command=%s\n' \
            "$(shell_command tools/iotox-repo.sh release-check "$channel" --iotox "$iotox")"
    fi
    printf 'source-input-command=%s\n' "$(shell_command tools/package-source-inputs.sh)"
    printf 'seed-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --seed)"
    printf 'public-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --public)"
    printf 'datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --seed)"
    printf 'upload-datacube-command=%s\n' "$(shell_command tools/iotox-repo.sh datacube --upload)"
    printf 'conversation-datacube-command=%s\n' \
        "$(shell_command tools/iotox-repo.sh datacube --conversation)"
    printf 'datacube-verify-command=%s\n' \
        "$(shell_command tools/make-repository-datacube.sh --verify ARCHIVE.zip)"
    printf 'cleanup-audit-command=%s\n' "$(shell_command tools/iotox-repo.sh clean)"
    printf 'release-doc=%s\n' "$release_doc"
    printf 'ship-readiness-doc=docs/ship-readiness.md\n'
    printf 'stable-without-concern=%s\n' \
        "$([[ "$channel" == stable ]] && printf required || printf blocked-nonclaim)"
    printf 'mutated=0\n'
    printf 'boundary=release-plan-is-a-command-trail-not-a-product-claim\n'
}

cmd_release_check() {
    local channel='founder-preview'
    local channel_seen=0
    local allow_dirty=0
    local iotox=''
    local evidence_manifest=''
    while (($# > 0)); do
        case "$1" in
            founder-preview|stable)
                ((channel_seen == 0)) || die "release-check accepts only one channel"
                channel=$(normalize_release_channel "$1")
                channel_seen=1
                ;;
            --iotox)
                shift
                [[ $# -gt 0 ]] || die "--iotox requires a path or command"
                iotox=$1
                ;;
            --evidence-manifest)
                shift
                [[ $# -gt 0 ]] || die "--evidence-manifest requires a path"
                evidence_manifest=$1
                ;;
            --allow-dirty)
                allow_dirty=1
                ;;
            --help|-h)
                cat <<'EOF'
Usage:
  tools/iotox-repo.sh release-check [founder-preview|stable] [--iotox PATH] [--evidence-manifest PATH] [--allow-dirty]

Checks the release command trail without packaging. Founder-preview must pass
the founder-preview ship gate and must still prove that stable/no-concern is
blocked. Stable must pass the stable ship gate with a complete evidence
manifest. A real release should not use --allow-dirty; that flag exists only for
local rehearsal.
EOF
                return 0
                ;;
            *)
                die "unknown release-check option: $1"
                ;;
        esac
        shift
    done

    cd "$root"
    [[ -n "$iotox" ]] || iotox=$(default_iotox_executable)
    require_iotox_executable "$iotox"
    ensure_iotox_provider_env

    local dirty
    dirty=$(git status --porcelain=v1 --untracked-files=all)
    if [[ -n "$dirty" && "$allow_dirty" -ne 1 ]]; then
        printf '%s\n' "$dirty" >&2
        die "release-check requires a clean worktree; use --allow-dirty only for rehearsal"
    fi

    git diff --check >/dev/null ||
        die "git diff --check failed"
    git diff --cached --check >/dev/null ||
        die "git diff --cached --check failed"
    local release_script
    for release_script in tools/iotox-repo.sh tools/make-repository-datacube.sh \
        tools/package-source-inputs.sh; do
        bash -n "$release_script" ||
            die "release shell syntax check failed: $release_script"
    done

    [[ -x tools/make-repository-datacube.sh ]] ||
        die "datacube builder is missing or not executable"
    [[ -x tools/package-source-inputs.sh ]] ||
        die "source-input packager is missing or not executable"

    local ship_args=(ship-check all "$channel")
    if [[ "$channel" == stable ]]; then
        [[ -n "$evidence_manifest" ]] ||
            die "stable release-check requires --evidence-manifest PATH"
        ship_args+=(--evidence-manifest "$evidence_manifest")
    fi

    local ship_output=''
    local ship_status=0
    ship_output=$("$iotox" "${ship_args[@]}" 2>&1) || ship_status=$?
    if [[ "$ship_status" -ne 0 ]]; then
        printf '%s\n' "$ship_output" >&2
        die "ship-check failed for release channel $channel"
    fi

    local stable_brake
    if [[ "$channel" == founder-preview ]]; then
        local stable_output=''
        local stable_status=0
        stable_output=$("$iotox" ship-check all stable 2>&1) || stable_status=$?
        [[ "$stable_status" -ne 0 ]] ||
            die "stable/no-concern ship-check unexpectedly passed during founder-preview release"
        stable_brake='blocked-as-expected'
    else
        stable_brake='passed-with-evidence-manifest'
    fi

    local commit
    commit=$(git rev-parse HEAD)
    local release_doc='docs/founder-preview-release.md'
    if [[ "$channel" == stable ]]; then
        release_doc='docs/ship-readiness.md'
    fi
    printf 'iotox-release-check-v1\n'
    printf 'channel=%s\n' "$channel"
    printf 'commit=%s\n' "$commit"
    if [[ -z "$dirty" ]]; then
        printf 'git-clean=1\n'
    else
        printf 'git-clean=0\n'
    fi
    printf 'dirty-allowed=%s\n' "$allow_dirty"
    printf 'diff-check=pass\n'
    printf 'shell-syntax=pass\n'
    printf 'iotox-executable=%s\n' "$iotox"
    printf 'ship-check=pass\n'
    if [[ -n "$evidence_manifest" ]]; then
        printf 'evidence-manifest=%s\n' "$evidence_manifest"
    fi
    printf 'stable-brake=%s\n' "$stable_brake"
    printf 'datacube-builder=present\n'
    printf 'source-input-packager=present\n'
    printf 'release-doc=%s\n' "$release_doc"
    printf 'ship-readiness-doc=docs/ship-readiness.md\n'
    printf 'mutated=0\n'
    if [[ "$channel" == founder-preview ]]; then
        printf 'decision=founder-preview-release-path-ready\n'
    else
        printf 'decision=stable-release-path-ready\n'
    fi
}

main() {
    local command=${1:-help}
    if (($# > 0)); then
        shift
    fi
    case "$command" in
        help|--help|-h)
            usage
            ;;
        doctor)
            [[ $# -eq 0 ]] || die "doctor takes no arguments"
            cmd_doctor
            ;;
        build)
            [[ $# -eq 0 ]] || die "build takes no arguments"
            cmd_build
            ;;
        test)
            local tier=${1:-}
            [[ -n "$tier" ]] || die "test requires quick or full"
            shift
            case "$tier" in
                quick)
                    [[ $# -eq 0 ]] || die "test quick takes no extra arguments"
                    cmd_test_quick
                    ;;
                full)
                    [[ $# -le 1 ]] || die "test full takes at most one CMake preset"
                    cmd_test_full "$@"
                    ;;
                *)
                    die "unknown test tier: $tier"
                    ;;
            esac
            ;;
        datacube)
            cmd_datacube "$@"
            ;;
        clean)
            cmd_clean "$@"
            ;;
        sync-recovery-drill)
            cmd_sync_recovery_drill "$@"
            ;;
        sync-loopback-custody-drill)
            cmd_sync_loopback_custody_drill "$@"
            ;;
        sync-dishonest-storage-drill)
            cmd_sync_dishonest_storage_drill "$@"
            ;;
        sync-dishonest-storage-matrix)
            cmd_sync_dishonest_storage_matrix "$@"
            ;;
        sync-log-writes-prefix-replay)
            cmd_sync_log_writes_prefix_replay "$@"
            ;;
        sync-production-prefix-replay)
            cmd_sync_production_prefix_replay "$@"
            ;;
        sync-backup-custody-verify)
            cmd_sync_backup_custody_verify "$@"
            ;;
        sync-precious-data-gates-plan)
            cmd_sync_precious_data_gates_plan "$@"
            ;;
        storage-readiness)
            cmd_storage_readiness "$@"
            ;;
        current-sync-long-soak-receipt)
            cmd_current_sync_long_soak_receipt "$@"
            ;;
        witness-custody)
            cmd_witness_custody "$@"
            ;;
        stable-evidence-plan)
            cmd_stable_evidence_plan "$@"
            ;;
        current-stable-evidence)
            cmd_current_stable_evidence "$@"
            ;;
        release-plan)
            cmd_release_plan "$@"
            ;;
        release-check)
            cmd_release_check "$@"
            ;;
        *)
            usage >&2
            die "unknown command: $command"
            ;;
    esac
}

main "$@"
