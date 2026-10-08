# Structural audit — rev0295

## Revision intent

Rev0295 keeps the cube explicitly nuclear-positive, but refactors the next weak plane: fuel-cycle and backend realism. Nuclear remains favored for clean firm power, integrated energy systems, industrial heat, water, hydrogen, data centers, AI loads and critical services, but now the preference is explicitly capped by fuel supply, HALEU, conversion/enrichment/fabrication, fuel qualification, safeguards, transport, spent fuel, backend consent, waste/decommissioning finance and security-safe publication controls.

## Audit/refactor performed

- Added canon files `459`–`463`.
- Added source register entries `S832`–`S841`.
- Added 29 nuclear fuel-cycle/backend service floors.
- Expanded nuclear assurance gates from 66 to 84, adding NG_67–NG_84.
- Rebuilt the nuclear gate-evaluation, gap-backlog, traceability, scorecard and maturity-cap planes.
- Added fuel-chain, HALEU, conversion/enrichment/fabrication, fuel qualification, spent-fuel/backend, transport/safeguards, backend consent, backend finance, publication-control and propagation-audit tables.
- Refactored sensitive fuel-cycle/publication handling so public auditability is separated from disclosure of material quantities, exact routes, package vulnerabilities, safeguards details or security details.

## Validation summary

- Numbered markdown files: 464 (`00`–`463`).
- Index rows: 464.
- Registered sources: 841.
- Service floors: 557.
- Nuclear service floors: 142.
- Nuclear assurance gates: 84.
- Nuclear gate evaluations: 11928.
- Fuel/backend gap rows: 2556.
- Cube CSV resources: 229.
- SQLite import failures: 0.
- SQLite view failures: 0.
- Validation rules passed: 15 / 15.

## Caveat

The new rows are templates and control-plane obligations, not proof of real HALEU supply, enrichment capacity, spent-fuel transport, safeguards performance, backend consent or repository progress. Rev0295 favors nuclear strongly, but it caps maturity until local project evidence supplies fuel-chain, backend, safeguards, transport, finance and security-safe public challenge records.
