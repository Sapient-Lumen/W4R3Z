import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-novelty", {
    "docs/10-method/operator-tokens-and-bootstrap-grammar.md": [
        "time-tag-neutralized, recency-scrubbed, or novelty-blanded variant",
        "recency-label privilege",
        "legacy-label privilege",
    ],
    "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md": [
        "time-tag-neutralized, recency-scrubbed, or novelty-blanded variant",
        "recency-label privilege",
        "legacy-label privilege",
    ],
    "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md": [
        "- **novelty**",
        "recent/current/new/updated labels, legacy/old/deprecated labels, explicit timestamps, or novelty/innovation cues",
    ],
    "docs/00-meta/trajectory-map.md": [
        "A parallel novelty extension",
        "recency-label privilege",
        "legacy-label privilege",
        trajectory_problem_phrase("novelty"),
    ],
    "docs/20-constitution/open-question-registry.md": [
        "time-tag-neutralized/recency-scrubbed/novelty-blanded variant",
        "recency-label privilege",
        "legacy-label privilege",
    ],
    "docs/50-promptcraft/prompt-pairs.md": [
        "time-tag-neutralized, recency-scrubbed, or novelty-blanded variant worth checking",
        "recency-label privilege",
        "legacy-label privilege",
    ],
    "docs/00-meta/llm-runbook.md": [
        "time-tag-neutralized, recency-scrubbed, or novelty-blanded variant",
        "recency-label privilege",
        "legacy-label privilege",
    ],
    "docs/90-quarantine/wild-speculations-2026-03-08.md": [
        "QWS-0173",
        "temporal-origin court / recency-prestige scaffold / novelty-default controller",
    ],
    "CHANGELOG.md": [
        "time-tag-neutralized / recency-scrubbed / novelty-blanded guard",
        "check_gpustorming_novelty_contract.py",
    ],
    "ARCHIVE_INDEX.md": [
        "time-tag-neutralized, recency-scrubbed, or novelty-blanded control",
    ],
})
print("check_gpustorming_novelty_contract: OK")
