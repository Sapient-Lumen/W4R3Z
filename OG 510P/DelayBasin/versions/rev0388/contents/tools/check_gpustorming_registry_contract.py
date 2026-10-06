import pathlib

from gpustorming_contract_lib import (
    EXCLUDED_GPUSTORMING_CONTRACTS,
    GPUSTORMING_LATE_SEARCH_BATCH_CHECKER,
    GPUSTORMING_STANDARD_BATCH_CHECKER,
    expected_gpustorming_family_contract_names,
    late_search_surface_families,
    standalone_gpustorming_families,
    standard_family_batch_families,
)
from gpustorming_standard_contract_specs import GPUSTORMING_STANDARD_CONTRACT_SPECS

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

expected = set(expected_gpustorming_family_contract_names())
present = {
    path.name
    for path in TOOLS.glob("check_gpustorming*_contract.py")
    if path.name not in EXCLUDED_GPUSTORMING_CONTRACTS
}

missing = sorted(expected - {GPUSTORMING_STANDARD_BATCH_CHECKER})
extra = sorted(present)
if missing or extra:
    raise SystemExit(f"gpustorming registry drift: missing={missing} extra={extra}")
for checker in [GPUSTORMING_STANDARD_BATCH_CHECKER, GPUSTORMING_LATE_SEARCH_BATCH_CHECKER]:
    if not (TOOLS / checker).exists():
        raise SystemExit(f"missing batched GPustorming checker: {checker}")
if standalone_gpustorming_families():
    raise SystemExit("standalone GPustorming wrappers should be empty after batching")
standard = {row.get("family") for row in GPUSTORMING_STANDARD_CONTRACT_SPECS}
expected_standard = set(standard_family_batch_families())
if standard != expected_standard:
    raise SystemExit(f"standard GPustorming batch families drift: missing={sorted(expected_standard-standard)} extra={sorted(standard-expected_standard)}")
if standard & set(late_search_surface_families()):
    raise SystemExit("standard and late-search GPustorming batch memberships overlap")
print("check_gpustorming_registry_contract: OK")
