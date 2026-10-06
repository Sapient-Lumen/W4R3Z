import pathlib

from gpustorming_contract_lib import ensure_needles, standard_family_contract_map

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-sourcecluster", standard_family_contract_map(
    family="sourcecluster",
    operator_variant="cluster-collapsed, syndication-scrubbed, or independence-counted variant",
    privileges=['source-salience privilege', 'same-origin multiplicity privilege', 'pseudo-corroboration privilege'],
    crosswalk_text="same-source grouped cards, syndicated mirrors, publisher-network duplicates, or repeated-origin result clusters",
    trajectory_intro="A parallel sourcecluster extension",
    oq_variant="cluster-collapsed/syndication-scrubbed/independence-counted variant",
    prompt_variant="cluster-collapsed, syndication-scrubbed, or independence-counted variant worth checking",
    runbook_variant="cluster-collapsed, syndication-scrubbed, or independence-counted variant",
    quarantine_id="QWS-0182",
    quarantine_text="independence court / corroboration board / source-cluster controller",
    changelog_text="cluster-collapsed / syndication-scrubbed / independence-counted guard",
    archive_index_text="cluster-collapsed, syndication-scrubbed, or independence-counted control",
))
print("check_gpustorming_sourcecluster_contract: OK")
