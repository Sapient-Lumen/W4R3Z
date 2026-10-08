# Structural audit rev0304 — nuclear radiological monitoring refactor

## Audit target

Rev0304 audits whether the cube's pro-nuclear orientation has a public measurement layer. The answer before this revision was: partially. Dose, effluent, groundwater, environmental media, emergency monitoring, independent monitoring, and public-health baselines existed as scattered concerns, but not as a unified maturity-cap plane.

## Refactor performed

- Added five canon files: 504–508.
- Registered S939–S952.
- Added 30 radiological-monitoring service floors.
- Added 18 nuclear assurance gates: NG_227–NG_244.
- Bound all nuclear service floors to the new gates.
- Added new monitoring, dose, effluent, tritium, emergency, independent monitoring, dashboard, source-authority, gap, traceability, maturity-cap, and publication-control tables.

## Key design decision

Nuclear remains preferred, but measured public dose, ALARA, radioactive effluent controls, environmental monitoring, tritium/groundwater surveillance, public-health baselines, independent review, and public dashboards now cap maturity. This prevents pro-nuclear system-benefit claims from outrunning the public measurement record.

## Security/privacy boundary

The cube should publish dose/effluent/environmental results, methods, uncertainty and challenge pathways. It should not publish security-sensitive monitoring-station vulnerabilities, exact tactical emergency-monitoring deployments, personal health data, or protected small-cell epidemiological records.
