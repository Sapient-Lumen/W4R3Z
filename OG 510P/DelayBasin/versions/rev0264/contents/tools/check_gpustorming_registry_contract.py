import pathlib

from gpustorming_contract_lib import EXCLUDED_GPUSTORMING_CONTRACTS, expected_gpustorming_family_contract_names

ROOT = pathlib.Path(__file__).resolve().parents[1]

expected = set(expected_gpustorming_family_contract_names())
present = {
    path.name
    for path in (ROOT / "tools").glob("check_gpustorming*_contract.py")
    if path.name not in EXCLUDED_GPUSTORMING_CONTRACTS
}

missing = sorted(expected - present)
extra = sorted(present - expected)
if missing or extra:
    raise SystemExit(f"gpustorming registry drift: missing={missing} extra={extra}")

print("check_gpustorming_registry_contract: OK")
