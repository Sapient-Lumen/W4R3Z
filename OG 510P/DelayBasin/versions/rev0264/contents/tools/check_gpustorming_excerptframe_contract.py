import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-excerptframe", standard_family_contract_map(
    family="excerptframe",
    operator_variant="span-balanced, excerpt-scrubbed, or counterspan-included variant",
    privileges=['supporting-span privilege', 'highlight-window privilege', 'excerpt-selection privilege'],
    crosswalk_text="highlighted passages, chosen supporting excerpts, bolded snippet spans, or top-snippet sentences",
    trajectory_intro="A parallel excerptframe extension",
    oq_variant="span-balanced/excerpt-scrubbed/counterspan-included variant",
    prompt_variant="span-balanced, excerpt-scrubbed, or counterspan-included variant worth checking",
    runbook_variant="span-balanced, excerpt-scrubbed, or counterspan-included variant",
    quarantine_id="QWS-0181",
    quarantine_text="excerpt court / highlight-window board / snippet-span controller",
    changelog_text="span-balanced / excerpt-scrubbed / counterspan-included guard",
    archive_index_text="span-balanced, excerpt-scrubbed, or counterspan-included control",
))
print("check_gpustorming_excerptframe_contract: OK")
