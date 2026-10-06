import pathlib

from gpustorming_contract_lib import run_phrase_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_phrase_family_contract(
    ROOT,
    "gpustorming-citationframe",
    family="citationframe",
    operator_variant="citation-hidden, reference-link-scrubbed, or source-card-neutralized variant",
    privileges=["citation privilege", "reference-link privilege", "source-card privilege"],
    crosswalk_text="inline citation badges, reference links, source cards, or used-sources panels",
    quarantine_id="QWS-0185",
    quarantine_text="citation court / attribution board / link-rights controller",
    changelog_text="citation-hidden / reference-link-scrubbed / source-card-neutralized guard",
    archive_index_text="citation-hidden, reference-link-scrubbed, or source-card-neutralized control",
)
