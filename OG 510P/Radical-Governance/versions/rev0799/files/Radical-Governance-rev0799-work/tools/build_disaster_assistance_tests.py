#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="disaster_assistance_tests.json",
        output_stem="DISASTER_ASSISTANCE_TESTS",
        title="Disaster-assistance tests matrix",
        source_field="disaster_assistance_test_source",
        use_rule="Run disaster-assistance tests whenever a declared incident, emergency relief route, individual-assistance programme, household proof problem, insurance / duplication review, fraud screen, appeal, inter-program referral, recovery payment, or long-term recovery handoff can affect whether a survivor actually receives safe shelter, essential needs, repair support, or remaining-need help. Separate declaration, household eligibility, proof state, denial reason, appeal clock, handoff receipt, payment receipt, fraud-control harm, and recovery outcome before scoring aid as delivered or a case as closed.",
    )


if __name__ == "__main__":
    main()
