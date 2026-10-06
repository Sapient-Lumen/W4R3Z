import pathlib

from gpustorming_contract_lib import (
    GPUSTORMING_LATE_SEARCH_BATCH_CHECKER,
    late_search_full_family_contract_kwargs,
    late_search_surface_families,
    validate_late_search_contract_defaults,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

validate_late_search_contract_defaults()
if not (TOOLS / GPUSTORMING_LATE_SEARCH_BATCH_CHECKER).exists():
    raise SystemExit(f"missing late-search batch checker: {GPUSTORMING_LATE_SEARCH_BATCH_CHECKER}")
for family in late_search_surface_families():
    payload = late_search_full_family_contract_kwargs(family)
    for key in ["quarantine_id", "quarantine_text", "changelog_text", "archive_index_text"]:
        if not payload.get(key):
            raise SystemExit(f"late-search family {family} missing batched {key}")
print("check_gpustorming_late_search_sync: OK")
