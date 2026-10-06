import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-warningframe", standard_family_contract_map(
    family="warningframe",
    operator_variant="warning-hidden, caution-scrubbed, or confidence-label-neutralized variant",
    privileges=["warning-banner privilege", "caution-strip privilege", "confidence-label privilege"],
    crosswalk_text="warning banners, low-confidence labels, may-not-be-reliable notices, or evolving-information strips",
    oq_variant="warning-hidden/caution-scrubbed/confidence-label-neutralized variant",
    prompt_variant="warning-hidden, caution-scrubbed, or confidence-label-neutralized variant worth checking",
    runbook_variant="warning-hidden, caution-scrubbed, or confidence-label-neutralized variant",
    quarantine_id="QWS-0186",
    quarantine_text="warning court / caution board / reliability-banner controller",
    changelog_text="warning-hidden / caution-scrubbed / confidence-label-neutralized guard",
    archive_index_text="warning-hidden, caution-scrubbed, or confidence-label-neutralized control",
))

print("check_gpustorming_warningframe_contract: OK")
