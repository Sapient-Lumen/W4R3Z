# Revision Summary — rev0096

rev0096 focuses on a concrete unfinished risk: the normalization layer had remained recommendation-only while free-text statuses continued to carry release-critical meaning.

Substantive changes:

- Added `tools/ledger_code_overlay.py`.
- Replaced the old planning-only `META/Normalized-Code-Overlay-current.*` with 1,040 row-level companion code rows.
- Added `META/Normalized-Code-Overlay-Audit-current.*` and release gate `gate_079`.
- Updated `META/Controlled-Vocabulary-Normalization-current.*` from deferred recommendations to implemented companion-overlay status.
- Corrected the controlled vocabulary by adding `requires_family_community_or_governance_confirmation`, the actual boundary-lift code already used by the permission ledger.
- Kept all core ledger headers stable; this is a companion overlay, not a schema migration.
- Kept the public layer closed.

No candidates, claims, sources, public URLs, referrals, contacts, routes, service capacity, case/client details, images, stories, testimony, legal/medical guidance, or public-release permission were added.
