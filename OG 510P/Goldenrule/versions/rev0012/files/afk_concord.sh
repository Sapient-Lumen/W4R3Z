#!/usr/bin/env bash
set -euo pipefail

# afk_concord.sh - AFK mission controller
# Multi-objective gating for candidate promotion and adversarial discovery.

export LANG="${LANG:-C.UTF-8}"
export LC_ALL="${LC_ALL:-C.UTF-8}"

# ---- NixOS/systemd PATH bootstrap ----
# systemd user services often start with a minimal PATH, so ensure common NixOS
# locations are present (best-effort, no hard dependency).
add_path() {
  local d="$1"
  [[ -d "$d" ]] || return 0
  case ":${PATH:-}:" in *":$d:"*) ;; *) PATH="$d:${PATH:-}" ;; esac
}
add_path /run/wrappers/bin
add_path /run/current-system/sw/bin
if [[ -n "${USER:-}" ]]; then add_path "/etc/profiles/per-user/$USER/bin"; fi
add_path "${HOME:-/home/${USER:-}}/.nix-profile/bin"
add_path /nix/var/nix/profiles/default/bin
export PATH
# -------------------------------------

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
RUST_EXEC="$ROOT/tools/rust_exec.sh"

# If systemd started us with a minimal environment (missing `python3`/Rust toolchain),
# optionally re-exec inside the repo’s dev shell (requires `nix` + flakes).
if [[ "${AFK_IN_NIX_DEVELOP:-0}" != "1" ]]; then
  need_shell=0
  command -v python3 >/dev/null 2>&1 || need_shell=1
  "$RUST_EXEC" cargo --version >/dev/null 2>&1 || need_shell=1
  if [[ "$need_shell" == "1" ]] && command -v nix >/dev/null 2>&1; then
    mkdir -p "runs/afk_discovery" 2>/dev/null || true
    now_utc="unknown"
    if command -v date >/dev/null 2>&1; then
      now_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    fi
    {
      echo "=== Concord AFK worker: entering nix develop (missing python3/cargo) ==="
      echo "time_utc=$now_utc"
      echo "cwd=$PWD"
      echo "path=$PATH"
    } >>"runs/afk_discovery/mission_control.log" 2>/dev/null || true
    export AFK_IN_NIX_DEVELOP=1
    exec nix --extra-experimental-features "nix-command flakes" develop --accept-flake-config -c bash "$0" "$@"
  fi
fi

ONCE=0
FAIL_SLEEP_SEC="${FAIL_SLEEP_SEC:-5}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --once)
      ONCE=1
      shift
      ;;
    --fail-sleep-sec)
      if [[ $# -lt 2 ]]; then
        echo "ERROR: --fail-sleep-sec requires a value" >&2
        exit 2
      fi
      FAIL_SLEEP_SEC="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: afk_concord.sh [--once] [--fail-sleep-sec <seconds>]

Runs the Concord AFK "Mission Control" loop.
  --once               Run a single mission iteration, then exit (debug).
  --fail-sleep-sec N   Sleep N seconds before retrying after mission failure (default: 5; env FAIL_SLEEP_SEC).
EOF
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

AFK_DIR="runs/afk_discovery"
PROMOTE_DIR="examples/strategies/candidates"
PROMOTE_DIR_LEGACY="examples/strategies/discovered"
ADVERSARY_DIR="examples/strategies/adversaries"
ADVERSARY_DIR_LEGACY="examples/strategies/vampires"
mkdir -p "$AFK_DIR" "$PROMOTE_DIR" "$PROMOTE_DIR_LEGACY" "$ADVERSARY_DIR" "$ADVERSARY_DIR_LEGACY"

MISSION_LOG="$AFK_DIR/mission_control.log"
touch "$MISSION_LOG"
if command -v tee >/dev/null 2>&1; then
  exec > >(tee -a "$MISSION_LOG") 2>&1
else
  exec >>"$MISSION_LOG" 2>&1
fi

echo "=== Concord AFK worker starting ==="
echo "time_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "cwd=$PWD"
echo "pid=$$"
echo "path=$PATH"
echo "python3=$(command -v python3 || echo missing)"
echo "cargo=$("$RUST_EXEC" cargo --version 2>/dev/null || echo missing)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is missing; cannot run missions" >&2
  exit 127
fi

ENGINE_BIN="${GRLAB_ENGINE_BIN:-$ROOT/target/debug/gr-engine}"
if [[ -x "$ENGINE_BIN" ]]; then
  echo "engine=$ENGINE_BIN (prebuilt)"
else
  if "$RUST_EXEC" cargo --version >/dev/null 2>&1; then
    echo "building engine (cargo build -p gr_engine --bin gr-engine)..."
    "$RUST_EXEC" cargo build -p gr_engine --bin gr-engine --quiet
  else
    echo "ERROR: rust toolchain unavailable and engine binary missing at $ENGINE_BIN" >&2
    exit 127
  fi
fi
export GRLAB_ENGINE_BIN="$ENGINE_BIN"

cleanup() {
    echo "Concord worker shutting down..."
    trap - SIGTERM SIGINT
    kill 0 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

echo "Concord Mission Control: Gauntlet gating enabled."

# Mission Definitions
# Each mission returns a set of arguments for `grlab search`
get_mission() {
    local m=$((RANDOM % 11))
    case $m in
        0) # Mission: Defeat Baseline Extortionist (Mem1)
            echo "search --world examples/worlds/ipd_long.json --opponent examples/strategies/extortion_chi3.json --metric avg_a --mode hill_climb --sigma 0.1 --trials 100"
            ;;
        1) # Mission: Golden Rule Self-Play (Maximize Cooperation)
            echo "search --world examples/worlds/ipd_long.json --self-play --metric mutual_c --mode hill_climb --sigma 0.05 --trials 100"
            ;;
        2) # Mission: Noisy Survival
            echo "search --world examples/worlds/ipd_noisy.json --opponent examples/strategies/tft.json --metric avg_a --mode random --trials 100"
            ;;
        3) # Mission: Out-earn WSLS
            echo "search --world examples/worlds/ipd_long.json --opponent examples/strategies/wsls.json --metric avg_a --mode hill_climb --sigma 0.1 --trials 100"
            ;;
        4) # Mission: Exit Discovery (Partner Choice)
            echo "search --world examples/worlds/ipd_long.json --opponent examples/strategies/extortion_chi3.json --metric avg_a --mode hill_climb --exit --sigma 0.1 --trials 100"
            ;;
        5|6) # Mission: Red Team (adversarial search against top candidates)
            local TARGET=""
            shopt -s nullglob
            local candidates=(examples/strategies/candidates/*.json)
            local legacy=(examples/strategies/discovered/saint_*.json)
            shopt -u nullglob
            if ((${#candidates[@]})); then
              TARGET="${candidates[RANDOM % ${#candidates[@]}]}"
            elif ((${#legacy[@]})); then
              TARGET="${legacy[RANDOM % ${#legacy[@]}]}"
            else
              TARGET="examples/strategies/tft.json"
            fi
            
            local EXTRA=""
            # 50% chance to use FSM in the adversarial search loop.
            if [[ $((RANDOM % 2)) -eq 0 ]]; then EXTRA="--fsm-states 4"; fi
            
            echo "search --world examples/worlds/ipd_long.json --opponent $TARGET --metric exploitation --mode hill_climb --sigma 0.1 --trials 100 $EXTRA"
            ;;
        7) # Mission: FSM candidate discovery (4 states)
            echo "search --world examples/worlds/ipd_long.json --self-play --metric mutual_c --mode hill_climb --fsm-states 4 --sigma 0.1 --trials 100"
            ;;
        8) # Mission: Global Welfare (Maximize Efficiency)
            echo "search --world examples/worlds/ipd_long.json --self-play --metric efficiency --mode hill_climb --sigma 0.05 --trials 100"
            ;;
        9) # Mission: Symmetry Enforcement
            echo "search --world examples/worlds/ipd_long.json --self-play --metric symmetry --mode hill_climb --sigma 0.1 --trials 100"
            ;;
        10) # Mission: Lindy Survival (Ecological Dominance)
            echo "ecology --world examples/worlds/ipd_long.json --generations 10"
            ;;
    esac
}

while true; do
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    SEED=$RANDOM
    MISSION=$(get_mission)
    M_KIND="${MISSION%% *}"
    M_ARGS="${MISSION#* }"
    
    case "$M_KIND" in
      search)
        OUT="$AFK_DIR/mission_${TIMESTAMP}.json"
        echo "[$(date)] Mission: search $M_ARGS"
        if ! python3 -m grlab search $M_ARGS --out "$OUT" --seed "$SEED"; then
          echo "[$(date)] Mission failed (sleep ${FAIL_SLEEP_SEC}s): search $M_ARGS" >&2
          sleep "$FAIL_SLEEP_SEC"
          continue
        fi
        ;;
      ecology)
        echo "[$(date)] Mission: ecology $M_ARGS"
        if ! python3 -m grlab ecology $M_ARGS > "$AFK_DIR/lindy_last.log" 2>&1; then
          echo "[$(date)] Mission failed (sleep ${FAIL_SLEEP_SEC}s): ecology $M_ARGS" >&2
          sleep "$FAIL_SLEEP_SEC"
        fi
        continue
        ;;
      *)
        echo "unknown mission kind: $M_KIND" >&2
        continue
        ;;
    esac

    # For the top 3 candidates from this search, run the GAUNTLET
    for i in {0..2}; do
        CAND_FILE="$AFK_DIR/cand_${TIMESTAMP}_${i}.json"
        
        # Extract candidate i
        TMP_CAND_FILE="$CAND_FILE.tmp"
        if ! python3 -c "import json; d=json.load(open('$OUT')); c=d['top'][$i]['candidate']; print(json.dumps(c))" > "$TMP_CAND_FILE" 2>/dev/null; then
          rm -f "$TMP_CAND_FILE" 2>/dev/null || true
          continue
        fi
        mv "$TMP_CAND_FILE" "$CAND_FILE"
        
        echo "Testing Candidate $i in Gauntlet..."
        if python3 -m grlab gauntlet --candidate "$CAND_FILE" --world examples/worlds/ipd_long.json; then
            PROMOTE_PATH="$PROMOTE_DIR/candidate_${TIMESTAMP}_v${i}.json"
            cp "$CAND_FILE" "$PROMOTE_PATH"
            # Legacy mirror for older tooling.
            cp "$CAND_FILE" "$PROMOTE_DIR_LEGACY/saint_${TIMESTAMP}_v${i}.json"
            echo "!!! GAUNTLET PASSED: PROMOTED $PROMOTE_PATH !!!"
        else
            rm -f "$CAND_FILE"
        fi
    done

    # Adversarial promotion: if we found a significant exploit.
    METRIC=$(python3 -c "import json; print(json.load(open('$OUT'))['metric'])" 2>/dev/null || echo "none")
    VAL=$(python3 -c "import json; print(json.load(open('$OUT'))['top'][0]['metric_value'])" 2>/dev/null || echo "0.0")
    if [[ "$METRIC" == "exploitation" ]] && python3 -c "import sys; sys.exit(0 if float('$VAL') > 0.5 else 1)"; then
        ADVERSARY_OUT="$ADVERSARY_DIR/adversary_${TIMESTAMP}_v${VAL}.json"
        python3 -c "import json; d=json.load(open('$OUT')); s=d['top'][0]['candidate']; s['id']='adversary_${TIMESTAMP}'; print(json.dumps(s, indent=2))" > "$ADVERSARY_OUT"
        # Legacy mirror for older tooling/specs.
        cp "$ADVERSARY_OUT" "$ADVERSARY_DIR_LEGACY/vampire_${TIMESTAMP}_v${VAL}.json"
        echo "!!! ADVERSARIAL SUCCESS: DISCOVERED NEW ADVERSARY $ADVERSARY_OUT !!!"
    fi

    # Cleanup logs
    (ls -t "$AFK_DIR"/mission_*.json | tail -n +51 | xargs rm -f) 2>/dev/null || true

    if [[ "$ONCE" == "1" ]]; then
      echo "[$(date)] --once set; exiting after one mission."
      exit 0
    fi
done
