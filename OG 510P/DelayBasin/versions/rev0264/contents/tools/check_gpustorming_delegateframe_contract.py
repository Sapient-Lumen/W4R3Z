import pathlib

from gpustorming_contract_lib import late_search_standard_family_contract_kwargs, run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-delegateframe",
    **late_search_standard_family_contract_kwargs("delegateframe"),
    quarantine_id="QWS-0195",
    quarantine_text="delegate court / authority-transfer board / permission-budget controller",
    changelog_text="delegate-neutralized / authority-withdrawn / manual-steps-replayed guard",
    archive_index_text="delegate-neutralized, authority-withdrawn, or manual-steps-replayed control",
)
