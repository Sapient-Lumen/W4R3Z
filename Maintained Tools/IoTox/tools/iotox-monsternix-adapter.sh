#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

iotox_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
monsternix_root=${IOTOX_MONSTERNIX_ROOT:-"$iotox_root/../monsternix"}

die() {
    printf 'iotox-monsternix-adapter: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<'EOF'
Usage:
  tools/iotox-monsternix-adapter.sh help
  tools/iotox-monsternix-adapter.sh doctor
  tools/iotox-monsternix-adapter.sh plan

Read-only IoTox/MonsterNix adapter sketch. It inspects local paths and prints
the intended admission/projection boundary. It does not write into MonsterNix,
install service state, enroll secrets, grant IoTox authority, or run mnx switch.

Environment:
  IOTOX_MONSTERNIX_ROOT  MonsterNix checkout (default: ../monsternix)
EOF
}

have() {
    command -v "$1" >/dev/null 2>&1
}

git_value() {
    local repo=$1
    shift
    git -C "$repo" "$@" 2>/dev/null || printf 'unavailable'
}

cmd_doctor() {
    printf 'iotox-root        %s\n' "$iotox_root"
    printf 'monsternix-root   %s\n' "$monsternix_root"
    if [[ -d "$iotox_root/.git" ]]; then
        printf 'iotox-commit      %s\n' "$(git_value "$iotox_root" rev-parse --short=12 HEAD)"
        printf 'iotox-dirty       %s\n' "$(git -C "$iotox_root" status --porcelain=v1 --untracked-files=all | wc -l | tr -d ' ')"
    else
        printf 'iotox-git         unavailable\n'
    fi
    if [[ -d "$monsternix_root/.git" ]]; then
        printf 'monsternix-commit %s\n' "$(git_value "$monsternix_root" rev-parse --short=12 HEAD)"
        printf 'monsternix-dirty  %s\n' "$(git -C "$monsternix_root" status --porcelain=v1 --untracked-files=all | wc -l | tr -d ' ')"
    else
        printf 'monsternix-git    unavailable\n'
    fi

    printf '\nmonsternix objects\n'
    [[ -x "$monsternix_root/foundation/mnx-transaction" ]] &&
        printf '%-20s present\n' foundation-mnx ||
        printf '%-20s missing\n' foundation-mnx
    [[ -x "$monsternix_root/werx/werx" ]] &&
        printf '%-20s present\n' werx ||
        printf '%-20s missing\n' werx
    [[ -f "$monsternix_root/foundation/tool-lifecycle.json" ]] &&
        printf '%-20s present\n' tool-lifecycle ||
        printf '%-20s missing\n' tool-lifecycle
    [[ -f "$monsternix_root/foundation/projections.json" ]] &&
        printf '%-20s present\n' projections ||
        printf '%-20s missing\n' projections

    printf '\nrequired host tools\n'
    for tool in bash git nix; do
        if have "$tool"; then
            printf '%-20s %s\n' "$tool" "$(command -v "$tool")"
        else
            printf '%-20s missing\n' "$tool"
        fi
    done
}

cmd_plan() {
    local iotox_commit
    local monsternix_commit
    iotox_commit=$(git_value "$iotox_root" rev-parse HEAD)
    monsternix_commit=$(git_value "$monsternix_root" rev-parse HEAD)
    cat <<EOF
IoTox -> MonsterNix adapter plan

Inputs:
  iotox-root:        $iotox_root
  iotox-commit:      $iotox_commit
  monsternix-root:   $monsternix_root
  monsternix-commit: $monsternix_commit

Allowed first actions:
  1. admit exact IoTox source/package/proof object into MonsterNix as inert material
  2. produce a content-free receipt naming commit, package output, proof tier, and host projection
  3. generate a service/config candidate that the operator can inspect
  4. let MonsterNix own its normal test/switch/apply ceremony

Forbidden adapter actions:
  - no RecallRoot or private key import
  - no authority-ledger mutation
  - no sync namespace creation
  - no sudo profile enablement
  - no service installation by presence
  - no evidence bundle containing paths, file contents, terminal bytes, or secrets
  - no claim that a same-disk backup or same-host witness is independent

First implementation target:
  add a MonsterNix-side object/admission contract, then make this script call that
  contract only after it exists and only through an explicit --execute boundary.
EOF
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
        plan)
            [[ $# -eq 0 ]] || die "plan takes no arguments"
            cmd_plan
            ;;
        *)
            usage >&2
            die "unknown command: $command"
            ;;
    esac
}

main "$@"
