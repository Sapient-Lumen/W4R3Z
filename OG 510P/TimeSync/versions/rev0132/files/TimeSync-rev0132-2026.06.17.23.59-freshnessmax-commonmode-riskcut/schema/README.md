# TimeSync rev0132 schema catalog

rev0130 changes no JSON Schema shape. The chrony and ntpq adapters are executable code and fixtures; the corrective timestamp change from rev0121 remains in semantic arithmetic: RFC 3339 `date-time` strings can carry fractional precision beyond Python microseconds, so `tools/temporal_coherence.py` now compares/subtracts them exactly.

The schema set remains standalone and intentionally broad, but repeated inline subtrees are a documented maintenance cost. Future source-generation or `$defs` work must prove that published standalone schemas and validation behavior remain equivalent.

Current `$id` values use `https://example.invalid/timesync/schema/`; they are placeholders, not a stable public schema namespace.
