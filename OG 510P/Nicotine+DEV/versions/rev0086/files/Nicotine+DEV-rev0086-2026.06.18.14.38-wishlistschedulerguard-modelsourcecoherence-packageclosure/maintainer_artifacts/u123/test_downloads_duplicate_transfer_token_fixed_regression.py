# SPDX-License-Identifier: GPL-3.0-or-later
"""Composite gate for the selected reachable-state U-123 invariants."""

from test_downloads_duplicate_transfer_token_burst_bound_regression import (
    DuplicateDownloadTransferTokenBurstBoundRegression,  # noqa: F401
)
from test_downloads_duplicate_transfer_token_collision_rejection_regression import (
    DuplicateDownloadTransferTokenCollisionRejectionRegression,  # noqa: F401
)
from test_downloads_duplicate_transfer_token_identity_guard_regression import (
    DuplicateDownloadTransferTokenIdentityGuardRegression,  # noqa: F401
)


if __name__ == "__main__":
    import unittest

    unittest.main()
