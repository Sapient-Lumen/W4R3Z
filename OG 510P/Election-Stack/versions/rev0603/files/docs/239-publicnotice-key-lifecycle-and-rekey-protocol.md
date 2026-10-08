# 239 — PublicNotice key lifecycle + rekey protocol (bounded, digest-first)

**Track:** A (Deployable core)

Docs `186`–`206` treat operational comms as evidence via **PublicNotice**. Doc `208` adds a
pre-committed allow-list (**PublicNoticeSigningKeyset**) so audiences can answer “which keys may speak?”
under attack.

This doc turns “rotation” into an explicit, auditable **lifecycle protocol** without adding new
high-risk surfaces or expanding claim scope.

## 239.1 Goals and non-goals

**Goals**
- Make **key rotation and revocation legible** to verifiers and the public (no “trust me, new key” moments).
- Make rollback / split-view attacks on key authorization **detectable** (hash chain + receipts + gossip).
- Provide a compact, repeatable **emergency rekey** sequence that minimizes rumor vacuum.

**Non-goals**
- This is not a complete PKI spec.
- This doc does not define jurisdiction legal obligations; it defines **evidence discipline**.

## 239.2 Terms (bounded)

- **Keyset:** `hfv.public.notice_signing_keyset` payload (schema `schemas/PublicNoticeSigningKeyset.json`) (`208`).
- **kid:** key identifier used by signers/verifiers; stable within the election scope.
- **status:** `active | retired | revoked` (payload-level semantics; not a cryptographic guarantee).
- **previous_keyset_payload_sha256:** optional hash-chain pointer to the prior keyset (anti-rollback).

## 239.3 Normal rotation (planned, non-emergency)

**Operator sequence (recommended)**

1) **Publish the new keyset payload**
   - Include both old and new keys during the overlap window.
   - Set key statuses (`active` / `retired`) and bounded `valid_from` / `valid_to` when possible.
   - Populate `previous_keyset_payload_sha256` to extend the keyset hash chain (`208`).

2) **Publish the keyset as a receipted + gossiped envelope**
   - Envelope kind: `hfv.public.notice_signing_keyset`.
   - Required attachments: `transparency_receipt` + `gossip_summary` (registry requirements).
   - Update discovery anchors (`203`/`204`) to point at the **new keyset payload digest** (`208`).

3) **Issue a PublicNotice “key rotation” status update**
   - Use a PublicNotice to explain the rotation window and to reference the new keyset payload digest.
   - Keep the message **digest-first** (“verify this by checking keyset digest X”).

**Verifier policy baseline (recommended)**
- Accept PublicNotice signatures from keys marked `active` in the latest keyset for scope.
- Accept signatures from `retired` keys only within the stated overlap window (if provided).
- Treat appearance of an **older keyset** on an official surface as a **split view / rollback** (`201`, `202`, `208`).

## 239.4 Compromise / emergency rekey (hard mode)

When compromise is suspected, the goal is to minimize time-to-clarity while preserving verifiability.

**Emergency sequence (minimal)**

1) **Emit a KeyCompromiseEvent (bounded, factual)**
   - Evidence object: `schemas/KeyCompromiseEvent.json` (see template in `docs/20`).
   - Focus on: what is known, what is not known, and which keys are affected.

2) **Issue a PublicNotice incident advisory referencing the compromise event**
   - Publish quickly (uncertainty-safe language per `219`).
   - State what audiences should trust **now** (e.g., “only notices signed by keys in keyset digest X”).

3) **Publish a new keyset**
   - Mark compromised keys as `revoked`.
   - Include `previous_keyset_payload_sha256` to extend the chain.
   - Ensure receipts + gossip (hard to bury).

4) **Update discovery anchors**
   - `hfv.public.official_channel_directory` and `.well-known` discovery should point to the new keyset digest (`203`, `204`, `208`).

5) **Optional post-incident: transparency + destruction**
   - Use `hfv.key.transparency_entry` and/or `KeyDestructionAttestation` for postmortem closure when appropriate.

**Verifier posture during emergency**
- Prefer the newest receipted keyset digest for the scope (anti-rollback).
- If multiple competing keysets exist, treat this as a **public-surface split view** and escalate (`202`).

## 239.5 Operator hooks (tight)

- **Template:** `artifacts/templates/public-notice-key-rotation-payload.json`
- **Example packet (minimal):** `artifacts/examples/evidence_packet_public_notice_signing_keyset_minimal`
- **Related:** `05` (key management), `186` (comms-as-evidence), `208` (keyset), `199` (security snapshots), `201`/`202` (split views), `216` (incident triage quickmap)

