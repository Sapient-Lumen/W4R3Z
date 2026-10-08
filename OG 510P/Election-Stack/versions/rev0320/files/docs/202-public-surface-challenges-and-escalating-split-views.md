# 202 — Public surface challenges and escalating split‑view findings

**Track:** A (Deployable core)

A PublicNotice feed (`docs/200`) is a bounded discovery surface, and parity snapshots (`docs/201`) are a bounded *proof artifact*.
This doc ties them into the **public inspection challenge** machinery so independent monitors can be *compelled (by public expectation and auditability)* to check the same surface and publish comparable evidence.

This is intentionally tight: it specifies *how to ask*, *what to publish*, and *how to escalate*, without inventing new protocol surface.

## 202.1 Threats addressed
- **Targeted split‑view:** different audiences see different “latest feed” / status surface bytes.
- **Soft suppression:** a party claims “we never saw that notice/feed” because discovery surfaces drifted.
- **Selective disclosure by monitors:** a monitor detects a mismatch but only tells some parties.

## 202.2 The challenge artifact (already in-scope)

Use the existing `PublicInspectionChallenge` schema (`schemas/PublicInspectionChallenge.json`).
For comms/public surfaces, use `targets[].type = "endpoint"` and set `targets[].ref` to a stable surface URL.

Minimal template: `artifacts/templates/public-inspection-challenge-endpoint-parity.json`.

Example targets (stable paths, not “latest tweet IDs”):
- `/notices/feed/latest.json` (feed “latest” surface) (`docs/200`)
- `/status/` (status board surface) (`docs/195`)
- `/notices/` (rumor-control landing) (`docs/195`)

Sampling guidance (deterministic, auditable): `tools/challenge_sampler.py` + `docs/146`/`149`.

## 202.3 What a monitor should publish in response (bounded)

For each challenged endpoint, a monitor SHOULD publish:

1) a **PublicSurfaceParitySnapshot** envelope (`hfv.public.surface_parity_snapshot`) that records:
   - the URL fetched,
   - HTTP status,
   - body digest (`body_sha256`),
   - when parseable, the served envelope digests (payload + TBS) (`docs/201`).

   When a mismatch is plausible, monitors SHOULD also include bounded request-context + variance hints in `observations[].notes` using the compact notation from `DOC:docs/224-request-context-and-variant-probing-for-public-surfaces.md` (224.2a): `req[...] vary[...] age[...]`.

2) a **MonitorAttestation** that links the snapshot digest into the monitor’s public inspection trail (`docs/140`).

For **cache / stale-pointer** disputes, pair snapshots with at least two independent `hfv.coverage.liveness_beacon` entries (`docs/210`) so freshness-relevant headers (`Age`, `ETag`, `Cache-Control`, `Last-Modified`) can be compared across vantages without expanding the snapshot schema.

Do **not** embed long bodies. Hashes first; use `EvidencePointer` only when raw bytes are crucial (`docs/201.3`).

Snapshots and feeds that are meant to be publishable SHOULD carry receipt + gossip attachments as declared in the registries (`docs/180`).

## 202.4 Escalation ladder (how to go from “mismatch” to public proof)

When monitors disagree (or a monitor sees drift over time), escalate in this order:

1) **Publish the snapshot(s)** immediately (portable proof of what was served).
2) **Publish a MonitorInconsistencyReport** when multiple monitors’ snapshots conflict, referencing the snapshot digests and challenged endpoint (`schemas/MonitorInconsistencyReport.json`; see `docs/140`).
3) **Publish a PublicNotice** (`adr/0002`, `docs/186`) that:
   - states what surface is inconsistent,
   - cites the snapshot / inconsistency-report digests,
   - provides an operator action (e.g., “treat channel X as compromised; use mirror Y; rotate keys; re-issue feed digest”).

This keeps narrative in PublicNotice, and keeps proof objects bounded and comparable.

## 202.5 “Forced visibility” (anti selective disclosure)

To reduce “only the good evidence got published” failure modes:

- Prefer **chained snapshots** (`previous_snapshot_sha256`, `docs/201.4`) for monitors that run continuously.
- Anchor challenge IDs + response digests in MonitorAttestations (`docs/140`) so missing responses become inspectable.
- Ensure challenged surfaces are themselves parity‑monitored (`artifacts/checklists/audience-parity-monitoring-checklist.md`).

## 202.6 Deployment note: don’t create a new surface you can’t maintain

If you cannot support challenges at a given cadence:
- reduce the target set (prefer the feed “latest” surface and the primary status board),
- or publish a PublicNotice declaring the reduced inspection scope.

The goal is *auditable, bounded truth*, not maximal coverage.

