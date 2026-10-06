import json
import pathlib

from canary_runs_lib import build_canary_runs

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "CANARY-RUNS.json"
if not PATH.exists():
    raise SystemExit("missing CANARY-RUNS.json")
observed = json.loads(PATH.read_text(encoding="utf-8"))
expected = build_canary_runs(ROOT)
if observed != expected:
    raise SystemExit("CANARY-RUNS.json drifted; run tools/gen_canary_runs.py")
scorecard = observed.get("scorecard", {})
if scorecard.get("observed_score") != scorecard.get("max_score") or scorecard.get("passing") is not True:
    raise SystemExit("CANARY-RUNS.json scorecard is not passing")
if len(observed.get("negative_mutation_runs", [])) < 25:
    raise SystemExit("CANARY-RUNS.json must include core-method, artifact-smoke, and release-integrity negative mutation runs")
positive_ids = {row.get("id") for row in observed.get("positive_runs", [])}
if "package-artifact-smoke-mutation-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing package artifact smoke mutation canary score row")
if "package-deterministic-zip-writer-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing deterministic zip writer canary score row")
if "release-filename-identity-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing release filename identity canary score row")
if "package-sha256-sidecar-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing package SHA256 sidecar canary score row")
if "release-integrity-mutation-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing release integrity mutation canary score row")
if "ledger-coldstore-mutation-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing ledger coldstore mutation canary score row")
if "receipt-coldstore-mutation-canaries" not in positive_ids:
    raise SystemExit("CANARY-RUNS.json missing receipt coldstore mutation canary score row")
if len(observed.get("deterministic_writer_rows", [])) < 5:
    raise SystemExit("CANARY-RUNS.json must include deterministic writer canary rows")
if len(observed.get("release_identity_rows", [])) < 7:
    raise SystemExit("CANARY-RUNS.json must include release identity canary rows")
if len(observed.get("sidecar_rows", [])) < 5:
    raise SystemExit("CANARY-RUNS.json must include package sidecar canary rows")
if len(observed.get("release_integrity_rows", [])) < 7:
    raise SystemExit("CANARY-RUNS.json must include release integrity canary rows")
if len(observed.get("ledger_coldstore_rows", [])) < 7:
    raise SystemExit("CANARY-RUNS.json must include ledger coldstore canary rows")
if len(observed.get("receipt_coldstore_rows", [])) < 7:
    raise SystemExit("CANARY-RUNS.json must include receipt coldstore canary rows")
for bad in ["canary-run-court", "release-legitimacy-notary", "registry-bureaucracy-ratchet"]:
    if bad not in observed.get("non_claim", ""):
        raise SystemExit(f"CANARY-RUNS.json missing non-claim {bad}")
print("check_canary_runs_contract: OK")
