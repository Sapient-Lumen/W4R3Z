# Strict/front patch hunk-scope preimage gate — rev0066

rev0066 adds a reviewer-facing hunk-scope gate for the exported strict/front split patch series. The gate confirms that each patch only touches its bundle-approved file set and that every hunk preimage matches the uploaded archived source bundle before the patched file is rebuilt and hash-checked.

The gate is intended as filing-support evidence, not a new vulnerability report. It strengthens confidence that the selected archived-source patch series is narrow, reproducible, and reviewable.
