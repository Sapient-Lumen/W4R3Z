# Aggregates locality-sized core method contract spec segments.
# These rows preserve simple one-file method/state contract checks without wrapper regrowth.

from collections.abc import Iterator

from core_method_contract_specs_part_1 import CORE_METHOD_CONTRACT_SPECS_PART_1
from core_method_contract_specs_part_2 import CORE_METHOD_CONTRACT_SPECS_PART_2

CORE_METHOD_CONTRACT_SPEC_SEGMENTS = [
    ("tools/core_method_contract_specs_part_1.py", CORE_METHOD_CONTRACT_SPECS_PART_1),
    ("tools/core_method_contract_specs_part_2.py", CORE_METHOD_CONTRACT_SPECS_PART_2),
]


def iter_core_method_contract_specs() -> Iterator[tuple[str, dict]]:
    for segment_path, rows in CORE_METHOD_CONTRACT_SPEC_SEGMENTS:
        for row in rows:
            yield segment_path, row


CORE_METHOD_CONTRACT_SPECS = [row for _segment_path, row in iter_core_method_contract_specs()]
CORE_METHOD_CONTRACT_SPEC_PARTS = [segment_path for segment_path, _rows in CORE_METHOD_CONTRACT_SPEC_SEGMENTS]
