# Packet-capture evidence joins in incident bundles boundary

**Tier:** B (Cross-cutting product-shape decision)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, operability  
**Patterns:** Bundles, Plan→Apply→Receipt  

`docs/507-packet-capture-session-and-summary-first-export-boundary.md` already made packet capture summary-first.
`docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md` and `docs/512-packet-capture-normalization-redaction-receipt-boundary.md` then fixed the stronger import + normalization story.
This doc fixes the next practical gap:
**how packet-capture evidence officially joins `incident.bundle` / `bundle.plan` without quietly turning support bundles into `.pcap` cargo containers.**

See also:
- ADR: `adrs/ADR-0103-packet-capture-evidence-joins-in-incident-bundles.md`
- incident bundles: `docs/216-incident-snapshots-and-support-bundles.md`
- official support handoff contract: `docs/481-support-bundle-contract-and-timeline-first-handoff.md`
- bundle plans and deterministic exports: `docs/253-bundle-plans-and-deterministic-exports.md`
- packet-capture session/export contract: `docs/507-packet-capture-session-and-summary-first-export-boundary.md`
- packet-capture summary surface: `docs/508-packet-capture-summary-review-surface-boundary.md`
- packet-capture strong-artifact intake boundary: `docs/511-packet-capture-strong-artifact-safe-open-intake-and-normalize-boundary.md`
- packet-capture normalization proof boundary: `docs/512-packet-capture-normalization-redaction-receipt-boundary.md`
- stronger packet-capture export proof boundary: `docs/514-packet-capture-export-proof-chain-and-profile-posture-boundary.md`
- incident-bundle schema: `spec/incident.bundle.schema.json`
- bundle-plan schema: `spec/bundle.plan.schema.json`

## Why this needs a hard decision

The archive already says support bundles should remain summary-first and explainable.
It also already says packet capture should remain session-shaped, summary-first, and proof-bound when stronger imported artifacts are normalized.

But until now the bundle contract still had a hole:

- docs mentioned packet-capture evidence,
- `incident.bundle` had no first-class include knobs for it,
- `bundle.plan` therefore had no first-class selection surface for it,
- and the easiest implementation fallback was either “throw the `.pcapng` in the payload” or “hide packet-capture evidence in `extra`.”

That is expensive ambiguity.
It makes packet capture look implemented in prose while remaining blob-shaped in the one contract support tooling actually needs.

DeriveBSD needs a narrower answer:
**incident/support bundles should carry packet-capture evidence by typed digest joins, while raw packet bytes remain non-default payload members.**

## Accepted boundary

Across all profiles:

- `incident.bundle.scope.include` now has first-class packet-capture selection knobs,
- `incident.bundle.includes` now has first-class packet-capture digest joins,
- `bundle.plan` inherits the same packet-capture selection knobs because it already reuses the `incident.bundle` include-knob surface,
- the ordinary bundle members for packet capture are typed evidence digests (`packet.capture.session`, `packet.capture.summary`, and when relevant `content.import.packet-capture.receipt` + packet-capture `redaction.receipt`),
- and raw packet bytes remain out of the default payload even when a normalized derivative exists.

This keeps packet capture aligned with the bundle contract instead of making bundles the place raw `.pcapng` habits come back.

## Canonical include knobs

The official bundle-selection surface now carries:

- `packet_capture_sessions`
- `packet_capture_summaries`
- `packet_capture_import_receipts`
- `packet_capture_redaction_receipts`

These are deliberately metadata/proof selectors, not blob selectors.
The bundle-plan question stays: *which typed packet-capture evidence objects are part of the handoff?*
Not: *which raw capture file should we smuggle into the tarball?*

## Canonical incident-bundle joins

The official bundle metadata surface now carries:

- `packet_capture_session_digests`
- `packet_capture_summary_digests`
- `packet_capture_import_receipt_digests`
- `packet_capture_redaction_receipt_digests`

That gives one typed explanation chain when packet capture mattered:

1. the authoritative capture session,
2. the compact summary-first review object,
3. the safe-open import receipt when a stronger foreign/richer artifact entered the system,
4. and the deterministic normalization proof when a stronger artifact yielded a promotion-safe derivative.

## Raw bytes remain a stronger separate action

This is the hard decision that makes the rest coherent:
**packet capture can join support bundles without making packet bytes ordinary bundle members.**

In practice:

- the original stronger artifact remains quarantined evidence,
- a normalized `packet-records-only` derivative can be referenced by digest through the import/redaction evidence chain,
- but ordinary support bundles still carry the typed evidence joins rather than the raw payload by default,
- and if raw bytes actually leave the system, that remains a stronger export action governed by export policy / export receipts rather than a quiet side effect of bundle construction.

## Product-shape defaults

| Profile | Default bundle packet-capture posture | Practical meaning |
|---|---|---|
| **A fleet_host** | `session+summary joins default; import/redaction proof joins when used; raw bytes separate` | Oncall bundles can explain packet capture cleanly without normalizing packet blobs into the fleet handoff. |
| **B workstation** | `trusted-ui-visible session+summary joins; stronger lanes stay proof-first` | Local troubleshooting remains shareable, but the trusted UI can keep packet bytes as a deliberate stronger action instead of a hidden bundle member. |
| **C general_os** | `official bundle lane digest-first; adapter tooling may exist separately` | Compatibility remains possible, but the archive keeps one packet-capture support contract that does not depend on legacy bundle folklore. |
| **D appliance_factory** | `metadata/proof-only default; strongest anti-blob posture` | Production/regulatory handoff can include the fact of packet capture and its proofs without making raw packet payloads part of the normal bundle. |

## Review guidance

When reviewing packet-capture support-bundle changes, ask:

1. Does `bundle.plan` select packet-capture evidence through typed include knobs rather than through a free-form “extra files” story?
2. Does `incident.bundle` carry `packet.capture.session` and `packet.capture.summary` digests when packet capture participated?
3. If a stronger imported packet artifact was involved, does the bundle carry the matching import + redaction receipt digests rather than only a safer-looking filename?
4. Are raw packet bytes still a stronger separate export decision rather than a default bundle member?
5. Does the target product shape keep the support/export posture it claims under incident pressure?

## Why this is worth locking now

This is not a new collector or a packet-only support subsystem.
It is a small coherence cut that turns existing packet-capture decisions into something bundle tooling can actually implement:

- A keeps oncall packet troubleshooting explainable,
- B keeps workstation support visible and deliberate,
- C keeps general-purpose compatibility without archive drift,
- D keeps the appliance/regulatory story auditable.

That is enough practical progress for this iteration.

Last updated: 2026-03-09r243
