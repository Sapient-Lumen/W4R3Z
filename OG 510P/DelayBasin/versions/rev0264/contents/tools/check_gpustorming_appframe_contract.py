import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-appframe",
    **late_search_standard_family_contract_kwargs("appframe"),
    quarantine_id="QWS-0197",
    quarantine_text="app court / connector-eligibility board / widget-governance controller",
    changelog_text="app-neutralized / widget-detached / host-only-replayed guard",
    archive_index_text="app-neutralized, widget-detached, or host-only-replayed control",
)
