#!/bin/sh
# One-command strict real FreeBSD host-proof collection, handoff verification,
# import, and post-import audit.  This wrapper intentionally exposes no
# checker-simulation or failed/refusal modes: it is for operator evidence only.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd -P)
PYTHON=${PYTHON:-python3}
IMPORT_ROOT=${DERIVEBSD_HOST_PROOF_IMPORT_ROOT:-"$ROOT/validation/freebsd-host-proof-imports"}
KEEP_HANDOFF=${DERIVEBSD_KEEP_HOST_PROOF_HANDOFF:-0}
USER_HANDOFF_DIR=${DERIVEBSD_HOST_PROOF_HANDOFF_DIR:-}
RESUME_HANDOFF_DIR=${DERIVEBSD_RESUME_HOST_PROOF_HANDOFF_DIR:-}
RUN_RECEIPT=${DERIVEBSD_HOST_PROOF_RUN_RECEIPT:-}
REPLACE=${DERIVEBSD_HOST_PROOF_IMPORT_REPLACE:-0}
COLLECT_IMPORT_OK=0
AUTO_HANDOFF=0
RESUME_MODE=0
CURRENT_STAGE=initializing
STAGES_COMPLETED=
HANDOFF_RETENTION_RESULT=not-decided
CUBE_CUT_VERSION=$(
  "$PYTHON" -B -S -c 'import sys, pathlib; root = pathlib.Path(sys.argv[1]); sys.path.insert(0, str(root / "tools" / "freebsd")); import host_proof_contract as c; print(c.CURRENT_CUBE_CUT_VERSION)' "$ROOT" 2>/dev/null || printf unknown
)

refuse_operator_path() {
  printf '%s\n' "host-proof strict collect/import refused: $*" >&2
  exit 2
}

refuse_symlink_path() {
  if [ -L "$1" ]; then
    refuse_operator_path "$2 must not be a symlink before host proof collection/import: $1"
  fi
}

# Emits the shared: must not contain existing symlink components before host proof work
refuse_symlink_components() {
  [ -n "$1" ] || return 0
  path_guard_error=$("$PYTHON" -B -S -c '
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "tools" / "freebsd"))
import host_proof_contract as contract
try:
    contract.require_no_existing_symlink_component(Path(sys.argv[2]), sys.argv[3])
except Exception as exc:
    print(exc, file=sys.stderr)
    raise SystemExit(2)
' "$ROOT" "$1" "$2" 2>&1) || refuse_operator_path "$path_guard_error"
}

usage() {
  cat <<'USAGE'
Usage: tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh [--resume-handoff HANDOFF_DIR] [--import-root IMPORT_ROOT] [--run-receipt RUN_RECEIPT]
       tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh [IMPORT_ROOT]

Strict real-host path:
  1. run the fail-fast FreeBSD/root/Capsicum preflight through the collector
  2. collect receipt.json and bundle.json into a finite handoff directory
  3. verify the handoff in default real-host-proof mode
  4. import it into a digest-named import directory
  5. audit the import root in default real-proof mode

Strict resume path:
  --resume-handoff HANDOFF_DIR skips collection and reuses a preserved finite
  handoff directory. It still verifies, imports, and audits in default
  real-host-proof mode; it exposes no checker-simulation flags.

Run receipt:
  --run-receipt RUN_RECEIPT or DERIVEBSD_HOST_PROOF_RUN_RECEIPT writes a
  machine-readable collect/import run receipt from the exit trap.  The receipt
  records the current/failing stage, completed stages, handoff directory,
  import root, resume mode, replacement mode, and handoff-retention decision.

Evidence-retention rule:
  Auto-created temporary handoff directories are removed only after a fully
  successful collect/import/audit.  On any failure, the wrapper preserves the handoff directory so scarce real-host evidence can be inspected or re-imported.

Environment:
  PYTHON                               Python command, default python3
  DERIVEBSD_HOST_PROOF_IMPORT_ROOT     Import root override
  DERIVEBSD_HOST_PROOF_HANDOFF_DIR     Collector output handoff directory
  DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=1  Deliberately replace existing receipt/bundle/SHA256SUMS members in a handoff directory
  DERIVEBSD_RESUME_HOST_PROOF_HANDOFF_DIR  Existing handoff directory to resume/import
  DERIVEBSD_HOST_PROOF_RUN_RECEIPT     Machine-readable run receipt path
  DERIVEBSD_KEEP_HOST_PROOF_HANDOFF=1  Preserve auto-created temporary handoff even after success
  DERIVEBSD_HOST_PROOF_IMPORT_REPLACE=1  Deliberately replace duplicate digest import
USAGE
}

complete_stage() {
  if [ -n "$STAGES_COMPLETED" ]; then
    STAGES_COMPLETED="$STAGES_COMPLETED $1"
  else
    STAGES_COMPLETED=$1
  fi
}

write_run_receipt() {
  status=$1
  [ -n "$RUN_RECEIPT" ] || return 0
  RUN_RECEIPT_PATH=$RUN_RECEIPT \
  ROOT_PATH=$ROOT \
  WRAPPER_REL=tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh \
  CUBE_CUT_VERSION=$CUBE_CUT_VERSION \
  EXIT_STATUS=$status \
  COLLECT_IMPORT_OK=$COLLECT_IMPORT_OK \
  CURRENT_STAGE=$CURRENT_STAGE \
  STAGES_COMPLETED=$STAGES_COMPLETED \
  HANDOFF_DIR=${HANDOFF_DIR:-} \
  IMPORT_ROOT=$IMPORT_ROOT \
  AUTO_HANDOFF=$AUTO_HANDOFF \
  KEEP_HANDOFF=$KEEP_HANDOFF \
  RESUME_MODE=$RESUME_MODE \
  REPLACE=$REPLACE \
  HANDOFF_RETENTION_RESULT=$HANDOFF_RETENTION_RESULT \
  "$PYTHON" -B -S "$ROOT/tools/freebsd/write_collect_import_run_receipt.py" "$RUN_RECEIPT"
}

POSITIONAL_IMPORT_ROOT_SEEN=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --import-root)
      shift
      if [ "$#" -eq 0 ]; then
        printf '%s\n' "--import-root requires a directory" >&2
        exit 2
      fi
      IMPORT_ROOT=$1
      ;;
    --resume-handoff)
      shift
      if [ "$#" -eq 0 ]; then
        printf '%s\n' "--resume-handoff requires a directory" >&2
        exit 2
      fi
      RESUME_HANDOFF_DIR=$1
      ;;
    --run-receipt)
      shift
      if [ "$#" -eq 0 ]; then
        printf '%s\n' "--run-receipt requires a path" >&2
        exit 2
      fi
      RUN_RECEIPT=$1
      ;;
    --)
      shift
      while [ "$#" -gt 0 ]; do
        if [ "$POSITIONAL_IMPORT_ROOT_SEEN" = "1" ]; then
          printf '%s\n' "only one IMPORT_ROOT positional argument is supported" >&2
          exit 2
        fi
        IMPORT_ROOT=$1
        POSITIONAL_IMPORT_ROOT_SEEN=1
        shift
      done
      break
      ;;
    -*)
      usage >&2
      exit 2
      ;;
    *)
      if [ "$POSITIONAL_IMPORT_ROOT_SEEN" = "1" ]; then
        printf '%s\n' "only one IMPORT_ROOT positional argument is supported" >&2
        exit 2
      fi
      IMPORT_ROOT=$1
      POSITIONAL_IMPORT_ROOT_SEEN=1
      ;;
  esac
  shift
done

if [ -n "$RESUME_HANDOFF_DIR" ] && [ -n "$USER_HANDOFF_DIR" ]; then
  printf '%s\n' "DERIVEBSD_HOST_PROOF_HANDOFF_DIR cannot be combined with --resume-handoff or DERIVEBSD_RESUME_HOST_PROOF_HANDOFF_DIR" >&2
  exit 2
fi

cleanup_handoff() {
  status=$?
  if [ "$RESUME_MODE" = "1" ]; then
    HANDOFF_RETENTION_RESULT=resume-handoff-reused
  elif [ "$AUTO_HANDOFF" = "1" ] && [ -n "${HANDOFF_DIR:-}" ] && [ -d "$HANDOFF_DIR" ]; then
    if [ "$KEEP_HANDOFF" = "1" ]; then
      HANDOFF_RETENTION_RESULT=preserved-by-request
    elif [ "$COLLECT_IMPORT_OK" = "1" ]; then
      HANDOFF_RETENTION_RESULT=removed-after-success
    else
      HANDOFF_RETENTION_RESULT=preserved-on-failure
    fi
  elif [ -n "${HANDOFF_DIR:-}" ]; then
    HANDOFF_RETENTION_RESULT=user-supplied-handoff-not-deleted
  else
    HANDOFF_RETENTION_RESULT=no-handoff-directory-selected
  fi

  RECEIPT_WRITE_STATUS=0
  write_run_receipt "$status" || RECEIPT_WRITE_STATUS=$?
  if [ "$RECEIPT_WRITE_STATUS" -ne 0 ]; then
    printf 'host-proof run receipt write failed=%s\n' "$RUN_RECEIPT" >&2
    if [ "$status" -eq 0 ]; then
      status=$RECEIPT_WRITE_STATUS
      if [ "$AUTO_HANDOFF" = "1" ] && [ "$KEEP_HANDOFF" != "1" ]; then
        HANDOFF_RETENTION_RESULT=preserved-after-run-receipt-write-failure
      fi
    fi
  fi

  if [ "$AUTO_HANDOFF" = "1" ] && [ -n "${HANDOFF_DIR:-}" ] && [ -d "$HANDOFF_DIR" ]; then
    if [ "$KEEP_HANDOFF" = "1" ]; then
      printf 'handoff_dir_preserved=%s\n' "$HANDOFF_DIR" >&2
    elif [ "$COLLECT_IMPORT_OK" = "1" ] && [ "$RECEIPT_WRITE_STATUS" -eq 0 ] && [ "$status" -eq 0 ]; then
      rm -rf "$HANDOFF_DIR"
      printf 'handoff_dir_removed_after_success=%s\n' "$HANDOFF_DIR"
    else
      printf 'host-proof strict collect/import did not complete; preserving auto-created handoff_dir=%s\n' "$HANDOFF_DIR" >&2
    fi
  fi
  return "$status"
}
trap cleanup_handoff EXIT HUP INT TERM

if [ -n "$RESUME_HANDOFF_DIR" ]; then
  RESUME_MODE=1
  HANDOFF_DIR=$RESUME_HANDOFF_DIR
elif [ -n "$USER_HANDOFF_DIR" ]; then
  HANDOFF_DIR=$USER_HANDOFF_DIR
  refuse_symlink_path "$HANDOFF_DIR" "handoff directory"
  refuse_symlink_components "$HANDOFF_DIR" "handoff directory"
  mkdir -p "$HANDOFF_DIR"
  refuse_symlink_components "$HANDOFF_DIR" "handoff directory"
else
  HANDOFF_DIR=$(mktemp -d "${TMPDIR:-/tmp}/derivebsd-host-proof-handoff.XXXXXX")
  AUTO_HANDOFF=1
fi

refuse_symlink_path "$HANDOFF_DIR" "handoff directory"
refuse_symlink_components "$HANDOFF_DIR" "handoff directory"
refuse_symlink_path "$IMPORT_ROOT" "import root"
refuse_symlink_components "$IMPORT_ROOT" "import root"
if [ -n "$RUN_RECEIPT" ]; then
  refuse_symlink_path "$RUN_RECEIPT" "run receipt output"
  refuse_symlink_components "$RUN_RECEIPT" "run receipt output"
fi

if [ "$RESUME_MODE" = "1" ]; then
  printf '%s\n' "host-proof strict collect/import resume starting"
  printf 'resume_handoff_dir=%s\n' "$HANDOFF_DIR"
else
  printf '%s\n' "host-proof strict collect/import starting"
fi
printf 'handoff_dir=%s\n' "$HANDOFF_DIR"
printf 'import_root=%s\n' "$IMPORT_ROOT"
if [ -n "$RUN_RECEIPT" ]; then
  printf 'run_receipt=%s\n' "$RUN_RECEIPT"
fi

# In resume mode, skip the scarce host collector and reuse the preserved finite
# handoff.  The verifier/importer/auditor still run in default real-proof mode.
if [ "$RESUME_MODE" != "1" ]; then
  CURRENT_STAGE=collect
  "$ROOT/tools/freebsd/collect_removable_media_local_fallback_host_proof.sh" \
    "$HANDOFF_DIR/receipt.json" \
    "$HANDOFF_DIR/bundle.json" \
    "$HANDOFF_DIR"
  complete_stage collect
else
  CURRENT_STAGE=resume_handoff
  complete_stage resume_handoff
fi

CURRENT_STAGE=verify_handoff
"$PYTHON" -B -S "$ROOT/tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py" \
  "$HANDOFF_DIR"
complete_stage verify_handoff

IMPORT_ARGS=""
if [ "$REPLACE" = "1" ]; then
  IMPORT_ARGS="--replace"
fi

CURRENT_STAGE=import_handoff
# shellcheck disable=SC2086 # IMPORT_ARGS is intentionally either empty or one fixed flag.
"$PYTHON" -B -S "$ROOT/tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py" \
  "$HANDOFF_DIR" \
  --import-root "$IMPORT_ROOT" \
  $IMPORT_ARGS
complete_stage import_handoff

CURRENT_STAGE=audit_import_root
"$PYTHON" -B -S "$ROOT/tools/freebsd/audit_removable_media_local_fallback_host_proof_imports.py" \
  "$IMPORT_ROOT"
complete_stage audit_import_root

COLLECT_IMPORT_OK=1
CURRENT_STAGE=complete
if [ "$RESUME_MODE" = "1" ]; then
  printf '%s\n' "host-proof strict collect/import resume OK"
else
  printf '%s\n' "host-proof strict collect/import OK"
fi
printf 'handoff_dir=%s\n' "$HANDOFF_DIR"
printf 'import_root=%s\n' "$IMPORT_ROOT"
if [ -n "$RUN_RECEIPT" ]; then
  printf 'run_receipt=%s\n' "$RUN_RECEIPT"
fi
