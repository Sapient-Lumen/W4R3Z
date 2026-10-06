import pathlib

from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ROOT = pathlib.Path(__file__).resolve().parents[1]

ensure_needles(ROOT, "gpustorming-formatting", {
    "docs/10-method/operator-tokens-and-bootstrap-grammar.md": [
        "markup-blanded, list-shape-swapped, or presentation-neutralized variant",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
    ],
    "docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md": [
        "markup-blanded, list-shape-swapped, or presentation-neutralized variant",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
    ],
    "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md": [
        "- **formatting**",
        "markdown wrappers, bullet or table layout, headings, code fences, comments, spacing, or other presentation scaffolds",
    ],
    "docs/00-meta/trajectory-map.md": [
        "A parallel formatting extension",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
        trajectory_problem_phrase("formatting"),
    ],
    "docs/20-constitution/open-question-registry.md": [
        "markup-blanded/list-shape-swapped/presentation-neutralized variant",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
    ],
    "docs/50-promptcraft/prompt-pairs.md": [
        "markup-blanded, list-shape-swapped, or presentation-neutralized variant worth checking",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
    ],
    "docs/00-meta/llm-runbook.md": [
        "markup-blanded, list-shape-swapped, or presentation-neutralized variant",
        "markup privilege",
        "list-shape privilege",
        "presentation-scaffold privilege",
    ],
    "docs/90-quarantine/wild-speculations-2026-03-08.md": [
        "QWS-0176",
        "format court / markdown-scaffold / presentation controller",
    ],
    "CHANGELOG.md": [
        "markup-blanded / list-shape-swapped / presentation-neutralized guard",
        "check_gpustorming_formatting_contract.py",
    ],
    "ARCHIVE_INDEX.md": [
        "markup-blanded, list-shape-swapped, or presentation-neutralized control",
    ],
})
print("check_gpustorming_formatting_contract: OK")
