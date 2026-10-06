import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-consensus", {
    "docs/10-method/operator-tokens-and-bootstrap-grammar.md": [
        "consensus-blanded, majority-scrubbed, or popularity-neutralized variant",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
    ],
    "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md": [
        "consensus-blanded, majority-scrubbed, or popularity-neutralized variant",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
    ],
    "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md": [
        "- **consensus**",
        "majority endorsements, popularity counts, consensus labels, or peer-preference scaffolds",
    ],
    "docs/00-meta/trajectory-map.md": [
        "A parallel consensus extension",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
        trajectory_problem_phrase("consensus"),
    ],
    "docs/20-constitution/open-question-registry.md": [
        "consensus-blanded/majority-scrubbed/popularity-neutralized variant",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
    ],
    "docs/50-promptcraft/prompt-pairs.md": [
        "consensus-blanded, majority-scrubbed, or popularity-neutralized variant worth checking",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
    ],
    "docs/00-meta/llm-runbook.md": [
        "consensus-blanded, majority-scrubbed, or popularity-neutralized variant",
        "consensus-signal privilege",
        "majority-label privilege",
        "popularity-glamour privilege",
    ],
    "docs/90-quarantine/wild-speculations-2026-03-08.md": [
        "QWS-0175",
        "consensus court / bandwagon scaffold / popularity controller",
    ],
    "CHANGELOG.md": [
        "consensus-blanded / majority-scrubbed / popularity-neutralized guard",
        "check_gpustorming_consensus_contract.py",
    ],
    "ARCHIVE_INDEX.md": [
        "consensus-blanded, majority-scrubbed, or popularity-neutralized control",
    ],
})
print("check_gpustorming_consensus_contract: OK")
