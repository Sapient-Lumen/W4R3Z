import pathlib

from gpustorming_contract_lib import (
    canonical_group_titles,
    discover_gpustorming_families,
    families_for_group,
    family_bullet_needle,
    group_section_text,
    grouped_family_entries,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md"
text = DOC.read_text(encoding="utf-8")
required = [
    "# GPUstorming control-family crosswalks and sync guards",
    "## Why this surface exists",
    "## Current grouped families",
    "## Sync expectations",
    "## Explicit non-takes",
    "operator-tokens-and-bootstrap-grammar.md",
    "alias-packets-handle-collision-budgets-and-namespace-hygiene.md",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("crosswalk contract missing: " + ", ".join(missing))

previous_heading_index = -1
for title in canonical_group_titles():
    needle = f"### {title}"
    idx = text.find(needle)
    if idx == -1:
        raise SystemExit(f"crosswalk missing group heading for {title}")
    if idx <= previous_heading_index:
        raise SystemExit(f"crosswalk group headings out of canonical order near {title}")
    previous_heading_index = idx

previous_index = -1
for family in discover_gpustorming_families(ROOT):
    needle = family_bullet_needle(family)
    idx = text.find(needle)
    if idx == -1:
        raise SystemExit(f"crosswalk missing family bullet for {family}")
    if idx <= previous_index:
        raise SystemExit(f"crosswalk family bullets out of canonical order near {family}")
    previous_index = idx

for title, entries in grouped_family_entries():
    try:
        section = group_section_text(text, title)
    except KeyError as exc:
        raise SystemExit(str(exc))
    for family, needle in entries:
        if needle not in section:
            raise SystemExit(f"crosswalk placed {family} outside its canonical section {title}")

print("check_gpustorming_crosswalk_contract: OK")
