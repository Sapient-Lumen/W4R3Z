import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-reasonframe", standard_family_contract_map(
    family="reasonframe",
    operator_variant="why-hidden, explanation-scrubbed, or rationale-swapped variant",
    privileges=['explanation-frame privilege', 'why-this-result privilege', 'trust-cue privilege'],
    crosswalk_text="why this result blurbs, explanation chips, coverage notes, or other rationale surfaces",
    trajectory_intro="A parallel reasonframe extension",
    oq_variant="why-hidden/explanation-scrubbed/rationale-swapped variant",
    prompt_variant="why-hidden, explanation-scrubbed, or rationale-swapped variant worth checking",
    runbook_variant="why-hidden, explanation-scrubbed, or rationale-swapped variant",
    quarantine_id="QWS-0179",
    quarantine_text="contest court / result-appeal board / explanation-rights controller",
    changelog_text="why-hidden / explanation-scrubbed / rationale-swapped guard",
    archive_index_text="why-hidden, explanation-scrubbed, or rationale-swapped control",
))
print("check_gpustorming_reasonframe_contract: OK")
