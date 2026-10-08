#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="entitlement_continuity_tests.json",
        output_stem="ENTITLEMENT_CONTINUITY_TESTS",
        title="Entitlement-continuity tests matrix",
        source_field="entitlement_continuity_test_source",
        use_rule="Run entitlement-continuity tests whenever an existing public benefit, health coverage, income support, tax credit, status proof, housing support, disability-linked support, or service entitlement is renewed, redetermined, migrated, converted, closed, procedurally terminated, deadline-gated, or moved into a new proof / account / portal / claim route. Separate legal eligibility from administrative completion, and require notice, assistance, continuity, review, metric, and remedy proof before scoring loss as clean.",
    )


if __name__ == "__main__":
    main()
