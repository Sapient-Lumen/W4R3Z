# Ledger row-ID uniqueness audit

The generated row-ID audit checks registered route-support ledgers for duplicate row identifiers. It is a restart-safety and refactor-safety control: duplicate row IDs can make dependency edges, bindings, and summaries refer to the wrong object even when every individual ledger is schema-valid.

The audit is not scientific evidence. It prevents hidden authority-handle collisions.
