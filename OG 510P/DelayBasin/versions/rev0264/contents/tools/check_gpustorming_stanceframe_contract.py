import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-stanceframe", standard_family_contract_map(
    family="stanceframe",
    operator_variant="stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant",
    privileges=['stance-label privilege', 'viewpoint-balance privilege', 'counterposition-cue privilege'],
    crosswalk_text="pro/con/neutral badges, balanced-vs-biased markers, or other stance overlays",
    trajectory_intro="A parallel stanceframe extension",
    oq_variant="stance-hidden/stance-label-scrubbed/balance-badge-neutralized variant",
    prompt_variant="stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant worth checking",
    runbook_variant="stance-hidden, stance-label-scrubbed, or balance-badge-neutralized variant",
    quarantine_id="QWS-0180",
    quarantine_text="stance court / balance board / counterposition-rights controller",
    changelog_text="stance-hidden / stance-label-scrubbed / balance-badge-neutralized guard",
    archive_index_text="stance-hidden, stance-label-scrubbed, or balance-badge-neutralized control",
))
print("check_gpustorming_stanceframe_contract: OK")
