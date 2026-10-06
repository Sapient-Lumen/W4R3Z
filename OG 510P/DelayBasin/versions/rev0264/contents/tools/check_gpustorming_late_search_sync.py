import pathlib

from gpustorming_contract_lib import expected_late_search_family_contract_names, late_search_surface_families, validate_late_search_contract_defaults

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

validate_late_search_contract_defaults()
missing = [name for name in expected_late_search_family_contract_names() if not (TOOLS / name).exists()]
if missing:
    raise SystemExit(f"missing late-search family contract files: {missing}")

for family in late_search_surface_families():
    path = TOOLS / f"check_gpustorming_{family}_contract.py"
    if not path.exists():
        raise SystemExit(f"missing contract checker for {family}")

print("check_gpustorming_late_search_sync: OK")
