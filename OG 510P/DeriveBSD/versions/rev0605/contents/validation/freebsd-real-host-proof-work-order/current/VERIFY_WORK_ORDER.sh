#!/bin/sh
set -eu

# Verify that this work order still matches the checked-out DeriveBSD tree.
# Usage: sh VERIFY_WORK_ORDER.sh [/path/to/DeriveBSD] [work-order-dir]
SCRIPT_DIR=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
REPO_ROOT=${1:-$(pwd)}
WORK_ORDER_DIR=${2:-$SCRIPT_DIR}
PYTHON=${PYTHON:-python3}

cd "$REPO_ROOT"

"$PYTHON" -B -S "$REPO_ROOT/tools/freebsd/verify_real_host_proof_work_order.py"   "$WORK_ORDER_DIR"   --repo-root "$REPO_ROOT"

printf '%s
' "real FreeBSD host-proof work order verified against checked-out tree"
