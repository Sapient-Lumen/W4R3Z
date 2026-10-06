# ADR-0100: Packet capture local-artifact metadata and retention boundary

- Status: Accepted
- Date: 2026-03-09

## Context

`adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md` made packet capture a bounded typed session,
`adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md` gave it a compact evidence-first review object,
and `adrs/ADR-0099-packet-capture-selector-compiler-boundary.md` kept capture intent typed instead of backend-filter folklore.

One practical drift surface still remained:
**what exactly is a local raw capture artifact allowed to carry, and how long may it live?**

If the answer is merely "whatever `.pcap` / `.pcapng` file the tool wrote", the archive quietly loses its boundary again:

- filenames and tool defaults become the real retention workflow,
- packet files start carrying comments, name-resolution records, or other sideband metadata that bypass the typed session/summary surfaces,
- some formats can even embed decryption material,
- and support/export pressure turns those files back into the real handoff artifact.

DeriveBSD needs a narrower answer:
**raw capture files may exist, but they stay opaque local evidence objects with explicit retention bounds, and embedded capture-file metadata must not become the product surface.**

## Decision

1. Keep local raw capture artifacts subordinate to the typed packet-capture lane.
   - `packet.capture.session` remains the authoritative pre-capture object.
   - `packet.capture.summary` remains the normal compact review/export object.
   - local raw artifacts are referenced by digest only; path and filename stay implementation detail.

2. Make local-retention budgets reviewable in the session.
   - `packet.capture.session.retention.max_local_retention_seconds` is the authoritative upper bound on how long Derive-managed raw capture artifacts may remain locally retained after the bounded capture window ends.
   - `local_storage` remains the coarse storage posture (`ephemeral-local`, `sealed-local`, `incident-bundle-reference-eligible`).

3. Make raw-artifact metadata posture explicit in the summary.
   Each `packet.capture.summary.artifacts.local_capture_artifacts[]` entry must carry:
   - `digest`
   - `format`
   - `storage`
   - `metadata_posture`
   - `retention_until`

4. Define the canonical metadata-posture vocabulary.
   - `packet-records-only`: packet records plus minimal file framing only; no sideband comments, name-resolution sections, or embedded decryption material.
   - `sideband-metadata-present`: extra capture-file metadata exists and must be treated as stronger review/export risk.
   - `decryption-material-present`: the artifact embeds packet-decryption material or equivalent secrets and therefore belongs to a stronger handling lane.

5. Fix the Derive-generated default.
   - Derive-generated raw capture artifacts default to `metadata_posture = packet-records-only`.
   - `sideband-metadata-present` and `decryption-material-present` are compatibility / imported-artifact states, not the normal generated posture.
   - If such artifacts are referenced at all, they require stronger review and should not quietly ride the default support/export lane.

## Consequences

- Packet files stop being a metadata side channel that competes with `packet.capture.session` and `packet.capture.summary`.
- Retention becomes bounded and reviewable rather than filename- or operator-habit-driven.
- Safe incident handling stays viable: local packet bytes can still exist, but they remain digest-addressed opaque evidence with explicit expiry.
- General-purpose compatibility is preserved because foreign/legacy artifacts can still be described, but they are clearly marked as a stronger lane.
- A small guardrail can now keep the schemas, examples, and docs aligned around this boundary.

## Why this is narrow enough

This ADR does **not** standardize:

- the on-disk filename or directory layout for local capture files,
- the exact packet-file writer backend,
- a new packet-analysis subsystem,
- or the full foreign-capture import workflow.

It only fixes two narrow but expensive questions:
what local raw capture artifacts may mean, and how long they are allowed to survive before the archive boundary is considered violated.
