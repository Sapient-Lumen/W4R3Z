#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix
from test_matrix_registry import COMMON_TEST_MATRICES


def main() -> None:
    spec = next(item for item in COMMON_TEST_MATRICES if item["metadata_filename"] == "subnational_ai_tests.json")
    build_test_matrix(
        metadata_filename=spec["metadata_filename"],
        output_stem=spec["output_stem"],
        title=spec["title"],
        source_field=spec["source_field"],
        use_rule=spec["use_rule"],
    )


if __name__ == "__main__":
    main()
