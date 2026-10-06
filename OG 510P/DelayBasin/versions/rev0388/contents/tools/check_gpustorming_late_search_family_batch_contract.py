import pathlib

from gpustorming_contract_lib import (
    late_search_full_family_contract_kwargs,
    late_search_surface_families,
    run_standard_family_contract,
    validate_late_search_contract_defaults,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
validate_late_search_contract_defaults()
for family in late_search_surface_families():
    run_standard_family_contract(
        ROOT,
        f"gpustorming-{family}",
        **late_search_full_family_contract_kwargs(family),
    )
print("check_gpustorming_late_search_family_batch_contract: OK")
