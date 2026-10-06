import pathlib

from gpustorming_contract_lib import run_phrase_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_phrase_family_contract(
    ROOT,
    "gpustorming-openframe",
    family="openframe",
    operator_variant="search-open-neutralized, host-shell-detached, or source-root-replayed variant",
    privileges=["host-shell privilege", "source-open-overlay privilege", "in-search-view privilege"],
    crosswalk_text="search-hosted side panels, in-search page viewers, retained host-chrome source opens, or other source-open overlays",
    quarantine_id="QWS-0198",
    quarantine_text="open court / host-shell board / source-view controller",
    changelog_text="search-open-neutralized / host-shell-detached / source-root-replayed guard",
    archive_index_text="search-open-neutralized, host-shell-detached, or source-root-replayed control",
)
