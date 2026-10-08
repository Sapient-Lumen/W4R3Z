#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="unemployment_insurance_tests.json",
        output_stem="UNEMPLOYMENT_INSURANCE_TESTS",
        title="Unemployment-insurance integrity and access tests matrix",
        source_field="unemployment_insurance_test_source",
        use_rule="Run unemployment-insurance tests whenever UI claims, pandemic or emergency benefit programs, identity proofing, payment holds, fraud controls, overpayment notices, waivers, appeals, recovery actions, state IT modernization, or public integrity dashboards can determine whether a valid claimant is paid or a fraudulent claim is stopped. Separate claim issue state, identity route, payment reason, fraud signal, overpayment category, waiver, appeal, recovery, and state performance before scoring blocked payment as integrity or paid benefit as success.",
    )


if __name__ == "__main__":
    main()
