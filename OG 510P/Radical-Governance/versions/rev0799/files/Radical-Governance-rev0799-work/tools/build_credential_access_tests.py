#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


def main() -> None:
    build_test_matrix(
        metadata_filename="credential_access_tests.json",
        output_stem="CREDENTIAL_ACCESS_TESTS",
        title="Credential-access tests matrix",
        source_field="credential_access_test_source",
        use_rule="Run credential-access tests whenever a public login, account, identity-proofing route, federation layer, passkey, wallet, delegated mandate, biometric check, or shared identity provider becomes a practical gate to a public service, entitlement, payment, notice, status proof, authorisation, filing, deadline, or representative action. Separate person, credential, account, session, mandate, entitlement, fallback, and service-owner duties before scoring access or denial.",
    )


if __name__ == "__main__":
    main()
