import pathlib

from gpustorming_contract_lib import run_phrase_family_contract

ROOT = pathlib.Path(__file__).resolve().parents[1]

run_phrase_family_contract(
    ROOT,
    "gpustorming-warningframe",
    family="warningframe",
    operator_variant="warning-hidden, caution-scrubbed, or confidence-label-neutralized variant",
    privileges=["warning-banner privilege", "caution-strip privilege", "confidence-label privilege"],
    crosswalk_text="warning banners, low-confidence labels, may-not-be-reliable notices, or evolving-information strips",
    quarantine_id="QWS-0186",
    quarantine_text="warning court / caution board / reliability-banner controller",
    changelog_text="warning-hidden / caution-scrubbed / confidence-label-neutralized guard",
    archive_index_text="warning-hidden, caution-scrubbed, or confidence-label-neutralized control",
)
