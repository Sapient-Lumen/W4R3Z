import pathlib

from gpustorming_contract_lib import run_standard_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_standard_family_contract(
    ROOT,
    "gpustorming-workspaceframe",
    family="workspaceframe",
    operator_variant="workspace-neutralized, project-state-reset, or underlier-replayed variant",
    privileges=["workspace privilege", "project-state privilege", "mutable-artifact privilege"],
    crosswalk_text="Canvas side panels, editable draft documents, generated study guides, custom interactive tools, or other in-search workspace artifacts",
    oq_variant="workspace-neutralized/project-state-reset/underlier-replayed variant",
    prompt_variant="workspace-neutralized, project-state-reset, or underlier-replayed variant worth checking",
    runbook_variant="workspace-neutralized, project-state-reset, or underlier-replayed variant",
    quarantine_id="QWS-0189",
    quarantine_text="workspace court / project-state board / mutable-artifact controller",
    changelog_text="workspace-neutralized / project-state-reset / underlier-replayed guard",
    archive_index_text="workspace-neutralized, project-state-reset, or underlier-replayed control",
)
