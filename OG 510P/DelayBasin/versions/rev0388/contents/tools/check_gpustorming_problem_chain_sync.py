import pathlib

from gpustorming_contract_lib import (
    late_search_problem_chain_anchor_families,
    late_search_standard_family_contract_kwargs,
    trajectory_problem_phrase,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRE_TAIL, TAIL = late_search_problem_chain_anchor_families()
TAIL_KW = late_search_standard_family_contract_kwargs(TAIL)

CHECKS = [
    ("docs/00-meta/trajectory-map.md", [trajectory_problem_phrase(PRE_TAIL), trajectory_problem_phrase(TAIL)]),
    ("docs/20-constitution/open-question-registry.md", [TAIL_KW["oq_variant"], *TAIL_KW["privileges"]]),
]

for rel, needles in CHECKS:
    text = (ROOT / rel).read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            raise SystemExit(f"check_gpustorming_problem_chain_sync: {rel} missing required text: {needle}")

print("check_gpustorming_problem_chain_sync: OK")
