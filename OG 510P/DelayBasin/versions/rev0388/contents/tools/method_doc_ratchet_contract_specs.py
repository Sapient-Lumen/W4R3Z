# Aggregates locality-sized method-doc ratchet contract spec segments.
# These rows preserve formerly separate doc/prompt/runbook contract needles without wrapper regrowth.

from collections.abc import Iterator

from method_doc_ratchet_contract_specs_part_1 import METHOD_DOC_RATCHET_CONTRACT_SPECS_PART_1
from method_doc_ratchet_contract_specs_part_2 import METHOD_DOC_RATCHET_CONTRACT_SPECS_PART_2

METHOD_DOC_RATCHET_CONTRACT_SPEC_SEGMENTS = [
    ("tools/method_doc_ratchet_contract_specs_part_1.py", METHOD_DOC_RATCHET_CONTRACT_SPECS_PART_1),
    ("tools/method_doc_ratchet_contract_specs_part_2.py", METHOD_DOC_RATCHET_CONTRACT_SPECS_PART_2),
]


def iter_method_doc_ratchet_contract_specs() -> Iterator[tuple[str, dict]]:
    for segment_path, rows in METHOD_DOC_RATCHET_CONTRACT_SPEC_SEGMENTS:
        for row in rows:
            yield segment_path, row


METHOD_DOC_RATCHET_CONTRACT_SPECS = [row for _segment_path, row in iter_method_doc_ratchet_contract_specs()]
METHOD_DOC_RATCHET_CONTRACT_SPEC_PARTS = [segment_path for segment_path, _rows in METHOD_DOC_RATCHET_CONTRACT_SPEC_SEGMENTS]
