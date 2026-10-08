# Tools directory (status + intended use)

This directory contains small, stdlib-first helpers plus research scaffolding.
Treat **EvidenceEnvelope / packet schemas** and **Track A drift firewalls** as authoritative; tools here are convenience layers.

## Operator-facing helpers (Track A ergonomics)

These are intended to be usable during drills/incidents (still review before deployment):

- `evidence_object_card.py` — one-command card renderer: given a packet/envelope, dispatches to the right specialized card tool when available, or prints a small generic digest card.
- `public_notice_card.py` — recompute PublicNotice payload/TBS digests and print a copy/pasteable “digest card”; resolves `payload.channels` via `artifacts/registries/official-channels.csv`.
- `observer_verify_packet.py` — offline packet integrity checker; supports publishable `--public` reports, `--emit-evidence-object` minimal report packets, optional linkage to an implementation report (`--verifier-report-envelope` / `--verifier-report-tbs-digest`), and problem-code UX (`--list-codes`, `--explain`).
- `packet_verification_report_card.py` — recompute PacketVerificationReport payload/TBS digests and print a copy/pasteable “packet verification card” suitable for publishing verifier results.
- `verifier_report_card.py` — recompute VerifierReport payload/TBS digests and print a copy/pasteable “verifier card” for publishing verifier identity/conformance.
- `public_surface_pins.py` — print sha256 pins for stable registry bytes (used as optional comparability pins in publishable verifier outputs).
- `evidence_packager.py` — build a canonical packet directory layout from inputs.
- `envelope_wrap.py` — wrap a JSON payload into an `EvidenceEnvelope` using the canonical digest rules.
- `bundle_hash_report.py` — produce a compact hash report for a packet/bundle.

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
