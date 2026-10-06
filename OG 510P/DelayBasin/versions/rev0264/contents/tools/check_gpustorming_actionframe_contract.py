import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-actionframe",
    **late_search_standard_family_contract_kwargs("actionframe"),
    quarantine_id="QWS-0188",
    quarantine_text="action court / task-router board / partner-execution controller",
    changelog_text="action-neutralized / partner-link-scrubbed / manual-route-replayed guard",
    archive_index_text="action-neutralized, partner-link-scrubbed, or manual-route-replayed control",
)
