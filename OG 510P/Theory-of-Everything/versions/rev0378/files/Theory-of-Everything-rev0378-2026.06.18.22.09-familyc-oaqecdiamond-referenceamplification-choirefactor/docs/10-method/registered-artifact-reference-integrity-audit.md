# Registered artifact-reference integrity audit

This audit scans selected path-like references in registered executable JSON surfaces and verifies that the referenced archive artifact exists. It covers ledger files, schema files, generated summaries, owner surfaces, controlling ledgers, and generated audit pointers.

The audit is archive-control only. It does not promote any route; it prevents stale paths from hiding in otherwise schema-valid ledgers or bindings.
