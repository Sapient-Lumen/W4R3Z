# Aggregates locality-sized GPU witness contract spec segments.
# The split keeps exact contract data reviewable without restoring one wrapper per witness.

from collections.abc import Iterator

from gpu_witness_contract_specs_part_1 import GPU_WITNESS_CONTRACT_SPECS_PART_1
from gpu_witness_contract_specs_part_2 import GPU_WITNESS_CONTRACT_SPECS_PART_2
from gpu_witness_contract_specs_part_3 import GPU_WITNESS_CONTRACT_SPECS_PART_3
from gpu_witness_contract_specs_part_4 import GPU_WITNESS_CONTRACT_SPECS_PART_4

GPU_WITNESS_CONTRACT_SPEC_SEGMENTS = [
    ("tools/gpu_witness_contract_specs_part_1.py", GPU_WITNESS_CONTRACT_SPECS_PART_1),
    ("tools/gpu_witness_contract_specs_part_2.py", GPU_WITNESS_CONTRACT_SPECS_PART_2),
    ("tools/gpu_witness_contract_specs_part_3.py", GPU_WITNESS_CONTRACT_SPECS_PART_3),
    ("tools/gpu_witness_contract_specs_part_4.py", GPU_WITNESS_CONTRACT_SPECS_PART_4),
]


def iter_gpu_witness_contract_specs() -> Iterator[tuple[str, dict]]:
    for segment_path, rows in GPU_WITNESS_CONTRACT_SPEC_SEGMENTS:
        for row in rows:
            yield segment_path, row


GPU_WITNESS_CONTRACT_SPECS = [row for _segment_path, row in iter_gpu_witness_contract_specs()]
GPU_WITNESS_CONTRACT_SPEC_PARTS = [segment_path for segment_path, _rows in GPU_WITNESS_CONTRACT_SPEC_SEGMENTS]
