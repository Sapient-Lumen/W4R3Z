# Aggregates locality-sized declarative GPustorming standard contract specs.
# The batch checker consumes the maps directly; it never executes stored source.

from collections.abc import Iterator

from gpustorming_standard_contract_specs_part_1 import GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_1
from gpustorming_standard_contract_specs_part_2 import GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_2
from gpustorming_standard_contract_specs_part_3 import GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_3
from gpustorming_standard_contract_specs_part_4 import GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_4

GPUSTORMING_STANDARD_CONTRACT_SPEC_SEGMENTS = [
    ("tools/gpustorming_standard_contract_specs_part_1.py", GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_1),
    ("tools/gpustorming_standard_contract_specs_part_2.py", GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_2),
    ("tools/gpustorming_standard_contract_specs_part_3.py", GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_3),
    ("tools/gpustorming_standard_contract_specs_part_4.py", GPUSTORMING_STANDARD_CONTRACT_SPECS_PART_4),
]


def iter_gpustorming_standard_contract_specs() -> Iterator[tuple[str, dict]]:
    for segment_path, rows in GPUSTORMING_STANDARD_CONTRACT_SPEC_SEGMENTS:
        for row in rows:
            yield segment_path, row


GPUSTORMING_STANDARD_CONTRACT_SPECS = [row for _segment_path, row in iter_gpustorming_standard_contract_specs()]
GPUSTORMING_STANDARD_CONTRACT_SPEC_PARTS = [segment_path for segment_path, _rows in GPUSTORMING_STANDARD_CONTRACT_SPEC_SEGMENTS]
