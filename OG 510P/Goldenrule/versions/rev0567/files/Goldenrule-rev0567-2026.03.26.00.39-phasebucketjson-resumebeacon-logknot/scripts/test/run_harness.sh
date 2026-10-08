#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${1:-quick}"

if [[ "$MODE" != "quick" && "$MODE" != "full" ]]; then
  echo "usage: scripts/test/run_harness.sh [quick|full]" >&2
  exit 2
fi

mkdir -p "$ROOT/artifacts/timing"

export TZ="${TZ:-UTC}"
export LANG="${LANG:-C}"
export LC_ALL="${LC_ALL:-C}"
export PYTHONHASHSEED="${PYTHONHASHSEED:-0}"
export TEST_SEED="${TEST_SEED:-424242}"
export NO_NETWORK="${NO_NETWORK:-1}"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY

seed_file="$ROOT/artifacts/timing/seed_${MODE}.json"
rows_file="$ROOT/artifacts/timing/timing_${MODE}.tsv"

cat > "$seed_file" <<JSON
{
  "mode": "$MODE",
  "seed": "$TEST_SEED",
  "tz": "$TZ",
  "lang": "$LANG",
  "lc_all": "$LC_ALL",
  "no_network": "$NO_NETWORK"
}
JSON

printf "step\tseconds\tstatus\n" > "$rows_file"
python3 "$ROOT/scripts/test/record_env_metadata.py" "$MODE" "$ROOT/artifacts/timing/env_${MODE}.json"

if [[ "$MODE" == "quick" ]]; then
  total_budget="${QUICK_TOTAL_BUDGET_SEC:-240}"
  step_budget="${QUICK_STEP_BUDGET_SEC:-180}"
  steps=(
    "control_tests|python3 -m unittest discover -s tests/control -p 'test_*.py'"
    "rust_lib_tests|tools/rust_exec.sh cargo test -p gr_engine --lib"
    "python_fast|python3 -m unittest grlab.tests.test_certify_solver grlab.tests.test_certify_cli"
  )
else
  total_budget="${FULL_TOTAL_BUDGET_SEC:-1800}"
  step_budget="${FULL_STEP_BUDGET_SEC:-1200}"
  steps=(
    "control_tests|python3 -m unittest discover -s tests/control -p 'test_*.py'"
    "project_check|tools/check.sh"
  )
fi

start_total="$(date +%s)"

run_step() {
  local name="$1"
  local cmd="$2"
  local start end elapsed
  start="$(date +%s)"

  if command -v timeout >/dev/null 2>&1; then
    if timeout "$step_budget" bash -lc "cd '$ROOT' && $cmd"; then
      end="$(date +%s)"
      elapsed="$((end - start))"
      printf "%s\t%s\t%s\n" "$name" "$elapsed" "ok" >> "$rows_file"
    else
      end="$(date +%s)"
      elapsed="$((end - start))"
      printf "%s\t%s\t%s\n" "$name" "$elapsed" "fail" >> "$rows_file"
      echo "harness: step failed ($name)" >&2
      exit 1
    fi
  else
    if bash -lc "cd '$ROOT' && $cmd"; then
      end="$(date +%s)"
      elapsed="$((end - start))"
      if (( elapsed > step_budget )); then
        printf "%s\t%s\t%s\n" "$name" "$elapsed" "timeout" >> "$rows_file"
        echo "harness: step over budget ($name, ${elapsed}s > ${step_budget}s)" >&2
        exit 1
      fi
      printf "%s\t%s\t%s\n" "$name" "$elapsed" "ok" >> "$rows_file"
    else
      end="$(date +%s)"
      elapsed="$((end - start))"
      printf "%s\t%s\t%s\n" "$name" "$elapsed" "fail" >> "$rows_file"
      echo "harness: step failed ($name)" >&2
      exit 1
    fi
  fi
}

for item in "${steps[@]}"; do
  name="${item%%|*}"
  cmd="${item#*|}"
  run_step "$name" "$cmd"
done

end_total="$(date +%s)"
elapsed_total="$((end_total - start_total))"

if (( elapsed_total > total_budget )); then
  echo "harness: total budget exceeded (${elapsed_total}s > ${total_budget}s)" >&2
  exit 1
fi

echo "harness: mode=$MODE elapsed=${elapsed_total}s seed=$TEST_SEED"
