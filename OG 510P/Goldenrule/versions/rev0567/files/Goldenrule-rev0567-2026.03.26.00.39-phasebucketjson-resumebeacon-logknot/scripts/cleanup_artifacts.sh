#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$ROOT/artifacts"
KEEP_COUNT=20
MAX_AGE_DAYS=14
DRY_RUN=0
YES=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --path)
      TARGET="$2"
      shift 2
      ;;
    --keep-count)
      KEEP_COUNT="$2"
      shift 2
      ;;
    --max-age-days)
      MAX_AGE_DAYS="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --yes)
      YES=1
      shift
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$TARGET" ]]; then
  echo "cleanup: target missing: $TARGET"
  exit 0
fi

mapfile -t files < <(find "$TARGET" -type f -printf '%T@ %p\n' | sort -nr)

now_epoch="$(date +%s)"
max_age_sec="$((MAX_AGE_DAYS * 86400))"

delete_list=()
idx=0
for row in "${files[@]}"; do
  idx=$((idx + 1))
  ts="${row%% *}"
  path="${row#* }"
  ts_int="${ts%.*}"
  age="$((now_epoch - ts_int))"
  if (( idx > KEEP_COUNT )) || (( age > max_age_sec )); then
    delete_list+=("$path")
  fi
done

if (( ${#delete_list[@]} == 0 )); then
  echo "cleanup: nothing to delete"
  exit 0
fi

echo "cleanup: target=$TARGET keep_count=$KEEP_COUNT max_age_days=$MAX_AGE_DAYS"
printf '%s\n' "${delete_list[@]}"

if (( DRY_RUN == 1 )); then
  echo "cleanup: dry-run enabled"
  exit 0
fi

if [[ -t 0 && "$YES" -ne 1 ]]; then
  read -r -p "cleanup: delete listed files? [y/N] " ans
  if [[ "$ans" != "y" && "$ans" != "Y" ]]; then
    echo "cleanup: aborted"
    exit 1
  fi
fi

for p in "${delete_list[@]}"; do
  rm -f "$p"
done

echo "cleanup: done"
