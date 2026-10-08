# session_wording_drift_freeze

An imported `cargo report rebuilds` explanation changed wording between nightly versions, but the downstream bundle still exports the same stable exactness and cause categories.

This scenario exists so P-0469 does not quietly treat unstable upstream text as if it were already the long-term machine contract.
