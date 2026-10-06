import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from core_method_contract_lib import CoreMethodContractError, core_method_negative_canary_results
from core_method_contract_specs import iter_core_method_contract_specs

try:
    results = core_method_negative_canary_results(ROOT, list(iter_core_method_contract_specs()))
except CoreMethodContractError as exc:
    raise SystemExit(str(exc)) from exc
failures = [row for row in results if row.get("status") != "pass"]
if failures:
    preview = "; ".join(f"{row['id']}: {row.get('observed_failure')!r}" for row in failures[:3])
    raise SystemExit("core-method negative canary failure: " + preview)
print(f"check_core_method_batch_negative_canaries: OK ({len(results)} mutation canaries)")
