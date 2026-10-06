import pathlib

from gpustorming_contract_lib import run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-handoffframe",
    family="handoffframe",
    operator_variant="handoff-neutralized, context-reset, or manual-query-replayed variant",
    privileges=["handoff privilege", "context-carry privilege", "next-query privilege"],
    crosswalk_text="follow-up question prompts, continue-exploring links, dive-deeper transitions, or suggested next searches",
    oq_variant="handoff-neutralized/context-reset/manual-query-replayed variant",
    prompt_variant="handoff-neutralized, context-reset, or manual-query-replayed variant worth checking",
    runbook_variant="handoff-neutralized, context-reset, or manual-query-replayed variant",
    quarantine_id="QWS-0187",
    quarantine_text="handoff court / route-transfer board / next-query controller",
    changelog_text="handoff-neutralized / context-reset / manual-query-replayed guard",
    archive_index_text="handoff-neutralized, context-reset, or manual-query-replayed control",
)
