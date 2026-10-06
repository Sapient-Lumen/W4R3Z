import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-scoreframe", {
    "docs/10-method/operator-tokens-and-bootstrap-grammar.md": [
        "rubric-permuted, score-id-swapped, or score-anchor-neutralized variant",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
    ],
    "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md": [
        "rubric-permuted, score-id-swapped, or score-anchor-neutralized variant",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
    ],
    "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md": [
        "- **scoreframe**",
        "rubric ordering, score IDs, or in-context score anchors",
    ],
    "docs/00-meta/trajectory-map.md": [
        "A parallel scoreframe extension",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
        trajectory_problem_phrase("scoreframe"),
    ],
    "docs/20-constitution/open-question-registry.md": [
        "rubric-permuted/score-id-swapped/score-anchor-neutralized variant",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
    ],
    "docs/50-promptcraft/prompt-pairs.md": [
        "rubric-permuted, score-id-swapped, or score-anchor-neutralized variant worth checking",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
    ],
    "docs/00-meta/llm-runbook.md": [
        "rubric-permuted, score-id-swapped, or score-anchor-neutralized variant",
        "rubric-order privilege",
        "score-ID privilege",
        "reference-score-anchor privilege",
    ],
    "docs/90-quarantine/wild-speculations-2026-03-08.md": [
        "QWS-0174",
        "scoring court, rubric-order scaffold, or score-id controller",
    ],
    "CHANGELOG.md": [
        "rubric-permuted / score-id-swapped / score-anchor-neutralized guard",
        "check_gpustorming_scoreframe_contract.py",
    ],
    "ARCHIVE_INDEX.md": [
        "rubric-permuted, score-id-swapped, or score-anchor-neutralized control",
    ],
})
print("check_gpustorming_scoreframe_contract: OK")
