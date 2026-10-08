#!/usr/bin/env python3
from __future__ import annotations

from test_matrix_common import build_test_matrix


if __name__ == "__main__":
    build_test_matrix(
        metadata_filename="watchlist_border_tests.json",
        output_stem="WATCHLIST_BORDER_TESTS",
        title="Watchlist / border / law-enforcement automation tests",
        source_field="watchlist_border_tests_source",
        use_rule="Use these tests when watchlists, border screening, biometric candidates, NCIC / nonfederal alerts, mobile field capture, DHS TRIP redress, or AI / facial-recognition inventories shape liberty, travel, immigration, police, or public-safety consequences. A match opens an inquiry lane; it does not itself prove identity, threat, authority, or remedy completion.",
    )
