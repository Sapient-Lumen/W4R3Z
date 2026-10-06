import pathlib

from gpustorming_contract_lib import late_search_surface_families, late_search_variant, ordered_needles_for_family_sequence, validate_late_search_contract_defaults

ROOT = pathlib.Path(__file__).resolve().parents[1]
validate_late_search_contract_defaults()
FAMILIES = late_search_surface_families()

CHECKS = [
    (
        "docs/00-meta/trajectory-map.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES, formatter=lambda family: f"A parallel {family} extension"
        ),
    ),
    (
        "docs/10-method/operator-tokens-and-bootstrap-grammar.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES,
            formatter=lambda family: late_search_variant(family, "operator"),
        ),
    ),
    (
        "docs/20-constitution/open-question-registry.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES,
            formatter=lambda family: late_search_variant(family, "oq"),
        ),
    ),
    (
        "docs/50-promptcraft/prompt-pairs.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES,
            formatter=lambda family: late_search_variant(family, "prompt"),
        ),
    ),
    (
        "docs/50-promptcraft/prompt-pairs.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES,
            formatter=lambda family: late_search_variant(family, "alias_prompt"),
        ),
    ),
    (
        "docs/00-meta/llm-runbook.md",
        ordered_needles_for_family_sequence(
            families=FAMILIES,
            formatter=lambda family: late_search_variant(family, "operator"),
        ),
    ),
]

for rel, needles in CHECKS:
    text = (ROOT / rel).read_text(encoding="utf-8")
    positions = []
    for needle in needles:
        idx = text.find(needle)
        if idx == -1:
            raise SystemExit(f"check_gpustorming_path_sync: {rel} missing required text: {needle}")
        positions.append(idx)
    if positions != sorted(positions):
        raise SystemExit(
            f"check_gpustorming_path_sync: {rel} has late-search family order drift for {FAMILIES}"
        )

print("check_gpustorming_path_sync: OK")
