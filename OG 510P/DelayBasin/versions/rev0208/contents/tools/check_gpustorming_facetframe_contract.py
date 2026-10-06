import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-facetframe", standard_family_contract_map(
    family="facetframe",
    operator_variant="facet-hidden, route-scrubbed, or related-question-neutralized variant",
    privileges=['facet privilege', 'aspect-route privilege', 'related-question privilege'],
    crosswalk_text="People Also Ask ladders, related-search modules, facet tabs, or refine-this-search chips",
    trajectory_intro="A parallel facetframe extension",
    oq_variant="facet-hidden/route-scrubbed/related-question-neutralized variant",
    prompt_variant="facet-hidden, route-scrubbed, or related-question-neutralized variant worth checking",
    runbook_variant="facet-hidden, route-scrubbed, or related-question-neutralized variant",
    quarantine_id="QWS-0183",
    quarantine_text="navigation court / route-selection board / aspect-facet controller",
    changelog_text="facet-hidden / route-scrubbed / related-question-neutralized guard",
    archive_index_text="facet-hidden, route-scrubbed, or related-question-neutralized control",
))
print("check_gpustorming_facetframe_contract: OK")
