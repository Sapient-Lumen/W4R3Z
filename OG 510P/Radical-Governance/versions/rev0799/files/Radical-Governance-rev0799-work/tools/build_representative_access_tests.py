#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="representative_access_tests.json",
        output_stem="REPRESENTATIVE_ACCESS_TESTS",
        title="Representative-access tests matrix",
        source_field="representative_access_test_source",
        use_rule="Run representative-access tests whenever a payee, appointee, guardian, attorney-in-fact, tax representative, professional authorisation, appeal representative, helper, caregiver, organisation, delegated account user, or informal proxy can receive notices, control money, submit claims, access records, bind filings, preserve deadlines, or speak for a person. Separate person, credential, authority, scope, capacity, wishes, revocation, fiduciary duty, payment control, and public-service outcome before accepting proxy action or denial.",
    )


if __name__ == "__main__":
    main()
