# Structural audit — rev0314

Created: 2026-06-04T08:40:41-04:00

## Focus

This revision audits the path where official public records could accidentally become real-site readiness evidence. The correction is to route each public record through source discovery, raw acquisition, parsing, normalization, local evidence demand, verification, and public claim review.

## Findings

- New numbered canon file 521 is present and metadata rows align.
- Source register is continuous through S1024.
- Public machine feeds for event notifications, PI raw data, action matrix, and exercise schedule are registered as acquisition targets, not silently claimed as downloaded.
- EN58200 has 20 open closure requirements; no closure claim is made.
- Offsite public plans/brochures produce 18 evidence-demand rows; they do not close alerting, route, AFN, KI, or ingestion-pathway readiness.
- The rev0314 validator rejects public-source closure, future-exercise-as-passed, stale EP03-current, route-brochure-as-capacity, and positive green/ready claims.
- SQLite integrity is `ok` and the public-source closure leak view returns `0` rows.

## Still open

The next highest-value packet is an actual or anonymized EN58200 EOF closure packet, followed by raw PI/action-matrix/exercise feed acquisition and one offsite county capacity packet.
