import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-rankframe", standard_family_contract_map(
    family="rankframe",
    operator_variant="order-balanced, position-scrubbed, or top-slot-neutralized variant",
    privileges=['rank privilege', 'top-slot privilege', 'order-primacy privilege'],
    crosswalk_text="top-ranked placement, first-card position, search-result reorder advantage, or other raw list-position privilege",
    oq_variant="order-balanced/position-scrubbed/top-slot-neutralized variant",
    prompt_variant="order-balanced, position-scrubbed, or top-slot-neutralized variant worth checking",
    runbook_variant="order-balanced, position-scrubbed, or top-slot-neutralized variant",
    quarantine_id="QWS-0184",
    quarantine_text="ranking court / top-slot board / order-primacy controller",
    changelog_text="order-balanced / position-scrubbed / top-slot-neutralized guard",
    archive_index_text="order-balanced, position-scrubbed, or top-slot-neutralized control",
))
print("check_gpustorming_rankframe_contract: OK")
