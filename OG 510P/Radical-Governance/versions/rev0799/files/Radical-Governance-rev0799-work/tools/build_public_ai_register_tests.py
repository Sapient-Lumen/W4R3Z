#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="public_ai_register_tests.json",
        output_stem="PUBLIC_AI_REGISTER_TESTS",
        title="Public AI register maintenance tests matrix",
        source_field="public_ai_register_test_source",
        use_rule="Run public-AI-register tests whenever an AI inventory, algorithmic transparency record, high-risk AI database entry, agency AI page, public/internal inventory split, COTS AI rollup, high-impact count, missing row, paused tool, or withdrawn row is cited as evidence. Separate source-of-truth hierarchy, public/internal/exempt reconciliation, lifecycle state, risk classification, authority, procurement, model/data/vendor drift, monitoring, incident, redress, machine-readable row identity, and retirement receipts before treating a listing as governance or an absence as non-use.",
    )


if __name__ == "__main__":
    main()
