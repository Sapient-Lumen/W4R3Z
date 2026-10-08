# rev0037 audit/refactor notes — trained mechanism guards

Added `tools/trained_mechanism_guard_report.py`.

Purpose: trained toy probes can overclaim just as easily as C++ symbolic probes. A trained probe should carry mechanism guards: exactness/reachability, sparse-edge or route/gain fields, and a primary metric.

Initial report:

- current trained artifacts scanned: 2
- guard-ready artifacts: 2
- exactness-ready artifacts: 2
- route/gain-ready artifacts: 1
- sparsity-ready artifacts: 1

This report is intentionally not a truth oracle. It is a promotion guard against treating high final accuracy as mechanism evidence.
