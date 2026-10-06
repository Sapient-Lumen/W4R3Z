import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-prefill", standard_family_contract_map(
    family="prefill",
    operator_variant="blank-started, prefill-scrubbed, or suggestion-free variant",
    privileges=['prefill privilege', 'prompt-suggestion privilege', 'starter-example privilege'],
    crosswalk_text="prefilled starters, suggested prompt chips, autocomplete shells, example-library scaffolds, or copied template frames",
    trajectory_intro="A parallel prefill extension",
    oq_variant="blank-started/prefill-scrubbed/suggestion-free variant",
    prompt_variant="blank-started, prefill-scrubbed, or suggestion-free variant worth checking",
    runbook_variant="blank-started, prefill-scrubbed, or suggestion-free variant",
    quarantine_id="QWS-0177",
    quarantine_text="suggestion court / default-scaffold / prompt-chip controller",
    changelog_text="blank-started / prefill-scrubbed / suggestion-free guard",
    archive_index_text="blank-started, prefill-scrubbed, or suggestion-free control",
))
print("check_gpustorming_prefill_contract: OK")
