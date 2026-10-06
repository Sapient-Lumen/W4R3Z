import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-catalogframe",
    **late_search_standard_family_contract_kwargs("catalogframe"),
    quarantine_id="QWS-0196",
    quarantine_text="catalog court / merchant-feed board / inventory-eligibility controller",
    changelog_text="catalog-neutralized / feed-disconnected / open-web-replayed guard",
    archive_index_text="catalog-neutralized, feed-disconnected, or open-web-replayed control",
)
