#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="payment_redress_tests.json",
        output_stem="PAYMENT_REDRESS_TESTS",
        title="Payment-redress tests matrix",
        source_field="payment_redress_test_source",
        use_rule="Run payment-redress tests whenever a public body owes or may owe money through compensation, redress, tax refund, refundable credit, support-scheme conversion, settlement implementation, wrongful-conviction payment, emergency relief, or administrative-harm repair. Separate claim registration, offer, acceptance, payment issuance, payment receipt, interim, final, challenge, reopening, fraud-screen, and remaining tails before scoring repair or closure.",
    )


if __name__ == "__main__":
    main()
