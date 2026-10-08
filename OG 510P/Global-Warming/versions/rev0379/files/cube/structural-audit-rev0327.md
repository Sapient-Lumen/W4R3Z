
# Structural audit rev0327

Rev0327 adds an alert-originator authority and delivery-receipt layer on top of the rev0326 CAP-lineage and evidence-bag integrity layer.

## Key correction

The package now separates authority, gateway acceptance, channel delivery, public receipt, public archive visibility, public meeting remarks, and final AAR/CAP closure. This prevents the most likely June 2026 overclaim path: a public CAP archive hit or preliminary public statement being treated as proof of local emergency readiness.

## Compatibility posture

The legacy universal nuclear crossproduct tables remain compatibility surfaces only. The Beaver Valley branch remains REAL_BVPS_PUBLIC_ONLY and cannot inherit synthetic readiness scores.

## Integrity checks

The rev0327 SQLite mirror, validation report, table catalogs, source canonical map, and resource manifest were rebuilt. Public-context-to-local-closure leak count is zero.
