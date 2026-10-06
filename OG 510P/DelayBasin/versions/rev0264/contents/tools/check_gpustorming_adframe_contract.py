import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-adframe",
    **late_search_standard_family_contract_kwargs("adframe"),
    quarantine_id="QWS-0194",
    quarantine_text="ad court / sponsor-placement board / monetization-eligibility controller",
    changelog_text="ad-hidden / sponsor-scrubbed / organic-basis-replayed guard",
    archive_index_text="ad-hidden, sponsor-scrubbed, or organic-basis-replayed control",
)
