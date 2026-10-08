# Ledger-family namespace audit

The route-support stack is now large enough that family ids, ledger files, schema files, and generated summary paths are authority handles. `docs/30-program/ledger-family-namespace-audit.generated.md` checks for duplicate family ids, duplicate ledger files, duplicate schema files, duplicate summary files, and nonmonotone introduced-revision metadata.

This audit is administrative. It does not promote any scientific route; it keeps registered layer families from colliding or disappearing during refactor.
