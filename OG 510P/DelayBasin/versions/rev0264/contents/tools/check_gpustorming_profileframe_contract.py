import pathlib

from gpustorming_contract_lib import run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-profileframe",
    family="profileframe",
    operator_variant="profile-blinded, history-disconnected, or public-basis-replayed variant",
    privileges=["profile privilege", "personal-context privilege", "history-carry privilege"],
    crosswalk_text="saved memories, past-search carryover, connected Gmail or Photos context, or other personal-context profile surfaces",
    oq_variant="profile-blinded/history-disconnected/public-basis-replayed variant",
    prompt_variant="profile-blinded, history-disconnected, or public-basis-replayed variant worth checking",
    runbook_variant="profile-blinded, history-disconnected, or public-basis-replayed variant",
    quarantine_id="QWS-0190",
    quarantine_text="profile court / personal-context board / memory-eligibility controller",
    changelog_text="profile-blinded / history-disconnected / public-basis-replayed guard",
    archive_index_text="profile-blinded, history-disconnected, or public-basis-replayed control",
)
