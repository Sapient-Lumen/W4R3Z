# Structural audit — rev0293

## Scope

Audited rev0292 and added a nuclear operations assurance refactor. The target gap was the distance between a nuclear-positive build/finance preference and actual deliverable clean-firm performance during operation.

## Findings

- Rev0292 strengthened bankability/buildability, but operations maturity still relied too much on policy preference and nameplate/project claims.
- The cube needed first-class evidence for fleet availability, capacity/availability factors, regulatory performance indicators, outage/refueling controls, maintenance/spares, configuration management, grid/flexibility claims, and operating-experience feedback.
- Rev0292's validation report showed an inherited SQLite export failure for `sqlite-resource-map.csv` because the generated table name began with SQLite's reserved `sqlite_` prefix.

## Actions

- Added files `449`–`453`.
- Added gates `NG_41`–`NG_52`.
- Added 18 nuclear operations service floors.
- Added nuclear operations/performance/outage/maintenance/configuration/performance-indicator/operating-experience/grid-services/cyber-physical/operator-training scorecard tables.
- Regenerated nuclear gate evaluations, gap backlog, traceability matrix, service-floor scorecards, maturity evaluations, route/source/tag/file-field artifacts and SQLite mirror.
- Repaired the SQLite reserved-name import by mapping `sqlite-resource-map.csv` to `cube_sqlite_resource_map`.

## Validation

13 / 13 rev0293 validation rules passed.
