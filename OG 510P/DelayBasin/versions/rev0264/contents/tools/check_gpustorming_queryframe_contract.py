import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-queryframe", standard_family_contract_map(
    family="queryframe",
    operator_variant="query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant",
    privileges=['query-slant privilege', 'retrieval-wording privilege', 'evidence-selection privilege'],
    crosswalk_text="benefits/risks search phrasing, loaded retrieval synonyms, slanted issue terms, or filter-label prompts",
    trajectory_intro="A parallel queryframe extension",
    oq_variant="query-blanded/slant-scrubbed/retrieval-phrase-swapped variant",
    prompt_variant="query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant worth checking",
    runbook_variant="query-blanded, slant-scrubbed, or retrieval-phrase-swapped variant",
    quarantine_id="QWS-0178",
    quarantine_text="search court / query-routing board / retrieval-bias controller",
    changelog_text="query-blanded / slant-scrubbed / retrieval-phrase-swapped guard",
    archive_index_text="query-blanded, slant-scrubbed, or retrieval-phrase-swapped control",
))
print("check_gpustorming_queryframe_contract: OK")
