import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-deepframe",
    **late_search_standard_family_contract_kwargs("deepframe"),
    quarantine_id="QWS-0193",
    quarantine_text="deep court / exploration-budget board / research-plan controller",
    changelog_text="deep-neutralized / breadth-capped / seed-query-replayed guard",
    archive_index_text="deep-neutralized, breadth-capped, or seed-query-replayed control",
)
