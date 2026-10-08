# Audit/refactor notes — rev0035

Added `tools/sparse_program_report.py` to summarize sparse attention mechanisms from the new C++ schema probe. The report treats direct reachability, depth reachability, target miss, and cost fraction as common fields across fixed-block, sliding, periodic, bridge, anchor, and dense masks.

Updated smoke validation to require the sparse program report.
