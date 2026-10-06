import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-citationframe", standard_family_contract_map(
    family="citationframe",
    operator_variant="citation-hidden, reference-link-scrubbed, or source-card-neutralized variant",
    privileges=["citation privilege", "reference-link privilege", "source-card privilege"],
    crosswalk_text="inline citation badges, reference links, source cards, or used-sources panels",
    oq_variant="citation-hidden/reference-link-scrubbed/source-card-neutralized variant",
    prompt_variant="citation-hidden, reference-link-scrubbed, or source-card-neutralized variant worth checking",
    runbook_variant="citation-hidden, reference-link-scrubbed, or source-card-neutralized variant",
    quarantine_id="QWS-0185",
    quarantine_text="citation court / attribution board / link-rights controller",
    changelog_text="citation-hidden / reference-link-scrubbed / source-card-neutralized guard",
    archive_index_text="citation-hidden, reference-link-scrubbed, or source-card-neutralized control",
))
print("check_gpustorming_citationframe_contract: OK")
