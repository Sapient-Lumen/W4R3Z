# Packet-capture strong-artifact safe-open intake and normalize-before-promotion boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Plan→Apply→Receipt, Bundles  

`docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md` already fixed how retained local raw artifacts are classified.
This doc fixes the next practical question:
**what is the official way to inspect and potentially promote a packet-capture artifact once it is stronger than `packet-records-only` or arrives from outside the trusted generated lane?**

See also:
- ADR: `adrs/ADR-0101-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`
- local-artifact posture boundary: `docs/510-packet-capture-local-artifact-metadata-and-retention-boundary.md`
- packet-capture summary surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- safe-open support-bundle intake boundary: `docs/498-safe-open-support-bundle-intake-and-repro-boundary.md`
- typed safe-open support-bundle profiles: `docs/502-support-bundle-intake-typed-plan-and-receipt-shapes.md`
- generic import lane: `spec/content.import.plan.schema.json`, `spec/content.import.receipt.schema.json`
- canonical packet-capture import profiles: `spec/content.import.packet-capture.plan.schema.json`, `spec/content.import.packet-capture.receipt.schema.json`
- normalization proof boundary: `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`

## Why this needs a hard decision

The last packet-capture iteration fixed a crucial boundary:
raw artifacts now say whether they stayed `packet-records-only`, carried stronger sideband metadata, or embedded decryption material.

That classification is useful, but not yet sufficient.
Without one more decision, the archive still drifts under pressure:

- responders open a foreign `.pcap` / `.pcapng` directly on the host,
- packet-file sideband metadata becomes the real explanation surface,
- decryption-bearing packet captures get handled like ordinary support files,
- and support/export tooling starts promoting the original risky file because there is no typed safer handoff shape.

DeriveBSD needs a narrower answer:
**stronger packet-capture artifacts should use the safe-open import lane, and ordinary promotion should target typed summaries or normalized `packet-records-only` derivatives rather than the original risky file.**

## Accepted boundary

Across all profiles:

- `packet.capture.session` remains the authoritative bounded capture-session object,
- `packet.capture.summary` remains the normal review/share object for packet-capture results,
- `metadata_posture = packet-records-only` remains the strict generated default,
- artifacts classified as `sideband-metadata-present` or `decryption-material-present`, plus foreign/unknown-posture packet captures, enter via the generic `content.import.*` safe-open lane,
- the official packet-capture intake path is a typed specialization of that lane rather than a new subsystem,
- the original strong artifact remains quarantined opaque evidence,
- and only normalized `packet-records-only` derivatives and/or `packet.capture.summary` outputs are eligible for ordinary promotion/export.
- a normalized derivative is not ordinary evidence just because it exists; it becomes an ordinary promotion candidate only once the import lane binds it to generic deterministic redaction evidence (`docs/512-packet-capture-normalization-redaction-receipt-boundary.md`).

This keeps stronger packet-capture compatibility viable without letting risky `.pcapng` habits redefine the product boundary.

## Canonical typed shapes

The archive now carries constrained specialization schemas:

- `spec/content.import.packet-capture.plan.schema.json`
- `spec/content.import.packet-capture.receipt.schema.json`

These are typed profiles over the generic import lane.
Canonical examples therefore stay:

- `kind = content.import.plan`
- `kind = content.import.receipt`

The authoritative import lane remains `content.import.*`.
The packet-capture typed profile only fixes the **official safe-open shape** for this stronger class of artifact.

## Canonical execution and operations

The official execution boundary is conservative and fixed:

- `execution.isolation = microvm`
- `execution.network = none`
- `execution.lifetime = disposable`

The canonical operation sequence is also intentionally small:

- `scan`
- `classify`
- `strip-metadata`

Meaning:

- `scan` checks the artifact before deeper use,
- `classify` records whether the capture file carries stronger sideband metadata or decryption material,
- `strip-metadata` derives a normalized `packet-records-only` candidate artifact for later review/export when policy allows.

This is enough to make the boundary implementable without standardizing a full packet-analysis stack.

## Normalize-before-promotion rule

The narrow hard decision is:
**ordinary promotion does not target the original strong artifact.**

Instead:

- the original imported artifact remains quarantined and digest-addressed,
- ordinary incident/support review should trade in `packet.capture.summary` and other typed evidence,
- and if packet bytes still matter, the promotion candidate is a normalized `packet-records-only` derivative rather than the original sideband/decryption-bearing file.

That means `decryption-material-present` is never just “another local file.”
It is a stronger secret-bearing case that stays on the safe-open lane until a secret-free derivative exists.

## Product-shape defaults

| Profile | Default strong-artifact handling posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `safe-open-required + normalize-before-promotion` | Oncall capture review stays viable, but foreign or secret-bearing captures do not become ambient host-open support artifacts. |
| **B workstation** | `trusted-ui-visible safe-open + normalize-before-promotion` | Local troubleshooting remains practical, but the trusted host still surfaces when a richer capture file needs the stronger no-network review lane. |
| **C general_os** | `explicit-local-admin compatibility allowed, official lane stays safe-open` | Compatibility tooling can exist, but the archive still has one strict official path for derived workflows and supportability. |
| **D appliance_factory** | `safe-open-only + digest-reference-first + strongest promotion limits` | Production/regulatory environments can inspect risky captures, but ordinary export/support posture still prefers summaries and normalized derivatives only. |

## Review guidance

When reviewing a packet-capture workflow involving stronger artifacts, ask:

1. Did the workflow keep the original artifact on `content.import.plan` / `content.import.receipt` rather than quietly host-opening it?
2. Was the execution boundary still `microvm` + `network = none` + `lifetime = disposable`?
3. Is the original strong artifact still quarantined and digest-addressed rather than becoming the ordinary handoff object?
4. Are review/share surfaces centered on `packet.capture.summary` or normalized `packet-records-only` derivatives?
5. If decryption material was present, did the workflow keep the stronger secret-bearing file out of the normal promotion/export lane?

## Why this is worth locking now

This is not a new packet-analysis subsystem.
It is a small coherence cut that connects three decisions already made:

- packet capture is a stronger authority lane,
- packet capture review/export is summary-first,
- retained raw artifacts must classify stronger metadata posture explicitly.

This step gives the archive an actual safe-open and promotion story for the stronger cases:

- A keeps incident response viable without ambient risky imports,
- B keeps local troubleshooting visible and bounded,
- C preserves compatibility without weakening the official lane,
- D keeps the appliance/regulatory story credible when risky captures appear.

Last updated: 2026-03-09r242
