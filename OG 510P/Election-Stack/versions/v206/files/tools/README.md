# Tools directory (status + intended use)

This directory contains small, stdlib-first helpers plus research scaffolding.
Treat **EvidenceEnvelope / packet schemas** and **Track A drift firewalls** as authoritative; tools here are convenience layers.

See also: `artifacts/registries/tool-maturity.csv` and `docs/212-tooling-maturity-and-evidence-safety.md` (small intent surface: which tools are operator-facing vs research/skeleton, and which outputs are evidence-safe).

## Operator-facing helpers (Track A ergonomics)

These are intended to be usable during drills/incidents (still review before deployment):

- `evidence_object_card.py` — one-command card renderer: given a packet/envelope, dispatches to the right specialized card tool when available, or prints a small generic digest card.
- `public_notice_card.py` — recompute PublicNotice payload/TBS digests and print a copy/pasteable “digest card”; resolves `payload.channels` via `artifacts/registries/official-channels.csv`.
- `public_notice_feed_card.py` — recompute PublicNoticeFeed payload/TBS digests and print a bounded “feed digest card” (docs/200).
- `official_channel_directory_card.py` — recompute OfficialChannelDirectory payload/TBS digests and print a bounded directory digest card (docs/203).
- `well_known_discovery_card.py` — recompute WellKnownElectionStackDiscovery payload/TBS digests and print a bounded `/.well-known` digest card (docs/204).
- `official_surface_security_snapshot_card.py` — recompute OfficialSurfaceSecuritySnapshot payload/TBS digests and print a bounded snapshot digest card (docs/199).
- `public_surface_parity_snapshot_card.py` — recompute PublicSurfaceParitySnapshot payload/TBS digests and print a bounded parity snapshot card (docs/201).
- `liveness_beacon_card.py` — recompute LivenessBeacon payload/TBS digests and print a compact, copy/pasteable liveness + freshness header summary (docs/210).
- `publication_coverage_report_card.py` — recompute PublicationCoverageReport payload/TBS digests and print a bounded deadline-coverage card (docs/187).
- `http_capture_to_observation.py` — convert a bounded HTTP response capture (curl/wget output) into an `observations[]` snippet: status + `sha256:<hex>` digest + freshness headers (and always includes `observed_at`) (pairs with cache/split-view drill artifacts; docs/205, docs/210).
- `http_capture_to_parity_observation.py` — convert a bounded HTTP response capture (curl/wget output) into a `PublicSurfaceParitySnapshot.observations[]` entry: status + `sha256:<hex>` body digest + (when parseable) served envelope `kind` / `payload_digest` / `tbs_digest` (docs/201).
- `compact_notes.py` — parse + canonicalize bounded compact request-context notes (`req[...] vary[...] age[...]`) for stable diffs and publishable hygiene (docs/232).
- `compare_public_surface_parity_snapshots.py` — compare two parity snapshots (payloads or packets) and print a tight “what changed” summary; exits 0 if no diffs, 3 if diffs.
- `compare_liveness_beacons.py` — compare two liveness beacons (payloads or packets) and print a tight “what changed” summary; exits 0 if no diffs, 3 if diffs.
- `surface_anomaly_rollup.py` — bounded rollup of publishable `surface_*` anomaly-note codes across packets/payloads (helps triage cache/split-view symptoms without shipping bodies).
- `public_artifact_lint.py` — conservative lint for publishable packets: flags obvious body/capture fields, unbounded strings/headers, and unknown `surface_*` anomaly-note codes (pairs with `artifacts/checklists/public-artifact-redaction-checklist.md`).
- `observer_verify_packet.py` — offline packet integrity checker; supports publishable `--public` reports, `--emit-evidence-object` minimal report packets, optional linkage to an implementation report (`--verifier-report-envelope` / `--verifier-report-tbs-digest`), and problem-code UX (`--list-codes`, `--explain`).
- `packet_verification_report_card.py` — recompute PacketVerificationReport payload/TBS digests and print a copy/pasteable “packet verification card” suitable for publishing verifier results.
- `verifier_report_card.py` — recompute VerifierReport payload/TBS digests and print a copy/pasteable “verifier card” for publishing verifier identity/conformance.
- `public_surface_pins.py` — print sha256 pins for stable registry bytes (used as optional comparability pins in publishable verifier outputs).
- `evidence_packager.py` — build a canonical packet directory layout from inputs.
- `envelope_wrap.py` — wrap a JSON payload into an `EvidenceEnvelope` using the canonical digest rules.
- `bundle_hash_report.py` — produce a compact hash report for a packet/bundle.
- `public_fingerprint_report.py — compute a deterministic *public fingerprint* for a packet over bounded, publishable surfaces (envelopes + JSON objects + small notes), using RFC8785-JCS for JSON to reduce formatting drift.
- `compare_public_fingerprints.py` — compare two packets' public fingerprints and print a tight, path-keyed diff when they differ.

## Research / prototype utilities (Track B/C)

These are useful for exploration but are not “drop-in deployable”:

- `enr_drift_detector.py`, `vrdb_change_detector.py` — prototype drift/change detection helpers.
- `availability_log_builder.py`, `availability_gossip_checker.py` — availability evidence scaffolding.
- `cohort_audit_reporter.py`, `probe_reputation_scorer.py`, `multi_perspective_probe_sampler.py` — cohort/measurement scaffolding.
- `path_safety.py`, `path_correlation_analyzer.py` — network path analysis helpers.

## Skeletons / placeholders (NOT complete)

Files with `_skeleton.py` are intentionally incomplete and may contain `TODO` fields (do not treat outputs as evidence without finishing the spec + adding drift firewalls):

- `endpoint_validator_skeleton.py`
- `parity_monitor_skeleton.py`
- `urp_builder_skeleton.py`

If you productionize any tool:
1) add a proof obligation (docs/159–164),
2) add an ADR (adr/INDEX.md), and
3) wire a drift firewall into the release gate (docs/162).
