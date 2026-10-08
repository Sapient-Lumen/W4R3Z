# Ledger summary coverage audit

The route-support registry now records generated-summary paths for mature support families. The generated audit `docs/30-program/ledger-summary-coverage-audit.generated.md` checks that registered summaries exist and that route-support families do not silently lose their compact mirrors.

This is a refactor/audit surface, not a science claim. It protects restart quality and prevents generated summaries from under-reporting the live ledger stack.
