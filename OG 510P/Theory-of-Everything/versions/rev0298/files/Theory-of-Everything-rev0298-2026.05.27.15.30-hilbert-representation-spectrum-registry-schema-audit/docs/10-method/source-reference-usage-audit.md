# Source-reference usage audit

The bibliography can no longer be checked only for missing IDs. The executable cube now carries many `source_refs` across route-support ledgers, so the archive needs a generated source-reference usage audit.

The generated audit checks:

- bibliography IDs present in `docs/00-meta/bibliography.md`;
- JSON `source_refs` that point to unknown bibliography IDs;
- duplicate bibliography URL entries;
- source IDs used by executable JSON ledgers;
- retired duplicate IDs that should not keep receiving route-credit references.

This is an audit/refactor surface, not a scientific source of authority. It improves source custody and citation hygiene; it does not promote any candidate route.
