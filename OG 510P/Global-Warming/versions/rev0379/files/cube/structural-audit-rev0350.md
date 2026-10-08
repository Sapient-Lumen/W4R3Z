# Structural audit rev0350

Base: `Global-Warming-rev0349-2026.06.05.17.04-preflightrehearsal-snapshotseal-operatorreceipts-refactor.zip`

Finding: the cloudtainer working state contained ghost/prelinked rev0350 artifacts from side attempts, including duplicate `557-...` candidates. The selected base remained the last linked rev0349 zip. Rev0350 records the ghost/staging artifacts in `cube/package-ghost-rev0350-artifact-audit-rev0350.csv` and keeps one canonical `557` file in the linked package.

Substantive operational change: a 54-case red-team live-drop drill now tests receipt issuance, hash-only packets, redacted-only packets, synthetic replay, public-meeting overclaims, MSEL overclaims, duplicate source IDs, and complete-looking candidate packets. All cases are non-closure.

SQLite mirror: `cube/datacube-rev0350-emergency.sqlite`.

Claim boundary: no real/anonymized Beaver Valley exercise evidence was imported; `REAL_BVPS_PUBLIC_ONLY` remains public-context-only.
