# ADR 0002: Public communications as evidence via PublicNotice

**Track:** Shared (cross-cutting)


- Status: **Accepted**
- Date: **2026-02-22**

## Context

During an election incident, adversaries can win by manipulating the **verification ecosystem** and the public narrative:
- forged screenshots / “official” statements,
- split-view comms (different audiences see different updates),
- silent edits and deletions,
- selective disclosure (publishing evidence only where it is convenient).

If comms are not verifiable, later disputes become narrative warfare.

## Decision

Treat operational public communications as a first-class **evidence surface**.

1. Publish verifiable notices as `hfv.public.notice` EvidenceEnvelopes.
   - Payload schema: `schemas/PublicNotice.json`
   - Offline-verifiable example packet: `artifacts/examples/evidence_packet_public_notice/`

2. Require explicit correction linkage.
   - New notices SHOULD use `correction_of_notice_id`.
   - `correction_of` remains a legacy alias for compatibility.

3. Bind notices to a canonical list of official comms surfaces.
   - `PublicNotice.channels` SHOULD reference `channel_id` values in `artifacts/registries/official-channels.csv`.

4. Make authenticity cheap to check across comms surfaces.
   - Use a human-postable digest short form (`tools/public_notice_card.py`) and mirror pointers.
   - Prefer digests / object pointers over screenshots.

Legacy drafting templates remain, but are treated as **worksheets** that map into PublicNotice payload fields.

## Consequences

- Independent observers can confirm what was communicated, when, and whether it was selectively omitted.
- Corrections become auditable (no silent edits).
- Operators gain a bounded, auditable comms surface (channel registry) suitable for parity monitoring.

## Follow-ups

- Add drill scenarios that simulate channel takeover / forged statements and validate parity across channels.
- Add lightweight hardening guidance for official channel surfaces (email/web) as cite-only references.
