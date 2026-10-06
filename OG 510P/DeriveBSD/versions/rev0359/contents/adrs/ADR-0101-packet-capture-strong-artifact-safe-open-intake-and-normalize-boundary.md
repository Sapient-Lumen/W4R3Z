# ADR-0101: Packet-capture strong-artifact safe-open intake and normalize-before-promotion boundary

- Status: Accepted
- Date: 2026-03-09

## Context

`adrs/ADR-0100-packet-capture-local-artifact-metadata-and-retention-boundary.md` already decided that retained raw packet artifacts stay subordinate to the typed packet-capture lane and that stronger cases are explicitly classified as `sideband-metadata-present` or `decryption-material-present`.

That still leaves one practical workflow decision open:
**what is the official way to inspect, normalize, and potentially promote a stronger packet-capture artifact without turning it into an ambient host workflow?**

If the answer is merely “open the `.pcap` / `.pcapng` with your favorite tool”, the archive loses the boundary again:

- foreign or compatibility packet captures become host-open folklore,
- capture-file sideband metadata becomes the real explanation surface,
- decryption-bearing artifacts get treated like ordinary support files,
- and support/export pressure starts promoting the original risky artifact instead of a derived safe review object.

DeriveBSD needs a narrower answer:
**strong packet-capture artifacts should use the existing safe-open import lane, and only normalized packet-records-only derivatives or typed summaries should be eligible for ordinary promotion/export.**

## Decision

1. Keep stronger packet-capture artifacts on the generic import lane.
   - The official inspection path for foreign packet captures, unknown-posture packet captures, and any artifact already classified as `sideband-metadata-present` or `decryption-material-present` is `content.import.plan` → `content.import.receipt`.
   - This remains a specialization of the generic import lane, not a new packet-capture authority kind.

2. Fix one canonical safe-open execution boundary.
   - The official path uses `execution.isolation = microvm`.
   - It uses `execution.network = none`.
   - It uses `execution.lifetime = disposable`.

3. Fix one canonical intake/normalization shape.
   - The archive now carries constrained specialization schemas:
     - `spec/content.import.packet-capture.plan.schema.json`
     - `spec/content.import.packet-capture.receipt.schema.json`
   - Canonical examples keep `kind = content.import.plan` and `kind = content.import.receipt`.
   - The canonical operation sequence is:
     - `scan`
     - `classify`
     - `strip-metadata`

4. Make normalize-before-promotion the default promotion rule.
   - The imported original strong artifact remains quarantined and digest-addressed.
   - Ordinary incident/support workflows may promote or export:
     - a derived `packet.capture.summary`, and/or
     - a derived `packet-records-only` normalized artifact.
   - They must not quietly promote/export the original `sideband-metadata-present` or `decryption-material-present` artifact as the default handoff object.

5. Treat embedded decryption material as a stricter case.
   - `decryption-material-present` artifacts stay on the stronger safe-open lane even when packet bytes themselves are otherwise useful.
   - Any promotion/export path must derive a secret-free normalized artifact or summary instead of treating the original decryption-bearing file as ordinary evidence.

## Consequences

- Packet-capture compatibility remains viable without normalizing host-open `.pcapng` habits.
- The archive now has a concrete implementable path for “risky capture file came from somewhere else” or “capture file posture is stronger than default”.
- Incident/support workflows stay summary-first even when foreign or richer packet captures enter the picture.
- The original strong artifact remains quarantined evidence, while normalized derivatives become the review/share candidates.
- A small guardrail can now keep the typed specialization schemas, examples, and docs aligned.

## Why this is narrow enough

This ADR does **not** standardize:

- the final parser/block inventory backend,
- every compatibility conversion format,
- a full packet-analysis product,
- or the final UX for reviewing normalized outputs.

It only fixes the official intake/promotion posture for the already-decided stronger packet-capture artifact lane.
